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
