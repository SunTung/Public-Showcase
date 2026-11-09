# CELL 中英繁簡細胞字典 v0.5｜2026-11-09

接續 v0.4 已驗證基線（525 概念）增量建立，**不移除、不更改先前 525 個概念 ID**，新增第 5 批 60 個 CELL 自編常見動詞與形容詞草稿；共 585 個概念、1,755 筆繁／簡／英表述。

## 本輪完成

- `src/build_v05.py`：從 v0.4 重新建置，保留原有概念，增量加入第 5 批詞條；新條目維持 `draft_review`，未確認讀音不填寫。
- `glyph_evidence_audit`：逐條比對 20 條繁簡字形候選與所指概念的繁體詞例；修復舊版 `发→發` 所連結的概念 ID（原指「發展」，示例卻是「發送」）。這是**詞例內部一致性驗證**，不是人工批准轉換規則。
- `cell_candidate_view`：提供 Android／Windows／CELL 代理人共用的查詢介面。`lookup(...,allow_drafts=False)` 預設**只查已批准詞條**，目前沒有任何人工批准紀錄，因此不以 CELL 草稿取代舊輸入法詞庫。
- `dual_lookup`：模擬**舊詞庫優先 + CELL 附加候選**；可選擇是否顯示草稿，但不修改舊 SQLite，且按顯示詞形去重。
- 1090 筆待審核隊列（語義、讀音、字形）；原有 180 筆待覆核注音與拼音記錄保留，另外 495 個概念目前沒有讀音。

## 建置與驗證

```sh
python src/build_v05.py
python -m unittest discover -s tests -q
python src/query_v04.py --export build/cell_concepts.json
```

**狀態：BUILD_PASS / REVIEW_PENDING / DUAL_LOOKUP_READY**。這並非完整通用字典，也不等於已在 Android／Windows 真實輸入服務接上新的字典。現行 158,905 筆獨立輸入法詞庫仍保持使用中。

## 已知限制與下一關

- 詞條、地域用法、讀音和義項仍要逐條查核；`glyph_evidence_audit` 只核對本地字形例詞與概念關係，不是外部詞典的獨立驗證。
- 預設「未審核草稿不入正式候選」；將來要建立每筆詞條的證據鏈與雙人校對，才能 `approved`。
- Android、Windows 的正式雙詞庫接入需要獨立 CI、實機／系統整合與回退測試。
- 不使用外部詞庫批次複製為 CELL 自編詞條。
