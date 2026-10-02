# T67 — Weighted shell telescoping reduces back to O_FINAL

**Date:** 2026-09-16

**Status:** `[CONFIRMED REDUCTION]`. No new independent OPEN is created.

## 1. Purpose

After T66 removes naive branching entropy as an independent obstruction, the next task is to restore the critical H^{1/2}-type scale weight and determine what survives exact shell recombination.

## 2. Weighted summation-by-parts identity

Let

T_j = Π_{j-1} - Π_j

be the signed nonlinear transfer into shell j, and let w_j be an increasing shell weight. Then

Σ_{j=J}^M w_j T_j
= Σ_{j=J}^M w_j(Π_{j-1}-Π_j)
= w_J Π_{J-1} - w_M Π_M + Σ_{j=J}^{M-1}(w_{j+1}-w_j)Π_j.

Thus unweighted telescoping survives only when w_j is constant. For critical weights, the interior term

Σ_{j=J}^{M-1}(w_{j+1}-w_j)Π_j

remains.

For a dyadic critical H^{1/2}-type ledger, w_j is proportional to K_j (equivalently the shell energy is weighted by one power of frequency). Then w_{j+1}-w_j is of the same scale as K_j, so there is no automatic small factor from summation by parts.

## 3. Relation to earlier C10 / STEP155-172 line

This is exactly the previously identified distinction:

- unweighted signed shell transfer: exact telescoping, CLOSED;
- weighted critical transfer: interior weighted signed flux survives;
- the surviving object is not a new genealogy obstruction but the already-existing critical signed-work obligation.

Therefore the T52-T66 line does not create an additional mother OPEN. It returns to the same O_FINAL identified before T46-T49.

## 4. Closure classification

The following are now aligned:

- shell-by-shell positive payment: ELIMINATED;
- Duhamel tree-count / branching entropy as independent payment: ELIMINATED / MERGED;
- cutoff geometry / collar / excess viscosity: structural reductions only;
- unweighted flux accumulation: CLOSED by exact telescoping;
- critical weighted interior flux: REDUCED TO O_FINAL.

## 5. Remaining mother obligation

The surviving mother obligation remains a terminal critical signed-work estimate of the form

∫_I N_{1/2}(t) dt <= (1-δ) ν ∫_I Y(t) dt + F_low(I),

with δ>0 and no extra assumptions, or an equivalent cumulative form strong enough for continuation.

Equivalently, after shell decomposition, one must control the terminal-uniform interior weighted signed flux produced by summation by parts.

## 6. Consequence

T52-T67 are not a new proof branch. They have backtracked and rederived, in the T-system, the same final obstruction that the C/STEP closure audit had already named O_FINAL. This is a successful closure alignment: apparent new gaps have been merged back to one mother gate instead of being double-counted.
