package tw.cell.taiwankeyin.core;
import java.util.*;
/** Offline Pinyin input. Resolves Pinyin readings against the existing on-device dictionary. */
public final class PinyinComposer {
  private static final Map<String,String> I=new HashMap<>(), F=new HashMap<>();
  static {
    for(String pair:"b=ㄅ p=ㄆ m=ㄇ f=ㄈ d=ㄉ t=ㄊ n=ㄋ l=ㄌ g=ㄍ k=ㄎ h=ㄏ j=ㄐ q=ㄑ x=ㄒ zh=ㄓ ch=ㄔ sh=ㄕ r=ㄖ z=ㄗ c=ㄘ s=ㄙ".split(" ")){String[] x=pair.split("=");I.put(x[0],x[1]);}
    for(String pair:"a=ㄚ o=ㄛ e=ㄜ ai=ㄞ ei=ㄟ ao=ㄠ ou=ㄡ an=ㄢ en=ㄣ ang=ㄤ eng=ㄥ ong=ㄨㄥ er=ㄦ i=ㄧ ia=ㄧㄚ ie=ㄧㄝ iao=ㄧㄠ iu=ㄧㄡ ian=ㄧㄢ in=ㄧㄣ iang=ㄧㄤ ing=ㄧㄥ iong=ㄩㄥ u=ㄨ ua=ㄨㄚ uo=ㄨㄛ uai=ㄨㄞ ui=ㄨㄟ uan=ㄨㄢ un=ㄨㄣ uang=ㄨㄤ ueng=ㄨㄥ v=ㄩ ve=ㄩㄝ van=ㄩㄢ vn=ㄩㄣ".split(" ")){String[] x=pair.split("=");F.put(x[0],x[1]);}
  }
  public static String syllable(String original){
    if(original==null||original.isEmpty())return null;
    String s=original.toLowerCase(Locale.ROOT).replace("ü","v");
    if(Arrays.asList("zhi","chi","shi","ri","zi","ci","si").contains(s))return I.get(s.substring(0,s.length()-1));
    if(s.equals("yi"))s="i"; else if(s.equals("wu"))s="u"; else if(s.equals("yu"))s="v";
    else if(s.startsWith("y")){
      String t=s.substring(1);
      s=t.equals("ou")?"iu":t.equals("in")?"in":t.equals("ing")?"ing":t.equals("ue")?"ve":t.equals("uan")?"van":t.equals("un")?"vn":t.startsWith("u")?"v"+t.substring(1):"i"+t;
    }else if(s.startsWith("w")){
      String t=s.substring(1);s=t.equals("ei")?"ui":t.equals("en")?"un":t.equals("eng")?"ueng":"u"+t;
    }
    String initial="";
    for(String p:new String[]{"zh","ch","sh","b","p","m","f","d","t","n","l","g","k","h","j","q","x","r","z","c","s"})
      if(s.startsWith(p)){initial=p;s=s.substring(p.length());break;}
    if((initial.equals("j")||initial.equals("q")||initial.equals("x"))&&s.startsWith("u"))s="v"+s.substring(1);
    if((initial.equals("n")||initial.equals("l"))&&s.equals("ue"))s="ve";
    if(s.equals("iou"))s="iu";if(s.equals("uei"))s="ui";if(s.equals("uen"))s="un";
    String finalSound=F.get(s);if(finalSound==null)return null;
    return (initial.isEmpty()?"":I.get(initial))+finalSound;
  }
  public interface SimplifiedLookup {
    List<KeyinCore.Candidate> findSimplified(String bareReading, int limit);
  }
  private final KeyinCore.Lexicon lexicon; private final KeyinCore.Memory memory;
  private final SimplifiedLookup simplifiedLookup;
  private final StringBuilder input=new StringBuilder();
  private List<KeyinCore.Candidate> menu=Collections.emptyList();
  public PinyinComposer(KeyinCore.Lexicon l,KeyinCore.Memory m){this(l,m,null);}
  public PinyinComposer(KeyinCore.Lexicon l,KeyinCore.Memory m,SimplifiedLookup s){lexicon=l;memory=m;simplifiedLookup=s;}
  public boolean active(){return input.length()>0;}
  public String preedit(){return input.toString();}
  public List<KeyinCore.Candidate> candidates(){return menu;}
  public void clear(){input.setLength(0);menu=Collections.emptyList();}
  public boolean backspace(){if(!active())return false;input.setLength(input.length()-1);refresh();return true;}
  public boolean type(char c){
    if(input.length()>=48 || !(c>='a'&&c<='z') && c!='\'')return false;
    if(c=='\'' && (input.length()==0 || input.charAt(input.length()-1)=='\''))return false;
    input.append(c);refresh();return true;
  }
  private static void segment(String raw,int pos,List<String> parts,List<String> out){
    if(out.size()>=24)return;
    if(pos==raw.length()){if(!parts.isEmpty())out.add(String.join(" ",parts));return;}
    if(parts.size()>=8)return;
    if(raw.charAt(pos)=='\''){segment(raw,pos+1,parts,out);return;}
    int separator=raw.indexOf('\'',pos);
    for(int end=Math.min(raw.length(),pos+6);end>pos;end--){
      if(separator>=0 && end>separator)continue;
      String reading=syllable(raw.substring(pos,end));if(reading==null)continue;
      parts.add(reading);segment(raw,end,parts,out);parts.remove(parts.size()-1);
    }
  }
  public void refresh(){
    if(!active()){menu=Collections.emptyList();return;}
    List<String> readings=new ArrayList<>();segment(input.toString(),0,new ArrayList<>(),readings);
    Map<String,KeyinCore.Candidate> unique=new LinkedHashMap<>();
    for(String reading:readings){
      List<KeyinCore.Candidate> available = simplifiedLookup == null
          ? lexicon.lookupFlexible(reading,memory)
          : simplifiedLookup.findSimplified(reading,72);
      for(KeyinCore.Candidate c:available){
        double adjusted = simplifiedLookup == null ? c.score : c.baseline + memory.bonus(c.reading,c.text);
        KeyinCore.Candidate candidate = new KeyinCore.Candidate(c.text,c.reading,c.baseline,adjusted);
        KeyinCore.Candidate old=unique.get(candidate.text);
        if(old==null||old.score<candidate.score)unique.put(candidate.text,candidate);
      }
      if(unique.size()>80)break;
    }
    List<KeyinCore.Candidate> ranked=new ArrayList<>(unique.values());
    ranked.sort(Comparator.comparingDouble((KeyinCore.Candidate c)->c.score).reversed());
    menu=Collections.unmodifiableList(ranked.subList(0,Math.min(24,ranked.size())));
  }
}
