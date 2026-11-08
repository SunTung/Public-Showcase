package tw.cell.taiwankeyin.android;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Intent;
import android.os.Bundle;
import android.provider.Settings;
import android.view.Gravity;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.Switch;
import android.widget.TextView;
import android.view.inputmethod.InputMethodManager;
import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;

/** Launcher / setup screen: Android owns IME activation, not this app. */
public final class SettingsActivity extends Activity {
    private static final int PICK_LEXICON = 41;
    private TextView status;
    private int dp(float n){return Math.round(n*getResources().getDisplayMetrics().density);}
    private void add(LinearLayout root,String text,Runnable click) {
        Button b=new Button(this);b.setAllCaps(false);b.setText(text);
        b.setOnClickListener(v->click.run());root.addView(b,new LinearLayout.LayoutParams(-1,dp(52)));
    }
    @Override protected void onCreate(Bundle state) {
        super.onCreate(state);
        ScrollView scroll=new ScrollView(this);
        LinearLayout content=new LinearLayout(this);content.setOrientation(LinearLayout.VERTICAL);
        content.setPadding(dp(24),dp(35),dp(24),dp(24));
        scroll.addView(content);setContentView(scroll);
        TextView title=new TextView(this);title.setText("CELL 臺灣注音 · 單一正式版");title.setTextSize(24);
        title.setGravity(Gravity.CENTER);content.addView(title);
        TextView desc=new TextView(this);
        desc.setText("大千注音｜十字上下文｜本機經驗選字\n內建完整 Chewing 臺灣正體字詞庫（158,905筆）；也可自行匯入 UTF-8 TSV 詞庫補充。");
        desc.setTextSize(15);desc.setPadding(0,dp(14),0,dp(12));content.addView(desc);
        add(content,"1. 開啟 Android 輸入法設定",()->startActivity(new Intent(Settings.ACTION_INPUT_METHOD_SETTINGS)));
        add(content,"2. 選擇 CELL 臺灣注音鍵盤",()->{
            InputMethodManager manager=(InputMethodManager)getSystemService(INPUT_METHOD_SERVICE);
            if(manager!=null)manager.showInputMethodPicker();
        });
        Switch learning=new Switch(this);learning.setText("啟用本機十字經驗記憶");
        learning.setChecked(getSharedPreferences("keyboard_settings",MODE_PRIVATE).getBoolean("learning",true));
        learning.setOnCheckedChangeListener((v,on)->getSharedPreferences("keyboard_settings",MODE_PRIVATE)
                .edit().putBoolean("learning",on).apply());content.addView(learning);
        Switch elastic=new Switch(this);
        elastic.setText("彈性按鍵動畫（輕觸膨脹、慢速回彈）");
        elastic.setChecked(getSharedPreferences("keyboard_settings",MODE_PRIVATE)
                .getBoolean("elastic_feedback",true));
        elastic.setOnCheckedChangeListener((v,on)->getSharedPreferences("keyboard_settings",MODE_PRIVATE)
                .edit().putBoolean("elastic_feedback",on).apply());
        content.addView(elastic);
        TextView elasticNote=new TextView(this);
        elasticNote.setText("關閉時恢復靜態按鍵；重新切換鍵盤後套用。按鍵命中位置不因動畫改變。");
        elasticNote.setTextSize(13);
        content.addView(elasticNote);
        add(content,"匯入自己的注音 TSV 詞庫",()->{
            Intent intent=new Intent(Intent.ACTION_OPEN_DOCUMENT);
            intent.setType("*/*");intent.addCategory(Intent.CATEGORY_OPENABLE);
            startActivityForResult(intent,PICK_LEXICON);
        });
        add(content,"清除所有本機學習資料",()->new AlertDialog.Builder(this)
                .setTitle("清除詞句經驗？")
                .setMessage("這會刪除本機個人選字、上下文關聯及已學短句，不會刪除基本詞典。")
                .setNegativeButton("取消",null)
                .setPositiveButton("確定清除",(d,w)->{
                    ExperienceDatabase database=new ExperienceDatabase(this);
                    try{database.erase(); status.setText("本機學習資料已清除。請重新切換一次輸入法以刷新即時上下文。");}
                    finally{database.close();}
                }).show());
        TextView testLabel=new TextView(this);testLabel.setText("試打區（啟用 CELL 鍵盤後點入）");
        testLabel.setPadding(0,dp(17),0,dp(8));content.addView(testLabel);
        EditText test=new EditText(this);test.setHint("例如：你好，今天（台南）天氣很好。");
        test.setMinHeight(dp(110));test.setGravity(Gravity.TOP);content.addView(test);
        status=new TextView(this);status.setPadding(0,dp(18),0,0);status.setTextSize(14);
        status.setText("版本：1.0.1-unified（可與 Alpha1 並存）。完整字詞庫由官方來源生成；罕字與候選排名仍需測試。");content.addView(status);
    }
    @Override protected void onActivityResult(int request,int result,Intent data) {
        super.onActivityResult(request,result,data);
        if(request!=PICK_LEXICON || result!=RESULT_OK || data==null || data.getData()==null)return;
        File destination=new File(getFilesDir(),"imported_lexicon.tsv");
        File temporary=new File(getFilesDir(),"imported_lexicon.partial");
        long length=0;
        try(InputStream in=getContentResolver().openInputStream(data.getData());
            FileOutputStream out=new FileOutputStream(temporary)) {
            if(in==null)throw new IllegalStateException("無法開啟檔案");
            byte[] buf=new byte[8192];int n;
            while((n=in.read(buf))!=-1){length+=n;if(length>32L*1024*1024)throw new IllegalArgumentException("詞庫超過 32 MiB 上限");out.write(buf,0,n);}
            out.getFD().sync();
        } catch(Exception ex){temporary.delete();status.setText("匯入失敗："+ex.getMessage());return;}
        // Validate the *entire* TSV before replacing the user's previous lexicon.
        try {
            tw.cell.taiwankeyin.core.KeyinCore.Lexicon check=new tw.cell.taiwankeyin.core.KeyinCore.Lexicon();
            try(InputStream in=new java.io.FileInputStream(temporary)){check.load(in);}
            if(check.size()<1)throw new IllegalArgumentException("詞庫沒有可用詞條");
            File backup=new File(getFilesDir(),"imported_lexicon.previous");
            if(backup.exists() && !backup.delete())throw new IllegalStateException("舊備份佔用，無法更新");
            if(destination.exists() && !destination.renameTo(backup))throw new IllegalStateException("無法建立原詞庫備份");
            if(!temporary.renameTo(destination)) {
                if(backup.exists())backup.renameTo(destination);
                throw new IllegalStateException("無法完成詞庫更新，原詞庫已嘗試還原");
            }
            if(backup.exists())backup.delete();
            status.setText("詞庫匯入完成："+check.size()+" 條。請重新選擇 CELL 鍵盤載入。");
        }catch(Exception ex){temporary.delete();status.setText("詞庫驗證失敗："+ex.getMessage());}
    }
}
