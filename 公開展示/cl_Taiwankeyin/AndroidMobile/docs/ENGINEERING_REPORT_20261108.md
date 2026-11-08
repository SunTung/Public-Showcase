# cl_Taiwankeyin Android｜初版工程驗收 R0/R1
日期：2026-11-08（Asia/Taipei）

## 已完成

- Android 原生 Java 專案；正式 `android.view.InputMethod` Service 的 Manifest、輸入法 XML、啟用設定 Activity。
- `InputMethodService` + `InputConnection.commitText` 介接正式 Android 文字編輯框。
- 大千注音37符號、五聲調，中文／英文／全形符號三種觸控面板，候選選字及字串上屏。
- Android 設備本機 SQLite：學過的候選、前後文、最多10有效字的短句，支援關閉學習、清除資料、密碼欄位不學習。
- 依前文與已學短句提供候選排序及下文延伸建議。
- 支援匯入原 R2-B 格式的 UTF-8 TSV 詞庫，含32 MiB 限制與舊詞庫備份還原邏輯。
- 內建 R2-A 原版小型種子詞庫；未捏造真正完整詞庫已到位。

## 在 GPT Linux 環境實測

- Java 21 `javac` 編譯純 Java KeyinCore + 測試程式成功。
- `bash tests/run_java_tests.sh`：**116 項檢查 PASS**。
- `AndroidManifest.xml` 及 `res/xml/method.xml` XML 解析檢查通過。
- 測試範圍：鍵位正反映射、五聲調、十字上限、括號及冒號跨段、一般標點斷句、組合附加符與 ZWJ 範例、已選字才學習、同音改排序、下文建議、敏感模式、學習資料清除。

## 未驗收

- 此 GPT 容器沒有 Android SDK / Gradle，**不能宣稱 APK 已在本機成功編譯**。
- Android Service/Activity 尚未經 Gradle `assembleDebug` 或裝置手動操作的最終驗收。
- 全量繁體詞庫尚未校正；真實大量詞彙選字速度、字元等價性與跨應用穩定性尚待測。
- Java Unicode 分段是相容常見文字/組合 emoji 的工程近似，不是和 R1 ICU 完全同等的 Unicode UAX #29 實作。
- Android 使用者設定的詳細權限及鍵盤顯示，會依 Android 版本與系統 UI 有所不同。

## 下階段

1. GitHub Actions 建置 APK，查核 Gradle/Android SDK compile/manifest 稽核與上傳 artifact。
2. 實機/模擬器安裝；驗證啟用鍵盤、主流 App 輸入、候選 UI、焦點切換、密碼安全與清理。
3. 導入完整有來源的繁體詞庫；改善觸控按鍵大小、聲韻構字及 Unicode 字素完整性。
4. 依 Android 設備使用者測試，釋出 signed APK；此回合可提供 Debug 版工作流程，但不可稱為已簽章正式發行。
