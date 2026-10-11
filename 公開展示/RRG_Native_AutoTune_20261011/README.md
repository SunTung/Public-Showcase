# RRG Native C++ / Auto-Tuning Research — 2026-10-11

本展示整理 SmolLM 135M BF16 的 RRG tensorwise palette 壓縮、30 層 C++ 原生 KV Cache 推論，以及 v20–v27 區塊融合與自動搜尋結果。

- [完整階段技術報告](REPORT.md)
- 實驗結果以可追溯 JSON 與原始碼為基礎；原始與壓縮模型權重因授權與檔案體積另行管理。
- **工程界線**：尚非完整 O8 RRG、尚無原生 tokenizer、尚未完成 100 Token 長測試。
- **核心觀察**：v10 封包節省 23.12%；v22 RRG 相較 raw C++ streaming 未在速度與 RSS 勝出；v25 區塊融合顯著減少 I/O 呼叫；v27 自動搜尋選出統一 128 列候選。
