package tw.cell.taiwankeyin.android;

import android.app.Activity;
import android.os.Bundle;
import android.util.Log;
import android.view.inputmethod.EditorInfo;
import android.view.inputmethod.InputConnection;
import android.widget.EditText;
import tw.cell.taiwankeyin.core.CommitBridge;
import tw.cell.taiwankeyin.core.KeyinCore;
import tw.cell.taiwankeyin.core.NextWordRanker;

/** Only present in debug builds. Exercises Android's actual EditText InputConnection and SQLite. */
public final class ImeProbeActivity extends Activity {
    private static final String TAG = "CELL_IME_PROBE";
    private static void require(boolean yes, String reason) {
        if (!yes) throw new AssertionError(reason);
    }
    @Override protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EditText text = new EditText(this);
        text.setSingleLine(false);
        text.setText(" ");
        text.setSelection(1);
        setContentView(text);
        text.requestFocus();
        text.post(() -> {
            try (ExperienceDatabase storage = new ExperienceDatabase(this, "cell_taiwankeyin_probe_only.sqlite3")) {
                storage.erase(); // The debug package has an independent disposable testing database.
                KeyinCore.Memory memory = new KeyinCore.Memory(storage);
                KeyinCore.Lexicon words = new KeyinCore.Lexicon();
                words.load(getAssets().open("seed_zhuyin_tw.tsv"));
                try (FullLexiconStore full = new FullLexiconStore(this)) {
                    require(full.rowCount() == 158905, "expected validated RGOS full corpus rows");
                    words.setExternalLookup(full);
                    require(words.lookupFlexible("ㄓㄨㄥ ㄨㄣ", memory).stream()
                            .anyMatch(c -> "中文".equals(c.text)), "full corpus missing 中文");
                    require(full.followups("你",12).stream().anyMatch(h->"好".equals(h.suffix)),
                            "full corpus missing first-use next word prediction 你→好");
                    require(full.followups("今天",12).stream().anyMatch(h->"是".equals(h.suffix)),
                            "full corpus missing first-use next word prediction 今天→是");
                    require(NextWordRanker.merge(java.util.Collections.emptyList(),
                            full.followups("你",20),6).contains("的"),
                            "full corpus next word ranking failed");
                    words.setExternalLookup(null); // Normal candidate commit test below still isolates the seed.
                }
                KeyinCore.Session composing = new KeyinCore.Session(words, memory);
                require(composing.pressSymbol("ㄋ"), "ni initial");
                require(composing.pressSymbol("ㄧ"), "ni medial");
                require(composing.pressSymbol("ㄏ"), "auto tone-free syllable split");
                require(composing.pressSymbol("ㄠ"), "hao final");
                require(!composing.candidates().isEmpty(), "no candidates for ni-hao");
                require("你好".equals(composing.candidates().get(0).text), "wrong first candidate");
                InputConnection editor = text.onCreateInputConnection(new EditorInfo());
                require(editor != null, "EditText InputConnection unavailable");
                final int[] learningFailures = {0};
                require(CommitBridge.commitCandidate(composing, memory, 0,
                    value -> editor.commitText(value, 1), err -> {
                       learningFailures[0]++;
                       Log.e(TAG, "SQLITE_LEARNING_FAILURE", err);
                    }), "editor commitText returned false");
                require(learningFailures[0] == 0, "SQLite learning failed");
                require(text.getText().toString().contains("你好"), "candidate not delivered to EditText");
                // Exercise the exact production deletion bridge against a real EditText.
                text.setText("文件測試ABC");
                text.setSelection(text.length());
                require(EditorDeleteBridge.deleteOne(editor), "delete trailing ASCII failed");
                require("文件測試AB".contentEquals(text.getText()), "editor text did not delete");
                text.setSelection(2, 4);
                require(EditorDeleteBridge.deleteOne(editor), "delete selection failed");
                require("文件AB".contentEquals(text.getText()), "selected range not removed");
                text.setText("甲😀乙");
                text.setSelection("甲😀".length());
                require(EditorDeleteBridge.deleteOne(editor), "delete emoji failed");
                require("甲乙".contentEquals(text.getText()), "surrogate pair was split");
                text.setSelection(0);
                require(EditorDeleteBridge.deleteOne(editor), "start of document delete rejected");
                require("甲乙".contentEquals(text.getText()), "deletion at start changed text");
                require(memory.context().text().equals("你好"), "remembered context differs");
                require(storage.candidateBonus("ㄋㄧˇ ㄏㄠˇ", "你好", "") > 0, "missing choice statistic");
                memory.resetContext();
                memory.committed("你", "");
                require(memory.nextSuggestions(8).contains("好"), "SQLite next-word query failed");
                storage.erase();
                require(storage.candidateBonus("ㄋㄧˇ ㄏㄠˇ", "你好", "") == 0, "erase failed");
                Log.i(TAG, "PASS real EditText InputConnection, SQLite choice, phrase and erase");
            } catch (Throwable error) {
                Log.e(TAG, "FAIL real Android editor/SQLite integration", error);
            }
        });
    }
}
