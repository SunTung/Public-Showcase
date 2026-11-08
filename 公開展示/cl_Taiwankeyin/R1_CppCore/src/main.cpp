#include "cellkeyin/engine.hpp"
#include <iostream>
#include <sstream>
#include <string>
#include <vector>
int main(int argc,char** argv) {
 try {
  const std::string db=argc>1?argv[1]:":memory:";
  cellkeyin::Engine e(db);
  std::cout<<"CELL TaiwanKeyin R1 core CLI (NOT TSF IME)\nCommands: commit <text> | choose <reading> <word> | rank <reading> <candidate...> | reject <word> | context | clear | quit\n";
  std::string line;
  while(std::getline(std::cin,line)) {
   std::istringstream in(line);std::string cmd;in>>cmd;
   if(cmd=="quit")break;
   if(cmd=="commit") {std::string s;std::getline(in>>std::ws,s);e.commit(s);}
   else if(cmd=="choose") {std::string r,w;in>>r>>w;e.commit(w,r);}
   else if(cmd=="rank") {
    std::string r,w;in>>r;std::vector<cellkeyin::Candidate> cs;
    while(in>>w)cs.push_back({w,0,0});
    for(const auto& c:e.rank(r,cs))std::cout<<c.text<<" score="<<c.final_score<<"\n";
   }
   else if(cmd=="reject") {std::string w;in>>w;e.reject(w);}
   else if(cmd=="context")std::cout<<e.context().text()<<" ("<<e.context().effective_size()<<" chars)\n";
   else if(cmd=="clear")e.clear_learning();
   else std::cout<<"Unknown command\n";
  }
 }catch(const std::exception& e){std::cerr<<"error: "<<e.what()<<"\n";return 1;}
}
