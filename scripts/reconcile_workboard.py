#!/usr/bin/env python3
"""Compare a PRIVATE registry/WBS with the curated public tracker.

This tool NEVER writes private content to the public site. It emits a local
review queue with project IDs and change categories only. Human review and
scripts/update_workboard.py are required before public publication.

Example:
  python scripts/reconcile_workboard.py --registry /private/MASTER_REGISTRY.json \
    --wbs /private/NEXT_GATE_WBS.json --public workboard.json \
    --output /private/review_queue.json
"""
import argparse
import json
from pathlib import Path

SENSITIVE_KEYS = {"source", "source_path", "source_evidence", "audit_ref", "latest_audit",
                  "evidence_summary", "goal", "acceptance", "next_gate"}

def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def summarize(registry, wbs, public):
    records = registry["records"]
    packages = wbs["work_packages"]
    items = public["items"]
    private_ids = [r["id"] for r in records]
    wbs_ids = [r["project_id"] for r in packages]
    public_ids = [r["id"] for r in items]
    if len(set(private_ids)) != len(private_ids):
        raise ValueError("Duplicate private registry project ID")
    if len(set(wbs_ids)) != len(wbs_ids):
        raise ValueError("Duplicate WBS project ID")
    if len(set(public_ids)) != len(public_ids):
        raise ValueError("Duplicate public project ID")
    if set(private_ids) != set(wbs_ids):
        raise ValueError("Registry and WBS project IDs differ; review the private records first")

    reg = {r["id"]: r for r in records}
    work = {r["project_id"]: r for r in packages}
    site = {r["id"]: r for r in items}
    changes = []
    for project_id in sorted(set(private_ids) | set(public_ids)):
        if project_id not in site:
            reasons = ["NEW_PROJECT_REQUIRES_PUBLIC_CURATION"]
        elif project_id not in reg:
            reasons = ["PUBLIC_ONLY_PROJECT_REQUIRES_REVIEW"]
        else:
            reasons = []
            row, w, pub = reg[project_id], work[project_id], site[project_id]
            if pub.get("priority") != w.get("priority"):
                reasons.append("PRIORITY_CHANGED")
            if pub.get("source_reviewed") != (
                row.get("audit_round2", {}).get("status") not in (
                    "SOURCE_MISMATCH_PENDING", "SOURCE_ONLY_PENDING", "PRIMARY_EVIDENCE_PENDING"
                )
            ):
                reasons.append("SOURCE_REVIEW_STATUS_CHANGED")
            # Private 'next_gate' may contain sensitive unpublished descriptions.
            # Do not compare text or copy it into public files.
            if row.get("overall_completion_pct") is not None:
                reasons.append("PRIVATE_PERCENT_NEEDS_SCOPED_ACCEPTANCE_REVIEW")
        if reasons:
            changes.append({"id": project_id, "reasons": reasons})

    return {
        "schema": "private_to_public_review_queue_v1",
        "private_registry_project_count": len(private_ids),
        "private_wbs_project_count": len(wbs_ids),
        "public_project_count": len(public_ids),
        "review_required_count": len(changes),
        "review_items": changes,
        "automatic_publication": False,
        "instructions": "Review evidence privately; publish only curated public fields.",
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", required=True)
    parser.add_argument("--wbs", required=True)
    parser.add_argument("--public", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    output = Path(args.output).resolve()
    if output == root or root in output.parents:
        parser.error("Private review queue must be written OUTSIDE the public website repository")
    result = summarize(read(args.registry), read(args.wbs), read(args.public))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"REVIEW QUEUE: {result['review_required_count']} project(s); output: {output}")
    print("NO PUBLIC WRITE: curated updates must be verified and published separately.")

if __name__ == "__main__":
    main()
