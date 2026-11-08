# CELL 臺灣注音 Android Alpha 4｜完整詞庫歸檔與交接

日期：2026-11-08（Asia/Taipei）
工程路徑：SunTung/Public-Showcase/公開展示/cl_Taiwankeyin/AndroidMobile
Google Drive 專案資料夾：https://drive.google.com/drive/folders/1UOZumYikN0ygC-y9JSt6vGVHWnAf_IsJ

## 詞庫來源與版本性質

RGOS 私人倉庫原始驗證參照：`tools/zhuyin_ime/data/zhuyin_lexicon.sqlite3`，SHA-256 `57d3d3f332710d6dcab0bbef997407edeb56ca5e9483652fd42fb7404cc01586`，12,853,248 bytes。原件仍留在私人倉庫，沒有更動權限、也沒有直接移出。

本次依原固定上游 `chewing/libchewing-data` commit `c44e81aef24b06f1509f19e1be54c99812d0c43f`，核對 `word.csv` Git Blob `04308dd3b31ead3a61d9210ec3fd427dabced12a` 和 `tsi.csv` Git Blob `a13b3dd87c1c5205d3250ef296d76d2bb23f1900`，使用 OpenCC 1.4.2 s2twp 重建**Android 專用只讀 SQLite 索引**。這是可重建的內容同源資料，不是位元組相同的 RGOS 私人 SQLite 拷貝。

詞庫獨立統計（從 Google Drive 回讀後再以 SQLite 查詢）：
- 完整字詞／讀音對：158,905
- 多音節詞條：133,505
- 不同帶聲調讀音：121,377
- `PRAGMA integrity_check`：ok
- 例：`ㄋㄧ` -> 你／妳／倪，`ㄏㄠ` -> 好／號／耗，`ㄓㄨㄥ ㄨㄣ` -> 中文。

## Google Drive 交付檔（皆在現有 AndroidMobile 資料夾）

| 檔案 | 位元組 | SHA-256 | Google Drive |
| --- | ---: | --- | --- |
| full_zhuyin_mobile.sqlite3 | 27,340,800 | `04b98ccbfa609625e7d6ecbf6cbc3cd517a66a4b111bede1504c62c7fc755a11` | https://drive.google.com/file/d/198fo-6dOLGtgQl_mx7A0aF1ALG0gyceq/view |
| cl_Taiwankeyin_158905_full_mobile_lexicon_20261108.zip | 7,745,313 | `967468e9fd0e9c6aed19edf5a5511a2965dea21c1272769a5ea4bd3aab770578` | https://drive.google.com/file/d/1RQN5FA_xYxNjy-lOlQ1XVJMuqwaWKJ8T/view |
| cl_Taiwankeyin_Android_Alpha4_fulllexicon_20261108.apk | 8,949,707 | `f6d77bbc774e53511b0421d8a27e98cf7d9272bb2496c99e08942d363e8841cf` | https://drive.google.com/file/d/1C6ITw5BGfuQ5-9utmLdYNtrd_PBMgVls/view |
| cl_Taiwankeyin_Android_alpha4_fulllexicon_source_20261108.zip | 54,115 | `fc29b33ce1dc717da67a7061ec0d69efdf31f9ccc2f7b487c7d6a68e985cbfa4` | https://drive.google.com/file/d/18gQoJklSJmJmNtwyDkZIgCHrF280i9nr/view |

此外另有單獨的 `full_lexicon_manifest_158905.json`：https://drive.google.com/file/d/1EwtOvD4ej7nCg12NQRqhVod85r7ABKlC/view

## 實際 CI

- 完整詞庫重新建立與核對：https://github.com/SunTung/Public-Showcase/actions/runs/42485724924 → SUCCESS。
- 真正包含完整詞庫資產的 Alpha4 APK：https://github.com/SunTung/Public-Showcase/actions/runs/42486104911 → SUCCESS。
- Android 35 模擬器原生 EditText/SQLite/完整詞庫檢查：https://github.com/SunTung/Public-Showcase/actions/runs/42486104841 → SUCCESS。
- Alpha4 Java 核心與鍵盤邏輯測試：278/278 PASS（已在本地及 CI 執行）。
- Android APK 壓縮包中檢出 `assets/full_zhuyin_mobile.sqlite3`，內部 SHA-256 等於上列 Google Drive 完整詞庫的 SHA。
- Drive 備份的 APK、來源 ZIP、完整 SQLite、完整詞庫 ZIP 均已回讀 SHA-256 一致。

## 功能與剩餘驗收

Alpha4 Android 原始碼增加：大千按鍵對應熟悉的 QWERTY 實體位置、英文 Shift／Caps Lock／小寫模式、6 頁符號鍵盤以及整套詞庫的唯讀候選查詢。完整詞庫只作為候選來源，個人十字經驗仍儲存在獨立的 Android 私有 SQLite，不會寫回基礎詞庫。

Debug 安裝 ID：`tw.cell.taiwankeyin.alpha4test`，可與 Alpha1/2/3 並存，各版學習資料分離。上述 CI 與 Android 35 模擬器驗收不代表已在使用者 Android 16 手機實機確認選字手感、完整符號頁面或長時間連續輸入。下一關是使用者手機試打回報後進行 UI 與相容性驗收。
