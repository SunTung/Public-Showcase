import tw.cell.taiwankeyin.core.KeyinCore;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

public class KeyinCoreTest {
  static int checks=0;
  static void check(boolean yes,String msg){checks++;if(!yes)throw new AssertionError(msg);}
  static class Learning implements KeyinCore.LearningBackend{
    Map<String,Integer> choice=new HashMap<>(), phrases=new HashMap<>(), edges=new HashMap<>();
    public double candidateBonus(String r,String w,String before){return choice.getOrDefault(r+"|"+w,0)*35.0+edges.getOrDefault(before+"|"+w,0)*20.0;}
    public void learnChoice(String r,String w,String before){choice.merge(r+"|"+w,1,Integer::sum);edges.merge(before+"|"+w,1,Integer::sum);}
    public void rememberPhrases(List<String> suffixes){for(String p:suffixes)phrases.merge(p,1,Integer::sum);}
    public List<String> followups(String context,int limit){
      ArrayList<String> found=new ArrayList<>();if(context.isEmpty())return found;
      for(String suffix:phrases.keySet())if(suffix.startsWith(context)&&suffix.length()>context.length())found.add(suffix.substring(context.length()));
      Collections.sort(found);return found.subList(0,Math.min(limit,found.size()));
    }
    public void erase(){choice.clear();phrases.clear();edges.clear();}
  }
  public static void main(String[] argv)throws Exception{
    check(KeyinCore.KEY_CODES.length()==37,"37 phonetic keys");
    check(KeyinCore.SYMBOLS.length==37,"37 glyphs");
    for(int i=0;i<37;i++){char key=KeyinCore.KEY_CODES.charAt(i);String glyph=KeyinCore.SYMBOLS[i];check(KeyinCore.symbolForKey(key).equals(glyph),"key map "+i);check(KeyinCore.keyForSymbol(glyph)==key,"inverse map "+i);}
    check(KeyinCore.symbolForKey(' ').equals("ˉ"),"1st tone");
    check(KeyinCore.symbolForKey('6').equals("ˊ"),"2nd tone");
    check(KeyinCore.symbolForKey('3').equals("ˇ"),"3rd tone");
    check(KeyinCore.symbolForKey('4').equals("ˋ"),"4th tone");
    check(KeyinCore.symbolForKey('7').equals("˙"),"neutral tone");
    KeyinCore.Context10 ctx=new KeyinCore.Context10();
    for(String u:KeyinCore.units("今天（台南）天氣：好"))ctx.feed(u);
    check(ctx.text().equals("今天（台南）天氣：好"),"soft bridge");
    check(ctx.size()==7,"soft counts");
    ctx.feed("。");ctx.feed("明");ctx.feed("天");
    check(ctx.text().equals("明天"),"break prevents bridging");
    ctx.clear();for(String u:KeyinCore.units("12345678901"))ctx.feed(u);
    check(ctx.text().equals("2345678901"),"ten effective chars cap");
    ctx.clear();for(String u:KeyinCore.units("天地〔星空〕可愛：美麗"))ctx.feed(u);
    check(ctx.size()==8,"nested counted 8");
    check(ctx.suffixes().get(0).equals("麗"),"suffix recent");
    check(KeyinCore.units("A\u0301好").size()==2,"combining cluster");
    check(KeyinCore.units("👩‍💻好").size()==2,"zwj cluster");
    Learning learning=new Learning();KeyinCore.Memory memory=new KeyinCore.Memory(learning);
    KeyinCore.Lexicon lex=new KeyinCore.Lexicon();
    try(InputStream in=new FileInputStream(argv[0])){lex.load(in);}
    check(lex.size()>40,"actual R2 seed loaded");
    KeyinCore.Session s=new KeyinCore.Session(lex,memory);
    check(s.pressKey('s'),"ni initial");check(s.pressKey('u'),"ni medial");check(s.pressKey('3'),"ni tone");
    check(s.preedit().equals("ㄋㄧˇ"),"ni preedit");
    check(!s.candidates().isEmpty(),"ni candidate");
    KeyinCore.Selection chosen=s.choose(0);
    check(chosen!=null&&chosen.text.equals("你"),"select ni");
    check(memory.context().size()==0,"uncommitted does not learn");
    memory.committed(chosen.text,chosen.reading);
    check(memory.context().text().equals("你"),"confirmed learning");
    s.pressKey('c');s.pressKey('l');s.pressKey('3');
    check(s.candidates().get(0).text.equals("好"),"hao candidate");
    chosen=s.choose(0);memory.committed(chosen.text,chosen.reading);
    check(memory.context().text().equals("你好"),"sentence memory");
    check(learning.phrases.containsKey("你好"),"remember phrase");
    memory.resetContext();memory.committed("你", "");
    check(memory.nextSuggestions(5).contains("好"),"predict learned next short phrase");
    memory.resetContext();memory.committed("你好", "");
    memory.committed("（台南）","");
    check(memory.context().text().equals("你好（台南）"),"keep structure in memory");
    memory.committed("。","");
    check(memory.context().size()==0,"hard punctuation clears");
    s.pressKey('r');s.pressKey('u');s.pressKey('p');s.pressKey(' ');
    check(s.candidates().size()>0,"jin single");
    s.pressKey('w');s.pressKey('u');s.pressKey('0');s.pressKey(' ');
    check(s.reading().equals("ㄐㄧㄣˉ ㄊㄧㄢˉ"),"multi syllable");
    check(s.candidates().get(0).text.equals("今天"),"phrase candidate");
    check(s.backspace(),"backspace tone");check(s.backspace(),"backspace partial");
    check(!s.active()||!s.preedit().isEmpty(),"pending state");
    s.clear();check(!s.active(),"escape clears");
    s.pressKey('y');s.pressKey('9');s.pressKey('4');
    check(s.candidates().size()==2,"zai homophones");
    String key=s.reading();check(s.candidates().get(0).text.equals("在"),"baseline");
    for(int i=0;i<5;i++) memory.committed("再",key);
    s.refreshCandidates();
    check(s.candidates().get(0).text.equals("再"),"adaptive over baseline");
    memory.setSensitive(true);memory.committed("保密",key);
    check(!learning.phrases.containsKey("保密"),"privacy excludes text");
    memory.setSensitive(false);memory.erase();s.refreshCandidates();
    check(s.candidates().get(0).text.equals("在"),"erase resets rank");
    // R0R2 regression: tone marks are optional. Space is handled by the Android host
    // as a choose(0) event, not as another first-tone keystroke.
    KeyinCore.Memory noToneMemory=new KeyinCore.Memory(new Learning());
    KeyinCore.Session fast=new KeyinCore.Session(lex,noToneMemory);
    check(fast.pressKey('c'),"hao initial without tone");
    check(fast.candidates().isEmpty(),"partial hao does not offer fabricated candidate");
    check(fast.pressKey('l'),"hao final without tone");
    check(fast.candidates().size()>0,"hao appears without tone key");
    check(fast.candidates().get(0).text.equals("好"),"untuned hao top candidate");
    check(fast.preedit().equals("ㄏㄠ"),"preedit remains untoned");
    check(fast.choose(0).text.equals("好"),"space can select untoned hao");
    check(!fast.active(),"no stuck preedit after space selection");

    check(fast.pressKey('s'),"no-tone ni initial");
    check(fast.pressKey('u'),"no-tone ni medial");
    check(fast.candidates().get(0).text.equals("你"),"ni preview before any tone");
    check(fast.pressKey('c'),"new initial auto-advances ni without tone");
    check(fast.preedit().equals("ㄋㄧ ㄏ"),"syllable boundary inserted automatically");
    check(fast.candidates().isEmpty(),"no incomplete second syllable menu");
    check(fast.pressKey('l'),"finish hao in phrase without tone");
    check(fast.candidates().get(0).text.equals("你好"),"two-syllable phrase without any tones");
    KeyinCore.Selection autoPhrase=fast.choose(0);
    check(autoPhrase.text.equals("你好"),"space commits full untoned phrase");
    check(autoPhrase.reading.equals("ㄋㄧˇ ㄏㄠˇ"),"learning stores resolved dictionary tones");
    check(!fast.active(),"auto boundary phrase clears preedit");
    noToneMemory.committed(autoPhrase.text,autoPhrase.reading);
    check(noToneMemory.context().text().equals("你好"),"auto-commit feeds unchanged CELL Context10");

    check(fast.pressKey('s'),"restart untoned reading");
    check(fast.pressKey('u'),"finish untoned ni again");
    check(fast.pressKey('c'),"start second syllable again");
    check(fast.backspace(),"delete incomplete second syllable");
    check(fast.candidates().get(0).text.equals("你"),"first syllable candidate restored");
    check(fast.backspace(),"reopen prior untoned syllable");
    check(fast.preedit().equals("ㄋㄧ"),"reopened untoned spelling retained");
    check(fast.candidates().get(0).text.equals("你"),"reopened syllable candidates restored");
    fast.clear();

    check(fast.pressKey('y'),"homophone initial");
    check(fast.pressKey('9'),"homophone final");
    check(fast.candidates().size()==2,"no-tone homophones available without tone");
    check(fast.pressKey('4'),"explicit fourth tone remains usable");
    check(fast.reading().equals("ㄗㄞˋ"),"explicit tone is preserved");
    check(fast.candidates().size()==2,"tone-filtered candidates still available");
    check(fast.choose(0)!=null,"explicit tone confirmed");

    check(fast.pressKey('s'),"invalid partial test initial");
    check(!fast.pressKey('c'),"invalid incomplete phonetics must not auto-advance");
    check(fast.preedit().equals("ㄋ"),"bad boundary doesn't discard input");
    check(fast.candidates().isEmpty(),"partial phonetic key has no candidates");
    fast.clear();
    check(lex.lookupFlexible("ㄋㄧ",noToneMemory).size()>=1,"indexed tone-free lexicon lookup");
    check(lex.lookupFlexible("ㄋㄧˊ",noToneMemory).isEmpty(),"explicit mismatched tone strictly filtered");

    // Explicit tone on one syllable must not force a tone on the next one.
    KeyinCore.Session mixed=new KeyinCore.Session(lex,noToneMemory);
    check(mixed.pressKey('s'),"mixed first initial");
    check(mixed.pressKey('u'),"mixed first medial");
    check(mixed.pressKey('3'),"mixed first third tone");
    check(mixed.candidates().get(0).text.equals("你"),"mixed first toned preview");
    check(mixed.pressKey('c'),"next syllable starts after explicit tone");
    check(mixed.pressKey('l'),"next syllable no tone");
    check(mixed.candidates().get(0).text.equals("你好"),"mixed-tone phrase resolved");
    check(mixed.choose(0).reading.equals("ㄋㄧˇ ㄏㄠˇ"),"dictionary supplies missing next tone");

    KeyinCore.Session cap=new KeyinCore.Session(lex,noToneMemory);
    for (int n=0;n<10;n++) {
        check(cap.pressKey('s'),"10-syllable typed initial "+n);
        check(cap.pressKey('u'),"10-syllable typed final "+n);
        check(cap.pressKey('3'),"10-syllable typed tone "+n);
    }
    check(!cap.pressKey('s'),"hard 10-syllable limit prevents hidden overflow");
    check(cap.reading().split(" ").length==10,"10-syllable composition remains intact");


    System.out.println("PASS: "+checks+" Android pure Java keyboard/experience checks");
  }
}
