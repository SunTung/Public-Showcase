#include "cellkeyin/zhuyin.hpp"
#include "cellkeyin/unicode.hpp"
#include <unicode/translit.h>
#include <unicode/unistr.h>
#include <algorithm>
#include <fstream>
#include <iostream>
#include <memory>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {
std::string convert(icu::Transliterator& translator,const std::string& pinyin) {
 if(pinyin.size()<2 || pinyin.back()<'1'||pinyin.back()>'5')return {};
 for(size_t i=0;i+1<pinyin.size();++i) {
  const unsigned char x=static_cast<unsigned char>(pinyin[i]);
  if(!((x>='a'&&x<='z')||(x>='A'&&x<='Z')||x==':'||x==0xc3||x==0xbc))return {};
 }
 icu::UnicodeString value=icu::UnicodeString::fromUTF8(pinyin);
 translator.transliterate(value);
 std::string result;value.toUTF8String(result);
 if(pinyin.back()=='1')result+="ˉ";
 // ICU's Latin-Bopomofo omits the first-tone marker, requiring explicit ˉ.
 const std::string tone[5]={"ˉ","ˊ","ˇ","ˋ","˙"};
 const auto expected=tone[pinyin.back()-'1'];
 if(result.size()<expected.size()||result.substr(result.size()-expected.size())!=expected)return {};
 // Require only Bopomofo phonetic symbols and the explicit final tone.
 const std::string alphabet="ㄅㄆㄇㄈㄉㄊㄋㄌㄍㄎㄏㄐㄑㄒㄓㄔㄕㄖㄗㄘㄙㄧㄨㄩㄚㄛㄜㄝㄞㄟㄠㄡㄢㄣㄤㄥㄦ";
 for(const auto& glyph:cellkeyin::graphemes(result.substr(0,result.size()-expected.size()))) {
  if(alphabet.find(glyph)==std::string::npos)return {};
 }
 return result;
}
std::vector<std::string> split(const std::string& value,char c) {
 std::vector<std::string> result;
 std::stringstream ss(value);std::string item;
 while(std::getline(ss,item,c))result.push_back(item);
 return result;
}
}
int main(int argc,char** argv) {
 if(argc!=3) {
  std::cerr<<"Usage: cellkeyin_import_terra SOURCE_TERRA_PINYIN_YAML OUTPUT_ZHUYIN_TSV\n";
  return 2;
 }
 try {
  std::ifstream source(argv[1],std::ios::binary);
  if(!source)throw std::runtime_error("cannot open upstream source dictionary");
  UErrorCode status=U_ZERO_ERROR;
  std::unique_ptr<icu::Transliterator> translator(
    icu::Transliterator::createInstance("Latin-Bopomofo",UTRANS_FORWARD,status));
  if(U_FAILURE(status)||!translator)throw std::runtime_error("ICU Latin-Bopomofo transliterator unavailable");
  cellkeyin::Lexicon validation;
  std::set<std::string> seen;
  std::vector<std::string> rows;
  size_t total=0, accepted=0, skipped=0, duplicates=0;
  bool started=false;
  std::string line;
  while(std::getline(source,line)) {
   if(!line.empty()&&line.back()=='\r')line.pop_back();
   if(!started){if(line=="...")started=true;continue;}
   if(line.empty()||line[0]=='#')continue;
   ++total;
   const auto fields=split(line,'\t');
   if(fields.size()<2||fields.size()>3||fields[0].empty()||fields[1].empty()) {++skipped;continue;}
   if(cellkeyin::effective_length(fields[0])<1||cellkeyin::effective_length(fields[0])>10){++skipped;continue;}
   std::istringstream parts(fields[1]);std::string word;
   std::string reading;size_t syllables=0;
   bool valid=true;
   while(parts>>word) {
    const auto value=convert(*translator,word);
    if(value.empty()){valid=false;break;}
    if(!reading.empty())reading+=' ';
    reading+=value;++syllables;
   }
   if(!valid||syllables!=cellkeyin::effective_length(fields[0])){++skipped;continue;}
   const auto uniqueness=reading+"\t"+fields[0];
   if(!seen.insert(uniqueness).second){++duplicates;continue;}
   // Exported baseline is intentionally uniform; individualized ranking is learned independently.
   constexpr double baseline=10.0;
   try{validation.add(reading,fields[0],baseline);}catch(const std::exception&){++skipped;continue;}
   rows.push_back(reading+"\t"+fields[0]+"\t10");++accepted;
  }
  if(!started)throw std::runtime_error("Rime YAML end-of-header marker (...) missing");
  if(accepted==0)throw std::runtime_error("no valid imported rows");
  const std::string temp=std::string(argv[2])+".partial";
  {
   std::ofstream out(temp,std::ios::binary|std::ios::trunc);
   if(!out)throw std::runtime_error("cannot open temporary TSV");
   out<<"# CELL TaiwanKeyin generated reading lexicon\n"
      <<"# Source: Rime Terra Pinyin. Retain original provenance and licensing notices.\n";
   for(const auto& row:rows)out<<row<<"\n";
   out.flush();if(!out)throw std::runtime_error("TSV write failed");
  }
  // Platform-portable replacement on a fresh target path; caller chooses a new filename.
  {std::ifstream existing(argv[2]);if(existing)throw std::runtime_error("output exists; refusing overwrite (temporary file remains)");}
  if(std::rename(temp.c_str(),argv[2])!=0)throw std::runtime_error("cannot finalize output TSV");
  std::cout<<"source_records="<<total<<" accepted="<<accepted<<" skipped="<<skipped
           <<" duplicate="<<duplicates<<"\n";
 }catch(const std::exception& e){std::cerr<<"IMPORT ERROR: "<<e.what()<<"\n";return 1;}
}
