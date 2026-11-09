# CELL 中英繁簡共用概念字典 v0.4｜2026-11-09

**沿用 v0.3 已驗證 423 個概念及其 concept_id；沒有重新匯入或改名外部詞庫。**

## 本版實際功能

- 新增第 4 批 102 個 CELL 編寫的中英繁簡三語概念，累計 **525 個概念、1,575 筆表述**。
- 新增 `form_graph`：人工列舉的「发→發/髮」「后→後/后」「干→乾/幹」「里→裡/里」「面→麵/面」雙向候選，20 條關係，附上下文例詞及 concept ID。**全部標示 `context_required_draft`，不可當作無條件自動轉換規則**。
- 新增 `lexical_review_queue`：依義項、缺少讀音、歧義字形分配待人工確認任務。包含 970 筆任務，尚無任何人工審核通過。
- 保留最初 90 個概念的 180 筆待覆核讀音；後面 435 個概念不憑空填充注音或拼音。
- 完成 47 個標準函式庫 / SQLite 單元與整合測試；包括原 v0.2、v0.3 回歸，以及 v0.4 新測試。真實漢語義項校對依然未完成。
- **不取代 Android / Windows 已使用的 158,905 筆穩定候選字庫。**

## 無外部依賴的離線建置

```bash
python src/build_v04.py
python -m unittest discover -s tests -q
python src/query_v04.py --locale zh-Hans-CN --form 发
python src/query_v04.py --locale en --word 'speech synthesis'
python src/query_v04.py --review pronunciation
```

## 資料結構

- `concept`、`expression`、`pronunciation`：原概念、三語詞形與讀音。
- `form_graph`：雙向字形候選與詞例；保留一對多，絕不自動選錯義項。
- `lexical_review_queue`：讀音與語義審核任務；獨立列出所有待確認工作。
- `quality_issue`、`review_event`：保留 v0.3 的品質疑點和審核事件接口。
- `manifest.json`：資料庫 hash、增量種子 hash、數量及審核狀態。

## 尚待工程

提高常用詞覆蓋、繁簡歧義詞級測試、建立符合 evidence_ref 的人工審核機制，再做 Android / Windows 可回退雙庫試驗。現在是 **BUILD_PASS / REVIEW_PENDING**，不是已完成的通用大型字典。
