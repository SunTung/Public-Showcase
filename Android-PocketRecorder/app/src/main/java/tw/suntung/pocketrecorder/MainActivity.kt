package tw.suntung.pocketrecorder

import android.Manifest
import android.app.Activity
import android.content.pm.PackageManager
import android.media.MediaPlayer
import android.media.MediaRecorder
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.view.Gravity
import android.view.View
import android.widget.*
import android.graphics.Color
import org.json.JSONArray
import org.json.JSONObject
import java.io.File
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.UUID

class MainActivity : Activity() {
    private val handler = Handler(Looper.getMainLooper())
    private val records = mutableListOf<Entry>()
    private lateinit var status: TextView
    private lateinit var timer: TextView
    private lateinit var items: LinearLayout
    private lateinit var recordButton: Button
    private var recorder: MediaRecorder? = null
    private var player: MediaPlayer? = null
    private var pending: File? = null
    private var startedAt = 0L
    private var testing = false
    private var recording = false
    private val tick = object : Runnable {
        override fun run() {
            if (recording) {
                val elapsed = (System.currentTimeMillis() - startedAt) / 1000
                timer.text = formatDuration(elapsed * 1000)
                if (testing) {
                    val level = try { recorder?.maxAmplitude ?: 0 } catch (_: Exception) { 0 }
                    status.text = "麥克風測試中 · 音量 $level"
                }
                handler.postDelayed(this, 250)
            }
        }
    }
    data class Entry(val id: String, var name: String, val filename: String, val duration: Long, val timestamp: Long, var note: String)

    private fun dp(n: Int) = (n * resources.displayMetrics.density + 0.5f).toInt()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.statusBarColor = Color.rgb(245, 248, 252)
        window.navigationBarColor = Color.rgb(245, 248, 252)
        window.decorView.systemUiVisibility = View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR or View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(dp(16), dp(14), dp(16), dp(12))
            fitsSystemWindows = true
            setBackgroundColor(Color.rgb(245, 247, 251))
        }
        val title = TextView(this).apply { text = "手機錄音器"; textSize = 26f; setTypeface(null, android.graphics.Typeface.BOLD); setTextColor(Color.rgb(26,43,68)); gravity = Gravity.CENTER }
        root.addView(title, LinearLayout.LayoutParams(-1, dp(60)))
        status = TextView(this).apply { text = "待機中"; textSize = 20f; gravity = Gravity.CENTER; setTypeface(null, android.graphics.Typeface.BOLD); setTextColor(Color.rgb(0,129,115)) }
        root.addView(status, LinearLayout.LayoutParams(-1, dp(54)))
        timer = TextView(this).apply { text = "00:00"; textSize = 34f; setTextColor(Color.rgb(35,55,80)); gravity = Gravity.CENTER }
        root.addView(timer, LinearLayout.LayoutParams(-1, dp(55)))
        val row1 = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL; gravity = Gravity.CENTER_VERTICAL }
        recordButton = button("錄音") { ensureMicrophone { startRecording(false) } }
        row1.addView(recordButton, LinearLayout.LayoutParams(0, dp(64), 1f))
        row1.addView(button("播放") { playLatest() }, LinearLayout.LayoutParams(0, dp(64), 1f))
        root.addView(row1, LinearLayout.LayoutParams(-1, dp(78)))
        val row2 = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL; gravity = Gravity.CENTER_VERTICAL }
        row2.addView(button("停止") { stopAll() }, LinearLayout.LayoutParams(0, dp(64), 1f))
        row2.addView(button("新工作") { newWork() }, LinearLayout.LayoutParams(0, dp(64), 1f))
        root.addView(row2, LinearLayout.LayoutParams(-1, dp(78)))
        root.addView(button("麥克風測試（5 秒）") { ensureMicrophone { startRecording(true) } }, LinearLayout.LayoutParams(-1, dp(60)))
        val label = TextView(this).apply { text = "錄音檔案"; textSize = 19f; setTypeface(null, android.graphics.Typeface.BOLD); setTextColor(Color.rgb(26,43,68)); setPadding(dp(6), dp(18), 0, dp(10)) }
        root.addView(label)
        val scroller = ScrollView(this)
        items = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL }
        scroller.addView(items)
        root.addView(scroller, LinearLayout.LayoutParams(-1, 0, 1f))
        setContentView(root)
        load()
        render()
    }
    private fun button(name: String, action: () -> Unit) = Button(this).apply {
        text = name
        textSize = 16f
        setTypeface(null, android.graphics.Typeface.BOLD)
        setTextColor(Color.WHITE)
        isAllCaps = false
        setSingleLine(true)
        gravity = Gravity.CENTER
        minHeight = 0
        minimumHeight = 0
        minWidth = 0
        minimumWidth = 0
        setPadding(dp(4), 0, dp(4), 0)
        val color = when (name) {
            "錄音" -> Color.rgb(217, 66, 76)
            "停止", "刪除" -> Color.rgb(112, 123, 141)
            "新工作" -> Color.rgb(38, 116, 165)
            else -> Color.rgb(16, 135, 122)
        }
        background = android.graphics.drawable.GradientDrawable().apply {
            setColor(color)
            cornerRadius = dp(13).toFloat()
        }
        val margins = LinearLayout.LayoutParams(0, dp(60), 1f)
        setOnClickListener { action() }
    }
    private fun ensureMicrophone(action: () -> Unit) {
        if (checkSelfPermission(Manifest.permission.RECORD_AUDIO) == PackageManager.PERMISSION_GRANTED) action()
        else requestPermissions(arrayOf(Manifest.permission.RECORD_AUDIO), 12)
    }
    override fun onRequestPermissionsResult(requestCode: Int, permissions: Array<out String>, grantResults: IntArray) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == 12 && grantResults.firstOrNull() == PackageManager.PERMISSION_GRANTED) {
            Toast.makeText(this, "麥克風已授權，請再按一次按鈕", Toast.LENGTH_SHORT).show()
        } else if (requestCode == 12) Toast.makeText(this, "需要麥克風權限", Toast.LENGTH_LONG).show()
    }
    private fun recordingsDir(): File = File(filesDir, "recordings").apply { mkdirs() }
    private fun startRecording(test: Boolean) {
        if (recording) return
        stopPlayback()
        testing = test
        val filename = (if (test) "test_" else "rec_") + System.currentTimeMillis() + "_" + UUID.randomUUID().toString().take(8) + ".m4a"
        val file = File(recordingsDir(), filename)
        try {
            val r = MediaRecorder().apply {
                setAudioSource(MediaRecorder.AudioSource.MIC)
                setOutputFormat(MediaRecorder.OutputFormat.MPEG_4)
                setAudioEncoder(MediaRecorder.AudioEncoder.AAC)
                setAudioEncodingBitRate(128000)
                setAudioSamplingRate(44100)
                setOutputFile(file.absolutePath)
                prepare()
                start()
            }
            recorder = r
            pending = file
            startedAt = System.currentTimeMillis()
            recording = true
            status.text = if (test) "麥克風測試中" else "錄音中"
            handler.removeCallbacks(tick)
            handler.post(tick)
            if (test) handler.postDelayed({ if (recording && testing) stopRecording() }, 5000)
        } catch (e: Exception) {
            try { recorder?.release() } catch (_: Exception) {}
            recorder = null
            recording = false
            file.delete()
            status.text = "待機中"
            Toast.makeText(this, "無法開始錄音：${e.message}", Toast.LENGTH_LONG).show()
        }
    }
    private fun stopRecording() {
        if (!recording) return
        recording = false
        handler.removeCallbacks(tick)
        status.text = "儲存中"
        val file = pending
        val test = testing
        testing = false
        val duration = System.currentTimeMillis() - startedAt
        var success = true
        try { recorder?.stop() } catch (_: Exception) { success = false }
        try { recorder?.release() } catch (_: Exception) {}
        recorder = null
        pending = null
        if (test || !success || duration < 500 || file == null || !file.exists() || file.length() == 0L) {
            file?.delete()
            Toast.makeText(this, if (test) "麥克風測試完成（不保存）" else "錄音過短或儲存失敗", Toast.LENGTH_SHORT).show()
        } else {
            val time = System.currentTimeMillis()
            val name = "錄音_" + SimpleDateFormat("yyyyMMdd_HHmmss", Locale.TAIWAN).format(Date(time))
            records.add(0, Entry(UUID.randomUUID().toString(), name, file.name, duration, time, ""))
            save()
        }
        timer.text = "00:00"
        status.text = "待機中"
        render()
    }
    private fun stopPlayback() {
        try { player?.stop() } catch (_: Exception) {}
        try { player?.release() } catch (_: Exception) {}
        player = null
        if (!recording) status.text = "待機中"
    }
    private fun stopAll() {
        if (recording) stopRecording()
        else stopPlayback()
    }
    private fun newWork() {
        stopAll()
        timer.text = "00:00"
        status.text = "待機中"
        Toast.makeText(this, "新工作已準備，按錄音開始", Toast.LENGTH_SHORT).show()
    }
    private fun playLatest() {
        if (recording) return
        val entry = records.firstOrNull() ?: run { Toast.makeText(this,"尚無錄音",Toast.LENGTH_SHORT).show(); return }
        play(entry)
    }
    private fun play(entry: Entry) {
        if (recording) return
        stopPlayback()
        val f = File(recordingsDir(), entry.filename)
        if (!f.exists()) { Toast.makeText(this, "音訊檔案遺失", Toast.LENGTH_LONG).show(); return }
        try {
            player = MediaPlayer().apply {
                setDataSource(f.absolutePath)
                setOnCompletionListener { stopPlayback() }
                prepare()
                start()
            }
            status.text = "播放中"
        } catch (e: Exception) { stopPlayback(); Toast.makeText(this,"播放失敗：${e.message}",Toast.LENGTH_LONG).show() }
    }
    private fun askEdit(entry: Entry, note: Boolean) {
        val input = EditText(this).apply { setSingleLine(!note); setText(if(note) entry.note else entry.name); setSelection(text.length) }
        android.app.AlertDialog.Builder(this)
            .setTitle(if (note) "編輯備註" else "變更名稱")
            .setView(input)
            .setPositiveButton("儲存") { _, _ ->
                val value = input.text.toString().trim()
                if (note) entry.note = value else if (value.isNotEmpty()) entry.name = value
                save(); render()
            }
            .setNegativeButton("取消", null).show()
    }
    private fun delete(entry: Entry) {
        android.app.AlertDialog.Builder(this).setTitle("刪除錄音")
            .setMessage("確定刪除「${entry.name}」？無法復原。")
            .setPositiveButton("刪除") { _, _ ->
                if (player != null) stopPlayback()
                val file = File(recordingsDir(), entry.filename)
                if (file.exists() && !file.delete()) {
                    Toast.makeText(this, "檔案刪除失敗", Toast.LENGTH_LONG).show()
                } else { records.remove(entry); save(); render() }
            }.setNegativeButton("取消", null).show()
    }
    private fun formatDuration(ms: Long): String {
        val seconds = ms / 1000
        return String.format(Locale.US, "%02d:%02d", seconds / 60, seconds % 60)
    }
    private fun render() {
        items.removeAllViews()
        if (records.isEmpty()) {
            items.addView(TextView(this).apply { text = "尚無錄音檔案"; textSize = 17f; gravity = Gravity.CENTER; setPadding(0, 30, 0, 0) })
            return
        }
        for (entry in records) {
            val card = LinearLayout(this).apply {
                orientation = LinearLayout.VERTICAL
                setPadding(dp(12), dp(12), dp(12), dp(12))
                background = android.graphics.drawable.GradientDrawable().apply { setColor(Color.WHITE); cornerRadius = dp(14).toFloat() }
            }
            card.addView(TextView(this).apply { text = entry.name; textSize = 19f; setTextColor(Color.BLACK) })
            val date = SimpleDateFormat("yyyy/MM/dd HH:mm:ss", Locale.TAIWAN).format(Date(entry.timestamp))
            card.addView(TextView(this).apply { text = "長度：${formatDuration(entry.duration)}   類型：M4A / AAC\n紀錄時間：$date\n備註：${entry.note.ifEmpty { "無" }}"; textSize = 14f })
            val actions = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL }
            for ((name, cb) in listOf(
                "播放" to { play(entry) },
                "改名" to { askEdit(entry, false) },
                "備註" to { askEdit(entry, true) },
                "刪除" to { delete(entry) }
            )) actions.addView(button(name, cb), LinearLayout.LayoutParams(0, dp(58), 1f))
            card.addView(actions)
            val lp = LinearLayout.LayoutParams(-1, -2).apply { bottomMargin = dp(12) }
            items.addView(card, lp)
        }
    }
    private fun save() {
        val arr = JSONArray()
        for (r in records) arr.put(JSONObject().put("id", r.id).put("name", r.name).put("file", r.filename).put("duration", r.duration).put("timestamp", r.timestamp).put("note", r.note))
        getSharedPreferences("recorder", MODE_PRIVATE).edit().putString("records", arr.toString()).apply()
    }
    private fun load() {
        val saved = getSharedPreferences("recorder", MODE_PRIVATE).getString("records", "[]") ?: "[]"
        try {
            val arr = JSONArray(saved)
            for (i in 0 until arr.length()) {
                val o = arr.getJSONObject(i)
                val e = Entry(o.getString("id"), o.getString("name"), o.getString("file"), o.getLong("duration"), o.getLong("timestamp"), o.optString("note"))
                if (File(recordingsDir(), e.filename).exists()) records.add(e)
            }
        } catch (_: Exception) { Toast.makeText(this, "錄音索引讀取失敗", Toast.LENGTH_LONG).show() }
    }
    override fun onStop() {
        super.onStop()
        if (recording) stopRecording()
    }
    override fun onDestroy() {
        if (recording) stopRecording()
        stopPlayback()
        super.onDestroy()
    }
}
