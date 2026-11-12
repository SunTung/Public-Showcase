# OPS-F01 / OPS-KFRG — Public corpus staging

This directory is the public-facing staging area for the CELL English corpus collection project.

## Storage layout

- `sources/` — source manifests and public source references (planned)
- `indexes/` — provenance, language classification, SHA-256 and deduplication indexes (planned)
- `reports/` — per-run collection and verification reports (planned)
- `corpus/` — **only** individual texts verified as appropriate for public redistribution; not a mirror of the private corpus
- `quarantine/` — **metadata only**, never publish unverified downloaded bytes

## Current handoff

The existing collection implementation and candidate ledger remain in the private `SunTung/test/experiments/ops-f01/` repository until public-safe migration is completed. The previously reported 60,544,169 candidate UTF-8 bytes in 91 files are **not** a globally verified or public-published total. Do not count them again or assume they have been copied here.

## Acceptance rules

Only verified English main-body UTF-8 bytes count toward the 200,000,000-byte milestone; non-English and mixed-language materials remain indexed separately and do not count. Verify downloaded content, actual bytes, primary language, exact/near duplicates and provenance before publishing. Keep private credentials, restricted data and unverified redistribution rights out of this public repository. The long-term 5 GB goal is separate from the 200 MB milestone.

## Automation

Public GitHub-hosted standard runners can avoid private-repository compute charges. A harvesting workflow is **not yet enabled** here; migrate and validate the scripts and persistence path before scheduling. GitHub repository history is not suitable as an unlimited raw 5 GB archive; use controlled corpus storage for bulk bytes.
