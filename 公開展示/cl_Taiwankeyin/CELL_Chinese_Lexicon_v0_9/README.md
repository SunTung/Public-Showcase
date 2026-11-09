# CELL 中英繁簡細胞字典 v0.9｜第一輪實際教育部詞目觀測核對

在 v0.8 既有 585 個概念、1,755 筆表述、109 項回歸測試基礎上增量。保留所有概念 ID、SQLite 與原有程式。

## 新實作

- `data/observed_moe_samples_v09.tsv`：5 項教育部公開詞目頁面觀測結果：謝謝、再見、早安、晚安、今天。記錄明確的頁面 URL、注音、拼音、短篇自行編寫的語義摘要（非複製來源釋義）。
- `src/source_observation_v09.py`：把觀測結果與 CELL 已存原始注音、拼音和詞形核對；`謝謝` 的輕聲點在顯示位置不同，正規化後比對，不改原始詞庫。
- `build/observed_moe_audit_v09.json`：可重現的逐詞核對結果、來源指向與狀態。
- 保留 `evidence_snapshot` 零條、`cell_release_v08` 零條：網站觀測不等於可驗證的原始頁面完整快照，也不等於兩位真人審核批准。

## 驗證

```bash
python src/build_v08.py
python src/source_observation_v09.py
python -m unittest discover -s tests -q
```

**現況：** 來源網頁經查閱，5 筆原始拼音／注音和詞目比對一致；但未完成整本詞典，且英文義項僅為 CELL 自行撰寫概念，尚未經外部英語詞典交叉核驗。不得把本版視為已接入 Android 或 Windows 正式輸入法。
