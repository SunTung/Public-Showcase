# CELL 中英繁簡概念字典 v0.7 — 讀音一致性審查與證據來源索引

從 v0.6 的 585 概念／1,755 三語表述增量建置；原始詞條及全部概念 ID 不變。新增 90 筆原始種子讀音的「聲調及音節數」一致性核對，與繁簡歧義的證據待核清單。**本輪未自動核准詞條、未複製外部字典、未修改 Android／Windows 正式詞庫。**

## 工程重點

- `phonetic_quality_audit`：檢查原始 90 個概念中的拼音與注音聲調序列、音節數、基本格式。這是形式檢查，**並非**字音、字義、語境的外部獨立驗證。
- `verification_sources`：登記 Unicode Unihan UAX #38 與臺灣教育部國語辭典作為候選外部參考來源，並明記 *reference_registered*，不假裝已取得證據快照。
- `lexical_verification_targets`：90 個讀音核對任務及依字形關係建立的額外詞形查核任務，全部為 *awaiting_comparison*。
- `cell_release_v07`：新版正式候選檢視表，需先符合 v0.6 的雙人核准，再符合形式聲調檢查及其他待核對狀態；預設零筆。
- 原有 v0.6 雙審核流程與 75 項測試回歸保留。原有草稿不入正式候選。

## 使用

```bash
python src/build_v07.py
python -m unittest discover -s tests -v
python src/phonetic_v07.py --state tone_mismatch
python src/phonetic_v07.py --targets --limit 20
```

外部參考來源僅作證據索引，不混入 CELL 自編詞條或擅自變更其審核狀態。當前正式候選數為 0，不會覆蓋舊手機輸入法。
