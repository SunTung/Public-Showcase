#include "cellkeyin/zhuyin.hpp"
#include <cstdio>
#include <cmath>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

using namespace cellkeyin;
namespace {
size_t count=0;
void ok(bool yes,const char* title){++count;if(!yes)throw std::runtime_error(std::string("FAIL: ")+title);}
void type(ZhuyinSession& s,const std::string& keys){for(char k:keys)ok(s.key(k),"typed key accepted");}
}
int main(int argc,char** argv) {
 if(argc<2){std::cerr<<"missing seed dictionary\n";return 2;}
 try {
  ok(DachenMap::phonetic_key_count()==37,"all 37 Zhuyin phonetic keys");
  const std::string all="1qaz2wsxedcrfv5tgbyhnujm8ik,9ol.0p;/-";
  const std::string symbols="ㄅㄆㄇㄈㄉㄊㄋㄌㄍㄎㄏㄐㄑㄒㄓㄔㄕㄖㄗㄘㄙㄧㄨㄩㄚㄛㄜㄝㄞㄟㄠㄡㄢㄣㄤㄥㄦ";
  ok(DachenMap::decode(all)==symbols,"37-key mapping matches reference");
  ok(DachenMap::decode(" 6347")=="ˉˊˇˋ˙","five tones correct");
  ok(DachenMap::symbol('Q')=="ㄆ","uppercase key normalization");
  ok(!DachenMap::is_phonetic('6')&&DachenMap::is_tone('6'),"tone isolated from roots");
  ok(DachenMap::symbol('@').empty(),"unsupported key rejected");
  try{(void)DachenMap::decode("@");ok(false,"bad decode must reject");}
  catch(const std::invalid_argument&){ok(true,"bad decode rejects");}

  Lexicon lex; lex.load_tsv(argv[1]);
  ok(lex.entry_count()>=40,"seed has at least 40 entries");
  ok(lex.lookup("ㄋㄧˇ")[0].text=="你","seed lookup is usable");
  ok(lex.lookup("ㄗㄞˋ").size()==2,"homophone list retained");
  ok(lex.lookup("ㄨㄤˉ").empty(),"unknown lookup not invented");
  lex.add("ㄋㄧˇ","你",999);
  ok(lex.lookup("ㄋㄧˇ").size()==1,"duplicate word merges");
  ok(lex.lookup("ㄋㄧˇ")[0].base_score==999,"duplicate keeps best baseline");
  try{lex.add("BAD","字",1);ok(false,"invalid phoneme should fail");}
  catch(const std::invalid_argument&){ok(true,"invalid phoneme fails");}
  try{lex.add("ㄓˋ","長長長長長長長長長長長",1);ok(false,"11 character candidate forbidden");}
  catch(const std::invalid_argument&){ok(true,"11 character candidate forbidden");}
  try{lex.add("ㄓˋ","字",std::nan(""));ok(false,"nan score forbidden");}
  catch(const std::invalid_argument&){ok(true,"nan score forbidden");}

  const std::string db="cellkeyin_r2_test.sqlite3";
  std::remove(db.c_str());std::remove((db+"-wal").c_str());std::remove((db+"-shm").c_str());
  {
   Engine engine(db);ZhuyinSession s(engine,lex);
   ok(!s.key(' '),"tone cannot begin empty syllable");
   ok(!s.key('6'),"second tone cannot begin empty syllable");
   ok(!s.key('@'),"unknown key not consumed");
   ok(s.key('s'),"ㄋ key accepted");
   ok(!s.key('q'),"second initial forbidden");
   ok(s.preedit()=="ㄋ","raw preedit symbol shown");
   ok(s.key('u'),"ㄧ medial accepted");
   ok(!s.key('j'),"second medial forbidden");
   ok(s.preedit()=="ㄋㄧ","preedit maintains raw reading");
   ok(s.key('3'),"third tone accepted");
   ok(s.reading()=="ㄋㄧˇ","tone enters canonical reading");
   ok(s.ready(),"dictionary lookup opened menu");
   ok(s.candidates()[0].text=="你","candidate preview");
   ok(engine.context().effective_size()==0,"preedit creates zero learning context");
   ok(engine.store().choice_count("ㄋㄧˇ","你")==0,"preedit never writes choice stats");
   ok(!s.punctuation("，"),"no punctuation commits while composition pending");
   ok(!s.select(15).has_value(),"invalid candidate index never commits");
   ok(s.select(0).value()=="你","first candidate selected");
   ok(engine.context().text()=="你","only confirmed text reaches R1");
   ok(engine.store().choice_count("ㄋㄧˇ","你")==1,"confirmed reading persisted");
   ok(!s.active(),"after commit resets input state");

   type(s,"cl3");ok(s.select(0).value()=="好","ㄏㄠˇ maps to 好");
   ok(engine.context().text()=="你好","R1 context joins committed syllables");
   ok(s.punctuation("："),"colon commit accepted while idle");
   ok(engine.context().text()=="你好：","colon soft connection preserved");
   ok(s.punctuation("（"),"open paren accepted");
   ok(s.punctuation("）"),"close paren accepted");
   ok(engine.context().text()=="你好：（）","soft brackets do not break history");
   ok(s.punctuation("，"),"comma commit accepted");
   ok(engine.context().text().empty(),"hard sentence break clears live context");

   type(s,"rup ");
   ok(s.ready()&&s.reading()=="ㄐㄧㄣˉ","ㄐㄧㄣ first-tone reading");
   ok(s.candidates()[0].text=="今","first syllable candidates");
   ok(s.key('w'),"second syllable starts without auto commit");
   ok(!s.ready()&&s.preedit()=="ㄐㄧㄣˉ ㄊ","incremental multi-syllable preedit");
   ok(engine.context().text().empty(),"expanding pending composition still no commit");
   ok(s.backspace(),"backspacing tentative second syllable");
   ok(s.ready()&&s.candidates()[0].text=="今","backspace restores previous candidate menu");
   ok(s.key('w'),"continue second syllable after backspace");
   type(s,"u0 ");
   ok(s.reading()=="ㄐㄧㄣˉ ㄊㄧㄢˉ","multi reading separated");
   ok(s.candidates()[0].text=="今天","multi syllable phrase lookup");
   ok(s.select(0).value()=="今天","multi-syllable atomic commit");
   ok(engine.store().choice_count("ㄐㄧㄣˉ ㄊㄧㄢˉ","今天")==1,"phrase reading recorded only at selection");
   ok(engine.context().text()=="今天","phrase occupies two effective characters");

   type(s,"y94");
   ok(s.candidates().size()==2,"在/再 candidates both exist");
   ok(s.candidates()[0].text=="在","lexicon baseline first candidate");
   ok(s.move_selection(1)&&s.selection()==1,"candidate next navigation");
   ok(s.move_selection(1)&&s.selection()==0,"candidate cycling wraps");
   ok(s.move_selection(-1)&&s.selection()==1,"candidate reverse wraps");
   ok(s.select(s.selection()).value()=="再","explicit alternative candidate chosen");
   ok(engine.store().choice_count("ㄗㄞˋ","再")==1,"second candidate becomes learning event");
   ok(s.punctuation("。"),"full stop accepted");
   ok(engine.context().text().empty(),"full stop ends sentence");

   type(s,"su3");
   ok(s.backspace(),"backspace pops tone and reopens syllable");
   ok(s.preedit()=="ㄋㄧ","remove tone yields editable syllable");
   ok(s.backspace(),"backspace medial");
   ok(s.preedit()=="ㄋ","medial removed");
   ok(s.backspace()&&!s.active(),"backspace initial completes cancel");
   ok(!s.backspace(),"empty composition cannot backspace");
   type(s,"su3");s.escape();
   ok(!s.active()&&engine.store().choice_count("ㄋㄧˇ","你")==1,"escape clears without learning");

   type(s,"1");
   ok(!s.key(' '),"non-syllabic initial alone rejected on tone");
   ok(s.preedit()=="ㄅ","partial remains after invalid tone");
   s.escape();
   type(s,"t ");
   ok(s.reading()=="ㄔˉ","standalone retroflex consonant supported");
   ok(s.candidates().empty()&&!s.ready(),"missing lexicon entry cannot invent candidate");
   ok(!s.select(0).has_value(),"unknown candidate blocked");
   s.escape();

   // Adaptive selection with identical phonetics; freeze all preceding context via hard breaks.
   for(int i=0;i<8;++i) {
    type(s,"y94");
    const auto& candidates=s.candidates();
    size_t index=0;while(index<candidates.size()&&candidates[index].text!="再")++index;
    ok(index<candidates.size(),"alternative remains available during adaptive learning");
    ok(s.select(index).value()=="再","selected personalized candidate");
    ok(s.punctuation("。"),"separate training episodes");
   }
   type(s,"y94");
   ok(s.candidates()[0].text=="再","adaptive rank reorders within same reading");
   s.escape();
   engine.set_sensitive(true);
   type(s,"su3");
   ok(s.select(0).value()=="你","sensitive field may still input visible candidate");
   ok(engine.store().choice_count("ㄋㄧˇ","你")==1,"sensitive commit not learned");
   engine.set_sensitive(false);
  }
  {
   Engine engine(db); ZhuyinSession s(engine,lex);
   type(s,"y94");
   ok(s.candidates()[0].text=="再","previous selections persisted across restart");
   s.escape();engine.clear_learning();
   type(s,"y94");
   ok(s.candidates()[0].text=="在","clear learning restores baseline");
  }
  std::remove(db.c_str());std::remove((db+"-wal").c_str());std::remove((db+"-shm").c_str());
  std::cout<<"PASS "<<count<<" R2 checks\n";
  return 0;
 }catch(const std::exception& e){std::cerr<<e.what()<<" after "<<count<<" checks\n";return 1;}
}
