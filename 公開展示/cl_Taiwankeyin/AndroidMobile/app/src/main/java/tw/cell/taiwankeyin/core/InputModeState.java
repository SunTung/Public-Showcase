package tw.cell.taiwankeyin.core;

/** IME input-layer state. English and symbols remain independent of four Chinese scripts. */
public final class InputModeState {
    public enum Layer { CHINESE, ENGLISH, SYMBOLS }
    private ChineseMode chineseMode = ChineseMode.TRAD_ZHUYIN;
    private Layer layer = Layer.CHINESE;

    public ChineseMode chineseMode() { return chineseMode; }
    public Layer layer() { return layer; }
    public boolean isEnglish() { return layer == Layer.ENGLISH; }
    public boolean isSymbols() { return layer == Layer.SYMBOLS; }
    public boolean isPinyin() { return layer == Layer.CHINESE && chineseMode.pinyin; }
    public boolean isSimplified() { return layer == Layer.CHINESE && chineseMode.simplified; }

    public void restoreChineseMode(int id) { chineseMode = ChineseMode.fromId(id); }
    public void cycleChinese() {
        chineseMode = chineseMode.next();
        layer = Layer.CHINESE;
    }
    public void toggleEnglish() {
        layer = layer == Layer.ENGLISH ? Layer.CHINESE : Layer.ENGLISH;
    }
    public void toggleSymbols() {
        layer = layer == Layer.SYMBOLS ? Layer.CHINESE : Layer.SYMBOLS;
    }
    public String englishButton() { return isEnglish() ? "中" : "ABC"; }
    public String symbolsButton() { return isSymbols() ? "中" : "符號"; }
}
