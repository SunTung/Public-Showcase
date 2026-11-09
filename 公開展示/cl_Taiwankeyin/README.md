# cl_Taiwankeyin｜繁體細胞注音輸入法（Windows + Android）

## CELL 中英繁簡細胞字典 v0.9｜最新有效版本（2026-11-09）

- [v0.9 原始碼與觀測對照](CELL_Chinese_Lexicon_v0_9/README.md)：保留 585 個概念／1,755 筆表述，首次逐筆比對教育部五個真實詞目（謝謝、再見、早安、晚安、今天）；5/5 詞目、注音與拼音觀測結果一致。
- [Google Drive 完整 ZIP](https://drive.google.com/file/d/1_4HyFyWs_MpHZXFJGQiLDh-RaOml4Qa0/view)；回讀 SHA-256 6adc5ed24eb1e74d7d67a538f900c7dfcecdf32a19f4acd05b40805ee351f6ec 一致，36 個 ZIP 成員 CRC PASS。
- [GitHub v0.9 CI SUCCESS](https://github.com/SunTung/Public-Showcase/actions/runs/42543287220)：116/116 測試。
- 限制：五筆資料是有來源 URL 的網頁觀測對照，而不是完整頁面快照或雙人詞義批准；仍 0 筆發布許可。Android／Windows 仍使用原穩定正式詞庫。


## CELL 中英繁簡細胞字典 v0.8｜最新有效版本（2026-11-09）

- [v0.8 最新原始碼](CELL_Chinese_Lexicon_v0_8/README.md)：保留 v0.7 全部 585 概念／1,755 表述；新增更嚴格的發布查詢閘門、唯讀雙庫回退與 100 條待核任務 TSV 匯出。
- [Google Drive v0.8 完整 ZIP](https://drive.google.com/file/d/11iu1uIXoS8CQ8GtzyB0dSf6UT_EXXSLd/view)；本地與雲端 SHA-256 490587a9eaf68b138a4491eaa3f60d0248666957449a8acb9782cbccd4ce3b3c 相同，31 個 ZIP 成員通過 CRC。
- [v0.8 GitHub CI SUCCESS](https://github.com/SunTung/Public-Showcase/actions/runs/42542419387)：109/109 測試；**0 筆真實來源快照、0 筆正式可發布 CELL 概念**，未修改 Android／Windows 正式詞庫。
- 查證界線：證據連結、聲調形式及程式測試不等於真實人工詞義與讀音查證。


## CELL 中英繁簡細胞字典 v0.7｜最新有效版本（2026-11-09）

- [v0.7 完整 GitHub 工程](CELL_Chinese_Lexicon_v0_7/README.md)；保留全部 585 語義概念、1,755 中英繁簡表述，原始內容及概念 ID 不改。
- [Google Drive v0.7 完整 ZIP](https://drive.google.com/file/d/1HNhhUADBy-NB4BkNX1mM4fZ765Zex6Fi/view)；回讀 SHA-256 `2fd7d46b52883c3a6b439cfdcac6512f00f385281a4bbc96a2832cc66feb8857` 相同，26 個封裝檔案 CRC PASS。
- [CI v0.7 94/94 PASS](https://github.com/SunTung/Public-Showcase/actions/runs/42541756330)，新增 90 組拼音／注音音節數及聲調形式一致性測試與 100 條外部來源待核證任務。
- **語義、讀音的獨立查證及人工批准數仍為 0；不等於完成詞典校勘。** Android／Windows 正式輸入法沒有改動。後續以抽樣人工確認、來源證據快照與真實雙庫整合測試為 Gate。


## CELL 中英繁簡細胞字典 v0.6｜最新有效版本（2026-11-09）

- **[v0.6 完整原始碼](CELL_Chinese_Lexicon_v0_6/README.md)**：保留 v0.5 全部 585 概念、1,755 三語表述與 1,090 待審任務，新增詞義／讀音等證據紀錄、兩名不同審閱者核准與唯讀正式候選檢視表。現在 **0 筆獲批准**，草稿不得進入正式輸入法。
- [Google Drive v0.6 完整 ZIP](https://drive.google.com/file/d/1VFCEFXcIVTRcO22kMWPgp62gSmNBV8lB/view) · [字典工作區](https://drive.google.com/drive/folders/1HXBHw6XymF4Z9GNH8RMyRoT-bWJj0s82)，Drive 回讀 SHA-256 `0d407a69a4971865e5b54d33f9441cf6f35214164de9b1f1ed8193ceb4cea927` 一致。
- [GitHub v0.6 獨立 CI 成功](https://github.com/SunTung/Public-Showcase/actions/runs/42540834479)：75/75 項回歸測試。
- **聲明：** 程式可以驗證審閱流程及證據格式，但無法憑空證明外部來源內容真實；正式 Android/Windows 詞庫尚未變更。


## CELL 中英繁簡細胞字典 v0.5｜最新有效基線（2026-11-09）

- [GitHub v0.5 原始碼與測試](CELL_Chinese_Lexicon_v0_5/README.md)：累計 **585 個概念、1,755 筆繁／簡／英表述**，保存 v0.4 的全部 525 個概念 ID。
- [Google Drive v0.5 完整工程](https://drive.google.com/file/d/1gEkmdYfNpIAw9ClrMQ6-TQE9Klj5NFv5/view)；[工作資料夾](https://drive.google.com/drive/folders/1HXBHw6XymF4Z9GNH8RMyRoT-bWJj0s82)。雲端 ZIP 回讀 SHA-256 `7ff5a13693c08950d311dd35f3254d07f7a033bcd8a4b6538040b7d728153a67` 一致。
- [GitHub 獨立 CI 成功](https://github.com/SunTung/Public-Showcase/actions/runs/42539529706)：62/62 測試，詞例 20/20 內部一致。**1,090 條審核任務未完成，不得冒稱詞義與發音已驗證。**
- 新增雙庫查詢模擬；草稿預設不列為正式候選，現有 158,905 筆輸入法詞庫不受影響。


## CELL 中英繁簡細胞字典 v0.4｜最新有效版本（2026-11-09）

- **[v0.4 完整工程 GitHub](CELL_Chinese_Lexicon_v0_4/README.md)**：沿用 v0.3 的 423 概念，新增 102 概念，累計 525 概念／1,575 三語表述。建立 20 條雙向、語境限定字形候選與 970 條待審核任務。
- [Google Drive v0.4 SQLite／JSON／原始碼 ZIP](https://drive.google.com/file/d/1QKyCLMEb0uK8xI4OnNKG_Cej3E9hCdDv/view) · [專用資料夾](https://drive.google.com/drive/folders/1HXBHw6XymF4Z9GNH8RMyRoT-bWJj0s82)。
- [GitHub v0.4 獨立 CI PASS](https://github.com/SunTung/Public-Showcase/actions/runs/42538551939)，含全部 47 項回歸測試與查詢／JSON 匯出。雲端 ZIP 回讀 SHA-256 一致。
- 所有新概念及字形關係仍待人工校對，不可宣稱已全面支援準確繁簡轉換；既有 158905 筆輸入法詞庫維持原樣。


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
