# R6 有界關卡登記與核對規則（2026-11-13）

本階段沿用既有 R5 公開工作表，不重建網站與主登記簿。

## 資料權責
- 私人 `SunTung/library/research_tracking/20261112/MASTER_REGISTRY_V2_20261112.json`：研究/工程主清冊，承載內部來源與驗證證據。
- 私人 `NEXT_GATE_WBS_20261112.json`：每個工程的下一個關卡與依賴；不代表完整子任務數。
- 公開 `workboard.json`：公開工作狀態摘要與已核定的單一有界關卡。
- 公開 `workboard-gates.json`：與 `workboard.json.items[].gate_metric` 雙向一致的具體驗收集合。
- 公開 `workboard-events.json`：已核准的變更事件（增量保留，不能抹除舊紀錄）。
- 公開 `workboard-sync-status.json`：最近一次核對日期、來源快照日期及自動同步是否真的啟用。

## R6 已建立的有效有界驗收
- `CELL-CORE-S1-EXITS`：S1 原生出口 0/21。S0 12/12 來源稽核不計入此分母。
- `CELL-M-PHASE1`：固定第一階段 21/28，當中 7 項阻塞。它不是整體 CELL-M 的 75%。

其餘工程的整體完成率維持 `null`，直到完成明確工作分解、固定分母、逐項成果證據與驗收口徑。已有 38 項工程不表示只有 38 件子工作。

## 更新程序
1. 先在私人工作區核對新增功能證據。未變更的已驗證項目只檢查存在性，不重跑。
2. 如有新的有界關卡，定義固定範圍、`gate_id`、工程 `project_id`、已驗收數、總數、阻塞數、核對日期與公開限制文字。
3. 同步修改 `workboard-gates.json` 與 `workboard.json` 的同一個工程關卡摘要；公開端禁止自動抓取私人庫。
4. 更新 `workboard-events.json`，保留原有事件，不修改歷史驗收紀錄。
5. 執行 `python scripts/validate_site.py`；CI 同時檢查網頁 JavaScript 與有界關卡一致性，通過後才發布 Pages。
6. 遇到證據不足或 runner 未啟動，保留原狀及阻塞記錄，其他工程照常推進。

## 已知限制
目前這是一份手動審核的公開出版流程。沒有正式啟用私人到公開的自動同步或全部 38 項工程的完整功能驗收比例。
