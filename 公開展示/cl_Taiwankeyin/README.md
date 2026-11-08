# cl_Taiwankeyin｜繁體細胞注音輸入法（Windows + Android）

## CELL 中英繁簡細胞字典 v0.3｜2026-11-09

- **最新有效概念字典**：[GitHub v0.3 完整程式與三批自編詞條](CELL_Chinese_Lexicon_v0_3/README.md)，累計 423 個概念、1,269 筆三語表述，第三批新加 127 個概念。
- [Google Drive 字典工作區](https://drive.google.com/drive/folders/1HXBHw6XymF4Z9GNH8RMyRoT-bWJj0s82)／[v0.3 SQLite + JSON + 原始碼 ZIP](https://drive.google.com/file/d/1K2gCgy1McZc85r4K_wlY7yday7moAao1/view)。
- **[CI 35/35 PASS](https://github.com/SunTung/Public-Showcase/actions/runs/42536643257)**，雲端 ZIP SHA-256 比對成功。
- 新增繁簡字形歧義候選、簡體同形 QA 提醒、英繁簡搜尋 CLI；原 v0.2 全部概念和測試保留。
- 尚未完成人工語義／讀音逐條驗收，也**尚未取代 Android/Windows 的 158,905 筆舊輸入法詞庫**。下一步以字形層、多義詞審核及可回退雙庫實驗為主。


## CELL 中英繁簡字典 v0.2｜最新增量（2026-11-09）

- [**最新 v0.2 GitHub 原始碼**](CELL_Chinese_Lexicon_v0_2/README.md)：沿用 v0.1 的90個獨立概念，新增206個自編中英繁簡對照，共296概念／888三語表述。新詞不虛填讀音，全部標為 `draft_review`；14項 SQLite/查詢/匯出測試通過。
- [Google Drive 字典專用資料夾](https://drive.google.com/drive/folders/1HXBHw6XymF4Z9GNH8RMyRoT-bWJj0s82) · [v0.2 完整原始碼／SQLite／JSON 匯出 ZIP](https://drive.google.com/file/d/19JaNyPahwb15TrgCHOFaMigjaalYYY5A/view)。
- **現行 Android/Windows 仍使用 158,905 筆舊版輸入法詞庫**；此 v0.2 是獨立可查詢的自編字典，尚未達到替換既有輸入法的完整覆蓋率。
- 舊 v0.1 保留作回歸基線；往後只在 v0.2 增量，不重新建一套不同命名的字典。


## CELL 中英繁簡獨立概念字典｜2026-11-09

- **新建，不是舊詞庫改名**：[CELL_Chinese_Lexicon_v0_1 原始碼與自編種子](CELL_Chinese_Lexicon_v0_1/README.md)。第一批 **90 概念／270 中英繁簡表述／180 讀音／8 歧義字形案例**；6 項 Python/SQLite 測試通過。
- [Google Drive 專用工作資料夾](https://drive.google.com/drive/folders/1HXBHw6XymF4Z9GNH8RMyRoT-bWJj0s82) · [完整 SQLite+原始碼 ZIP](https://drive.google.com/file/d/1_adKcwxChSy6pgKYYO4YMJJC9hNkVm2V/view)。
- 字典以 concept_id 關聯繁體、簡體、英文與讀音；歧義與地區差異分開保存。既有 158,905 筆 Chewing 派生詞庫**保留作輸入法穩定基線**，尚未用 90 條試驗種子取代。
- 新專案詞條仍待多來源語義與讀音複核；外部資料僅用於比較驗證，不直接冒充 CELL 自編字典。完整版尚未完成。


## 最新有效版本｜2026-11-09

- **Android v1.0.2 單一正式版**：已上字後的詞庫智慧接續推薦，沿用原 App ID 與正式簽章，可直接覆蓋 v1.0.1。[Google Drive APK](https://drive.google.com/file/d/16B-hg97Sn1w5qT-AikFyzwzhg9AM79Em/view)／[GitHub 769項測試+編譯](https://github.com/SunTung/Public-Showcase/actions/runs/42498189189)／[Android 35 模擬器驗收](https://github.com/SunTung/Public-Showcase/actions/runs/42498189515)。
- **Windows v0.2.1 圖形預覽版**：最新 EXE 封裝內含 158905 筆離線詞庫，提供注音／可選聲調／候選選字／接續詞／四種配色／剪貼簿；**還不是 Windows TSF 系統 IME**。[Windows EXE ZIP](https://drive.google.com/file/d/1k0-gKoKlxI-j2VIl4_Xb9TYaqVfWcHci/view)／[原始碼](https://drive.google.com/file/d/1_wiZON_s3NxS0QfJoYhymhk5IFmrZh2m/view)／[Win CI](https://github.com/SunTung/Public-Showcase/actions/runs/42499718323)。
- **備份已清理**：Alpha1～5 和重複資料包已移除，保留 Android 最新及兩個正式回退版本、完整詞庫和簽章金鑰；原 R1/R2 C++ 和 RGOS 研究基線保留。
- **下一代規格（尚未完成）**：將配色列一枚按鈕更換為「注繁／拼簡」，真正接入漢語拼音解析、簡體字詞候選，不能只改 UI。[工作驗收及清理 Ledger](RELEASE_V102_WIN_V02_CLEANUP_20261109.md)。


## Android 單一正式版 v1.0.1｜彈性回彈＋每按鍵隨機調色

- **固定 applicationId `tw.cell.taiwankeyin`、versionCode 101**；沿用 v1.0.0 正式簽章，可覆蓋更新，絕不另建 Alpha 鍵盤。
- **[下載已簽署 v1.0.1 APK（Google Drive）](https://drive.google.com/file/d/1_kPc2hiqrK30WfkDCPBcpncUuB7BAfnK/view)** · [完整新版原始碼 ZIP](https://drive.google.com/file/d/1ZB5-TlNHjM1LVPgeceH_feJWFkRWKeoJ/view)。
- 第七色塊「彩」啟動隨機配色：每次按鍵後，全部主鍵從六組顏色中重新分配，且按鍵幾何不變；保留彈性膨脹與回彈。
- [詳細技術驗收報告](AndroidMobile/docs/UNIFIED_V101_ELASTIC_RANDOM_20261108.md) · [Release CI](https://github.com/SunTung/Public-Showcase/actions/runs/42496181137) · [Android 整合重測](https://github.com/SunTung/Public-Showcase/actions/runs/42496460708)。
- 簽章 v2/v3 驗證成功、Java 763/763 PASS；真實 Android 手機的視覺與手感仍待驗收。


## 正式單一 Android 版 v1.0.0（2026-11-08）

- **只保留一個正式套件 ID**：`tw.cell.taiwankeyin`，顯示名稱 `CELL 臺灣注音`。不再新增 `.alphaNtest` APK。
- **[下載固定簽章的統一版 Android APK（Google Drive）](https://drive.google.com/file/d/1X7jzBCAQ-ogJEKY1Zxrg3eD25TT_XyKu/view)**。
- [正式統一版交付／資料安全與更新規則](UNIFIED_ANDROID_V1_RELEASE_20261108.md)；完整詞庫、十字記憶、數字列注音、六色主題保留。
- [APK Release 編譯成功](https://github.com/SunTung/Public-Showcase/actions/runs/42493942210) · [Android 35 模擬器整合成功](https://github.com/SunTung/Public-Showcase/actions/runs/42493942177)。
- 以後更新需使用**相同長期私有簽章**及提高 `versionCode`；原 Alpha 版本因不同 ID 不會自動繼承個人 SQLite 記憶。


## Android Alpha5｜數字注音第一排＋六色快選（2026-11-08）

- 已將原本最下面的7個數字列注音移至**第一排**，與5個聲調鍵同排；原本 QWERTY／ASDF／ZXCV 三排保持在下方。
- 標點列旁新增6個可直接點按的顏色框，選色立即更新整個鍵盤並記住偏好；整體高度縮減。
- 完整詞庫 **158,905 筆**、Java **293/293 PASS**、[Alpha5 APK CI SUCCESS](https://github.com/SunTung/Public-Showcase/actions/runs/42492382617)、[Android35 模擬器 CI SUCCESS](https://github.com/SunTung/Public-Showcase/actions/runs/42492333373)。
- [Google Drive Alpha5 APK Artifact ZIP](https://drive.google.com/file/d/1GYYoQbb4kRSHqPOjDpiF43Z2hJ-kLXbu/view)（解壓得 `app-debug.apk`） · [原始碼 ZIP](https://drive.google.com/file/d/1Ybq1o9wbnBL2V-kPcZinnCZqAbbm7Lpp/view) · [正式驗收報告](ANDROID_ALPHA5_RELEASE_20261108.md)。
- 本版本與舊版並存，Samsung 真機畫面與觸感尚待驗收。


## Android Alpha 4｜完整繁體詞庫與常用鍵盤（2026-11-08）

- **158,905 筆詞庫已實際建置、驗證並備份 Google Drive。** [完整 SQLite](https://drive.google.com/file/d/198fo-6dOLGtgQl_mx7A0aF1ALG0gyceq/view) · [完整來源封裝](https://drive.google.com/file/d/1RQN5FA_xYxNjy-lOlQ1XVJMuqwaWKJ8T/view)
- **[下載 Alpha4 已內建完整詞庫的 Android APK](https://drive.google.com/file/d/1C6ITw5BGfuQ5-9utmLdYNtrd_PBMgVls/view)** · [Alpha4 完整原始碼](https://drive.google.com/file/d/18gQoJklSJmJmNtwyDkZIgCHrF280i9nr/view)
- 已實作 QWERTY 對照大千注音位置、英文字母 Shift/大寫鎖定、六頁符號鍵盤；Java **278/278 PASS**。
- [詞庫完整 CI](https://github.com/SunTung/Public-Showcase/actions/runs/42485724924)、[APK 編譯 CI](https://github.com/SunTung/Public-Showcase/actions/runs/42486104911)、[Android 35 模擬器整合 CI](https://github.com/SunTung/Public-Showcase/actions/runs/42486104841) 均 SUCCESS。
- [正式跨雲驗收報告](ANDROID_ALPHA4_FULL_LEXICON_RELEASE_20261108.md)；Android 16 手機操作及輸入手感仍需實機驗收。原 RGOS 私人原件沒有被公開搬移，這是固定來源重建的手機索引。


## Android Alpha 3｜真機故障修復（2026-11-08）

- [已重現並修復 Android SQLite 閃退](ANDROID_ALPHA3_RELEASE_20261108.md)：Alpha2 的 `execSQL("PRAGMA secure_delete=ON")` 導致 Android 35 拋出 SQLiteException；已改正為 `rawQuery`，並修正提交前清空組字等問題。
- **[下載 Alpha3 修正版 APK（Google Drive）](https://drive.google.com/file/d/1u1aYavXDD526mxZ0oPh_Zdp1iAVVgL-K/view)**；[GitHub APK 編譯 SUCCESS](https://github.com/SunTung/Public-Showcase/actions/runs/42480967383)；[Android 35 SQLite／EditText 整合 SUCCESS](https://github.com/SunTung/Public-Showcase/actions/runs/42480967204)。
- 介面已移除上方說明，聲調/符號列縮小，無聲調可直接空白選字。Alpha3 為獨立安裝測試版，不覆蓋 Alpha1/2 的記憶；**使用者真機試打仍需驗收**。


## Android Alpha 2 修正版（2026-11-08）

- **已完成真實 APK CI 編譯：** [Run #42478920166](https://github.com/SunTung/Public-Showcase/actions/runs/42478920166)，Android SDK 35、Java 197/197 測試、Gradle APK 打包與 Artifact 上傳全部 PASS。
- **[下載 Alpha 2 並存測試 APK](https://drive.google.com/file/d/13mwQsDO6UWQUWl85XFJu1CWTPyInI5xx/view)**；[原始碼 ZIP](https://drive.google.com/file/d/1arIuiMVYUpGv68U4swBM5ksmDcCRD9_V/view)。這版將過大的注音鍵改為 10 欄等寬，且 **不按聲調也能空白選字、連續音節自動推進**。
- Alpha 2 Debug 獨立套件 ID：`tw.cell.taiwankeyin.alpha2test`，可與 Alpha 1 並存而不覆蓋舊版學習資料；[完整發行驗收](ANDROID_ALPHA2_RELEASE_20261108.md)。
- **限制：** APK 已通過 CI 編譯與雲端讀回，尚未在使用者手機實機驗證；小型示範詞庫仍待擴充。


## Android 手機版（2026-11-08）

- [AndroidMobile 原生 Android IME 工程](AndroidMobile/)：Java 版大千注音鍵盤、候選列、十字經驗記憶、SQLite、本機詞庫匯入。
- Android 平台核心 116/116 Java 測試通過；Android Manifest/XML 結構已檢查；公開程式檔案逐檔讀回 19/19 一致。
- [Android Debug APK 已編譯成功](https://github.com/SunTung/Public-Showcase/actions/runs/42475919495)：可從 [Google Drive 下載 APK](https://drive.google.com/file/d/1ScIZjfTvC52iBRveVWTmy9jcmOEIRa_Y/view)，或 [查看 APK 驗收報告](AndroidMobile/docs/APK_CI_ACCEPTANCE_20261108.md)；**手機實機安裝與試打尚未驗收**。
- [手機版工程報告](AndroidMobile/docs/ENGINEERING_REPORT_20261108.md) · [Windows / Android 版本關係](AndroidMobile/docs/SOURCE_LINEAGE.md)。
- 手機版是對既有 R1、R2 的 **Java 功能移植**，沒有修改原有的 Windows C++ 核心，也不把測試用小詞庫稱作完整詞庫。

---

## 最新可驗證進度（2026-11-08）

| 階段 | 實際狀態 | 原始碼／證據 |
| --- | --- | --- |
| R0 規劃 | DONE | [PLAN.md](PLAN.md) |
| R1 C++17 十字細胞記憶 | Linux 37/37 PASS | [R1_CppCore](R1_CppCore/) |
| R2-A 大千注音組字與候選 | Linux 167/167 PASS；ASan/UBSan PASS | [R2_Zhuyin](R2_Zhuyin/) |
| R2-B 可擴展注音詞庫轉換器 | 合成詞庫導入、9項驗證、四組 CTest PASS；ASan/UBSan PASS | [R2_B_Dictionary](R2_B_Dictionary/) |
| R2-B 全量公開詞庫 | 轉換接口就緒；真實完整詞庫尚未在本地環境導入驗證 | [自動化 CI](../../.github/workflows/cl_taiwankeyin_r2b.yml) |
| R3 Windows 測試 EXE | 未編譯／未實機測試 | 待執行 |
| R4 系統 TSF DLL | 未實作／未安裝 | 待執行 |
| R5 發行版 | 未完成 | 待執行 |

目前實作：完整37根大千注音鍵位與五種聲調、逐鍵組字、退格、選字、候選排序、已確認詞彙才學習、10有效字的上下文、括號與冒號跨段關聯、一般標點斷句、SQLite WAL 本機經驗詞庫。

**注意：目前是可在 Linux 執行的 CLI＋C++ 工程，尚未提供 Windows 的 `cl_Taiwankeyin.exe` 或 TSF DLL。** 完整大型繁體詞庫也尚待全量匯入及驗收；附帶的小型測試詞庫不能視為成品。

公開區域僅保存可公開原始碼與合成測試資料；不會公開使用者輸入歷史、個人 SQLite 或未公開的 CELL 核心。Google Drive 專案工作區保存獨立完整來源 ZIP 與驗收報告。
