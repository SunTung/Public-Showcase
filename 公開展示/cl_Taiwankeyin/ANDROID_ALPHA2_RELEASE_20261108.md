# cl_Taiwankeyin Android 0.1.1-alpha2-test｜APK 發行驗收

日期：2026-11-08（Asia/Taipei）

## 版本關係與實際修復

- 原有 R1/R2 Windows C++ 核心保持不變；這是 Android Java IME Alpha1 的增量修復。
- 原本每排7鍵的注音主區改為每排10個等寬格，共4排；5個可選聲調鍵與5個常用標點鍵共排，主鍵區更緊湊。
- 未指定聲調的完整注音也直接查詢候選，支持「ㄏㄠ → 好」、「ㄋㄧㄏㄠ → 你好」，透過空白鍵確認，不額外插入空格；明確聲調仍可選。
- 同一行連續輸入下一個聲母時，前一個完整音節自動推進；維持退格後還原候選、十字上下文與敏感欄位不學習。
- Alpha1 與 Alpha2 首次 CI Debug APK 的 APK Signature v2 憑證指紋不同，Android 無法保證覆蓋升級。為避免卸載 Alpha1 時破壞本機學習資料，最新 Alpha2 Debug 使用獨立 package ID `tw.cell.taiwankeyin.alpha2test`，顯示名稱「CELL 臺灣注音 Alpha2 測試」，**可與 Alpha1 並存**。兩版 SQLite 資料分開。

## 經查核的測試與 APK

- 本地 Linux Java 核心：**197/197 PASS**。
- GitHub 變更 commit：`184b9eca24f27a87c94dd8cb6908481752493f5e`。
- [GitHub Actions #42478920166](https://github.com/SunTung/Public-Showcase/actions/runs/42478920166)：**SUCCESS**，Java 核心測試、Android SDK、Gradle `assembleDebug`、APK 存在及 Artifact 上傳全部通過。
- Artifact ID：`13616443219`；Google Drive 已永久備份並回讀一致。
- APK 大小 **36,509 bytes**；APK SHA-256：`dd9cedc3e8b989a9a93a3ece3a1104bdd1334b5df054ea876a958e37631f542e`。
- APK Binary AndroidManifest.xml 已核對：package `tw.cell.taiwankeyin.alpha2test`、顯示名稱「CELL 臺灣注音 Alpha2 測試」、版本 `0.1.1-alpha2-test`；含 `classes.dex` 與注音種子詞庫。

## 備份與取得

- [Alpha2 Android Debug APK（Google Drive）](https://drive.google.com/file/d/13mwQsDO6UWQUWl85XFJu1CWTPyInI5xx/view)
- [Alpha2 自包含原始碼 ZIP（Google Drive）](https://drive.google.com/file/d/1arIuiMVYUpGv68U4swBM5ksmDcCRD9_V/view)
- [GitHub 完整 Android 原始碼](AndroidMobile/)
- [GitHub 成功 CI Run](https://github.com/SunTung/Public-Showcase/actions/runs/42478920166)
- Google Drive APK 與 source ZIP 均已重新下載、比對 SHA-256 完全一致。

## 手機操作與驗收邊界

安裝 APK（不需卸載 Alpha1）→ 開啟「CELL 臺灣注音 Alpha2 測試」→ 啟用這個新輸入法 → 選擇 Alpha2 鍵盤 → 在試打區輸入「ㄏ、ㄠ、空白」檢查「好」，再輸入「ㄋ、ㄧ、ㄏ、ㄠ、空白」檢查「你好」。可再測試指定聲調、退格、標點、鍵盤寬度。

本次**已驗證 APK 編譯成功，不代表已完成 Android 真機 UX/長期效能驗收**。大型繁體字詞庫仍未完整導入。
