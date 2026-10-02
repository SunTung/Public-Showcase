# 第九篇論文：從漩渦普遍結構轉入 Navier–Stokes 奇異性目標

**副題：內外場非局部回饋、角向幾何耗減與可證偽研究方法**

Date: 2026-09-13 (+08:00)

RL_ONLY_PRODUCT_PATH = REFERENCE_ONLY_RESEARCH_NOT_PRODUCT
RG_STRUCTURE_BOUND = RESEARCH_ONLY
AUTHORITATIVE_LOWERER_LANGUAGE = Rl
EXTERNAL_SEMANTIC_EMITTER = NONE
ASSEMBLY_PRODUCT_SOURCE = NONE
C_CPP_PRODUCT_SOURCE = NONE
PYTHON_PRODUCT_SEMANTICS = NONE
LINUX_PRODUCT_DEPENDENCY = NONE

## 摘要

本論文記錄研究主線由「漩渦普遍性結構」轉入 Clay 三維不可壓縮 Navier–Stokes 光滑性／奇異性問題的關鍵方法階段。前序約 115 個計算步驟已處理 Fourier triad、polarization、signed/complex MERGE、True Null、Inner/Outer transfer、critical scaling、有限 seed 高頻 genealogy、曲率與差動旋轉等結構。本篇不再擴張一般漩渦理論，而將既有工具重新對準奇異性核心：局部渦量能否在有限時間內，透過 vorticity-aligned strain 持續放大並在縮小尺度上壓過黏性擴散。

方法上將 strain 依核心與巢狀外場殼層分解，追蹤每一層對 ξ^T S ξ 的正／負貢獻；再由 Biot-Savart 型非局部 kernel 抽出角向幾何因子。重要工作結論是：外場不能預設為阻尼，距離本身亦不自動提供有利冪次衰減；但 vorticity direction 的幾何排列可使 stretching contribution 精確為零或被 sin(theta) 因子耗減。因此下一階段的核心不再是「是否存在高頻路徑」，而是「危險 alignment 是否能在 L→0 時持續自我維持」。

## 1. 固定題目

三維不可壓縮 Navier–Stokes：

`∂_t u + (u·∇)u = -∇p + νΔu,  ∇·u = 0,  ν>0.`

基本能量帳本：

`(1/2)d||u||_2^2/dt + ν||∇u||_2^2 = 0.`

因此危險機制不是單純總動能無限，而是導數尺度的集中。

## 2. 奇異性核心量

`ω=∇×u`

`∂_tω+(u·∇)ω=(ω·∇)u+νΔω.`

令 `S=(∇u+∇u^T)/2`，則

`(1/2)d||ω||_2^2/dt = ∫ω·Sω dx - ν||∇ω||_2^2.`

在 `ω≠0` 處令 `ξ=ω/|ω|`，定義

`σ=ξ^T S ξ`, 且 `ω·Sω=|ω|^2 σ`。

STEP115 之後的核心審查量固定為 `L, W≈|ω|, σ, ν/L^2`。

## 3. 前 115 步重新定位

Fourier genealogy 已證明非線性可產生高頻後代，但高頻不等於有限時間奇異；polarization/MERGE/Null 已分類 interaction 的存活與取消，但仍需投影到 σ 的符號與強度；Inner/Outer transfer 已建立交換帳本，但需改成 stretching source ledger；critical scaling 顯示沒有自動 K^{-ε}；曲率與差動旋轉可產生 shear，但 shear 不自動等於 vorticity-aligned stretching。

## 4. STEP116：Core / Outer stretching source ledger

對候選點 x 與尺度 L，將 strain 寫成

`S(x)=S_C(x)+Σ_j S_j(x)`

因此

`σ(x)=σ_C(x)+Σ_j σ_j(x)`, `σ_j=ξ(x)^T S_j(x) ξ(x)`。

`σ_j>0` 表示該外殼餵大核心 stretching；`σ_j<0` 表示負回饋；`σ_j=0` 對此 observer 為 Null。Outer 因而是 signed feedback，不是先驗 damping。

三維 strain kernel 具有 critical 型 `|K(r)|~|r|^{-3}`。殼層體積元素 `r^2 dr` 使粗估只留下 logarithmic level，不自動產生 `2^{-εj}`。單靠距離不能取得所需 regularity gain。

## 5. STEP117：角向幾何耗減

令 `r=x-y`, `rhat=r/|r|`, `ξ=ω(x)/|ω(x)|`, `η=ω(y)/|ω(y)|`。投影到核心 stretching 後，工作角向因子可寫成

`A(ξ,η,rhat)=(ξ·rhat)[ξ·(η×rhat)]`。

因此

`|dσ| ≲ C |ω(y)| |x-y|^{-3} |A| dy`。

若 `η=ξ`，則 `A=0`。這是對 `ξ^T S ξ` 的幾何 True Null，而不是宣稱外場速度或全部 strain 消失。

令 `θ=angle(ξ,η)`，可得

`|A| ≤ (1/2)|sin θ|`。

對第 j 個 outer shell 定義

`Θ_j = sup_{y∈A_j}|sin angle(ξ(x),ξ(y))|`

則工作估計為

`|σ_j| ≲ C Ω_j Θ_j`。

因此 STEP116 中距離沒有提供的 depletion，可能由 vorticity-direction coherence 提供。但目前尚未證明 NS 動力學會強迫 `Θ_j→0`。

## 6. 淨增長 observer 與限制

研究用尺度 observer：

`G(x,L,t)=σ_C+Σ_jσ_j-ν/L^2`。

`G>0` 只代表尺度化瞬時危險候選，不等價於 singularity。精確 pointwise vorticity magnitude evolution 仍是

`D|ω|/Dt = σ|ω| + ν ξ·Δω`。

因此 `ν/L^2` 只能作尺度比較，未建立 localization inequality 前不能替代精確黏性項。R Header 可保存 G，但 Reference body 必須保留各 source、方向、符號、phase 與 genealogy。

## 7. 方法階段轉換

研究已由「一般漩渦如何存在」轉為「奇異候選能否跨尺度維持危險 alignment」。候選 feedback loop 是

`L↓ → σ維持正且足夠大 → |ω|↑ → 更強集中 → L↓`。

regularity 路線必須找此閉環必然斷裂的強制機制；blow-up mechanism 路線則必須建立能在有限時間維持此閉環的自洽狀態。

## 8. STEP118 唯一問題

vorticity direction 的 stretching 部分具有

`Dξ/Dt = (I-ξ⊗ξ)Sξ + viscous direction contribution`。

同一個 `Sξ` 的平行分量 `ξ^T S ξ` 控制強度增長，垂直分量 `(I-ξ⊗ξ)Sξ` 控制方向轉動。

下一步只問：NS 能否讓 `Sξ` 長時間近乎平行於 `ξ`，持續放大 `|ω|`，同時不付出足夠的方向旋轉／幾何耗減成本？若有強制 trade-off，可能形成 regularity obstruction；若無，則 angular depletion 仍不足以解題。

## 結論與研究邊界

本篇不宣稱已解決 Navier–Stokes Millennium Problem。成果是把前序 R/RRG 的 Reference、MERGE、Null、polarization、critical scaling 工具集中到 `ξ^T S ξ` 的來源與幾何條件，建立 Core/Outer signed source ledger 與 angular depletion factor，並將下一個未解核心壓縮成 alignment feedback dynamics。

`G`、Core/Outer shell R-record 與相關命名為研究觀察器／表示方法，不宣稱為標準 NS 不變量或既有定理。任何 regularity 或 blow-up 結論仍需嚴格 PDE 估計、完整時間演化與適用函數空間證明。