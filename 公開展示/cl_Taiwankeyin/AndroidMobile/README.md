# cl_Taiwankeyin Android｜CELL 繁體細胞注音輸入法

**Android 輸入法工程 alpha1；可在 Android Studio/CI 建置 APK。**

平台：Android 8.0+（API 26），系統 IME 使用官方 `InputMethodService` / `InputConnection`。

## 功能（目前實作）

- 37 個大千注音根鍵、五聲調、候選列、單字與多音節組詞、退格、英文字母切換、常用繁體標點。
- 最後 **10 個有效字元** 的 CELL 經驗窗；遇 `，。！？、；` 與半形對應標點斷句；`（）〔〕〈〉｛｝：` 保留連接。
- 只在 Android 編輯框確認接收文字後記入本機 SQLite；未選字時不學習。
- 個人選字、上下文關聯與最多 10 字短句經驗；支援學習開關、清除資料、密碼欄位不學習。
- 匯入由 R2-B 產生的 UTF-8 TSV 詞庫（reading<TAB>word<TAB>baseline）。內建示範詞庫來自 R2-A，**不是完整量產詞庫**。
- 禁止系統自動備份使用者學習資料。未使用網路權限，輸入資料僅儲存於裝置內。

## 安裝與開啟

1. 使用 Android Studio 開啟本資料夾，採 JDK 17 / Android SDK 35 / AGP 8.9.2。
2. 執行 Gradle `:app:assembleDebug`；APK 位於 `app/build/outputs/apk/debug/app-debug.apk`。
3. 在 Android 上安裝 APK，開啟 **CELL 臺灣注音** App。
4. 按「開啟 Android 輸入法設定」啟用；再按「選擇 CELL 臺灣注音鍵盤」。
5. 點「試打區」或在其他 App 的文字欄位開始使用。

> GitHub Actions workflow: `.github/workflows/cell-taiwankeyin-android.yml` under the public repository root. On every AndroidMobile folder update it runs headless tests and builds a debug APK artifact.

## 結構與版本關係

- `core/KeyinCore.java`：R1 Context10 + R2-A phonetic/selection contract 的 **Java 行為移植**；不是 C++ JNI 直接連結。R1/R2-A C++ 基線保留不變。
- `android/TaiwanKeyinImeService.java`：Android InputMethodService，真正把字寫入當前編輯框。
- `android/ExperienceDatabase.java`：SQLite 持久化（裝置私有），不與 Windows 資料共用路徑。
- `android/SettingsActivity.java`：開啟設定、選擇 IME、詞庫匯入、清除學習、試打。
- `tests/run_java_tests.sh`：Android SDK 之外獨立執行的純 Java 測試。

## 當前限制與下一關

- 此工作環境沒有 Android SDK / Gradle 安裝包，因此 **尚未在此環境實際編譯出 APK**，也未在真機安裝驗收；可經 GitHub Actions/Android Studio 建置。
- 臺灣全量繁體詞庫仍待匯入、異音字校對與詞頻驗收；不宣稱已完整可用。
- Android Core Java 版為原生平台行為移植，尚未做與 Windows C++ 的逐案例跨語言一致性全面比對。
- 後續追加完整候選分頁、全符號/英數鍵盤、語音、手勢、emoji、Android 真機性能與防撞誤觸設計。

## 隱私

輸入法在作業系統內具有接觸當前輸入欄位的能力。此原型 **不要求網路權限**、**不記錄敏感欄位文字**，且不使用遠端服務。SQLite 儲存可識別的短語，資料不等於匿名；手機遺失時仍應依賴 Android 裝置加密與螢幕鎖。

## 編譯驗收來源

- [工程紀錄](docs/ENGINEERING_REPORT_20261108.md)
- [R1/R2 與 Android Java 的版本關係](docs/SOURCE_LINEAGE.md)
- 此版核心通過 **116** 項 Java 測試；Android APK 的編譯與真機通過狀態需另外查核 GitHub Actions 結果。
