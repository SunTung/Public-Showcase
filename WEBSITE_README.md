# Sun Tung × CELL Research Lab — Website V1.1

This is the public-only studio website. The canonical internal research projects remain separate.

## Public data boundary

- Publish only studio-approved broad research goals, monthly completion figures, product descriptions, and explicit public product links.
- Never fetch private GitHub repositories or Google Drive databases at browser runtime or build time.
- Do not publish private architecture, source code, training data, internal test logs, credentials, storage locations, or unpublished research.
- Do not treat monthly progress percentages as project-wide completion or technical maturity.
- Product downloads are enabled only after a separate explicit public release has been approved.

## Update guide

1. Edit `history/YYYY-MM.json` using the strict public fields `name`, `progress`, `status`; do not add internal details.
2. Update `history/index.json` with the valid month.
3. Set `progress.json` to the same content as the latest public month.
4. Edit `products.json` only for explicitly approved public items; avoid linking private or unverified download files.
5. Run `python scripts/validate_site.py` locally, or let Actions validate on push.

## Deployment

Branch: `website-v1-20261111`.
Workflow: `.github/workflows/studio-site.yml`.

For Actions deployment, select **GitHub Actions** as the Pages build-and-deployment source in repository Settings → Pages. The workflow validates the public data and extracted JavaScript before attempting deployment. If repository Pages is not enabled, deployment remains blocked until GitHub settings are configured.

This branch is intentionally isolated from `main` until reviewed.
