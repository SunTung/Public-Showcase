# CELL 中英繁簡共用概念字典 v0.3｜2026-11-09

**本次是原 v0.2 的增量，不是新造另一個系統。** 既有 90 + 206 = 296 個概念保持原本 ID、原始詞條、讀音及審核狀態；第三批加入 127 個 CELL 自行編寫的三語對照草稿，共 **423 概念、1,269 表述**。

## 定位與資料品質

以 `concept_id` 為語義主鍵，表述分 zh-Hant-TW、zh-Hans-CN、en；讀音分注音、拼音，和語義分離。目前 **90 個種子有 180 筆尚待覆核的音標**；其餘 **333 個概念的讀音留空**，不猜測。所有 423 概念都還沒有完成人工交叉審核；不可把 `BUILD_PASS` 說成 `LEXICAL_REVIEW_PASS`。

第三批分為日常生活、時間、交通、醫學、科學、文學、溝通等領域。資料為工程自行編寫的短詞對照；**沒有批次複製 Chewing、OpenCC 或外部詞典**。工程文件保留來源比對資訊，不聲稱通用字詞是 CELL 發明的。

新增 `form_candidate` 以記錄繁簡一對多字形關係，而不是強制逐字轉換，例如 `发→發/髮`、`后→後/后`；`quality_issue` 將簡體同形、多義及需要檢查的項目列為 review，不偷偷合併。

## 建置

本版本兼容 Python 3.11+，僅需標準函式庫、SQLite，無需網路存取。

```bash
python src/build_v03.py
python -m unittest discover -s tests -v
python src/query.py --locale en --word "passport"
python src/query.py --locale zh-Hans-CN --word "血压"
python src/query.py --ambiguous "发"
python src/query.py --export build/export.json
```

v0.2 原始建置邏輯及原始兩批 TSV 被完整保留，v0.3 由 `src/build_v03.py` 實際調用 v0.2 建置基線後追加第三批。`build/cell_concepts.sqlite3` 是給其他 CELL 工程讀取的可用資料庫；`build/cell_concepts.json` 是可移植的 API 資料，`build/manifest.json` 記錄資料 SHA-256 和審核狀態。對舊 Android/Windows 輸入法的 158,905 筆完整候選庫不做替換。

## 下一批工程門檻

1. 建立繁體／簡體字形層專用的單字多對多索引（加上語境線索，避免假一對一）。
2. 擴充基礎字詞與多義詞概念，明確區別詞形相似、義項不同、地方用語差異。
3. 建立讀音審查隊列；每筆注音／拼音加上覆核依據和流程記錄。
4. 再逐批擴大，達到夠高的覆蓋率後才讓輸入法以可回滾方式雙庫試驗。

**目前尚不是完整字典，也還沒有正式通過逐條詞義／讀音人工審核。**
