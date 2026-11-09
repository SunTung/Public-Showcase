# CELL 中英繁簡字典 v0.10｜首批外部讀音實際對照

原 v0.9 585 個概念及 1,755 筆表述與完整程式、測試保留；本版不自動新增或改寫發音。

## 本次真正查核的詞條

- `CELL-C0023 頭髮`：種子 `tou2 fa5 / ㄊㄡˊ ㄈㄚ˙`，教育部《國語辭典簡編本》及《重編國語辭典修訂本》均記 `tóu fǎ / ㄊㄡˊ ㄈㄚˇ`。**兩項獨立辭典頁面觀察與原資料衝突**，標成 CONFLICT，並沒有逕改原值。參閱 `data/moe_first_comparisons_v10.tsv`，網址在檔內。
- `CELL-C0004 早安`：種子與教育部《國語辭典簡編本》 `zǎo ān / ㄗㄠˇ ㄢ` 一致，標成 MATCH。

## 工程性質

`src/comparison_v10.py` 用唯讀方式比對詞語、概念 ID、漢拼與注音；輸出 JSON 供審核。這些記錄是實際網頁查閱到的短摘記（web_result_observation），**不是經過來源原始 HTTP bytes、憑證及內容指紋驗證的快照，也不是第二名審閱者的核准**。沒有改動 v0.8／v0.9 的正式發布閘門，無詞條被自動批准。

執行：
```
python src/build_v08.py
python src/comparison_v10.py
python -m unittest discover -s tests -q
```

下一階段：抓取並驗證原始來源檔案，處理讀音地區差異或輕聲規範，再依逐詞核對進入雙人審閱。
