# CELL 中英繁簡細胞字典 v1.1｜官方來源離線匯入與全缺口追蹤

沿用 v1.0 已驗證的 585 概念、1,755 表述、180 原始讀音記錄，原始 ID 不變，未修改 Android/Windows 正式輸入法詞庫。

## 新增工程

- `src/moe_import_v11.py`：直接讀取官方 XLSX 或含 XLSX 的 ZIP，也可讀 CSV/TSV；依來源原有詞目和讀音欄位做逐詞比對，保留多音分歧，產出包含全部 585 個概念的 JSON 報告。
- 來源 SHA-256 校驗、版本和來源 URI 欄位、Unicode 表頭欄位對應、XLSX 共享字串及空白儲存格處理；所有操作只讀 CELL 資料庫。
- 13 項新增測試，連同既有 135 項測試共 148/148 PASS。

## 官方來源

教育部國語辭典公眾授權網：https://language.moe.gov.tw/001/Upload/Files/site_content/M0001/respub/dict_concised_download.html

來源版本：`dict_concised_2014_20260929`。下載網址已查明，但本輪環境無法實際取得官方 ZIP，故 **未完成真實詞條核對**。工具接受獨立下載的官方原始檔，來源 SHA-256 應由取得者核對。不得把測試 TSV 當作官方詞條或把完全一致當作人工批准。

## 執行

```bash
python -m unittest discover -s tests -q
python src/moe_import_v11.py build/cell_concepts.sqlite3 /path/to/dict_concised_2014_20260929.zip build/moe_comparison.json --source-uri https://language.moe.gov.tw/001/Upload/Files/site_content/M0001/respub/dict_concised_download.html --source-version dict_concised_2014_20260929
```

## 尚未完成（真實阻塞與驗收）

1. 取得官方原始 XLSX/ZIP，確認實際欄位與多工作表格式，並以真實資料完成 585 概念比對；目前未取得，正式外部查證為 0。
2. 人工詞義與讀音審核、異音／異義與繁簡地區用語判斷、不同審閱者及來源快照驗證；正式核准為 0。
3. 495 概念缺完整拼音／注音組；不以猜測補足。
4. Android IME 與 Windows TSF 真實原生整合及實機回退；目前只有 Python 雙庫唯讀相容層。
5. 既有舊版測試仍出現 Python 3.13 SQLite ResourceWarning，雖然不影響 148/148 PASS，仍須追查舊連線的關閉行為。

已驗證的舊版不覆寫；本版為後續可驗收基線，不表示全部缺口已消除。
