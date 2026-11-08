#include "cellkeyin/zhuyin.hpp"
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
int main(int argc,char** argv){
 if(argc!=2)return 2;
 try{
  cellkeyin::Lexicon lex;lex.load_tsv(argv[1]);
  const auto check=[&](const std::string& reading,const std::string& word){
   for(const auto& x:lex.lookup(reading))if(x.text==word)return;
   throw std::runtime_error("missing "+word+" / "+reading);
  };
  check("ㄋㄧˇ","你");check("ㄏㄠˇ","好");check("ㄋㄧˇ ㄏㄠˇ","你好");
  check("ㄊㄞˊ ㄋㄢˊ","台南");check("ㄓㄨˋ ㄧㄣˉ","注音");
  check("ㄓㄨㄥˉ","中");check("ㄋㄩˇ","女");check("ㄋㄩˇ ㄦˊ","女兒");
  if(lex.entry_count()!=8)throw std::runtime_error("accepted row total mismatch");
  std::cout<<"PASS 9 R2-B importer checks\n";
 }catch(const std::exception& e){std::cerr<<e.what()<<"\n";return 1;}
}
