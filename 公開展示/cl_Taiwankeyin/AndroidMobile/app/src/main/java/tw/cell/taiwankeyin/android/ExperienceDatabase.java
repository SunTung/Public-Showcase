package tw.cell.taiwankeyin.android;

import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;
import tw.cell.taiwankeyin.core.KeyinCore;
import java.util.List;
import java.util.ArrayList;
import java.util.LinkedHashSet;

/** Local-only personal learning; NEVER copy this database into public source archives. */
public final class ExperienceDatabase extends SQLiteOpenHelper implements KeyinCore.LearningBackend {
    public ExperienceDatabase(Context context) {
        super(context.getApplicationContext(), "cell_taiwankeyin_experience.sqlite3", null, 1);
        setWriteAheadLoggingEnabled(true);
    }
    @Override public void onCreate(SQLiteDatabase db) {
        db.execSQL("CREATE TABLE choice_stat (reading TEXT NOT NULL, word TEXT NOT NULL, n INTEGER NOT NULL DEFAULT 0, PRIMARY KEY (reading,word))");
        db.execSQL("CREATE TABLE context_edge (context TEXT NOT NULL, word TEXT NOT NULL, n INTEGER NOT NULL DEFAULT 0, PRIMARY KEY (context,word))");
        db.execSQL("CREATE TABLE phrase_stat (phrase TEXT NOT NULL PRIMARY KEY, n INTEGER NOT NULL DEFAULT 0)");
    }
    @Override public void onConfigure(SQLiteDatabase db) {
        super.onConfigure(db);
        db.execSQL("PRAGMA secure_delete=ON");
    }
    @Override public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {
        // No destructive migrations: first version has no older schema.
        throw new IllegalStateException("Unknown database version; refusing to drop learned data");
    }
    private static int readCount(SQLiteDatabase db, String table, String query, String[] args) {
        try (Cursor row = db.rawQuery("SELECT n FROM " + table + " WHERE " + query, args)) {
            return row.moveToFirst() ? row.getInt(0) : 0;
        }
    }
    @Override public synchronized double candidateBonus(String reading, String word, String beforeContext) {
        SQLiteDatabase db = getReadableDatabase();
        int choice = readCount(db, "choice_stat", "reading=? AND word=?", new String[] {reading,word});
        int mostSpecific = 0;
        if (!beforeContext.isEmpty()) {
            KeyinCore.Context10 ctx = new KeyinCore.Context10();
            for (String unit : KeyinCore.units(beforeContext)) ctx.feed(unit);
            for (String suffix : ctx.suffixes()) {
                int count = readCount(db, "context_edge", "context=? AND word=?", new String[] {suffix,word});
                if (count > mostSpecific) mostSpecific = count;
            }
        }
        return Math.log1p(choice) * 28.0 + Math.log1p(mostSpecific) * 32.0;
    }
    @Override public synchronized void learnChoice(String reading, String word, String beforeContext) {
        SQLiteDatabase db = getWritableDatabase();
        db.beginTransaction();
        try {
            db.execSQL("INSERT OR IGNORE INTO choice_stat(reading,word,n) VALUES(?,?,0)", new Object[]{reading,word});
            db.execSQL("UPDATE choice_stat SET n=n+1 WHERE reading=? AND word=?", new Object[]{reading,word});
            KeyinCore.Context10 ctx = new KeyinCore.Context10();
            for (String unit : KeyinCore.units(beforeContext)) ctx.feed(unit);
            for (String suffix : ctx.suffixes()) {
                db.execSQL("INSERT OR IGNORE INTO context_edge(context,word,n) VALUES(?,?,0)", new Object[]{suffix,word});
                db.execSQL("UPDATE context_edge SET n=n+1 WHERE context=? AND word=?", new Object[]{suffix,word});
            }
            db.setTransactionSuccessful();
        } finally { db.endTransaction(); }
    }
    @Override public synchronized void rememberPhrases(List<String> suffixes) {
        if (suffixes.isEmpty()) return;
        SQLiteDatabase db = getWritableDatabase();
        db.beginTransaction();
        try {
            for (String phrase : suffixes) {
                db.execSQL("INSERT OR IGNORE INTO phrase_stat(phrase,n) VALUES(?,0)", new Object[]{phrase});
                db.execSQL("UPDATE phrase_stat SET n=n+1 WHERE phrase=?", new Object[]{phrase});
            }
            db.setTransactionSuccessful();
        } finally { db.endTransaction(); }
    }
    @Override public synchronized List<String> followups(String context, int limit) {
        if (context == null || context.isEmpty() || limit <= 0) return new ArrayList<>();
        LinkedHashSet<String> suggestions = new LinkedHashSet<>();
        KeyinCore.Context10 clipped = new KeyinCore.Context10();
        for(String unit:KeyinCore.units(context)) clipped.feed(unit);
        List<String> suffixes=clipped.suffixes();
        SQLiteDatabase db=getReadableDatabase();
        for(int i=suffixes.size()-1;i>=0 && suggestions.size()<limit;i--) {
            String prefix=suffixes.get(i);
            try(Cursor c=db.rawQuery("SELECT phrase FROM phrase_stat WHERE substr(phrase,1,length(?))=? "
                    + "AND length(phrase)>length(?) ORDER BY n DESC LIMIT 30", new String[]{prefix,prefix,prefix})) {
                while(c.moveToNext() && suggestions.size()<limit) {
                    String phrase=c.getString(0);
                    if(phrase.startsWith(prefix)) suggestions.add(phrase.substring(prefix.length()));
                }
            }
        }
        return new ArrayList<>(suggestions);
    }
    @Override public synchronized void erase() {
        SQLiteDatabase db = getWritableDatabase();
        db.beginTransaction();
        try {
            db.execSQL("DELETE FROM phrase_stat");
            db.execSQL("DELETE FROM context_edge");
            db.execSQL("DELETE FROM choice_stat");
            db.setTransactionSuccessful();
        } finally { db.endTransaction(); }
        db.execSQL("PRAGMA wal_checkpoint(TRUNCATE)");
        db.execSQL("VACUUM");
    }
}
