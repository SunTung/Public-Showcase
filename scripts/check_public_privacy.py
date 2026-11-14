#!/usr/bin/env python3
"""Fail-closed prepublication privacy inspection of the public site.

This deliberately scans text shipped from the public repository, not private
research data. It never imports, fetches or prints confidential source files.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_REPOS = frozenset({"Public-Showcase", "CELL-DEFENDER"})
REPO_REF = re.compile(r"(?i)(?:\bSunTung/|github\.com/SunTung/|raw\.githubusercontent\.com/SunTung/)([A-Za-z0-9_.-]+)")
PROHIBITED = (
    re.compile(r"(?i)(?:research_tracking/[0-9]{8}|private_projects/|private_imports/|file_trees/|/home/[A-Za-z0-9_.-]+/)"),
    re.compile(r"(?i)https?://(?:drive\.google\.com|docs\.google\.com|raw\.githubusercontent\.com/SunTung/(?!Public-Showcase/|CELL-DEFENDER/))"),
    re.compile(r"(?i)\b(?:gh[pousr]_[A-Za-z0-9]{12,}|sk-proj-[A-Za-z0-9_-]{12,})\b"),
)
DISALLOWED_KEYS = {"private_path", "private_directory", "source_path", "private_repo_path",
                   "private_source_url", "repository_token", "credential", "access_token",
                   "secret", "private_file_list", "private_manifest"}

SITE_FILES = (
    "index.html", "research-index.html", "workboard.html", "public-catalog.json", "public-subprojects.json",
    "workboard.json", "workboard-latest.json", "workboard-p0-tasks.json",
    "workboard-events.json", "workboard-gates.json", "workboard-repositories.json",
    "workboard-research-topics.json", "workboard-repository-activity.json",
    "workboard-portfolio.json", "workboard-sync-status.json",
    "portfolio.json", "products.json", "progress.json", "estimates.json",
    "README.md", "TRANSFER_NOTICE.md", "WEBSITE_README.md",
    "docs/R6_GATE_LEDGER_POLICY_20261113.md",
)

def scan_text(text, file_label):
    problems = []
    for regex in PROHIBITED:
        if regex.search(text):
            problems.append(f"{file_label}: prohibited publication pattern")
    for match in REPO_REF.finditer(text):
        repo = match.group(1)
        if repo not in PUBLIC_REPOS:
            problems.append(f"{file_label}: reference to non-allowlisted GitHub repository")
    return problems

def scan_object(obj, file_label):
    errors = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key.lower() in DISALLOWED_KEYS:
                errors.append(f"{file_label}: forbidden JSON key")
            errors.extend(scan_object(value, file_label))
    elif isinstance(obj, list):
        for value in obj:
            errors.extend(scan_object(value, file_label))
    return errors

def validate(root=ROOT):
    errors = []
    paths = [root / p for p in SITE_FILES]
    paths.extend(sorted((root / "history").glob("*.json")))
    for path in paths:
        if not path.is_file():
            errors.append(f"Missing public file: {path.name}")
            continue
        text = path.read_text(encoding="utf-8")
        errors.extend(scan_text(text, path.name))
        if path.suffix == ".json":
            try:
                errors.extend(scan_object(json.loads(text), path.name))
            except ValueError:
                errors.append(f"{path.name}: invalid JSON")
    inventory = json.loads((root / "workboard-repositories.json").read_text(encoding="utf-8"))
    actual = {r["repository"] for r in inventory["repository_statuses"]}
    if not actual.issubset(PUBLIC_REPOS):
        errors.append("Public inventory includes a non-allowlisted repository")
    if inventory.get("privacy_policy") != "PUBLIC_REPOSITORIES_ONLY":
        errors.append("Public inventory privacy policy not set")
    taxonomy = json.loads((root / "workboard-research-topics.json").read_text(encoding="utf-8"))
    if taxonomy.get("privacy_policy") != "PUBLIC_ONLY_NO_PRIVATE_DERIVED_METRICS":
        errors.append("Public taxonomy privacy policy not set")
    if any(t.get("related_registered_project_ids") for t in taxonomy["records"]):
        errors.append("Private research/project crosswalk must not be published")
    # Fail closed: public catalog may only repeat previously approved public labels.
    board = json.loads((root / "workboard.json").read_text(encoding="utf-8"))
    catalog = json.loads((root / "public-catalog.json").read_text(encoding="utf-8"))
    allowed = {(r["id"], r["name"], r["category"]) for r in board["items"]}
    actual_catalog = [(x["id"], x["title"], group["id"], x["status"])
                      for group in catalog["groups"] for x in group["items"]]
    if len(actual_catalog) != len(allowed):
        errors.append("Public catalog does not match approved project count")
    if {(a, b, c) for a, b, c, status in actual_catalog} != allowed:
        errors.append("Public catalog contains non-allowlisted names or categories")
    if any(status not in ("進行中", "待確認", "已完成") for _, _, _, status in actual_catalog):
        errors.append("Public catalog contains unsupported status")
    if any(status == "已完成" for _, _, _, status in actual_catalog):
        errors.append("Completed labels require separate approved acceptance records")
    # Child topics have a strict public data shape: no source, measurements or receipts.
    subtree = json.loads((root / "public-subprojects.json").read_text(encoding="utf-8"))
    if subtree.get("privacy_policy") != "APPROVED_GENERIC_TITLES_ONLY":
        errors.append("Public child list privacy policy missing")
    base_ids = {r["id"] for r in board["items"]}
    if {g["project_id"] for g in subtree["projects"]} != base_ids:
        errors.append("Public child tree parent coverage differs from approved public list")
    child_ids = set()
    for g in subtree["projects"]:
        if set(g) != {"project_id", "subprojects"}:
            errors.append("Child group includes unexpected fields")
        for item in g["subprojects"]:
            if set(item) != {"id", "title", "status", "completion_scope"}:
                errors.append("Child row includes non-allowlisted fields")
            if item.get("id") in child_ids:
                errors.append("Child row ID reused")
            child_ids.add(item.get("id"))
            if item.get("status") not in ("已完成", "進行中", "待確認"):
                errors.append("Child row status not approved")
            if item.get("status") == "已完成" and item.get("completion_scope") != "局部階段":
                errors.append("Completed child not explicitly bounded")
    if len(child_ids) != subtree.get("subproject_count"):
        errors.append("Child catalog count mismatch")
    return errors

if __name__ == "__main__":
    errors = validate()
    if errors:
        print(f"PRIVACY GATE FAIL: {len(errors)} publication violation(s)", file=sys.stderr)
        for err in errors:
            print(err, file=sys.stderr)
        raise SystemExit(1)
    print("PRIVACY GATE PASS: allowlisted public repositories and site data only")
