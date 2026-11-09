package tw.cell.taiwankeyin.core;

/** One-button, four-state Chinese input selector. Persist ordinal via stable id. */
public enum ChineseMode {
    TRAD_ZHUYIN("繁注",false,false),
    SIMP_ZHUYIN("簡注",false,true),
    TRAD_PINYIN("繁拼",true,false),
    SIMP_PINYIN("簡拼",true,true);

    public final String label;
    public final boolean pinyin;
    public final boolean simplified;
    ChineseMode(String label,boolean pinyin,boolean simplified){
        this.label=label;this.pinyin=pinyin;this.simplified=simplified;
    }
    public ChineseMode next(){return values()[(ordinal()+1)%values().length];}
    public static ChineseMode fromId(int id){
        return id>=0&&id<values().length?values()[id]:TRAD_ZHUYIN;
    }
}
