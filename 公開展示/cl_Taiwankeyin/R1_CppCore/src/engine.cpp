#include "cellkeyin/engine.hpp"
#include "cellkeyin/unicode.hpp"
#include <algorithm>
#include <cmath>
#include <ctime>
#include <iomanip>
#include <sstream>
namespace cellkeyin {
std::string context_key(const std::string& text) {
 if(text.empty())return {};
 uint64_t h=14695981039346656037ULL;
 for(unsigned char c:text) {h^=c;h*=1099511628211ULL;}
 std::ostringstream out;out<<std::hex<<std::setfill('0')<<std::setw(16)<<h;
 return out.str();
}
Engine::Engine(const std::string& db_path):store_(db_path){}
void Engine::set_learning_enabled(bool enabled) {
 if(learning_enabled_!=enabled) context_.clear();
 learning_enabled_=enabled;
}
void Engine::set_sensitive(bool sensitive) {
 sensitive_=sensitive;
 context_.clear(); // no cross-field contamination
}
void Engine::commit(const std::string& text,const std::string& reading) {
 // Validate complete input before accepting any segment or writing the DB.
 const auto units=graphemes(text);
 if(sensitive_)return;
 const bool has_break=std::any_of(units.begin(),units.end(),[](const std::string& u){return hard_break(u);});
 const size_t length=effective_length(text);
 const auto previous_context=context_;
 if(learning_enabled_)store_.begin_transaction();
 try {
  if(learning_enabled_ && !has_break && length>=1 && length<=10)
   store_.record_choice(reading,text,context_key(context_.text()));
  for(const auto& u:units) {
   context_.feed(u);
   if(learning_enabled_&&!hard_break(u)&&!soft_connector(u)) {
    const auto suffixes=context_.suffixes();
    for(size_t i=0;i<suffixes.size();++i)store_.record_phrase(suffixes[i],i+1);
   }
  }
  if(learning_enabled_)store_.commit_transaction();
 }catch(...) {
  context_=previous_context;
  if(learning_enabled_) {try{store_.rollback_transaction();}catch(...){}}
  throw;
 }
}
void Engine::reject(const std::string& candidate) {
 if(sensitive_||!learning_enabled_||candidate.empty())return;
 if(effective_length(candidate)<1||effective_length(candidate)>10)return;
 store_.record_rejection(context_key(context_.text()),candidate);
}
std::vector<Candidate> Engine::rank(const std::string& reading,std::vector<Candidate> candidates) const {
 if(sensitive_||!learning_enabled_) {
  std::stable_sort(candidates.begin(),candidates.end(),[](const Candidate& a,const Candidate& b){return a.base_score>b.base_score;});
  for(auto& c:candidates)c.final_score=c.base_score;
  return candidates;
 }
 const std::string prefix=context_key(context_.text());
 const std::time_t now=std::time(nullptr);
 for(auto& c:candidates) {
  const double freq=static_cast<double>(store_.phrase_count(c.text));
  const double choices=static_cast<double>(store_.choice_count(reading,c.text));
  const double matched=prefix.empty()?0.0:static_cast<double>(store_.edge_count(prefix,c.text));
  const double rejected=static_cast<double>(store_.rejection_count(prefix,c.text));
  const auto last=store_.last_seen(c.text);
  const double age_days=last>0?std::max(0.0,std::difftime(now,static_cast<std::time_t>(last))/86400.0):0.0;
  const double recency=last>0?1.0/(1.0+age_days/30.0):0.0;
  c.final_score=c.base_score+0.8*std::log1p(freq)+1.2*std::log1p(matched)+0.8*std::log1p(choices)+0.3*recency-1.0*rejected;
 }
 std::stable_sort(candidates.begin(),candidates.end(),[](const Candidate& a,const Candidate& b){return a.final_score>b.final_score;});
 return candidates;
}
void Engine::clear_learning() {store_.clear();context_.clear();}
}
