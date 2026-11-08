# CELL 臺灣注音｜Android v1.0.2／Windows v0.2.1／雙雲清理驗收
日期：2026-11-09（Asia/Taipei）

## 1. Android v1.0.2：已上字後的智慧接續詞

固定套件 ID **tw.cell.taiwankeyin**，versionCode **102**，正式憑證 SHA-256 **347b51f0c52352e5b2a0047201c37a8c8e9913c0df805c1ab7a54c08881135b6**（沿用 v1.0.0／v1.0.1）。既有個人經驗 SQLite 不更名、不刪除。

修正：過去 `memory.nextSuggestions()` 只從已學的 phrase_stat 尋找接續，首次輸入沒有候選。v1.0.2 增加完整 158,905 詞庫的 `idx_mobile_word_prefix`，依最近 1～4 字片語、詞頻及個人學習資料合併、去重、排序；當注音組字已提交且編輯框仍在時，頂部顯示可直接點選並 `commitText` 的接續字詞，敏感欄位禁止讀取歷史上下文。保留彈性按鍵、隨機配色、37 鍵注音、英文 Shift/Caps、六頁符號。
- GitHub commit `51de27b0a5f11ecccbdb87f7fd774ca6acd4e60a`，純 Java **769/769** PASS。
- [Android APK Build #42498189189](https://github.com/SunTung/Public-Showcase/actions/runs/42498189189)：SUCCESS，含完整 158905 詞庫生成、新字首索引及 Release 輸出。
- [Android 35 Integration #42498189515](https://github.com/SunTung/Public-Showcase/actions/runs/42498189515)：SUCCESS，真實 Android SQLite 與 EditText InputConnection；Debug Probe 新增「你→好」「今天→是」詞庫接續查詢斷言及基本上屏/學習/清除驗證。
- 同一私有金鑰簽署 v1.0.2，APK v2/v3 Signature **PASS**。APK 10,441,636 bytes SHA256 **2e42926001bb8f737b83599657a1169d947081211b8f350c98b5ff13d45e0f57**，Google Drive 回讀完全一致。
- 完整字詞索引 36,028,416 bytes, 158905 rows, SQLite integrity=ok, `idx_mobile_word_prefix` exists，SHA256 **bce7818d479e2733685e2589ee4215a819bc7b48113a99d86d2ab0c01220e085**，Drive 回讀一致。
- [Google Drive v1.0.2 signed APK](https://drive.google.com/file/d/16B-hg97Sn1w5qT-AikFyzwzhg9AM79Em/view)
- [Google Drive v1.0.2 full source](https://drive.google.com/file/d/1uzejUh09-iCT-ejZCZEQNWaZMXbHFCOl/view)
- [Google Drive v1.0.2 full lexicon package](https://drive.google.com/file/d/1eWxLuDzpKASfR2k1uAPJZ8VApfHbrmmd/view)

## 2. Windows 舊版更新

在原 R1_CppCore、R2_Zhuyin、R2_B_Dictionary **不破壞已驗證 C++ 原件**的前提下，建立 `WindowsDesktop_v02/`：Python/Tkinter standalone Windows GUI（不是 Windows TSF 系統輸入法）。可開啟圖形鍵盤與文字欄，37 大千鍵、免聲調 `sucl` → 你好，15.9萬離線詞庫、候選選字、從詞庫推薦接續詞、四種顏色與複製全文。
- [Windows Build #42499718323](https://github.com/SunTung/Public-Showcase/actions/runs/42498556921)：Windows 2022 CI **SUCCESS**，完整詞庫驗證，6 項 Engine Tests PASS（包括聲調過濾），PyInstaller 生成 PE 格式 .exe，ZIP 解壓 CRC PASS。
- ZIP 22,841,086 bytes SHA256 **b60e9ea2726c71b47d5a0768b24285f0195d6133b11b02dfd2d4438d2b01a760**，Google Drive 回讀一致。
- [Windows v0.2.1 Desktop Preview ZIP](https://drive.google.com/file/d/1k0-gKoKlxI-j2VIl4_Xb9TYaqVfWcHci/view)
- [Windows v0.2.1 source ZIP](https://drive.google.com/file/d/1_wiZON_s3NxS0QfJoYhymhk5IFmrZh2m/view)
- **尚未完成 TSF 系統輸入法 DLL、安裝器與 Windows 真實 UI 人工試打。** 此 .exe 是可獨立啟動的圖形輸入與文字編輯預覽，不要稱為系統鍵盤。

## 3. Google Drive 備份清理

在新的 Android v1.0.2 APK/原始碼、Windows v0.2.1 EXE/原始碼及字詞庫**全部獨立回讀並通過 SHA-256**後，才刪除備份區的 44 個過時/重複項目，包括 Alpha1～Alpha5 的 APK、舊來源、CI 暫存 ZIP、Git 中繼 JSON、重複 Doc，以及 v1.0.1 多份重複來源與舊 27MB 詞庫。Google Drive 每項回傳刪除成功，清理後重新列出手機資料夾確認剩餘 9 個有效項目：

1. Android v1.0.2 正式簽章 APK與完整原始碼。
2. Android v1.0.1 上一可回退簽章 APK與驗證後原始碼。
3. Android v1.0.0 首份長期簽章基線 APK。
4. v1.0.2 完整 SQLite 詞庫、manifest與封裝。
5. 僅限內部的 `PRIVATE_SIGNING_KEY_DO_NOT_SHARE` 簽章金鑰資料夾（嚴禁公開）。

Google Drive Root Windows 範圍另保留原 R1/R2/RGOS 研究原始碼與相關驗證報告，確保不可替代的已驗證基線不會被版本清理誤刪。GitHub 仍保留歷史提交作版本溯源。

## 4. 下一版本 Gate：注繁／拼簡

將目前下方配色選擇列的一個色塊改為 `注繁 / 拼簡` 切換控制，但**不是直接調用文字簡繁變換就宣稱完成**。真正拼簡須：
- 按鈕切換注音繁體模式與拼音簡體模式；鍵盤版面從大千注音變為拼音 QWERTY。
- 解析 Hanyu Pinyin 音節、可選聲調與省略聲調的分詞規則；對應簡體字詞源與正規化，採固定資料版號。
- 模式切換時處理未完成的組字，禁止丟失/重複上字；各模式候選排序與 Context10 學習記錄須有模式辨識。
- 完整測試：`nihao`→`你好`，`zhongguo`→`中国`，注音 `ㄓㄨㄥ ㄍㄨㄛˊ`→`中國`，空白選字、連續輸入、回退、切換及隱私欄位。
- 這項**尚未編譯實作，仍為下一版的公開驗收規格**。

## 未驗收範圍

Android 16 Samsung 實機上的候選展示與觸控、長時間輸入及不同 App 的可用性仍需實機確認；Android 35 CI PASS 只代表模擬器自動驗收。Windows 系統全域 TSF IME 仍待另建；勿將 PyInstaller EXE 當成 TSF DLL。
