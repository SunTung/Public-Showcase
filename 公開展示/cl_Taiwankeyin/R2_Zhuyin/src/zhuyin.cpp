#include "cellkeyin/zhuyin.hpp"
#include "cellkeyin/unicode.hpp"
#include <algorithm>
#include <cctype>
#include <cmath>
#include <fstream>
#include <set>
#include <stdexcept>
#include <utility>

namespace cellkeyin {
namespace {
constexpr char kKeys[]="1qaz2wsxedcrfv5tgbyhnujm8ik,9ol.0p;/-";
const char* const kSymbols[]={
 "ㄅ","ㄆ","ㄇ","ㄈ","ㄉ","ㄊ","ㄋ","ㄌ","ㄍ","ㄎ","ㄏ","ㄐ","ㄑ","ㄒ",
 "ㄓ","ㄔ","ㄕ","ㄖ","ㄗ","ㄘ","ㄙ","ㄧ","ㄨ","ㄩ",
 "ㄚ","ㄛ","ㄜ","ㄝ","ㄞ","ㄟ","ㄠ","ㄡ","ㄢ","ㄣ","ㄤ","ㄥ","ㄦ"};
static_assert(sizeof(kKeys)-1==sizeof(kSymbols)/sizeof(kSymbols[0]),"Dachen layout mismatch");
std::string normalize(char key) {
 if(key>='A'&&key<='Z')key=static_cast<char>(key-'A'+'a');
 return std::string(1,key);
}
int slot(char ch) {
 std::string key=normalize(ch);
 const auto pos=std::string(kKeys).find(key);
 if(pos==std::string::npos)return -1;
 if(pos<21)return 0; // initial
 if(pos<24)return 1; // medial
 return 2;           // final
}
}
std::string DachenMap::symbol(char c) {
 c=normalize(c)[0];
 const auto position=std::string(kKeys).find(c);
 if(position!=std::string::npos)return kSymbols[position];
 switch(c){case ' ': return "ˉ"; case '6': return "ˊ";case '3':return "ˇ";case '4':return "ˋ";case '7':return "˙";default:return {};}
}
bool DachenMap::is_phonetic(char c){return std::string(kKeys).find(normalize(c)[0])!=std::string::npos;}
bool DachenMap::is_tone(char c){return c==' '||c=='6'||c=='3'||c=='4'||c=='7';}
size_t DachenMap::phonetic_key_count(){return sizeof(kKeys)-1;}
std::string DachenMap::decode(const std::string& keys){
 std::string out;
 for(char c:keys){const auto s=symbol(c);if(s.empty())throw std::invalid_argument("unmapped Dachen key");out+=s;}
 return out;
}
void Lexicon::add(const std::string& r,const std::string& t,double base) {
 if(r.empty()||t.empty()||!std::isfinite(base)||effective_length(t)>10||effective_length(t)<1||r.size()>256)
  throw std::invalid_argument("invalid lexicon entry");
 // Strictly prevent unrecognized reading symbols or Unicode control characters.
 static const std::set<std::string> alphabet=[] {
  std::set<std::string> s;for(char c:std::string(kKeys)+" 6347")s.insert(DachenMap::symbol(c));return s;
 }();
 bool last_space=true;
 for(const auto& c:graphemes(r)) {
  if(c==" ") {if(last_space)throw std::invalid_argument("invalid reading separator");last_space=true;}
  else {if(alphabet.find(c)==alphabet.end())throw std::invalid_argument("invalid reading symbol");last_space=false;}
 }
 if(last_space)throw std::invalid_argument("trailing reading separator");
 auto& candidates=entries_[r];
 for(auto& existing:candidates) {
  if(existing.text==t){existing.base_score=std::max(existing.base_score,base);return;}
 }
 candidates.push_back({t,base,base});++size_;
}
void Lexicon::load_tsv(const std::string& path) {
 std::ifstream in(path,std::ios::binary);
 if(!in)throw std::runtime_error("cannot open lexicon: "+path);
 std::string line;size_t number=0;
 while(std::getline(in,line)) {
  ++number;if(!line.empty()&&line.back()=='\r')line.pop_back();
  if(line.empty()||line[0]=='#')continue;
  const auto a=line.find('\t');const auto b=a==std::string::npos?a:line.find('\t',a+1);
  if(a==std::string::npos||b==std::string::npos||line.find('\t',b+1)!=std::string::npos)
   throw std::invalid_argument("lexicon TSV columns invalid at line "+std::to_string(number));
  try {
   const auto n=line.substr(b+1);size_t used=0;
   const double score=std::stod(n,&used);if(used!=n.size())throw std::invalid_argument("score tail");
   add(line.substr(0,a),line.substr(a+1,b-a-1),score);
  }catch(const std::exception& e){throw std::invalid_argument("lexicon line "+std::to_string(number)+": "+e.what());}
 }
}
std::vector<Candidate> Lexicon::lookup(const std::string& r,size_t limit) const {
 const auto it=entries_.find(r);
 if(it==entries_.end())return {};
 auto results=it->second;
 std::stable_sort(results.begin(),results.end(),[](const Candidate& a,const Candidate& b){return a.base_score>b.base_score;});
 if(results.size()>limit)results.resize(limit);
 return results;
}
ZhuyinSession::ZhuyinSession(Engine& e,const Lexicon& lexicon):engine_(e),lexicon_(lexicon){}
bool ZhuyinSession::valid_prefix(const std::string& raw) {
 if(raw.size()>3)return false;
 int last=-1;
 for(char c:raw){const int s=slot(c);if(s<0||s<=last)return false;last=s;}
 return true;
}
bool ZhuyinSession::valid_syllable(const std::string& raw) {
 if(!valid_prefix(raw)||raw.empty())return false;
 if(raw.size()==1&&slot(raw[0])==0) {
  // The only stand-alone Mandarin initial sounds are ㄓ ㄔ ㄕ ㄖ ㄗ ㄘ ㄙ.
  return std::string("5tgbyhn").find(raw[0])!=std::string::npos;
 }
 return true;
}
void ZhuyinSession::refresh_candidates() {
 menu_.clear();selected_=0;
 if(!raw_.empty()||completed_.empty())return;
 menu_=engine_.rank(reading(),lexicon_.lookup(reading()));
}
bool ZhuyinSession::key(char key) {
 if(DachenMap::is_phonetic(key)) {
  key=normalize(key)[0];
  if(!valid_prefix(raw_+key))return false;
  raw_.push_back(key);menu_.clear();selected_=0;return true;
 }
 if(DachenMap::is_tone(key)) {
  if(!valid_syllable(raw_)||completed_.size()>=10)return false;
  completed_.push_back({raw_,DachenMap::decode(raw_)+DachenMap::symbol(key)});
  raw_.clear();refresh_candidates();return true;
 }
 return false;
}
bool ZhuyinSession::backspace() {
 if(!raw_.empty()) {raw_.pop_back();refresh_candidates();return true;}
 if(!completed_.empty()) {
  raw_=completed_.back().raw;
  completed_.pop_back();menu_.clear();selected_=0;return true;
 }
 return false;
}
void ZhuyinSession::escape(){raw_.clear();completed_.clear();menu_.clear();selected_=0;}
bool ZhuyinSession::move_selection(int delta) {
 if(menu_.empty())return false;
 const auto length=static_cast<long long>(menu_.size());
 selected_=static_cast<size_t>((static_cast<long long>(selected_)+delta%length+length)%length);
 return true;
}
std::optional<std::string> ZhuyinSession::select(size_t idx) {
 if(!ready()||idx>=menu_.size())return std::nullopt;
 const auto chosen=menu_[idx].text;
 const auto key_reading=reading();
 // commit() is the only learning path; this is never called on raw composing keys.
 engine_.commit(chosen,key_reading);
 escape();return chosen;
}
bool ZhuyinSession::punctuation(const std::string& text) {
 if(active()||!(hard_break(text)||soft_connector(text)))return false;
 engine_.commit(text);return true;
}
std::string ZhuyinSession::reading() const {
 std::string output;
 for(const auto& x:completed_) {if(!output.empty())output+=' ';output+=x.reading;}
 return output;
}
std::string ZhuyinSession::preedit() const {
 auto text=reading();
 if(!raw_.empty()) {if(!text.empty())text+=' ';text+=DachenMap::decode(raw_);}
 return text;
}
}
