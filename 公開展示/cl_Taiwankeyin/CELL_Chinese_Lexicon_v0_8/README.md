# CELL 中英繁簡細胞字典 v0.8｜來源快照閘門與雙庫回退

本版是在 **v0.7（585 concepts / 1,755 expressions）** 的完整已驗證工程上增量建立，保留原始種子、概念 ID、審核佇列、音節形式檢查與全部舊版測試，不重新匯入第三方字典。

## 本輪已實作

- `src/build_v08.py`：新增 `evidence_snapshot`、`release_gate_issue`、`cell_release_v08`。與 v0.6 的 `lexical_evidence` 不同，`evidence_snapshot` 是需要實際捕獲且可檢驗來源內容的額外資料；只記錄 URL、兩位審閱者或 SHA 字串 **並不證明來源已核對**。
- `cell_release_v08`：查詢當下檢查兩份證據是否同屬該概念、涵蓋 meaning 和 pronunciation、為支持意見、兩位不同審閱者、來源快照摘要相符、音節形式一致、且不存在尚未支持的驗證任務。任何條件失敗不發布。
- `src/dualstore_v08.py`：**只讀模式**讀 CELL 核准候選；保留舊候選優先；CELL 檔案遺失、損壞或停用時自動返回舊候選，**不改寫 Android/Windows 正式 SQLite**。
- `src/review_export_v08.py`：輸出 100 條獨立來源查證任務為 Excel 可讀 TSV；所有任務仍標為 awaiting_comparison。
- 增加 15 項 v0.8 測試，總計 **109/109 PASS**。其中包含「虛構 URL 的雙人批准不能通過 v0.8 正式閘門」及來源摘要不符拒絕。

## 實際數據

| 指標 | 數量 |
|---|---:|
| 語義概念 | 585 |
| 三語表述 | 1,755 |
| 原有讀音（需外部核查） | 180 |
| 尚缺完整讀音組的概念 | 495 |
| 外部查核任務 | 100 |
| 真正外部已確認來源快照 | **0** |
| 正式可發布 CELL 概念 | **0** |
| 自動化測試 | **109/109 PASS** |

## 重新建置與驗收

```bash
python src/build_v08.py
python src/review_export_v08.py
python -m unittest discover -s tests -q
```

工程限制：目前並未取得外部字典逐條的真實來源快照，也沒有人工批准；不能把工程邏輯通過測試解讀成詞義或發音查證已完成。原本 158,905 筆正式輸入法候選庫保持不變。雙庫查詢僅是 Python 相容層，**尚未聲稱已實際整合至 Android IME 或 Windows TSF**。

後續 Gate：實際抓取並核驗少量 MOE 辭典詞條，持久化證據快照與來源版本；再執行人工審核與衝突偵測，最後做 Android/Windows 真實系統整合與回滾演練。
