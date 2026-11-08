#include "cellkeyin/engine.hpp"
#include "cellkeyin/unicode.hpp"
#include <cstdio>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>
using namespace cellkeyin;
int tests=0;
void require(bool x,const char* msg){++tests;if(!x)throw std::runtime_error(std::string("FAIL ")+msg);}
int main(){
 try {
  // For safety tests use a per-run dedicated db; no shared user files.
  const std::string path="cellkeyin_r1_test.sqlite3";
  std::remove(path.c_str());std::remove((path+"-wal").c_str());std::remove((path+"-shm").c_str());
  {
   Engine e(path);
   require(graphemes("中文").size()==2,"CJK grapheme split");
   require(graphemes("a\xcc\x81").size()==1,"combining grapheme counts one");
   require(graphemes("👨‍👩‍👧‍👦").size()==1,"emoji ZWJ one grapheme");
   require(effective_length("今天（台南）天氣：好")==7,"soft punctuation excludes effective length");
   require(effective_length("你好。世界")==4,"hard punctuation excludes effective length");
   try{graphemes("\xff");require(false,"invalid UTF8 must throw");}catch(const std::invalid_argument&) {require(true,"UTF8 strict rejection");}
   e.commit("今天（台南）天氣：好");
   require(e.context().text()=="今天（台南）天氣：好","brackets colon maintain context");
   require(e.context().effective_size()==7,"context effective=7");
   require(e.store().phrase_count("今天（台南）天氣：好")==1,"full structure learned");
   e.commit("。明天");
   require(e.context().text()=="明天","hard reset with follow-on");
   require(e.store().phrase_count("好明天")==0,"no cross-sentence association");
   e.reset_context();e.commit("1234567890甲乙");
   require(e.context().text()=="34567890甲乙","10 effective chars sliding");
   require(e.context().effective_size()==10,"bounded context");
   e.reset_context();e.commit("甲〔乙〈丙｛丁｝戊〉己〕庚");
   require(e.context().text()=="甲〔乙〈丙｛丁｝戊〉己〕庚","nested bracket connections");
   e.reset_context();e.commit("台南，安平");
   require(e.context().text()=="安平","comma cuts context");
   require(e.store().phrase_count("台南安平")==0,"comma cuts ngram");
   e.reset_context();e.commit("第一章：起點");
   require(e.store().phrase_count("第一章：起點")>=1,"colon crosses structure");
   e.reset_context();e.commit("甲乙丙丁戊己庚辛壬癸子");
   require(e.store().phrase_count("甲乙丙丁戊己庚辛壬癸子")==0,"no 11-char phrase recorded");
   require(e.store().phrase_count("乙丙丁戊己庚辛壬癸子")>=1,"last 10 valid phrase");
   e.clear_learning();
   const std::vector<Candidate> two={{"在",1.2,0},{"再",1.0,0}};
   require(e.rank("ㄗㄞˋ",two)[0].text=="在","baseline score wins cold start");
   e.commit("再","ㄗㄞˋ"); e.commit("。") ;e.commit("再","ㄗㄞˋ");
   e.reset_context();
   require(e.rank("ㄗㄞˋ",two)[0].text=="再","frequency affects candidate order");
   require(e.store().choice_count("ㄗㄞˋ","再")==2,"choice event count");
   e.clear_learning();
   require(e.rank("ㄗㄞˋ",two)[0].text=="在","clear resets ranking");
   e.commit("我想");const std::string pref=context_key(e.context().text());
   e.commit("練習","ㄌㄧㄢˋ");
   require(e.store().edge_count(pref,"練習")==1,"context relation saved");
   e.reset_context();e.commit("我想");
   auto top=e.rank("ㄌㄧㄢˋ",{{"聯繫",1.0,0},{"練習",0.9,0}});
   require(top[0].text=="練習","context rank wins");
   e.reject("練習");e.reject("練習");e.reject("練習");
   top=e.rank("ㄌㄧㄢˋ",{{"聯繫",1.0,0},{"練習",0.9,0}});
   require(top[0].text=="聯繫","rejections downgrade context choice");
   e.set_learning_enabled(false);
   require(e.context().text().empty(),"learning off clears context boundary");
   const auto seen=e.store().phrase_count("關閉學習");
   e.commit("關閉學習");
   require(e.store().phrase_count("關閉學習")==seen,"no writes disabled");
   e.set_learning_enabled(true);
   e.set_sensitive(true);e.commit("非常秘密資料");
   require(e.context().effective_size()==0,"sensitive clears and blocks current context");
   require(e.store().phrase_count("非常秘密資料")==0,"sensitive no write");
   e.set_sensitive(false);e.commit("測試｛設定｝通過");
   require(e.store().phrase_count("測試｛設定｝通過")==1,"curly bracket relation");
   e.commit("！");require(e.context().text().empty(),"exclamation hard breaks");
   e.commit("ABCDE;EFG");require(e.context().text()=="EFG","halfwidth semicolon hard break");
   e.commit("：新詞");require(e.context().text()=="EFG：新詞","colon soft join");
  }
  {
   Engine e(path);
   require(e.store().phrase_count("測試｛設定｝通過")==1,"persistent reload phrase");
   require(e.context().text().empty(),"relaunch resets immediate context");
   e.clear_learning();
   require(e.store().phrase_count("測試｛設定｝通過")==0,"sqlite clear persisted");
  }
  std::remove(path.c_str());std::remove((path+"-wal").c_str());std::remove((path+"-shm").c_str());
  std::cout<<"PASS "<<tests<<" R1 checks\n";
  return 0;
 }catch(const std::exception& e){std::cerr<<e.what()<<" after "<<tests<<" checks\n";return 1;}
}
