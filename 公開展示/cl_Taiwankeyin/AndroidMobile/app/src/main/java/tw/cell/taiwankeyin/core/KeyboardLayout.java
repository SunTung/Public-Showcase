package tw.cell.taiwankeyin.core;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

/** Physically aligned Dachen/QWERTY key positions and fully enumerated symbols. */
public final class KeyboardLayout {
    private KeyboardLayout() { }
    // Seven number-row roots sit on top, followed by the familiar Latin keyboard.
    // Five optional tone keys share the top numeric-root strip.
    public static final String[] ZHUYIN_PHYSICAL_ROWS = {
        "125890-", "qwertyuiop", "asdfghjkl;", "zxcvbnm,./"
    };
    public static final String[] LATIN_ROWS = { "qwertyuiop", "asdfghjkl", "zxcvbnm" };
    public static final String[] SYMBOL_PAGE_NAMES = {"常用", "數字", "括號", "數學", "貨幣", "特殊"};
    private static final String[][] SYMBOLS = {
        {"，","。","、","！","？","；","：","…","～","·","「","」","『","』","—","・","\"","'","!","?"},
        {"0","1","2","3","4","5","6","7","8","9",".",",","/","\\","@","#","*","+","-","="},
        {"（","）","〔","〕","〈","〉","｛","｝","【","】","《","》","[","]","{","}","(",")","<",">"},
        {"+","−","×","÷","=","≠","≈","≤","≥","∞","√","∑","∫","π","°","%","‰","±","^","_"},
        {"$","€","£","¥","₩","₹","₽","₫","฿","₱","¢","₿","NT$","USD","EUR","¥","＄","＄","₹","₪"},
        {"@","#","&","*","|","~","`","_","^","\\","/","%","©","®","™","§","¶","•","✓","→"}
    };
    public static String[] page(int index) {
        if (index < 0 || index >= SYMBOLS.length) return new String[0];
        return SYMBOLS[index].clone();
    }
    public static int pages() { return SYMBOLS.length; }
    public static List<String> allZhuyinKeys() {
        List<String> keys = new ArrayList<>();
        for (String row : ZHUYIN_PHYSICAL_ROWS)
            for (int i = 0; i < row.length(); i++) keys.add(KeyinCore.symbolForKey(row.charAt(i)));
        return Collections.unmodifiableList(keys);
    }
    public static final class LatinShift {
        public enum Mode { LOWER, NEXT_UPPER, CAPS_LOCK }
        private Mode mode = Mode.LOWER;
        public Mode mode() { return mode; }
        public void pressShift() {
            mode = (mode == Mode.LOWER ? Mode.NEXT_UPPER :
                    mode == Mode.NEXT_UPPER ? Mode.CAPS_LOCK : Mode.LOWER);
        }
        public void reset() { mode = Mode.LOWER; }
        public String print(char raw) {
            String s = String.valueOf(raw);
            if (mode == Mode.LOWER) return s.toLowerCase(java.util.Locale.ROOT);
            String upper = s.toUpperCase(java.util.Locale.ROOT);
            if (mode == Mode.NEXT_UPPER) mode = Mode.LOWER;
            return upper;
        }
        public String label(char raw) {
            String s = String.valueOf(raw);
            return mode == Mode.LOWER ? s.toLowerCase(java.util.Locale.ROOT)
                    : s.toUpperCase(java.util.Locale.ROOT);
        }
    }
}
