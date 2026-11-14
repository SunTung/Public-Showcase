# Sun Tung × CELL — Public Website Maintenance

This repository is the **public-only** presentation surface. Private GitHub repository identities, source files, technical acceptance logs, research notes, paper inventories, internal task dependencies, and private cloud references must **never** be committed or deployed here.

## Publication policy

- Default deny. Only approved generic categories, product information and broad public project labels are eligible for publication.
- Public repository metadata may be included only after checking repository visibility via GitHub; private repositories must not appear by name or per-repository statistics.
- Private-source full progress is kept in a restricted owner-controlled research index. Publication requires a separate explicit sanitized export and successful CI privacy gates.
- Avoid publishing exact source paths, branch names, commit hashes, internal implementation details, credentials, personal data, unreviewed test receipts or hidden workflow dependencies.
- Preserve earlier validated baselines and perform path/SHA delta checks privately. Public status categories are not project completion percentages.
- Changing the current public branch does not remove older public Git history, forks, external caches or downloaded copies. Historical exposure requires a separate authorized remediation process.

## Public entrypoints

- `index.html`: public introduction
- `research-index.html`: categories and public repositories only
- `workboard.html`: approved project overview only

## Verification

GitHub Actions `.github/workflows/studio-site.yml` runs the public data and script validation before GitHub Pages deployment.

## R12 public child-work ledger (2026-11-14)

The approved public main project catalog now has a companion, `public-subprojects.json`, representing 38 existing main-project IDs and 157 curated first-level child work entries. Each item contains **only** an ID, public-safe topic title, simple status and bounded-completion reminder. The private GitHub research ledger holds the authoritative evidence mapping and reconciliation receipts; none of that source data is included in this public artifact.

The status breakdown at this first-level snapshot is 31 bounded-phase `已完成`, 120 `進行中`, 6 `待確認`. A completed bounded phase does **not** mean its parent engineering project is complete. The current 157 entries do not claim to cover every experiment, paper version, historic research topic or unreviewed directory.

The `research-index.html#subprojects` view shows the title-only child directory by parent, searchable by title and status. The `workboard.html#subwork` view summarizes counts per parent and links to child details. CI compares child parent IDs to the preapproved 38-entry `workboard.json` and `public-catalog.json`, enforces a strict field allowlist, checks status arithmetic and rejects unexpected private-source fields.

The independently retained private reviewer receipt records **38/38 parents and 157/157 titles/statuses with 0 mismatches**. This is a catalog/source reconciliation, not a test rerun or whole-project acceptance.
