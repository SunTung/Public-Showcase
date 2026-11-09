# CELL 中英繁簡細胞字典 v0.9｜快照完整性稽核與雙庫回退強化

基於 v0.8 直接增量；原 585 概念／1,755 三語表述與全部舊測試保留。

## 新增
- `src/snapshot_audit_v09.py`：唯讀掃描每筆來源快照，驗證 `SHA-256(UTF-8 captured_text)` 與登記 digest 一致、HTTPS 來源、非測試方法、確認狀態。
- `src/dualstore_v09.py`：原詞庫優先；快照稽核失敗、CELL DB 缺失或損壞時回退，不改寫正式輸入法資料庫。
- `tests/test_v09.py`：包含摘要錯誤、測試方法、HTTP、資料庫遺失及唯讀測試。

## 注意
內容摘要相符只證明快照內部一致，**不能證明文字確實取自所標示的外部來源**。來源真實性、逐詞語義／音韻核查及雙人審核仍待完成。此版是 Python 整合層，不是已上線的 Android APK 或 Windows TSF。

## 執行
```bash
python src/build_v08.py
python src/snapshot_audit_v09.py build/cell_concepts.sqlite3
python -m unittest discover -s tests -q
```
