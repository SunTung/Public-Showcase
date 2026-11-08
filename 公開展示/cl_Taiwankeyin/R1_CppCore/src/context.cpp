#include "cellkeyin/context.hpp"
#include "cellkeyin/unicode.hpp"
#include <algorithm>
namespace cellkeyin {
void Context10::clear() { tokens_.clear(); effective_=0; }
void Context10::feed(const std::string& c) {
 if(hard_break(c)) { clear(); return; }
 const bool effective=!soft_connector(c);
 tokens_.push_back({c,effective});
 if(effective) ++effective_;
 trim();
}
void Context10::trim() {
 while(effective_>kMaxChars || tokens_.size()>32) {
  if(tokens_.front().effective) --effective_;
  tokens_.pop_front();
 }
 // Do not leave punctuation orphaned at the beginning of the clipped window.
 while(!tokens_.empty()&&!tokens_.front().effective) tokens_.pop_front();
}
std::string Context10::text() const {
 std::string t;
 for(const auto& p:tokens_) t+=p.text;
 return t;
}
std::vector<std::string> Context10::suffixes() const {
 std::vector<std::string> out;
 std::string current;
 size_t n=0;
 for(auto it=tokens_.rbegin();it!=tokens_.rend();++it) {
  current=it->text+current;
  if(it->effective) {
   ++n;
   if(n<=kMaxChars) out.push_back(current);
  }
 }
 return out;
}
}
