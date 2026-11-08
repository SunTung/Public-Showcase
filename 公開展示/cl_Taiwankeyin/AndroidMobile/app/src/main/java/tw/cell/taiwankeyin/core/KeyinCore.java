package tw.cell.taiwankeyin.core;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.Deque;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Android host-independent Java implementation of the confirmed R1/R2 input contracts.
 * R1/R2 C++ sources remain unchanged. This is a functional Java port, not JNI of C++.
 */
public final class KeyinCore {
    private KeyinCore() {}

    // Exact Dachen layout copied as a verified behavioral mapping, not external IME code.
    public static final String KEY_CODES = "1qaz2wsxedcrfv5tgbyhnujm8ik,9ol.0p;/-";
    public static final String[] SYMBOLS = {
        "ㄅ","ㄆ","ㄇ","ㄈ","ㄉ","ㄊ","ㄋ","ㄌ","ㄍ","ㄎ","ㄏ","ㄐ","ㄑ","ㄒ",
        "ㄓ","ㄔ","ㄕ","ㄖ","ㄗ","ㄘ","ㄙ","ㄧ","ㄨ","ㄩ",
        "ㄚ","ㄛ","ㄜ","ㄝ","ㄞ","ㄟ","ㄠ","ㄡ","ㄢ","ㄣ","ㄤ","ㄥ","ㄦ"
    };
    public static final String[] TONE_LABELS = {"ˉ", "ˊ", "ˇ", "ˋ", "˙"};
    public static final char[] TONE_KEYS = {' ', '6', '3', '4', '7'};

    public static String symbolForKey(char key) {
        int idx = KEY_CODES.indexOf(Character.toLowerCase(key));
        if (idx >= 0) return SYMBOLS[idx];
        for (int i = 0; i < TONE_KEYS.length; i++) if (key == TONE_KEYS[i]) return TONE_LABELS[i];
        return "";
    }
    public static char keyForSymbol(String symbol) {
        for (int i = 0; i < SYMBOLS.length; i++) if (SYMBOLS[i].equals(symbol)) return KEY_CODES.charAt(i);
        for (int i = 0; i < TONE_LABELS.length; i++) if (TONE_LABELS[i].equals(symbol)) return TONE_KEYS[i];
        return '\0';
    }
    public static boolean hardBreak(String s) { return "，。！？、；,.!?;\r\n".contains(s) && !s.isEmpty(); }
    public static boolean softConnector(String s) { return "（）〔〕〈〉｛｝：".contains(s) && !s.isEmpty(); }

    /** Unicode grapheme-like clusters, preserving combining marks, ZWJ and variation selectors.
     * This deliberately does not claim full UAX #29 coverage on every Android API level. */
    public static List<String> units(String text) {
        List<String> out = new ArrayList<>();
        StringBuilder current = new StringBuilder();
        boolean joinNext = false;
        for (int i = 0; i < text.length();) {
            int code = text.codePointAt(i);
            i += Character.charCount(code);
            int kind = Character.getType(code);
            boolean attach = kind == Character.NON_SPACING_MARK || kind == Character.COMBINING_SPACING_MARK
                    || kind == Character.ENCLOSING_MARK || (code >= 0xFE00 && code <= 0xFE0F)
                    || (code >= 0x1F3FB && code <= 0x1F3FF) || code == 0x200D;
            if (current.length() > 0 && !attach && !joinNext) {
                out.add(current.toString());
                current.setLength(0);
            }
            current.appendCodePoint(code);
            joinNext = code == 0x200D;
        }
        if (current.length() > 0) out.add(current.toString());
        return out;
    }

    private static final class Token {
        final String text; final boolean effective;
        Token(String text, boolean effective) { this.text = text; this.effective = effective; }
    }
    public static final class Context10 {
        private final Deque<Token> tokens = new ArrayDeque<>();
        private int effective;
        public void clear() { tokens.clear(); effective = 0; }
        public void feed(String unit) {
            if (hardBreak(unit)) { clear(); return; }
            boolean actual = !softConnector(unit);
            tokens.addLast(new Token(unit, actual));
            if (actual) effective++;
            while (effective > 10 || tokens.size() > 32) {
                if (tokens.removeFirst().effective) effective--;
            }
            while (!tokens.isEmpty() && !tokens.peekFirst().effective) tokens.removeFirst();
        }
        public int size() { return effective; }
        public String text() {
            StringBuilder b = new StringBuilder();
            for (Token t : tokens) b.append(t.text);
            return b.toString();
        }
        public List<String> suffixes() {
            ArrayList<Token> copy = new ArrayList<>(tokens);
            List<String> result = new ArrayList<>();
            String current = "";
            int n = 0;
            for (int i = copy.size() - 1; i >= 0; i--) {
                Token t = copy.get(i);
                current = t.text + current;
                if (t.effective && ++n <= 10) result.add(current);
            }
            return result;
        }
    }

    public interface LearningBackend {
        double candidateBonus(String reading, String text, String beforeContext);
        void learnChoice(String reading, String text, String beforeContext);
        void rememberPhrases(List<String> suffixes);
        List<String> followups(String context, int limit);
        void erase();
    }
    public static final class Memory {
        private final Context10 context = new Context10();
        private final LearningBackend backend;
        private boolean learning = true;
        private boolean sensitive = false;
        public Memory(LearningBackend backend) { this.backend = backend; }
        public Context10 context() { return context; }
        public void resetContext() { context.clear(); }
        public void setLearning(boolean on) { learning = on; }
        public void setSensitive(boolean on) { sensitive = on; if (on) context.clear(); }
        public boolean learning() { return learning; }
        public boolean sensitive() { return sensitive; }
        public double bonus(String reading, String word) {
            if (sensitive || !learning) return 0;
            return backend.candidateBonus(reading, word, context.text());
        }
        /** Must only be called after InputConnection.commitText has returned true. */
        public void committed(String text, String reading) {
            if (sensitive) return;
            String before = context.text();
            if (learning && reading != null && !reading.isEmpty()) backend.learnChoice(reading, text, before);
            for (String unit : units(text)) {
                context.feed(unit);
                if (learning && !hardBreak(unit) && !softConnector(unit)) {
                    backend.rememberPhrases(context.suffixes());
                }
            }
        }
        public List<String> nextSuggestions(int limit) {
            if (sensitive || !learning || limit < 1) return Collections.emptyList();
            return backend.followups(context.text(), limit);
        }
        public void erase() { backend.erase(); context.clear(); }
    }

    public static final class Candidate {
        public final String text;
        public final String reading;
        public final double baseline;
        public final double score;
        public Candidate(String text, String reading, double baseline, double score) {
            this.text = text; this.reading = reading; this.baseline = baseline; this.score = score;
        }
    }
    public static final class Lexicon {
        private final Map<String, Map<String, Double>> values = new HashMap<>();
        private int count;
        public void add(String reading, String word, double baseline) {
            if (reading == null || reading.isEmpty() || word == null || word.isEmpty()
                    || reading.length() > 256 || !reading.matches("[ㄅ-ㄩㄚ-ㄦˉˊˇˋ˙ ]+")
                    || word.contains("\n") || word.contains("\r") || word.contains("\t")
                    || units(word).size() > 10 || !Double.isFinite(baseline)) return;
            Map<String, Double> rows = values.computeIfAbsent(reading, k -> new HashMap<>());
            if (!rows.containsKey(word)) count++;
            rows.merge(word, baseline, Math::max);
        }
        public int size() { return count; }
        public void load(InputStream stream) throws IOException {
            try (BufferedReader reader = new BufferedReader(new InputStreamReader(stream, StandardCharsets.UTF_8))) {
                String line;
                while ((line = reader.readLine()) != null) {
                    if (line.startsWith("#") || line.trim().isEmpty()) continue;
                    String[] pieces = line.split("\t", -1);
                    if (pieces.length != 3) continue;
                    try { add(pieces[0], pieces[1], Double.parseDouble(pieces[2])); }
                    catch (NumberFormatException ignored) { /* skip malformed record */ }
                }
            }
        }
        public List<Candidate> lookup(String reading, Memory memory) {
            Map<String, Double> rows = values.get(reading);
            if (rows == null) return Collections.emptyList();
            List<Candidate> found = new ArrayList<>();
            for (Map.Entry<String, Double> row : rows.entrySet()) {
                double bonus = memory.bonus(reading, row.getKey());
                found.add(new Candidate(row.getKey(), reading, row.getValue(), row.getValue() + bonus));
            }
            found.sort(Comparator.comparingDouble((Candidate c) -> c.score).reversed()
                    .thenComparing(c -> c.text));
            return found;
        }
    }
    private static final class Syllable {
        final String keys; final String reading;
        Syllable(String keys, String reading) { this.keys = keys; this.reading = reading; }
    }
    public static final class Selection {
        public final String text;
        public final String reading;
        Selection(String text, String reading) { this.text = text; this.reading = reading; }
    }
    public static final class Session {
        private final Lexicon lexicon;
        private final Memory memory;
        private final StringBuilder raw = new StringBuilder();
        private final List<Syllable> completed = new ArrayList<>();
        private List<Candidate> menu = Collections.emptyList();
        public Session(Lexicon lexicon, Memory memory) { this.lexicon = lexicon; this.memory = memory; }
        private int slot(char c) {
            int pos = KEY_CODES.indexOf(Character.toLowerCase(c));
            if (pos < 0) return -1;
            return pos < 21 ? 0 : pos < 24 ? 1 : 2;
        }
        private boolean validPrefix(String keys) {
            if (keys.isEmpty() || keys.length() > 3) return false;
            int previous = -1;
            for (int i = 0; i < keys.length(); i++) {
                int next = slot(keys.charAt(i));
                if (next < 0 || next <= previous) return false;
                previous = next;
            }
            return true;
        }
        private boolean validSyllable() {
            if (!validPrefix(raw.toString())) return false;
            return !(raw.length() == 1 && slot(raw.charAt(0)) == 0
                    && "5tgbyhn".indexOf(raw.charAt(0)) < 0);
        }
        public boolean pressKey(char key) {
            key = Character.toLowerCase(key);
            int pos = KEY_CODES.indexOf(key);
            if (pos >= 0) {
                if (!validPrefix(raw.toString() + key)) return false;
                raw.append(key);
                menu = Collections.emptyList();
                return true;
            }
            String tone = symbolForKey(key);
            boolean isTone = key == ' ' || key == '6' || key == '3' || key == '4' || key == '7';
            if (!isTone || !validSyllable() || completed.size() >= 10) return false;
            StringBuilder reading = new StringBuilder();
            for (int i = 0; i < raw.length(); i++) reading.append(symbolForKey(raw.charAt(i)));
            completed.add(new Syllable(raw.toString(), reading + tone));
            raw.setLength(0);
            refresh();
            return true;
        }
        public boolean pressSymbol(String symbol) {
            char key = keyForSymbol(symbol);
            return key != '\0' && pressKey(key);
        }
        public boolean backspace() {
            if (raw.length() > 0) {
                raw.setLength(raw.length() - 1);
                refresh();
                return true;
            }
            if (!completed.isEmpty()) {
                raw.append(completed.remove(completed.size() - 1).keys);
                menu = Collections.emptyList();
                return true;
            }
            return false;
        }
        public void clear() { raw.setLength(0); completed.clear(); menu = Collections.emptyList(); }
        public boolean active() { return raw.length() > 0 || !completed.isEmpty(); }
        public String reading() {
            StringBuilder out = new StringBuilder();
            for (Syllable s : completed) {
                if (out.length() > 0) out.append(' ');
                out.append(s.reading);
            }
            return out.toString();
        }
        public String preedit() {
            StringBuilder out = new StringBuilder(reading());
            if (raw.length() > 0) {
                if (out.length() > 0) out.append(' ');
                for (int i = 0; i < raw.length(); i++) out.append(symbolForKey(raw.charAt(i)));
            }
            return out.toString();
        }
        public List<Candidate> candidates() { return menu; }
        private void refresh() {
            if (raw.length() > 0 || completed.isEmpty()) { menu = Collections.emptyList(); return; }
            String reading = reading();
            List<Candidate> matches = new ArrayList<>(lexicon.lookup(reading, memory));
            if (matches.isEmpty() && completed.size() > 1) {
                StringBuilder composed = new StringBuilder();
                double baseline = 0;
                for (Syllable s : completed) {
                    List<Candidate> one = lexicon.lookup(s.reading, memory);
                    if (one.isEmpty()) { composed.setLength(0); break; }
                    composed.append(one.get(0).text);
                    baseline += one.get(0).baseline;
                }
                if (composed.length() > 0) matches.add(new Candidate(composed.toString(), reading,
                        baseline * 0.50, baseline * 0.50 + memory.bonus(reading, composed.toString())));
            }
            menu = Collections.unmodifiableList(matches.size() > 24 ? matches.subList(0, 24) : matches);
        }
        public Selection choose(int index) {
            if (raw.length() != 0 || index < 0 || index >= menu.size()) return null;
            Candidate chosen = menu.get(index);
            Selection result = new Selection(chosen.text, reading());
            clear();
            return result;
        }
        public void refreshCandidates() { refresh(); }
    }
}
