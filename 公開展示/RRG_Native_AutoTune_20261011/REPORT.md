# RRG 原生模型結構化、壓縮、直接執行與自動最佳化：2026-10-11 完整階段報告

**範圍**：SmolLM 135M BF16；v10–v27。**定位**：可驗證的研究原型，並非完整 O8 RRG 或成熟通用推論引擎。

## 1. 原始模型及資料表示
原始 Safetensors 269,060,552 bytes，權重 269,030,016 bytes；272 tensors、30 layers、hidden 576、Q heads 9、KV heads 3、head dim 64、MLP intermediate 1536、vocab 49152、RoPE theta 100000。輸入 tokenizer JSON 與權重分離。

## 2. 結構轉換
解析 Safetensors header、建立 tensor 名稱／shape／dtype／offset 索引，逐 tensor 掃描 BF16 唯一值，產生 BF16 palette 字典及 bitpacked index。字典方案不適用者保留 dense BF16。寫入 packet、manifest、C++ 靜態 tensor index。v10 共 269 palette + 3 dense tensors；封包 **206,828,355 bytes**，對原始權重節省 **23.12%**。目前是 tensorwise lossless BF16 palette 格式，**不是** O8 Main/Branch/Gamma/Residual 全套。

## 3. 直接執行架構
C++ 使用 TENSORS[] 索引及 pread 按需讀取 packet，直接由索引查字典值並乘加，不建立完整 Float32 權重矩陣。30 層執行 embedding、RMSNorm、Q/K/V、RoPE、GQA causal attention、O projection、SwiGLU MLP、final norm 與 LM head。KV Cache 以每層 K/V float32 陣列維持，每 token 增加 46,080 bytes。推論本體不使用 Python/PyTorch；Python 僅作獨立驗證與外部 Auto-Tuner。

## 4. 實測演進
| 版本 | 工程結果 | 主要數據及限制 |
|---|---|---|
| v10 | 完整模型 tensorwise palette 封裝 | 206,828,355 bytes；23.12% |
| v15–v19 | 混合 forward、100 詞生成及記憶體基準 | PyTorch streaming 對照顯示 RSS 降低多由串流造成；非純 C++ |
| v20 | 純 C++ 單 Token 30 層 forward | 預測 token 260；與 PyTorch logits 最大絕對差約 0.000223 |
| v21 | 純 C++ Q/K/RoPE/GQA + KV Cache | 3 tokens [260,2914,553] 與 PyTorch 一致；約 1.147 秒；RSS 約 2.20 MiB |
| v22 | 同一 C++ 核心 raw BF16 / RRG 公平對照 | raw 0.608 秒、2188 KiB；RRG 1.105 秒、2248 KiB；RRG I/O 約少 23.15% |
| v23 | 字典快取 | 12 tokens 一致，未加速 |
| v24 | 共享唯讀字典、分項計時 | 12 tokens：無快取 5.181 秒／快取 5.236 秒；解碼 2.695 秒、I/O 0.989 秒、MAC 1.224 秒 |
| v25 | 區塊融合解碼+乘加 | 1/4/16/64 列時間中位數 1.120/0.813/0.768/0.741 秒；I/O 呼叫 615012→10590 |
| v26 | 自動掃描全模型 block_rows | 128 列約 0.711 秒；32 列約 0.714 秒，差異小 |
| v27 | 三級 Tensor 大小自適應策略搜尋 | 六策略比較；統一 128 列約 0.718 秒、2568 KiB，為該輪最快 |

## 5. v27 自動搜尋規則
以 tensor 元素數分類：小型 <200000、中型 200000–999999、大型 ≥1000000。候選包括 uniform 32、uniform 128、adaptive 8/32/128、16/32/128、32/64/128、16/64/256。每候選獨立執行兩次，檢查生成 [260,2914,553] 一致，再比較時間與外部 /usr/bin/time Peak RSS。這是**三類規則搜尋**，尚非 272 個 Tensor 各自獨立調優。最佳候選未必是最複雜方案。

## 6. 記憶體與效能解讀
v22 在公平 C++ streaming 條件下，RRG 雖節省封包及 I/O 量，仍比 raw BF16 慢且 Peak RSS 略高。v24 顯示瓶頸主要是 bitpacked index 解碼及大量小 pread。v25 區塊融合有效減少 I/O 呼叫。Peak RSS 不包含完整 OS page cache；早期 Python 父程序測量曾與外部程序測量不一致，不能混用。短 Token 一致不能代替全 logits bit-exact 或長文本品質驗證。

## 7. 後續壓縮與自動執行規劃
來源/授權檢查→掃描 tensor→產生 palette/dense/未來其他結構候選→驗證 BF16 無損或明確容差→封包及 manifest→C++ Runtime 編譯→短序列正確性測試→粗到細自動搜尋 block rows/緩衝區/解碼核心/SIMD/快取→記錄 latency、RSS、PSS、I/O、KV cache→Pareto 排名→長序列驗證→硬體專屬配置及 SHA256 封存。失敗配置不得覆寫穩定版本。

## 8. 未完成事項
原生 tokenizer／文字輸出、100-token 長序列、逐 tensor 調優、SIMD 搜尋、Windows 本機執行、PSS／冷啟動、跨硬體重現、O8 完整結構、RL 語言整合，皆尚未完成。

## 9. 發布與資料界線
公開展示可放報告、C++/Python 原始碼、測試 JSON、manifest、靜態索引及 checksum。原始權重（269,060,552 bytes）與 v10 RRG 權重（206,828,355 bytes）暫不公開，應先查核模型及衍生權重授權；需要時透過合法模型來源重新建置。完整本地技術封包另行封存，不應將本公開文字報告誤認為包含權重的完整推論套件。

**階段結論**：原生 C++ 直接運算壓縮權重、KV Cache、區塊融合及自動搜尋已實測；但 RRG 尚未在同核心 raw BF16 streaming 對照中取得全面速度或 RAM 優勢。
