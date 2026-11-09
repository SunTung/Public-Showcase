# CELL 中英繁簡細胞字典 v1.0｜外部來源逐詞比對工具

保留 v0.9 的 585 個概念、1,755 筆表述與全部既有測試。

新增 `src/external_alignment_v10.py`：讀取外部獨立取得的 TSV 字典資料，依繁體詞目及注音／拼音逐詞比對，輸出 JSON 結果，檢查來源檔 SHA-256、來源名稱與版本、重複來源 ID 與 NFC。輸入欄位為 `headword`, `zhuyin`, `pinyin`, `source_entry_id`。

狀態：`EXACT_TEXT_MATCH`、`PRONUNCIATION_DIFFERENCE`、`MISSING_CELL_PRONUNCIATION`、`AMBIGUOUS_SOURCE`、`NOT_FOUND`。

執行：
```
python src/build_v08.py
python src/external_alignment_v10.py build/cell_concepts.sqlite3 /path/to/source.tsv build/alignment.json --source-name SOURCE --source-version VERSION
python -m unittest discover -s tests -q
```

總計 135/135 測試通過。此工具不會自動批准詞條；比對一致不證明外部來源真實性。正式核准數 0，Android/Windows IME 未更動，外部官方資料仍待實際匯入。
