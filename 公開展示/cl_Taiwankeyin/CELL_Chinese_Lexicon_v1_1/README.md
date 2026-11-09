# CELL 中英繁簡細胞字典 v1.1｜全量來源比對入口與缺口清冊

**工程基線**：v1.0（585 個概念、1,755 筆中英繁簡表述、135/135 CI PASS）。

**本輪實作**：`src/batch_intake_v11.py` 提供 TSV/XLSX 批次讀取、來源欄位映射、唯一來源 ID/NFC 驗證、原始檔 SHA-256、SQLite 唯讀查詢、585 個概念完整逐詞比對、五種差異分類，以及原子化 JSON 報告寫入。新增 14 個測試，149/149 本地 PASS。

**使用方式**：

```bash
python -m unittest discover -s tests -q
python src/batch_intake_v11.py build/cell_concepts.sqlite3 /path/to/official_download.xlsx build/official_comparison.json --name 'MOE Concised Dictionary' --version '2014_20260929' --source-url 'https://language.moe.gov.tw/001/Upload/Files/site_content/M0001/respub/dict_concised_download.html' --column-map '{"headword":"詞目","zhuyin":"注音","source_entry_id":"編號"}'
```

**注意**：上述 XLSX 欄名僅為操作範例，需以實際下載檔的表頭調整，不能假定官方資料的表頭格式。若官方資料沒有穩定 ID，必須先另行制定並驗證穩定識別方案。`build/EXAMPLE_ONLY_*` 是**測試資料**，不是官方辭典，不得作為正式詞條證據。

**尚未完成**：本次執行環境的網路 DNS 無法下載教育部官方 ZIP；故官方實際核對 0、人工批准 0。尚未取得 Android IME 或 Windows TSF 原生專案執行環境，無實機驗收。所有未完成事項見 `build/GAP_LEDGER_v11.json`。原始正式輸入法 158,905 筆詞庫未被更改。
