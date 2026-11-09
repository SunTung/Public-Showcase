package tw.cell.taiwankeyin.android;

import android.os.SystemClock;
import android.view.KeyEvent;
import android.view.inputmethod.InputConnection;

/** Editor deletion only. Does not mutate the IME's Zhuyin composition. */
public final class EditorDeleteBridge {
    private EditorDeleteBridge() {}
    public static boolean deleteOne(InputConnection connection) {
        if (connection == null) return false;
        CharSequence selection = connection.getSelectedText(0);
        boolean deleted = selection != null && selection.length() > 0
                ? connection.commitText("", 1)
                : connection.deleteSurroundingTextInCodePoints(1, 0);
        if (deleted) return true;
        long now = SystemClock.uptimeMillis();
        boolean down = connection.sendKeyEvent(
                new KeyEvent(now, now, KeyEvent.ACTION_DOWN, KeyEvent.KEYCODE_DEL, 0));
        boolean up = connection.sendKeyEvent(
                new KeyEvent(now, now, KeyEvent.ACTION_UP, KeyEvent.KEYCODE_DEL, 0));
        return down && up;
    }
}
