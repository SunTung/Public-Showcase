# CELL 臺灣注音 Android Alpha 3｜崩潰根因與修復驗收

日期：2026-11-08（Asia/Taipei）
版本：0.1.2-alpha3-test
套件 ID：`tw.cell.taiwankeyin.alpha3test`

## Android 模擬器已重現的故障

Alpha2 的 `ExperienceDatabase.onConfigure()` 第25行以 `db.execSQL("PRAGMA secure_delete=ON")` 啟用 SQLite secure_delete。Android 35 的 `SQLiteDatabase.execSQL` 不允許這類會回傳結果的語句，於 SQLite 初次開啟時拋出：

```text
android.database.sqlite.SQLiteException:
unknown error (code 0 SQLITE_OK):
Queries can be performed using SQLiteDatabase query or rawQuery methods only.
at tw.cell.taiwankeyin.android.ExperienceDatabase.onConfigure(ExperienceDatabase.java:25)
```

首次 Android 真實 SQLite 模擬器測試：[Run #42480577292](https://github.com/SunTung/Public-Showcase/actions/runs/42480577292) 失敗，Logcat 明確指向上述程式碼。此故障可讓 Android IME 首次存取候選統計/學習資料庫時崩潰，與使用者反映的鍵盤突然關閉高度一致；**沒有取得使用者 Samsung 真機 Logcat，不能宣稱手機每次崩潰的 stack trace 已被直接證明相同。**

## 修復內容

1. `ExperienceDatabase.onConfigure()` 改為用 `db.rawQuery("PRAGMA secure_delete=ON",null)`，驗證 SQLite 游標回傳值；清除資料時 `PRAGMA wal_checkpoint(TRUNCATE)` 也改為 `rawQuery`。
2. `CommitBridge` 調整提交交易順序：先 `InputConnection.commitText`，Android 編輯框確認成功後才清除注音組字並寫入記憶；拒絕提交、失去連線與例外時保留候選。
3. 候選查詢、SQLite 學習/預測失敗都有 Logcat 記錄並容錯，不再讓單純資料庫失敗直接中斷鍵盤。
4. 移除永久的「CELL 注音／十字經驗」標題與提示，候選列只顯示動態注音、候選字及預測。
5. 聲調/符號鍵排由49dp縮至36dp；保留37個注音符號的10欄布局。
6. Debug 專用模擬器測試使用獨立 `cell_taiwankeyin_probe_only.sqlite3`，不會刪除使用者學習資料；Alpha3 使用獨立 package ID，可與 Alpha1/Alpha2 並存。

## 修復後的實際驗收

- GitHub 原始碼修復 commit：`efb244b0edf1cd28abe69e775fce2cbc7fc80b8e`。
- Java 核心回歸：**215/215 PASS**，包含提交被拒絕、連線失效、學習例外等。
- [Alpha3 APK GitHub Actions #42480967383](https://github.com/SunTung/Public-Showcase/actions/runs/42480967383)：**SUCCESS**；Android SDK35、Gradle 編譯、APK 存在性與 Artifact 上傳通過。
- [Android 35 模擬器整合測試 #42480967204](https://github.com/SunTung/Public-Showcase/actions/runs/42480967204)：**SUCCESS**。Job log 實際輸出：
  `CELL_IME_PROBE: PASS real EditText InputConnection, SQLite choice, phrase and erase`
- 這次整合測試是 Android 真實 `EditText`、`InputConnection` 與 SQLite，包含「ㄋㄧㄏㄠ」選「你好」、確定上屏、候選統計、下一字提示與清除。
- APK 大小 **40,369 bytes**。SHA-256：`421ab561333f00cc2defc636bff6e3f09185e3c21611d8833dabcfcd0637a734`。
- Google Drive APK 已重新下載，其大小及 SHA-256 與本地一致。
- 修復版完整來源 ZIP SHA-256：`64e4b26dfbf51e5689c967ab9e356363a0624341f7f01d93d49cebeaf2d64e14`，Google Drive 回讀一致。

## 原始碼與備份

- [GitHub AndroidMobile 原始碼](AndroidMobile/)
- [Google Drive 修正後 APK](https://drive.google.com/file/d/1u1aYavXDD526mxZ0oPh_Zdp1iAVVgL-K/view)
- [Google Drive Alpha3 修正後完整原始碼 ZIP](https://drive.google.com/file/d/1Pz5LtnhQUaZBJs2An3zmMgF46J6WC3sp/view)
- [GitHub Android 編譯測試](https://github.com/SunTung/Public-Showcase/actions/runs/42480967383)
- [GitHub Android SQLite/編輯框整合測試](https://github.com/SunTung/Public-Showcase/actions/runs/42480967204)

## 未驗收項

Android 模擬器的內建 Debug Probe 測試不等於對 ChatGPT、Word、各家手機鍵盤切換的完整實機端對端驗收。Samsung Android 16 的輸入法切換、觸控、鍵盤高度、不同編輯框、長時間輸入及個人詞庫仍待使用者手機試打。內建詞庫仍是小型測試種子，非完整繁體語料。
