# CELL 中英繁簡概念字典 v0.6｜證據審核及雙人核准閘門

沿用 v0.5 已驗證的 **585 概念、1,755 筆三語表述、180 筆待覆核讀音、1,090 條審核任務**；保留全部概念 ID。**本版沒有聲稱任何詞條已經完成真實外部證據審核**。

新功能：`lexical_evidence` 保留每筆詞義／發音／字形／地區用語的來源 URI、SHA-256、審閱者與決定；`lexical_approval` 必須兩個不同審閱者對同一概念提供詞義與讀音支持紀錄，才能進入 `cell_release_candidates` 唯讀檢視表。預設零筆批准，正式輸入法不讀取草稿。

建置與測試：
```
python src/build_v06.py
python -m unittest discover -s tests -v
python src/review_v06.py --queue --limit 10
```

注意：API 對 URI、摘要、審閱者做的是**結構驗證**，不是查明證據是否真實。自動測試的 example.org 僅為模擬；真實資料審核另需人工或受信任證據核對流程。所有正式資料仍待審核。Android／Windows 現有輸入法詞庫保持不變，雙庫整合尚待系統驗收。
