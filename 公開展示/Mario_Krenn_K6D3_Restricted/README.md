# Mario Krenn — K6,D=3 Restricted Result

## 研究範圍

本展示研究的是：

- simple graph `K6`；
- 每一對 unordered vertex pair 只有一條 primitive edge；
- 每條 primitive edge 使用一組固定 ordered endpoint-colour pair；
- `D = 3`；
- 複數 edge weights；
- 三個 monochromatic inherited vertex colourings 的 amplitude 為 `1`；
- 所有 mixed inherited vertex colourings 的 amplitude 為 `0`。

這是 restricted calibration model，不是 unrestricted Krenn–Gu conjecture 的完整解答。

## 結果

結構路線為：

```text
three monochromatic witnesses
    -> pairwise edge-disjoint witnesses
    -> nine-edge backbone
    -> triangular prism or K3,3
    -> 13 + 10 = 23 support orbits
    -> mixed singleton fiber
    -> nonzero mixed amplitude contradiction
```

兩條不同的 exact verifier 都通過：

```text
23/23 support-orbit representatives: PASS
semantic endpoint-colour assignments checked: 1,217,855
maximum minimum UNSAT core size: 3
```

## Mario Krenn 建議的對應狀態

- unrestricted `(6,3)` Lean proof：已引用。
- 我們的 restricted mathematical mechanism：已整理並以兩支 verifier 重現。
- 我們自己的 restricted Lean formalization：尚未完成。
- DeepMind formal-conjectures augmentation：handoff 已準備；upstream issue/PR 尚未提交。
- 對方公開 certificate 的本機獨立 rerun：曾啟動，但該次背景程序在完成 release gate 前中斷；不把它宣稱為 PASS。

## 內容

- `MANUSCRIPT/` — 公開展示用稿件片段。
- `SUPPLEMENT/` — 兩支 verifier、輸出與重現方式。
- `FORMALIZATION/` — DeepMind formal-conjectures handoff 與目前狀態。
- `NOVELTY_AND_SCOPE_STATEMENT.md` — 與 unrestricted result 的範圍區分。

## 重現

進入 [`SUPPLEMENT/REPRODUCE.md`](./SUPPLEMENT/REPRODUCE.md)，可在不需要第三方 Python 套件的 Python 3.11+ 環境執行兩支 verifier。

## 公開副本說明

這是對外展示副本；作者聯絡、ORCID、私人信件與投稿行政資料已移除。數學範圍、結果、驗證程式與目前未完成項目保持明確記錄。
