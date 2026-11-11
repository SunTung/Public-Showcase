# Sun Tung × CELL Research Lab — Website V1.2

This is the public-only studio website. The canonical internal research projects remain separate.

## Logo-sampled background revision (2026-11-11)

- Original 1536×864 logo A examined for its actual color clusters: warm paper `#FAFAF7`, inner navy `#112C53`, medium blue `#20446C`, lilac `#987DAF`, orange `#EA8C53`, golden yellow `#E5CF5B`, and burgundy `#C03E49`.
- Website canvas and navigation use logo-paper off-white. Information cards retain legible dark navy; accents reflect the logo’s hand-drawn rainbow, not a generic neon palette.
- Preserves content, bilingual controls, 37 project entries, 20/37 review counter, original image assets, and private/public boundary.

## Visual palette update (2026-11-11)

- Palette inspired by the user-provided **Space V1 icon A**: navy core plus restrained pastel rainbow accents (lilac, coral, gold, mint, sky).
- The site retains navy information cards and a neutral gray page canvas; mobile layout, bilingual controls and portfolio data remain unchanged.
- This commit changes CSS only; it does not upload or reproduce the icon artwork, alter the monthly percentage values, or expose private research materials.

## Audit tracker update (2026-11-11)

- The public first-pass review counter now shows **20 of 37 reviewed**, next **021 RGOS**. This is NOT project completion or a monthly progress percentage.
- The audit tracker contains only public-safe counts and the already-public project name. No private report link, internal experiment result, source location or research architecture is exposed.
- The monthly progress figures and original 37 portfolio items remain unchanged. The website now displays reviewed/not-yet-reviewed status and a curated one-line milestone for each of the first 20 entries; these summaries do not publish internal evidence, locations, or secrets.

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

## Public review synchronization (2026-11-11, through item 020)

- `index.html` displays **20/37** deep reviews, followed by **021 RGOS**, separately from project development completion or monthly plan percentages.
- Reviewed entries 001–020 display concise, public-safe status summaries; remaining entries display an explicit review-pending note.
- Bilingual rendering, project search/category filtering, existing monthly progress bars, logo imagery and gray background are preserved.
- Approved public copy is manually curated. Internal/private audit ledgers, paths, training data, architecture, model weights and detailed test reports are not embedded or requested from the browser.
- Latest website update uses the existing GitHub Pages CI validation and deployment workflow.

## Evidence-informed estimated readiness ranges (2026-11-11)

- Added `estimates.json` for all 37 public portfolio entries. Each shows a **coarse range** of readiness, a confidence label, and a brief public-safe reason, based on the available engineering/research phase evidence.
- **These are subjective estimates, not experimentally measured percentages, not scientific proof progress, and not release-acceptance percentages.** Research manuscripts, datasets, games, and compilers have different acceptance obligations; ranges cannot be averaged or compared as interchangeable quantities.
- First 20 entries draw on in-depth audits; remaining 17 use high-level source/registry discovery and explicitly have **low confidence**. No new in-depth audit was claimed.
- Original **seven studio-provided monthly-plan percentages** in `portfolio.json` and `progress.json` remain unchanged and separately displayed.
- Page shows a horizontal **uncertainty band** from estimate low to high, not a fabricated exact-point completion or a progress bar with a single authoritative value.
- JSON fields are strictly allowlisted by `scripts/validate_site.py`; GitHub Pages workflow validates and includes `estimates.json` in deployment.
- Review counter is **20/37**; estimating the other 19 does not count as their deep audits.

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
