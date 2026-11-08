#include "cellkeyin/zhuyin.hpp"
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>

int main(int argc,char** argv) {
 if(argc<2){std::cerr<<"Usage: cellkeyin_r2_cli DICTIONARY.tsv [user.sqlite3|:memory:]\n";return 2;}
 try {
  cellkeyin::Lexicon lex;lex.load_tsv(argv[1]);
  cellkeyin::Engine engine(argc>2?argv[2]:":memory:");
  cellkeyin::ZhuyinSession s(engine,lex);
  std::cout<<"CELL TaiwanKeyin R2 headless Zhuyin, NOT a Windows TSF IME.\n"
   <<"Commands: key <raw_Dachen_key_or_space> | tone <1|2|3|4|5> | backspace | escape | next | prev | choose <1-based> | punct <punctuation> | context | quit\n";
  std::string line;
  while(std::getline(std::cin,line)) {
   std::istringstream in(line);std::string cmd;in>>cmd;
   if(cmd=="quit")break;
   bool accepted=true;
   if(cmd=="key"){
    std::string arg;in>>arg;
    accepted=s.key(arg=="space"?' ':arg.size()==1?arg[0]:'\0');
   } else if(cmd=="tone"){
    std::string arg;in>>arg;const char k=arg=="1"?' ':arg=="2"?'6':arg=="3"?'3':arg=="4"?'4':arg=="5"?'7':'\0';accepted=s.key(k);
   } else if(cmd=="backspace")accepted=s.backspace();
   else if(cmd=="escape")s.escape();
   else if(cmd=="next")accepted=s.move_selection(1);
   else if(cmd=="prev")accepted=s.move_selection(-1);
   else if(cmd=="choose"){
    size_t i=0;in>>i;
    const auto committed=s.select(i>0?i-1:static_cast<size_t>(-1));
    accepted=committed.has_value();if(committed)std::cout<<"COMMIT "<<*committed<<"\n";
   } else if(cmd=="punct") {
    std::string text;in>>text;accepted=s.punctuation(text);
    if(accepted)std::cout<<"COMMIT "<<text<<"\n";
   } else if(cmd=="context")std::cout<<"CONTEXT "<<engine.context().text()<<"\n";
   else {std::cout<<"unknown command\n";continue;}
   if(!accepted)std::cout<<"REJECTED\n";
   std::cout<<"PREEDIT "<<s.preedit()<<"\n";
   auto c=s.candidates();for(size_t i=0;i<c.size()&&i<9;++i)
    std::cout<<(s.selection()==i?">":" ")<<(i+1)<<" "<<c[i].text<<" ["<<c[i].final_score<<"]\n";
  }
 }catch(const std::exception& e){std::cerr<<"error: "<<e.what()<<"\n";return 1;}
}
