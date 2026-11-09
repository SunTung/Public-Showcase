package tw.cell.taiwankeyin.android;

import android.content.SharedPreferences;
import android.view.MotionEvent;
import android.os.Handler;
import android.os.Looper;
import android.inputmethodservice.InputMethodService;
import android.text.InputType;
import android.view.Gravity;
import android.view.KeyEvent;
import android.view.View;
import android.graphics.drawable.GradientDrawable;
import android.view.inputmethod.EditorInfo;
import android.view.inputmethod.InputConnection;
import android.widget.Button;
import android.animation.ValueAnimator;
import android.view.animation.DecelerateInterpolator;
import android.widget.HorizontalScrollView;
import android.widget.LinearLayout;
import android.widget.Space;
import android.widget.TextView;
import android.util.Log;
import tw.cell.taiwankeyin.core.CommitBridge;
import tw.cell.taiwankeyin.core.KeyinCore;
import tw.cell.taiwankeyin.core.KeyboardLayout;
import tw.cell.taiwankeyin.core.KeyboardTheme;
import tw.cell.taiwankeyin.core.ElasticKeyCurve;
import tw.cell.taiwankeyin.core.NextWordRanker;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.util.List;
import java.util.ArrayList;
import java.util.Random;

public final class TaiwanKeyinImeService extends InputMethodService {
    private static final String TAG = "CellTaiwanKeyin";
    private static final String LEXICON = "imported_lexicon.tsv";
    private ExperienceDatabase store;
    private FullLexiconStore verifiedFullLexicon;
    private final KeyboardLayout.LatinShift latinShift = new KeyboardLayout.LatinShift();
    private int symbolPage;
    private KeyboardTheme.Palette theme = KeyboardTheme.get(0);
    private boolean randomColors;
    private final Random colorRandom = new Random();
    private final List<Button> coloredKeys = new ArrayList<>();
    private final java.util.IdentityHashMap<Button,Integer> lastKeyColors = new java.util.IdentityHashMap<>();
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
    private final Handler deleteHandler = new Handler(Looper.getMainLooper());
    private boolean deleteHeld;
    private final Runnable deleteRepeat = new Runnable() {
        @Override public void run() {
            if (!deleteHeld) return;
            backspace();
            deleteHandler.postDelayed(this, 65L);
        }
    };
    private void stopDeleteRepeat() {
        deleteHeld = false;
        deleteHandler.removeCallbacks(deleteRepeat);
    }
    private void attachRepeatDelete(Button button) {
        button.setOnTouchListener((view, event) -> {
            switch (event.getActionMasked()) {
                case MotionEvent.ACTION_DOWN:
                    stopDeleteRepeat();
                    deleteHeld = true;
                    view.setPressed(true);
                    backspace();
                    deleteHandler.postDelayed(deleteRepeat, 420L);
                    return true;
                case MotionEvent.ACTION_UP:
                case MotionEvent.ACTION_CANCEL:
                    stopDeleteRepeat();
                    view.setPressed(false);
                    return true;
                case MotionEvent.ACTION_MOVE:
                    if (event.getX() < 0 || event.getY() < 0
                            || event.getX() >= view.getWidth() || event.getY() >= view.getHeight()) {
                        stopDeleteRepeat();
                        view.setPressed(false);
                    }
                    return true;
                default: return true;
            }
        });
    }

    private int dp(float value) { return Math.round(value * getResources().getDisplayMetrics().density); }
    private SharedPreferences prefs() { return getSharedPreferences("keyboard_settings", MODE_PRIVATE); }

    @Override public void onCreate() {
        super.onCreate();
        int storedTheme = prefs().getInt("theme_index", 0);
        randomColors = storedTheme == KeyboardTheme.RANDOM_MODE;
        theme = KeyboardTheme.get(randomColors ? 0 : storedTheme);
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
        stopDeleteRepeat();
        reloadLexicon();
        memory.resetContext();
        session.clear();
        sensitiveField = isPassword(attribute) || attribute == null || attribute.inputType == InputType.TYPE_NULL;
        memory.setLearning(prefs().getBoolean("learning", true));
        memory.setSensitive(sensitiveField);
        if (root != null) updatePreview();
    }
    @Override public void onFinishInput() {
        stopDeleteRepeat();
        session.clear();
        memory.resetContext();
        super.onFinishInput();
    }
    @Override public void onDestroy() {
        stopDeleteRepeat();
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
        root.setClipChildren(false);
        root.setClipToPadding(false);
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
        keysArea.setClipChildren(false);
        keysArea.setClipToPadding(false);
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
        // Draw the key surface ourselves. Android's stock button tint would hide
        // the elastic corner-radius animation.
        GradientDrawable surface = new GradientDrawable();
        surface.setColor(color);
        surface.setCornerRadius(dp(7));
        button.setBackgroundTintList(null);
        button.setBackground(surface);
        if (prefs().getBoolean("elastic_feedback", true)) attachElasticFeedback(button, surface);
        button.setIncludeFontPadding(false);
        button.setMinHeight(0);
        button.setMinimumHeight(0);
        button.setMinWidth(0);
        button.setMinimumWidth(0);
        button.setPadding(0,0,0,0);
        button.setOnClickListener(view -> {
            try { onClick.run(); }
            finally { if (randomColors) redistributeKeyColors(); }
        });
        if ("⌫".equals(text)) attachRepeatDelete(button);
        return button;
    }
    /** Visual-only elastic key feedback: touch hit regions never change geometry.
     * Each key has its own animation, so rapid neighbors naturally overlap and
     * temporarily squeeze the visible gaps without overlapping input dispatch.
     */
    private void attachElasticFeedback(Button button, GradientDrawable surface) {
        final ValueAnimator[] running = { null };
        final float[] progress = { 0f };
        button.setOnTouchListener((view, event) -> {
            int action = event.getActionMasked();
            if (action != MotionEvent.ACTION_DOWN && action != MotionEvent.ACTION_UP
                    && action != MotionEvent.ACTION_CANCEL) return false;
            if (running[0] != null) running[0].cancel();
            final float from = progress[0];
            final float to = action == MotionEvent.ACTION_DOWN ? 1f : 0f;
            ValueAnimator animator = ValueAnimator.ofFloat(from, to);
            animator.setDuration(action == MotionEvent.ACTION_DOWN
                    ? ElasticKeyCurve.PRESS_MS : ElasticKeyCurve.RECOVER_MS);
            animator.setInterpolator(new DecelerateInterpolator());
            animator.addUpdateListener(a -> {
                float amount = (Float) a.getAnimatedValue();
                progress[0] = amount;
                float scale = ElasticKeyCurve.scale(amount);
                view.setScaleX(scale);
                view.setScaleY(scale);
                surface.setCornerRadius(dp(ElasticKeyCurve.cornerDp(amount)));
                // Keep the pressed visual surface above adjacent keys only.
                view.setTranslationZ(dp(ElasticKeyCurve.zDp(amount)));
            });
            running[0] = animator;
            animator.start();
            // Let Button handle its usual DOWN/UP/click; animation cannot steal a key.
            return false;
        });
    }
    private LinearLayout row() { return row(45); }
    private LinearLayout row(int height) {
        LinearLayout row = new LinearLayout(this);
        row.setOrientation(LinearLayout.HORIZONTAL);
        row.setClipChildren(false);
        row.setClipToPadding(false);
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
        coloredKeys.add(button);
    }
    private void redistributeKeyColors() {
        if (!randomColors) return;
        // Recolor existing button drawables in place: no layout rebuild, hit-area
        // movement, animation restart or expensive SQLite access per key.
        for (Button button : coloredKeys) {
            if (button.getParent() == null) continue;
            Integer old = lastKeyColors.get(button);
            int color = KeyboardTheme.randomKeyColor(colorRandom, old == null ? 0 : old);
            lastKeyColors.put(button, color);
            android.graphics.drawable.Drawable drawable = button.getBackground();
            if (drawable instanceof GradientDrawable)
                ((GradientDrawable) drawable).setColor(color);
            button.setTextColor(KeyboardTheme.readableText(color));
        }
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
        if (index < 0 || index >= KeyboardTheme.modeCount()) return;
        boolean switchToRandom = index == KeyboardTheme.RANDOM_MODE;
        if (randomColors == switchToRandom && (switchToRandom || theme.index == index)) return;
        randomColors = switchToRandom;
        theme = KeyboardTheme.get(switchToRandom ? 0 : index);
        prefs().edit().putInt("theme_index", index).apply();
        if (root != null) root.setBackgroundColor(theme.background);
        rebuildKeys();
        updatePreview();
    }
    private void rebuildKeys() {
        if (keysArea == null) return;
        if (root != null) root.setBackgroundColor(theme.background);
        keysArea.removeAllViews();
        coloredKeys.clear();
        lastKeyColors.clear();
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
            // True physical ordering: number-row Dachen roots are FIRST (not fourth).
            // Five optional tones travel with the number-row roots in the top strip.
            LinearLayout numberAndTone = row(37);
            String numberRoots = KeyboardLayout.ZHUYIN_PHYSICAL_ROWS[0];
            for (char code : numberRoots.toCharArray()) {
                String glyph = KeyinCore.symbolForKey(code);
                addKey(numberAndTone, glyph, () -> phonetic(glyph), 1, theme.panel, 15, 34);
            }
            for (String tone : KeyinCore.TONE_LABELS)
                addKey(numberAndTone, tone, () -> phonetic(tone), 1, theme.accent, 14, 34);

            // The familiar QWERTY / ASDF / ZXCV rows remain below the original number row.
            for (int r = 1; r < KeyboardLayout.ZHUYIN_PHYSICAL_ROWS.length; r++) {
                String rowKeys = KeyboardLayout.ZHUYIN_PHYSICAL_ROWS[r];
                LinearLayout strip = row(45);
                for (char code : rowKeys.toCharArray()) {
                    String glyph = KeyinCore.symbolForKey(code);
                    addKey(strip, glyph, () -> phonetic(glyph), 1, theme.panel, 17, 42);
                }
                for (int i = rowKeys.length(); i < 10; i++) addEmptyCell(strip);
            }
            // Keep punctuation below; add immediate palette controls beside it.
            // This row replaces the old bottom tone row, without adding keyboard height.
            LinearLayout punctuationAndThemes = row(29);
            for (String mark : new String[]{"，", "。", "？", "！"})
                addKey(punctuationAndThemes, mark, () -> insertPlain(mark), 1, theme.panel, 13, 26);
            for (int index = 0; index < KeyboardTheme.modeCount(); index++) {
                final int selectedTheme = index;
                boolean randomChoice = index == KeyboardTheme.RANDOM_MODE;
                KeyboardTheme.Palette palette = KeyboardTheme.get(randomChoice ? 2 : index);
                boolean active = randomChoice ? randomColors : !randomColors && index == theme.index;
                Button swatch = key(randomChoice ? (active ? "✓彩" : "彩") : (active ? "✓" : ""),
                        () -> selectTheme(selectedTheme), palette.accent, 12);
                // The checkmark is white on all selected accent chips.
                swatch.setTextColor(0xFFFFFFFF);
                LinearLayout.LayoutParams chipParams = new LinearLayout.LayoutParams(0, dp(26), 1);
                chipParams.setMargins(dp(2), dp(1), dp(2), dp(1));
                punctuationAndThemes.addView(swatch, chipParams);
                swatch.setContentDescription(randomChoice ? "鍵盤顏色：每按一次隨機重新分配" : "鍵盤顏色：" + palette.name);
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
        if (randomColors) redistributeKeyColors();
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
                List<String> learned = memory.nextSuggestions(12);
                List<NextWordRanker.Hit> fromDictionary = verifiedFullLexicon == null
                        ? java.util.Collections.emptyList()
                        : verifiedFullLexicon.followups(memory.context().text(), 24);
                for (String next : NextWordRanker.merge(learned,fromDictionary,6)) {
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
        if (session.active() && session.backspace()) {
            updatePreview();
            return;
        }
        InputConnection connection = getCurrentInputConnection();
        if (connection != null) {
            try {
                CharSequence selected = connection.getSelectedText(0);
                boolean deleted = selected != null && selected.length() > 0
                        ? connection.commitText("", 1)
                        : connection.deleteSurroundingTextInCodePoints(1, 0);
                if (!deleted) {
                    long now = android.os.SystemClock.uptimeMillis();
                    connection.sendKeyEvent(new KeyEvent(now, now, KeyEvent.ACTION_DOWN,
                            KeyEvent.KEYCODE_DEL, 0));
                    connection.sendKeyEvent(new KeyEvent(now, now, KeyEvent.ACTION_UP,
                            KeyEvent.KEYCODE_DEL, 0));
                }
            } catch (RuntimeException ex) {
                Log.w(TAG, "Editor deletion failed", ex);
            }
        }
        memory.resetContext();
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
