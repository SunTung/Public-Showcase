# Sun Tung × CELL Research Lab — Website V1.2

This is the public-only studio website. The canonical internal research projects remain separate.

## Logo-sampled background revision (2026-11-11)

- Original 1536×864 logo A examined for its actual color clusters: warm paper `#FAFAF7`, inner navy `#112C53`, medium blue `#20446C`, lilac `#987DAF`, orange `#EA8C53`, golden yellow `#E5CF5B`, and burgundy `#C03E49`.
- Website canvas and navigation use logo-paper off-white. Information cards retain legible dark navy; accents reflect the logo’s hand-drawn rainbow, not a generic neon palette.
- Preserves content, bilingual controls, 37 project entries, 26/37 review counter, original image assets, and private/public boundary.

## Visual palette update (2026-11-11)

- Palette inspired by the user-provided **Space V1 icon A**: navy core plus restrained pastel rainbow accents (lilac, coral, gold, mint, sky).
- The site retains navy information cards and a neutral gray page canvas; mobile layout, bilingual controls and portfolio data remain unchanged.
- This commit changes CSS only; it does not upload or reproduce the icon artwork, alter the monthly percentage values, or expose private research materials.

## Audit tracker update (2026-11-11)

- The public first-pass review counter now shows **26 of 37 reviewed**, next **027 JSP-000244**. This is NOT project completion or a monthly progress percentage.
- The audit tracker contains only public-safe counts and the already-public project name. No private report link, internal experiment result, source location or research architecture is exposed.
- The monthly progress figures and original 37 portfolio items remain unchanged. The website now displays reviewed/not-yet-reviewed status and a curated one-line milestone for each of the first 26 entries; these summaries do not publish internal evidence, locations, or secrets.

## Public data boundary

- Publish only studio-approved broad research goals, monthly completion figures, product descriptions, and explicit public product links.
- Never fetch private GitHub repositories or Google Drive databases at browser runtime or build time.
- Do not publish private architecture, source code, training data, internal test logs, credentials, storage locations, or unpublished research.
- Do not treat monthly progress percentages as project-wide completion or technical maturity.
- Product downloads are enabled only after a separate explicit public release has been approved.

## Approved public portfolio (V1.2)

- `portfolio.json`: 37 **manually curated** public project entries with stable number, name, broad research/engineering goal, category, and month-plan progress.
- No private GitHub/Drive path, model architecture, experiment data, implementation details or underlying evidence are copied into `portfolio.json`.
- The seven supplied progress percentages are **monthly plans**, not overall maturity. Remaining 30 entries show **待評估 / Not assessed** (not zero).
- The private source-of-truth registry remains in the separate private GitHub library. Changes do **not** auto-publish to the public site; public fields must be reviewed before modifying the static file.
- Page supports search and category filtering and both Traditional Chinese / English language switching.

## Update guide

1. Edit `history/YYYY-MM.json` using the strict public fields `name`, `progress`, `status`; do not add internal details.
2. Update `history/index.json` with the valid month.
3. Set `progress.json` to the same content as the latest public month.
4. Edit `products.json` only for explicitly approved public items; avoid linking private or unverified download files.
5. Curate `portfolio.json` without copying internal descriptions or paths; for new entries maintain stable IDs and 3-digit numbers. Do not assign unverified percentages.
6. Run `python scripts/validate_site.py` locally, or let Actions validate on push.

## Deployment

Branch: `website-v1-20261111`.
Workflow: `.github/workflows/studio-site.yml`.

For Actions deployment, select **GitHub Actions** as the Pages build-and-deployment source in repository Settings → Pages. The workflow validates the public data and extracted JavaScript before attempting deployment. If repository Pages is not enabled, deployment remains blocked until GitHub settings are configured.

This branch is intentionally isolated from `main` until reviewed.

## Public review synchronization (2026-11-11, through item 026)

- `index.html` displays **26/37** deep reviews, followed by **027 JSP-000244**, separately from project development completion or monthly plan percentages.
- Reviewed entries 001–026 display concise, public-safe status summaries; remaining entries display an explicit review-pending note.
- Bilingual rendering, project search/category filtering, existing monthly progress bars, logo imagery and gray background are preserved.
- Approved public copy is manually curated. Internal/private audit ledgers, paths, training data, architecture, model weights and detailed test reports are not embedded or requested from the browser.
- Latest website update uses the existing GitHub Pages CI validation and deployment workflow.

## Evidence-informed estimated readiness ranges (2026-11-11)

- Added `estimates.json` for all 37 public portfolio entries. Each shows a **coarse range** of readiness, a confidence label, and a brief public-safe reason, based on the available engineering/research phase evidence.
- **These are subjective estimates, not experimentally measured percentages, not scientific proof progress, and not release-acceptance percentages.** Research manuscripts, datasets, games, and compilers have different acceptance obligations; ranges cannot be averaged or compared as interchangeable quantities.
- First 26 entries draw on in-depth audits; remaining 11 use high-level source/registry discovery and explicitly have **low confidence**. No new in-depth audit was claimed.
- Original **seven studio-provided monthly-plan percentages** in `portfolio.json` and `progress.json` remain unchanged and separately displayed.
- Page shows a horizontal **uncertainty band** from estimate low to high, not a fabricated exact-point completion or a progress bar with a single authoritative value.
- JSON fields are strictly allowlisted by `scripts/validate_site.py`; GitHub Pages workflow validates and includes `estimates.json` in deployment.
- Review counter is **26/37**; estimating the other 19 does not count as their deep audits.

## Featured R&D and portfolio synchronization (2026-11-11)

- Featured seven R&D cards now resolve **project name → public portfolio ID → shared estimate** from the same `portfolio.json` and `estimates.json` used in the 37-item overview.
- Both surfaces show the **same estimated readiness low–high range** and public milestone text. A link on each featured card selects the corresponding project in the portfolio list.
- The historical **monthly-plan** value stays visible as a separate annotation; the featured readiness range never copies or overwrites it.
- `scripts/validate_site.py` now verifies that all featured entries have a matching portfolio ID and public estimate, and that the dashboard actually uses the shared estimate.
- `history/*.json`, `progress.json`, original seven studio-provided monthly figures and audit counter (18/37) remain unchanged.

## 019 SRV-QUANTUM audit update

- In-depth audit found **VSR** named original research and actual Linux x86-64 G8-B CI verification, plus Linux cross-CPU G5 records and separate restricted-state SSQC quantum evidence.
- The public label **SRV** has not been conclusively mapped to VSR; avoid presenting these distinct results as one fully accepted simulator.
- Public stage-readiness range stays **20–50% (estimated)**; its evidence confidence is upgraded to medium, not a measured completion rate. Next deep audit is 020 DECISION-SEARCH.

## 020 Decision Search audit update

- The separate `SunTung/RG-Decision-Search-Lab` holds a historical six-solver 100-layer by 100x100 dynamic maze host-reference benchmark; all six solvers completed 100/100 layers with no invalid paths in archived results. This **does not** establish universal performance or Rl-native search.
- A new non-destructive GitHub Actions current-scope validation on existing sources returned **17/17 PASS**, plus archived aggregate internal consistency PASS. Historical race was **not** rerun. Original legacy regression workflow is still failing and must not be represented as fixed.
- Public review counter is **20/37**, next project **021 RGOS**. Decision search public estimated readiness remains **30–55%** with updated evidence note and medium confidence.

## 021 RGOS / RGSS audit update

- A true scope-specific RlEC Quick Verify failure came from using the **historical frozen README certificate** against the later edited README. Three existing reference/native-hash/P1B test consumers were repaired to retrieve and verify the **certificate-pinned Git blob** without overwriting or relaxing the original certificate. Current run 43017848846 passed. Conditional self-hosted native job was skipped, not a qualified Rl-only production OS boot.
- RGOS host/freestanding Taiwanese Zhuyin validations on 2026-11-08 had PASS results for **158,905** entries and portable target compilation; these are *not* full RGOS physical keyboard/display acceptance.
- 100 STEP and 28 work orders identify planned and scoped work, not 100 completed product gates. STEP005 hardware certification remains open. Estimated readiness remains **25–50% (subjective band)**.
- Public overview is **21/37** deeply reviewed; next is **022 CLAW**.

## 022 CLAW formal model-authority audit

- The formal donor is **R7H step 2600**, SHA-pinned in `CLAW-Agent-System/CURRENT_AUTHORITY.md` and the model registry. CLAW's outdated project entrypoint was corrected from R7G to R7H. R7G remains a historical parent; R7I-B/R7M/R8 are failed-generation experimental branches, not promoted donors.
- New GitHub Actions source-consistency validation [run 43021406294](https://github.com/SunTung/CLAW-Agent-System/actions/runs/43021406294) **SUCCESS**, which checks source authority without any checkpoint binary/model inference. CLAW's Chinese free generation and independent real agent operation are still not qualified; model binaries not proven backed up to GitHub.
- Audit coverage **22/37**, next **023 SPACE-SIM**. CLAW's previous **10–30%** range remains a subjective engineering-readiness estimate; source confidence upgraded from low to medium. The seven original monthly-plan values remain independently shown.

## 023 SPACE-SIM cross-domain audit

- 13/13 model families have **first RRG-1 structural baselines**, not full physics engines. Phase-2 multi-structure is eligible but not yet started.
- Newly added GitHub Actions [run 43035015201](https://github.com/SunTung/Simulation-Field-Animation-Mathematical-Structure-Algorithms/actions/runs/43035015201) **SUCCESS**: retained Python reference 05–13 suite PASS and independently authored nine-family guards/conservation checks PASS. **Not Rl-native or hardware tests.**
- B Space A-to-AB has separately reported, bounded Rl-native evidence; full CFD, coupled world, visuals and physical hardware acceptance are not proven. Formula-world v0.3/v0.5 Drive papers remain **candidate specifications**.
- Audit tracker **23/37**, next **024 NAVIER-STOKES**; public subjective readiness range remains **20–45%**, with upgraded medium-confidence evidence label.

## 024 Navier–Stokes finite-scale closure audit

- **Confirmed closure:** Theorem 10.1 of the Sept 18 Google Drive manuscript states and establishes finite-scale/finite-order **representation closure** on every already-smooth finite classical cylinder `T < T*`, with return to the original Eulerian pair after dyadic reconstruction, mixed derivative recovery, pressure and auxiliary elimination. It is not merely a proposed manuscript.
- The theorem's `C_T` is uniform in dyadic step `h`, via Grönwall coefficients using time integrals of solution gradient norms; the paper does not thereby establish uniform continuation as `T` approaches `T*`. Global arbitrary-data regularity remains a distinct claim, not established by Theorem 10.1.
- New archival claim-status checker GitHub Actions #43036631844 **SUCCESS** validates the status ledger, not a new theorem or independent peer review.
- Deep audit **24/37**, next **025 Perfect Cuboid**. Public subjective manuscript readiness estimate remains 25–50%, not proof completion.

## 025 Perfect Cuboid / Ring Search audit

- The newer Sept 22 anti-recompute ledger supersedes the Aug 28 archive: certified bounded Ring/OBSERVE U=5,000,000; rational-angle q≤700 with 4,288,819,733 pair checks and no Perfect Cuboid; fixed denominator(u)≤50,000 with 268,260,332 rational states. Historical denominator≤100,000 attempt was interrupted and is **not** a complete search.
- Fixed (399,26) family has exact genus-5 covering, elliptic and genus-2 quotients; the elliptic rational torsion `Z/4 × Z/2` has exact small-prime certificate. New GitHub Actions 43039388737 **SUCCESS** for existing PCLIFT 001/002/003C-D-E-F exact small certificates and saved receipt consistency. Large searches were **not rerun**.
- Rank, Mordell–Weil generators, complete successive lifts, whole fixed-family exclusion and global Perfect Cuboid remain **OPEN**. Public subjective readiness estimate 30–55% remains unchanged; source confidence moved from low to medium. Coverage 25/37; next 026 KRENN.

## 026 Krenn restricted K6,D3 double verification

- The frozen 2026-09-21 v1.1 manuscript defines **restricted simple K6**, one primitive edge and one fixed ordered endpoint-colour pair per vertex pair; three monochromatic target amplitudes one and mixed target amplitudes zero. Not the unrestricted multi-edge-type conjecture.
- The direct verifier checks 1,217,855 distinct semantic assignments; 23/23 symmetry-reduced support orbits UNSAT. A different symbolic verifier certifies 23/23 exact equality UNSAT cores of size at most three. New GitHub Actions [43041263800](https://github.com/SunTung/Finished-Products-Showcase/actions/runs/43041263800) reran **both Python programs** successfully and matched their frozen receipts.
- Earlier attempted local Lean re-verification runs 35558519393 and 35558559543 failed. Do **not** conflate them with the Python PASS or upstream stronger Lean artifact. Manuscript submission is prepared; a portal receipt is not verified.
- Public readiness band remains 35–60% as a subjective research-packaging estimate, **not a theorem completion percentage**. Audit coverage 26/37; next 027 JSP-000244.
