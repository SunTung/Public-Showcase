# CELL TaiwanKeyin Android Alpha 3｜手機選字故障查核與修復

日期：2026-11-08（Asia/Taipei）
版本：0.1.2-alpha3-test，獨立 package `tw.cell.taiwankeyin.alpha3test`。

## 問題與證據

實際手機回報：多餘標題/說明占用高度、聲調符號排過高、「ㄋㄧㄏㄠ」無法提交，輸入法有時會關閉。

原始碼確認的**流程缺陷**：`TaiwanKeyinImeService.chooseCandidate()` 先執行 `session.choose(index)`（此動作會清除 pending phonetics / candidates），然後才呼叫 `InputConnection.commitText()`。Android 編輯框拒絕提交、回傳 false 或已斷線時，原先組字仍被無條件丟棄，且沒有恢復途徑。舊版 `memory.committed()`、候選查詢和預測查詢的 Android SQLite 例外也沒有防護。先前 197 項是 JVM 測試，使用記憶型 mock backend，未經真 Android SQLite/ InputConnection 驗證。

**限制：** 以上是實際程式碼缺陷，不等於已經從使用者手機 logcat 取得導致 IME 程序關閉的確切 Java exception；具體手機 crash stacktrace 仍待 Android 端擷取。不能把假說當成已驗證的特定崩潰原因。

## 已在 Android 35 模擬器實際重現的確切 SQL 崩潰點

- CI Run #42480577292 模擬器 smoke FAILED，Logcat 顯示：
  `android.database.sqlite.SQLiteException: unknown error (code 0 SQLITE_OK): Queries can be performed using SQLiteDatabase query or rawQuery methods only.`
- Stacktrace 落在 `ExperienceDatabase.onConfigure(ExperienceDatabase.java:25)`，舊版執行 `db.execSQL("PRAGMA secure_delete=ON")`。
- **這是比最初 transaction ordering 更直接、可重現的 Android 閃退原因。** 資料庫初次開啟時就能發生，完全不需要已上屏的文字。
- 已改成 `db.rawQuery("PRAGMA secure_delete=ON", null)`，明確讀取驗證回傳結果；同時修正清除資料時 `PRAGMA wal_checkpoint(TRUNCATE)` 也不能再用 `execSQL`。
- Debug Probe 使用獨立 SQLite 檔案 `cell_taiwankeyin_probe_only.sqlite3`，不會清除一般 Alpha3 使用者的學習庫。
- 需以修正後的 Android Emulator 再次跑通，才可宣告 Android SQLite/編輯器整合 PASS。

## 修正

1. 新增 `core/CommitBridge.java`，編輯器確實回傳 commit 成功後，才清除候選並記憶；拒絕/空連線/拋例外均保留注音，不讓文字悄悄消失。
2. 本機 SQLite 學習/預測失敗時記錄 Logcat，停用本次學習而保持文字上屏；候選讀取異常則退回不學習的 baseline 再次產生候選，避免未處理例外讓 IME 服務被系統終止。
3. 移除上方永久標題與教學文字（37dp）；候選列只顯示正在組的注音及真正候選，不顯示多餘 placeholder。
4. 聲調與標點排由 49dp 縮到 36dp，按鈕由 46dp 縮到 33dp；37 個注音仍每排 10 個等寬格。
5. 擴充 JVM 測試至 215 項：成功、拒絕、null 編輯器、失去連線拋錯、SQLite 學習失敗後仍保留已上屏文字。
6. 新增 Android debug 專用 `ImeProbeActivity`，使用 Android 真正的 `EditText.onCreateInputConnection()`、SQLite WAL、短句預測與清除來做 Android 環境整合檢查。此 Probe 只存在於 debug source set，不會進入正式 release。
7. Alpha3 Debug 使用獨立 applicationId 後綴 `.alpha3test`，保留已安裝 Alpha1/Alpha2 與其本機學習資料，不強制卸載。

## 驗收條件

- Java JVM 215/215 PASS（本地）。
- Android SDK GitHub Actions `:app:assembleDebug` 必須通過，才能稱已編譯 APK。
- Emulator smoke 必須出現 `CELL_IME_PROBE: PASS real EditText InputConnection...` 才能宣告真 Android DB/Editor 提交流程 PASS。
- Android 手機實機仍需觀察是否可在 ChatGPT/記事本輸入法正常長期顯示並輸入，且不得無故退出。
- Android Logs：`adb logcat -v time -s CellTaiwanKeyin:E CELL_IME_PROBE:D AndroidRuntime:E`。

Windows R1/R2 C++ 檔案沒有更動；Android 10 字經驗規則仍與 Alpha2 相同。
