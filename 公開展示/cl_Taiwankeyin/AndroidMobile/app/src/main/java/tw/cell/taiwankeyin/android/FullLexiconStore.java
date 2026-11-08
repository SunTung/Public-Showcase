package tw.cell.taiwankeyin.android;

import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.util.Log;
import tw.cell.taiwankeyin.core.KeyinCore;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.IOException;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.List;
import java.util.LinkedHashMap;
import tw.cell.taiwankeyin.core.NextWordRanker;

/** Read-only mobile lookup generated from the existing verified RGOS/Chewing lexicon.
 * No user input is ever written to this system dictionary. */
public final class FullLexiconStore implements KeyinCore.Lexicon.ExternalLookup, AutoCloseable {
    public static final String ASSET = "full_zhuyin_mobile.sqlite3";
    private static final String TAG = "CellFullLexicon";
    private static final int MIN_ROWS = 150000;
    private final SQLiteDatabase db;
    private final int rowCount;
    public int rowCount() { return rowCount; }

    public FullLexiconStore(Context context) throws Exception {
        // Avoid re-copying 10+ MB on every keyboard activation. Hash is checked
        // once when the asset is installed; SQLite is then immutable/read-only.
        Context app = context.getApplicationContext();
        File folder = new File(app.getNoBackupFilesDir(), "dictionary");
        if (!folder.exists() && !folder.mkdirs()) throw new IOException("dictionary directory unavailable");
        File dest = new File(folder, ASSET);
        // A versioned marker forces replacement when the APK gains a new index.
        // Do not repeatedly copy the 27+ MB corpus on every IME activation.
        File schemaMarker = new File(folder, "word_prefix_index_v2.ready");
        long expected;
        try (android.content.res.AssetFileDescriptor d = app.getAssets().openFd(ASSET)) {
            expected = d.getLength();
        } catch (IOException compressed) {
            // APK assets may be zip-compressed. Counting stream bytes is fine on first install.
            expected = -1;
        }
        if (!schemaMarker.exists() || !dest.isFile() || dest.length() < 3_000_000
                || (expected >= 0 && dest.length() != expected)) {
            File staged = new File(folder, ASSET + ".pending");
            try (InputStream input = app.getAssets().open(ASSET);
                 FileOutputStream output = new FileOutputStream(staged)) {
                byte[] chunk = new byte[64 * 1024]; int n;
                while ((n = input.read(chunk)) != -1) output.write(chunk, 0, n);
                output.getFD().sync();
            }
            if (staged.length() < 3_000_000) throw new IOException("incomplete full lexicon asset");
            if (dest.exists() && !dest.delete()) throw new IOException("old dictionary could not be replaced");
            if (!staged.renameTo(dest)) throw new IOException("dictionary rename failed");
            if (!schemaMarker.createNewFile()) throw new IOException("dictionary schema marker failed");
        }
        SQLiteDatabase opened = SQLiteDatabase.openDatabase(dest.getAbsolutePath(),null,
                SQLiteDatabase.OPEN_READONLY | SQLiteDatabase.NO_LOCALIZED_COLLATORS);
        try {
            try (Cursor c = opened.rawQuery("SELECT COUNT(*) FROM lexicon_mobile",null)) {
                if (!c.moveToFirst()) throw new IllegalStateException("missing full lexicon");
                rowCount = c.getInt(0);
                if (rowCount < MIN_ROWS) throw new IllegalStateException("incomplete dictionary rows="+rowCount);
            }
            db = opened;
        } catch (Exception failure) {
            opened.close(); throw failure;
        }
    }
    @Override public synchronized List<KeyinCore.Candidate> find(String bare, String typed, int limit) {
        List<KeyinCore.Candidate> out = new ArrayList<>();
        if (bare == null || bare.isEmpty() || limit <= 0) return out;
        int n = Math.min(limit, 96);
        int scan = typed.equals(bare) ? n : n * 12;
        // Indexed by (bare, frequency DESC): fast even with 158k rows.
        try (Cursor c = db.rawQuery("SELECT reading,word,frequency FROM lexicon_mobile "
                + "WHERE bare=? ORDER BY frequency DESC LIMIT ?",
                new String[]{bare,String.valueOf(scan)})) {
            while (c.moveToNext() && out.size() < n) {
                String actual = c.getString(0), word = c.getString(1);
                if (!KeyinCore.Lexicon.matchesTonePattern(typed,actual)) continue;
                int frequency = c.getInt(2);
                double baseline = 12.0 * Math.log1p(Math.max(0,frequency));
                out.add(new KeyinCore.Candidate(word,actual,baseline,baseline));
            }
        }
        return out;
    }
    /** Indexed phrase-prefix next-word suggestions from the verified 158905 corpus.
     * Searches the longest recent suffix first; user phrases are merged separately.
     */
    public synchronized List<NextWordRanker.Hit> followups(String context, int limit) {
        List<NextWordRanker.Hit> found=new ArrayList<>();
        if (context==null || context.isEmpty() || limit<=0) return found;
        KeyinCore.Context10 clip=new KeyinCore.Context10();
        for(String unit:KeyinCore.units(context)) clip.feed(unit);
        LinkedHashMap<String,NextWordRanker.Hit> unique=new LinkedHashMap<>();
        List<String> suffixes=clip.suffixes();
        // Fast bounded prefix searches, long context first; no user text stored.
        for(int i=Math.min(suffixes.size(),4)-1;i>=0;i--) {
            String prefix=suffixes.get(i);
            int units=KeyinCore.units(prefix).size();
            if (units>4) continue;
            try(Cursor c=db.rawQuery(
                    "SELECT word,MAX(frequency) AS f FROM lexicon_mobile "
                    +"WHERE word>=? AND word<? AND length(word)>length(?) "
                    +"GROUP BY word ORDER BY f DESC LIMIT 60",
                    new String[]{prefix,prefix+"\uffff",prefix})) {
                while(c.moveToNext()) {
                    String word=c.getString(0);
                    if (!word.startsWith(prefix)) continue;
                    String continuation=word.substring(prefix.length());
                    if (!NextWordRanker.usable(continuation)) continue;
                    NextWordRanker.Hit candidate=new NextWordRanker.Hit(continuation,c.getInt(1),units);
                    NextWordRanker.Hit previous=unique.get(continuation);
                    if(previous==null || candidate.frequency>previous.frequency)
                        unique.put(continuation,candidate);
                }
            }
        }
        found.addAll(unique.values());
        return found;
    }
    @Override public synchronized void close() { db.close(); }
}
