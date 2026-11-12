#!/usr/bin/env python3
"""Edit the curated public tracker without accessing private source registries.

Usage:
  python scripts/update_workboard.py --id CELL-EN --date 2026-11-13 \
      --milestone "原生 67M 訓練與保留集評測已完成驗收。" \
      --next-gate "進行下一階段原生增量訓練與新題評測。"

This command does not verify engineering claims. Publish only after manual
evidence review; the website validator checks schema and public-data boundaries.
"""
import argparse
import datetime as dt
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "workboard.json"
EVENTS = ROOT / "workboard-events.json"
FORBIDDEN = re.compile(
    r"(github\.com|drive\.google\.com|/mnt/|[A-Za-z]:\\|token|password|secret|"
    r"private_repo|source_path|owner_repository|sha256|commit_sha)", re.I
)

def check_public_text(value):
    if not (8 <= len(value.strip()) <= 180):
        raise ValueError("Public description must be between 8 and 180 characters.")
    if FORBIDDEN.search(value):
        raise ValueError("Public description contains a restricted URL, path or keyword.")
    return value.strip()

def main():
    parser = argparse.ArgumentParser(description="Update approved public progress and log changes")
    parser.add_argument("--id", required=True, help="Exact project ID from workboard.json")
    parser.add_argument("--date", required=True, help="Evidence review date YYYY-MM-DD")
    parser.add_argument("--milestone", help="Public-safe independently verified milestone")
    parser.add_argument("--next-gate", help="Next concrete acceptance milestone")
    args = parser.parse_args()
    if not (args.milestone or args.next_gate):
        parser.error("Provide --milestone or --next-gate")
    date = dt.date.fromisoformat(args.date).isoformat()
    if dt.date.fromisoformat(date) > dt.date.today():
        raise ValueError("Evidence review date cannot be in the future.")
    doc = json.loads(DATA.read_text(encoding="utf-8"))
    log = json.loads(EVENTS.read_text(encoding="utf-8"))
    if doc.get("schema") != "studio_public_workboard_v1":
        raise ValueError("Unexpected workboard schema")
    if log.get("schema") != "studio_public_workboard_events_v1":
        raise ValueError("Unexpected events schema")
    matches = [r for r in doc["items"] if r["id"] == args.id]
    if len(matches) != 1:
        raise ValueError("Unknown or duplicate project ID")
    entry = matches[0]
    changed = []
    for arg, key in ((args.milestone, "verified_milestone"), (args.next_gate, "next_gate")):
        if arg is not None:
            value = check_public_text(arg)
            if entry[key] != value:
                entry[key] = value
                changed.append(key)
    if not changed:
        print("NO CHANGE: public tracker already contains these values.")
        return
    if date < entry["evidence_date"]:
        raise ValueError("Do not backdate below the latest published review.")
    entry["evidence_date"] = date
    doc["as_of"] = max(doc["as_of"], date)
    summary = "；".join(
        ("已知成果：" + entry["verified_milestone"]) if k == "verified_milestone"
        else ("下一關卡：" + entry["next_gate"])
        for k in changed
    )
    if len(summary) > 360:
        raise ValueError("Combined public event description exceeds 360 characters.")
    if FORBIDDEN.search(summary):
        raise ValueError("Public event contains a restricted location or keyword.")
    log["events"].append({
        "date": date, "project_id": args.id, "kind": "CURATED_MILESTONE_UPDATE",
        "summary": summary,
    })
    serialized_doc = json.dumps(doc, ensure_ascii=False, indent=2) + "\n"
    serialized_log = json.dumps(log, ensure_ascii=False, indent=2) + "\n"
    DATA.write_text(serialized_doc, encoding="utf-8")
    EVENTS.write_text(serialized_log, encoding="utf-8")
    print(f"UPDATED: {args.id} ({', '.join(changed)}) on {date}. Validate before committing.")

if __name__ == "__main__":
    main()
