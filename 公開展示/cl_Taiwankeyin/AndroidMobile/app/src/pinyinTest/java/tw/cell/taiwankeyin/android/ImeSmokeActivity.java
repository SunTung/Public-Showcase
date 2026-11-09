package tw.cell.taiwankeyin.android;

import android.app.Activity;
import android.os.Bundle;
import android.content.Context;
import android.text.InputType;
import android.view.WindowManager;
import android.view.inputmethod.InputMethodManager;
import android.widget.EditText;
import android.widget.LinearLayout;

/** Pilot-build only: deterministic real EditText for Android IME UI acceptance. */
public final class ImeSmokeActivity extends Activity {
    @Override protected void onCreate(Bundle state) {
        super.onCreate(state);
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(20,40,20,20);
        EditText editor = new EditText(this);
        editor.setInputType(InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_FLAG_MULTI_LINE);
        editor.setHint("CELL IME acceptance editor");
        editor.setMinHeight(160);
        root.addView(editor,new LinearLayout.LayoutParams(-1,-2));
        setContentView(root);
        getWindow().setSoftInputMode(WindowManager.LayoutParams.SOFT_INPUT_STATE_ALWAYS_VISIBLE);
        editor.requestFocus();
        editor.postDelayed(() -> {
            InputMethodManager imm=(InputMethodManager)getSystemService(Context.INPUT_METHOD_SERVICE);
            if(imm!=null) imm.showSoftInput(editor,InputMethodManager.SHOW_IMPLICIT);
        },800);
    }
}
