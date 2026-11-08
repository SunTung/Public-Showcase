package tw.cell.taiwankeyin.android;

import android.content.SharedPreferences;
import android.graphics.Color;
import android.graphics.Typeface;
import android.inputmethodservice.InputMethodService;
import android.text.InputType;
import android.view.Gravity;
import android.view.KeyEvent;
import android.view.View;
import android.view.inputmethod.EditorInfo;
import android.view.inputmethod.InputConnection;
import android.widget.Button;
import android.widget.HorizontalScrollView;
import android.widget.LinearLayout;
import android.widget.Space;
import android.widget.TextView;
import tw.cell.taiwankeyin.core.KeyinCore;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.util.List;

public final class TaiwanKeyinImeService extends InputMethodService {
    private static final int BACKGROUND = Color.rgb(22, 30, 43);
    private static final int PANEL = Color.rgb(39, 51, 70);
    private static final int ACCENT = Color.rgb(63, 149, 229);
    private static final int WHITE = Color.rgb(244, 247, 252);
    private static final String LEXICON = "imported_lexicon.tsv";
    private static final int PHONETIC_COLUMNS = 10; // Uniform 10-column touch targets across all Zhuyin rows.
    private ExperienceDatabase store;
    private KeyinCore.Memory memory;
    private KeyinCore.Lexicon lexicon;
    private KeyinCore.Session session;
    private long lastLexiconModification = Long.MIN_VALUE;
    private LinearLayout root;
    private LinearLayout candidateRow;
    private LinearLayout keysArea;
    private TextView preedit;
    private boolean englishMode;
    private boolean symbolMode;
    private boolean sensitiveField;

    private int dp(float value) { return Math.round(value * getResources().getDisplayMetrics().density); }
    private SharedPreferences prefs() { return getSharedPreferences("keyboard_settings", MODE_PRIVATE); }

    @Override public void onCreate() {
        super.onCreate();
        store = new ExperienceDatabase(this);
        memory = new KeyinCore.Memory(store);
        reloadLexicon();
        memory.setLearning(prefs().getBoolean("learning", true));
    }
    private void reloadLexicon() {
        File imported = new File(getFilesDir(), LEXICON);
        long stamp = imported.exists() ? imported.lastModified() : -1L;
        if (lexicon != null && stamp == lastLexiconModification) return;
        KeyinCore.Lexicon next = new KeyinCore.Lexicon();
        try {
            next.load(getAssets().open("seed_zhuyin_tw.tsv"));
            if (imported.exists()) try (FileInputStream in = new FileInputStream(imported)) { next.load(in); }
            lexicon = next;
            lastLexiconModification = stamp;
            session = new KeyinCore.Session(lexicon, memory);
        } catch (IOException ex) {
            // Retain the previous dictionary if a user-imported file is invalid/unreadable.
            if (lexicon == null) { lexicon = next; session = new KeyinCore.Session(lexicon, memory); }
        }
    }
    private static boolean isPassword(EditorInfo info) {
        if (info == null) return false;
        int cls = info.inputType & InputType.TYPE_MASK_CLASS;
        int var = info.inputType & InputType.TYPE_MASK_VARIATION;
        return cls == InputType.TYPE_CLASS_TEXT && (var == InputType.TYPE_TEXT_VARIATION_PASSWORD
                || var == InputType.TYPE_TEXT_VARIATION_VISIBLE_PASSWORD
                || var == InputType.TYPE_TEXT_VARIATION_WEB_PASSWORD)
                || cls == InputType.TYPE_CLASS_NUMBER && var == InputType.TYPE_NUMBER_VARIATION_PASSWORD;
    }
    @Override public void onStartInput(EditorInfo attribute, boolean restarting) {
        super.onStartInput(attribute, restarting);
        reloadLexicon();
        memory.resetContext();
        session.clear();
        sensitiveField = isPassword(attribute) || attribute == null || attribute.inputType == InputType.TYPE_NULL;
        memory.setLearning(prefs().getBoolean("learning", true));
        memory.setSensitive(sensitiveField);
        if (root != null) updatePreview();
    }
    @Override public void onFinishInput() {
        session.clear();
        memory.resetContext();
        super.onFinishInput();
    }
    @Override public void onDestroy() {
        if (store != null) store.close();
        super.onDestroy();
    }
    @Override public void onUpdateSelection(int oldSelStart, int oldSelEnd,
            int newSelStart, int newSelEnd, int candidatesStart, int candidatesEnd) {
        super.onUpdateSelection(oldSelStart, oldSelEnd, newSelStart, newSelEnd, candidatesStart, candidatesEnd);
        if (memory == null || sensitiveField || memory.context().size() == 0) return;
        // The editor can change the caret independently. Do not associate future text with stale context.
        InputConnection connection = getCurrentInputConnection();
        if (connection == null) return;
        CharSequence preceding = connection.getTextBeforeCursor(64, 0);
        if (preceding != null && !preceding.toString().endsWith(memory.context().text())) {
            memory.resetContext();
        }
    }
    private TextView label(String text, int size, int color) {
        TextView v = new TextView(this);
        v.setText(text); v.setTextColor(color); v.setTextSize(size);
        v.setGravity(Gravity.CENTER_VERTICAL); v.setPadding(dp(12),dp(4),dp(12),dp(4));
        return v;
    }
    @Override public View onCreateInputView() {
        root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setBackgroundColor(BACKGROUND);
        root.setPadding(dp(3),dp(6),dp(3),dp(5));
        preedit = label("CELL 注音", 16, WHITE);
        preedit.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        preedit.setMinHeight(dp(35));
        root.addView(preedit, new LinearLayout.LayoutParams(-1,dp(37)));
        HorizontalScrollView scroll = new HorizontalScrollView(this);
        scroll.setHorizontalScrollBarEnabled(false);
        candidateRow = new LinearLayout(this);
        candidateRow.setOrientation(LinearLayout.HORIZONTAL);
        scroll.addView(candidateRow);
        root.addView(scroll,new LinearLayout.LayoutParams(-1,dp(48)));
        keysArea = new LinearLayout(this);
        keysArea.setOrientation(LinearLayout.VERTICAL);
        root.addView(keysArea);
        rebuildKeys();
        updatePreview();
        return root;
    }
    private Button key(String text, Runnable onClick, int color, int textSize) {
        Button button = new Button(this);
        button.setText(text); button.setTextSize(textSize);
        button.setAllCaps(false);
        button.setTextColor(WHITE);
        button.setBackgroundTintList(android.content.res.ColorStateList.valueOf(color));
        button.setMinHeight(0);
        button.setMinimumHeight(0);
        button.setMinWidth(0);
        button.setMinimumWidth(0);
        button.setPadding(0,0,0,0);
        button.setOnClickListener(view -> onClick.run());
        return button;
    }
    private LinearLayout row() {
        LinearLayout row = new LinearLayout(this);
        row.setOrientation(LinearLayout.HORIZONTAL);
        keysArea.addView(row,new LinearLayout.LayoutParams(-1,dp(49)));
        return row;
    }
    private void addKey(LinearLayout target, String glyph, Runnable action, int weight, int color, int textSize) {
        Button button = key(glyph,action,color,textSize);
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(0,dp(46),weight);
        lp.setMargins(dp(1),dp(1),dp(1),dp(1));
        target.addView(button,lp);
    }
    private void phonetic(String glyph) {
        if (session.pressSymbol(glyph)) updatePreview();
    }
    private void addEmptyCell(LinearLayout target) {
        Space spacer = new Space(this); // Not a huge invisible clickable button.
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(0, dp(46), 1);
        lp.setMargins(dp(1), dp(1), dp(1), dp(1));
        target.addView(spacer, lp);
    }
    private void spaceBar() {
        // Space chooses the first candidate when the syllable has no explicit tone.
        // When the phonetics are incomplete, keep the preedit instead of inserting a space.
        if (!englishMode && !symbolMode && session.active()) {
            if (!session.candidates().isEmpty()) chooseCandidate(0);
            else updatePreview();
            return;
        }
        insertPlain(" ");
    }
    private void rebuildKeys() {
        if (keysArea == null) return;
        keysArea.removeAllViews();
        if (symbolMode) {
            String[][] rows = {
                {"（","）","〔","〕","〈","〉","｛","｝"},
                {"：","，","。","！","？","；","、","…"},
                {"1","2","3","4","5","6","7","8","9","0"},
                {"@","#","%","&","+","-","=","/"}
            };
            for(String[] glyphs:rows) {
                LinearLayout strip=row();
                for(String glyph:glyphs) addKey(strip,glyph,()->insertPlain(glyph),1,PANEL,17);
            }
        } else if (englishMode) {
            String[] rows = {"qwertyuiop","asdfghjkl","zxcvbnm"};
            for(String keys:rows) {
                LinearLayout strip=row();
                for(char ch:keys.toCharArray()) addKey(strip,String.valueOf(ch),()->insertPlain(String.valueOf(ch)),1,PANEL,17);
            }
        } else {
            // Phone-friendly equal-width 10 columns instead of the old seven oversized keys.
            for (int start = 0; start < KeyinCore.SYMBOLS.length; start += PHONETIC_COLUMNS) {
                LinearLayout strip = row();
                int end = Math.min(start + PHONETIC_COLUMNS, KeyinCore.SYMBOLS.length);
                for (int i = start; i < end; i++) {
                    String symbol = KeyinCore.SYMBOLS[i];
                    addKey(strip, symbol, () -> phonetic(symbol), 1, PANEL, 17);
                }
                for (int i = end; i < start + PHONETIC_COLUMNS; i++) addEmptyCell(strip);
            }
            // Five optional tones plus five quick punctuation keys in the same 10-slot row.
            // Tones do not need to be pressed; Space confirms an untoned candidate.
            LinearLayout tonesAndPunct = row();
            for (String tone : KeyinCore.TONE_LABELS)
                addKey(tonesAndPunct, tone, () -> phonetic(tone), 1, ACCENT, 16);
            for (String mark : new String[]{"（", "）", "：", "，", "。"})
                addKey(tonesAndPunct, mark, () -> insertPlain(mark), 1, PANEL, 16);
        }
        if (englishMode) {
            LinearLayout punct = row();
            for (String mark : new String[]{"（", "）", "：", "，", "。", "？", "！"})
                addKey(punct, mark, () -> insertPlain(mark), 1, PANEL, 14);
        }
        LinearLayout controls=row();
        addKey(controls,englishMode?"注音":"ABC",()->{
            session.clear(); symbolMode=false; englishMode=!englishMode; rebuildKeys(); updatePreview();
        },2,ACCENT,14);
        addKey(controls,symbolMode?"注音":"符號",()->{
            session.clear(); symbolMode=!symbolMode; englishMode=false; rebuildKeys(); updatePreview();
        },2,ACCENT,14);
        addKey(controls,"空白 / 選字",this::spaceBar,3,PANEL,13);
        addKey(controls,"⌫",this::backspace,2,PANEL,23);
        addKey(controls,"↵",this::enter,2,ACCENT,19);
    }
    private void updatePreview() {
        if (preedit == null || candidateRow == null) return;
        String pending=session.preedit();
        preedit.setText(pending.isEmpty() ? "CELL 注音 · 十字經驗" : pending);
        candidateRow.removeAllViews();
        List<KeyinCore.Candidate> list=session.candidates();
        if (list.isEmpty()) {
            List<String> predicted = session.active()?java.util.Collections.emptyList():memory.nextSuggestions(6);
            if (!predicted.isEmpty()) {
                for (String next : predicted) {
                    Button suggested = key(next,()->insertPlain(next),PANEL,17);
                    LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-2,dp(43));
                    lp.setMargins(dp(2),0,dp(2),0);
                    candidateRow.addView(suggested,lp);
                }
            } else {
                TextView placeholder = label(session.active()?"繼續注音；完整音節按空白選字":"注音可不選聲調 · 空白直接選字",14,0xFFABB5C8);
                candidateRow.addView(placeholder);
            }
        } else {
            for (int i=0;i<list.size();i++) {
                final int index=i;
                Button chosen=key(list.get(i).text,()->chooseCandidate(index),ACCENT,19);
                LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-2,dp(43));
                lp.setMargins(dp(2),0,dp(2),0);
                candidateRow.addView(chosen,lp);
            }
        }
    }
    private void chooseCandidate(int index) {
        KeyinCore.Selection choice=session.choose(index);
        if(choice==null) { updatePreview(); return; }
        InputConnection connection=getCurrentInputConnection();
        if (connection!=null && connection.commitText(choice.text,1)) {
            memory.committed(choice.text,choice.reading);
        }
        updatePreview();
    }
    private void insertPlain(String text) {
        if (session.active()) {
            // Composing text is never silently committed as letters or stale candidates.
            if (!session.candidates().isEmpty()) chooseCandidate(0);
            else session.clear();
        }
        InputConnection connection=getCurrentInputConnection();
        if (connection!=null && connection.commitText(text,1)) memory.committed(text,"");
        updatePreview();
    }
    private void backspace() {
        if (!session.backspace()) {
            InputConnection connection=getCurrentInputConnection();
            if (connection!=null) connection.deleteSurroundingTextInCodePoints(1,0);
            memory.resetContext(); // preceding context is now unknown; prevent stale association
        }
        updatePreview();
    }
    private void enter() {
        if(session.active() && !session.candidates().isEmpty()) chooseCandidate(0);
        else session.clear();
        EditorInfo editor=getCurrentInputEditorInfo();
        InputConnection connection=getCurrentInputConnection();
        if(connection!=null && editor!=null && (editor.imeOptions&EditorInfo.IME_MASK_ACTION)!=EditorInfo.IME_ACTION_NONE) {
            int action=editor.imeOptions&EditorInfo.IME_MASK_ACTION;
            if(action!=EditorInfo.IME_ACTION_UNSPECIFIED && connection.performEditorAction(action)) {
                memory.resetContext();updatePreview();return;
            }
        }
        if (connection!=null && connection.commitText("\n",1)) memory.committed("\n","");
        updatePreview();
    }
    @Override public boolean onKeyDown(int keyCode, KeyEvent event) {
        if (keyCode==KeyEvent.KEYCODE_DEL) { backspace(); return true; }
        if (keyCode==KeyEvent.KEYCODE_ESCAPE) { session.clear();updatePreview();return true; }
        if (keyCode==KeyEvent.KEYCODE_ENTER) { enter();return true; }
        if (keyCode==KeyEvent.KEYCODE_SPACE) { spaceBar();return true; }
        char c=(char)event.getUnicodeChar();
        if(c!='\0' && !englishMode && session.pressKey(c)) {updatePreview();return true;}
        return super.onKeyDown(keyCode,event);
    }
}
