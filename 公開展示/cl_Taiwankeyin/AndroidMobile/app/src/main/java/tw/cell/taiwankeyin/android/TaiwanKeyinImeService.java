package tw.cell.taiwankeyin.android;

import android.content.SharedPreferences;
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
import android.util.Log;
import tw.cell.taiwankeyin.core.CommitBridge;
import tw.cell.taiwankeyin.core.KeyinCore;
import tw.cell.taiwankeyin.core.KeyboardLayout;
import tw.cell.taiwankeyin.core.KeyboardTheme;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.util.List;

public final class TaiwanKeyinImeService extends InputMethodService {
    private static final String TAG = "CellTaiwanKeyin";
    private static final String LEXICON = "imported_lexicon.tsv";
    private ExperienceDatabase store;
    private FullLexiconStore verifiedFullLexicon;
    private final KeyboardLayout.LatinShift latinShift = new KeyboardLayout.LatinShift();
    private int symbolPage;
    private KeyboardTheme.Palette theme = KeyboardTheme.get(0);
    private KeyinCore.Memory memory;
    private KeyinCore.Lexicon lexicon;
    private KeyinCore.Session session;
    private long lastLexiconModification = Long.MIN_VALUE;
    private LinearLayout root;
    private LinearLayout candidateRow;
    private LinearLayout keysArea;
    private boolean englishMode;
    private boolean symbolMode;
    private boolean sensitiveField;

    private int dp(float value) { return Math.round(value * getResources().getDisplayMetrics().density); }
    private SharedPreferences prefs() { return getSharedPreferences("keyboard_settings", MODE_PRIVATE); }

    @Override public void onCreate() {
        super.onCreate();
        theme = KeyboardTheme.get(prefs().getInt("theme_index", 0));
        store = new ExperienceDatabase(this);
        memory = new KeyinCore.Memory(store);
        try {
            verifiedFullLexicon = new FullLexiconStore(this);
            Log.i(TAG, "Verified RGOS full Chinese lexicon ready: " + verifiedFullLexicon.rowCount());
        } catch (Exception ex) {
            Log.e(TAG, "Full corpus unavailable; retaining safe small fallback", ex);
        }
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
            if (verifiedFullLexicon != null) next.setExternalLookup(verifiedFullLexicon);
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
        if (verifiedFullLexicon != null) verifiedFullLexicon.close();
        super.onDestroy();
    }
    @Override public void onUpdateSelection(int oldSelStart, int oldSelEnd,
            int newSelStart, int newSelEnd, int candidatesStart, int candidatesEnd) {
        super.onUpdateSelection(oldSelStart, oldSelEnd, newSelStart, newSelEnd, candidatesStart, candidatesEnd);
        if (memory == null || sensitiveField || memory.context().size() == 0) return;
        // The editor can change the caret independently. Do not associate future text with stale context.
        InputConnection connection = getCurrentInputConnection();
        if (connection == null) return;
        try {
            CharSequence preceding = connection.getTextBeforeCursor(64, 0);
            if (preceding != null && !preceding.toString().endsWith(memory.context().text())) {
                memory.resetContext();
            }
        } catch (RuntimeException ex) {
            Log.w(TAG, "Editor cursor state unavailable; resetting stale context", ex);
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
        root.setBackgroundColor(theme.background);
        root.setPadding(dp(2),dp(2),dp(2),dp(2));
        HorizontalScrollView scroll = new HorizontalScrollView(this);
        scroll.setHorizontalScrollBarEnabled(false);
        candidateRow = new LinearLayout(this);
        candidateRow.setOrientation(LinearLayout.HORIZONTAL);
        scroll.addView(candidateRow);
        root.addView(scroll,new LinearLayout.LayoutParams(-1,dp(42)));
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
        button.setTextColor(theme.text);
        button.setBackgroundTintList(android.content.res.ColorStateList.valueOf(color));
        button.setIncludeFontPadding(false);
        button.setMinHeight(0);
        button.setMinimumHeight(0);
        button.setMinWidth(0);
        button.setMinimumWidth(0);
        button.setPadding(0,0,0,0);
        button.setOnClickListener(view -> onClick.run());
        return button;
    }
    private LinearLayout row() { return row(45); }
    private LinearLayout row(int height) {
        LinearLayout row = new LinearLayout(this);
        row.setOrientation(LinearLayout.HORIZONTAL);
        keysArea.addView(row,new LinearLayout.LayoutParams(-1,dp(height)));
        return row;
    }
    private void addKey(LinearLayout target, String glyph, Runnable action, float weight, int color, int textSize) {
        addKey(target, glyph, action, weight, color, textSize, 42);
    }
    private void addKey(LinearLayout target, String glyph, Runnable action, float weight, int color, int textSize, int height) {
        Button button = key(glyph,action,color,textSize);
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(0,dp(height),weight);
        lp.setMargins(dp(1),dp(1),dp(1),dp(1));
        target.addView(button,lp);
    }
    private void phonetic(String glyph) {
        try {
            if (session.pressSymbol(glyph)) updatePreview();
        } catch (RuntimeException ex) {
            // First candidate may read SQLite. If it is unavailable, fall back to
            // non-learning baseline candidates without closing the keyboard.
            Log.e(TAG, "Phonetic candidate retrieval failed", ex);
            memory.setLearning(false);
            try { session.refreshCandidates(); updatePreview(); }
            catch (RuntimeException fallback) { Log.e(TAG, "Baseline candidate fallback failed", fallback); }
        }
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
    private void latinLetter(char letter) {
        String emitted = latinShift.print(letter);
        insertPlain(emitted);
        // One-shot shift returns to lower after successful letter entry.
        if (latinShift.mode() == KeyboardLayout.LatinShift.Mode.LOWER) rebuildKeys();
    }
    private void chooseSymbolPage(int delta) {
        symbolPage = (symbolPage + delta + KeyboardLayout.pages()) % KeyboardLayout.pages();
        rebuildKeys();
    }
    private void selectTheme(int index) {
        KeyboardTheme.Palette selected = KeyboardTheme.get(index);
        if (selected.index == theme.index) return;
        theme = selected;
        prefs().edit().putInt("theme_index", theme.index).apply();
        if (root != null) root.setBackgroundColor(theme.background);
        rebuildKeys();
        updatePreview();
    }
    private void rebuildKeys() {
        if (keysArea == null) return;
        if (root != null) root.setBackgroundColor(theme.background);
        keysArea.removeAllViews();
        if (symbolMode) {
            // A dedicated paged palette, not just the 10 punctuation shortcuts.
            LinearLayout tabs = row(34);
            addKey(tabs, "‹", () -> chooseSymbolPage(-1), 1, theme.panel, 18, 31);
            addKey(tabs, KeyboardLayout.SYMBOL_PAGE_NAMES[symbolPage],
                    () -> chooseSymbolPage(1), 4, theme.accent, 15, 31);
            addKey(tabs, "›", () -> chooseSymbolPage(1), 1, theme.panel, 18, 31);
            String[] symbols = KeyboardLayout.page(symbolPage);
            for (int start = 0; start < symbols.length; start += 8) {
                LinearLayout strip = row(45);
                for (int i = start; i < Math.min(start + 8,symbols.length); i++) {
                    String mark = symbols[i];
                    addKey(strip, mark, () -> insertPlain(mark), 1, theme.panel, 16, 42);
                }
                for (int i = Math.min(start+8,symbols.length); i < start+8; i++) addEmptyCell(strip);
            }
        } else if (englishMode) {
            // Familiar English QWERTY, including one-shot uppercase and Caps Lock.
            for (int index = 0; index < KeyboardLayout.LATIN_ROWS.length; index++) {
                LinearLayout strip = row(49);
                if (index == 2) {
                    String shiftGlyph = latinShift.mode() == KeyboardLayout.LatinShift.Mode.CAPS_LOCK ? "⇪"
                            : latinShift.mode() == KeyboardLayout.LatinShift.Mode.NEXT_UPPER ? "⇧" : "↑";
                    addKey(strip, shiftGlyph, () -> { latinShift.pressShift(); rebuildKeys(); },
                            1.5f, theme.accent, 19);
                }
                for (char ch : KeyboardLayout.LATIN_ROWS[index].toCharArray()) {
                    char value = ch;
                    addKey(strip,latinShift.label(value),()->latinLetter(value),1,theme.panel,18);
                }
                if (index == 2) addKey(strip, "⌫", this::backspace, 1.5f, theme.panel, 20);
            }
            LinearLayout punctuation = row(33);
            for (String mark : new String[]{".", ",", "'", "?", "!", "@", "-", "/"})
                addKey(punctuation,mark,()->insertPlain(mark),1,theme.panel,14,30);
        } else {
            // True physical ordering: number-row Dachen roots are FIRST.
            // The five optional tones share the first strip.
            LinearLayout numberAndTone = row(37);
            String numberRoots = KeyboardLayout.ZHUYIN_PHYSICAL_ROWS[0];
            for (char code : numberRoots.toCharArray()) {
                String glyph = KeyinCore.symbolForKey(code);
                addKey(numberAndTone, glyph, () -> phonetic(glyph), 1, theme.panel, 15, 34);
            }
            for (String tone : KeyinCore.TONE_LABELS)
                addKey(numberAndTone, tone, () -> phonetic(tone), 1, theme.accent, 14, 34);
            // The QWERTY / ASDF / ZXCV rows remain directly beneath.
            for (int r = 1; r < KeyboardLayout.ZHUYIN_PHYSICAL_ROWS.length; r++) {
                String rowKeys = KeyboardLayout.ZHUYIN_PHYSICAL_ROWS[r];
                LinearLayout strip = row(45);
                for (char code : rowKeys.toCharArray()) {
                    String glyph = KeyinCore.symbolForKey(code);
                    addKey(strip, glyph, () -> phonetic(glyph), 1, theme.panel, 17, 42);
                }
                for (int i = rowKeys.length(); i < 10; i++) addEmptyCell(strip);
            }
            // Punctuation and six direct-tap color swatches occupy one compact row.
            LinearLayout punctuationAndThemes = row(29);
            for (String mark : new String[]{"，", "。", "？", "！"})
                addKey(punctuationAndThemes, mark, () -> insertPlain(mark), 1, theme.panel, 13, 26);
            for (int index = 0; index < KeyboardTheme.count(); index++) {
                final int selectedTheme = index;
                KeyboardTheme.Palette palette = KeyboardTheme.get(index);
                Button swatch = key(index == theme.index ? "✓" : "", () -> selectTheme(selectedTheme),
                        palette.accent, 14);
                swatch.setTextColor(0xFFFFFFFF);
                LinearLayout.LayoutParams chipParams = new LinearLayout.LayoutParams(0, dp(26), 1);
                chipParams.setMargins(dp(2), dp(1), dp(2), dp(1));
                punctuationAndThemes.addView(swatch, chipParams);
                swatch.setContentDescription("鍵盤顏色：" + palette.name);
            }
        }
        LinearLayout controls=row(46);
        addKey(controls, englishMode ? "注音" : "ABC", () -> {
            session.clear(); symbolMode=false; englishMode=!englishMode;
            rebuildKeys(); updatePreview();
        },2,theme.accent,14);
        addKey(controls, symbolMode ? "注音" : "符號", () -> {
            session.clear(); symbolMode=!symbolMode; englishMode=false;
            rebuildKeys(); updatePreview();
        },2,theme.accent,14);
        addKey(controls,"空白 / 選字",this::spaceBar,3,theme.panel,13);
        addKey(controls,"⌫",this::backspace,2,theme.panel,23);
        addKey(controls,"↵",this::enter,2,theme.accent,19);
    }
    private void updatePreview() {
        if (candidateRow == null || session == null) return;
        candidateRow.removeAllViews();
        String pending = session.preedit();
        // No permanent headline or instruction row. Show live preedit only in the candidate strip.
        if (!pending.isEmpty()) {
            TextView spelling = label(pending, 14, theme.text);
            spelling.setSingleLine(true);
            spelling.setBackgroundColor(theme.background);
            candidateRow.addView(spelling);
        }
        List<KeyinCore.Candidate> choices = session.candidates();
        if (!choices.isEmpty()) {
            for (int i = 0; i < choices.size(); i++) {
                final int index = i;
                Button selected = key(choices.get(i).text, () -> chooseCandidate(index), theme.accent, 18);
                LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(-2, dp(43));
                lp.setMargins(dp(2), 0, dp(2), 0);
                candidateRow.addView(selected, lp);
            }
        } else if (!session.active()) {
            // Learning database failures must not kill the input-method process.
            try {
                for (String next : memory.nextSuggestions(6)) {
                    Button suggestion = key(next, () -> insertPlain(next), theme.panel, 17);
                    LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(-2, dp(43));
                    lp.setMargins(dp(2), 0, dp(2), 0);
                    candidateRow.addView(suggestion, lp);
                }
            } catch (RuntimeException ex) {
                Log.e(TAG, "Failed to read local next-word predictions", ex);
                memory.setLearning(false);
            }
        }
    }
    private void warnLearningFailure(RuntimeException ex) {
        Log.e(TAG, "Text delivered; disabling local learning after SQLite failure", ex);
        memory.setLearning(false); // Keep IME usable; no silent inconsistent learning writes.
    }
    private void chooseCandidate(int index) {
        InputConnection connection = getCurrentInputConnection();
        if (connection == null) {
            Log.w(TAG, "Candidate not committed: editor InputConnection is null");
            updatePreview();
            return; // Keep the pending composition.
        }
        try {
            // Unlike Alpha2, never call session.choose() before Android commitText succeeds.
            if (!CommitBridge.commitCandidate(session, memory, index,
                    text -> connection.commitText(text, 1), this::warnLearningFailure)) {
                Log.w(TAG, "Candidate not committed: target rejected text or selection invalid");
            }
        } catch (RuntimeException ex) {
            Log.e(TAG, "InputConnection.commitText failed; retaining phonetic composition", ex);
        }
        updatePreview();
    }
    private void insertPlain(String text) {
        if (session.active()) {
            if (!session.candidates().isEmpty()) {
                chooseCandidate(0);
                if (session.active()) return; // Do not insert punctuation if candidate was rejected.
            } else session.clear();
        }
        InputConnection connection = getCurrentInputConnection();
        try {
            if (connection != null && connection.commitText(text, 1)) {
                try { memory.committed(text, ""); }
                catch (RuntimeException ex) { warnLearningFailure(ex); }
            }
        } catch (RuntimeException ex) {
            Log.e(TAG, "Editor rejected plain text", ex);
        }
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
        if(c!='\0' && !englishMode && KeyinCore.KEY_CODES.indexOf(Character.toLowerCase(c))>=0) { phonetic(KeyinCore.symbolForKey(c));return true; }
        return super.onKeyDown(keyCode,event);
    }
}
