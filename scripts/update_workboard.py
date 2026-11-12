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
GATES = ROOT / "workboard-gates.json"
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
    parser.add_argument("--gate-scope", help="Scope of an independently reviewed bounded gate")
    parser.add_argument("--gate-accepted", type=int, help="Verified accepted gates in scope")
    parser.add_argument("--gate-total", type=int, help="Frozen gate denominator in scope")
    parser.add_argument("--gate-note", help="Public-safe acceptance limitation")
    parser.add_argument("--gate-id", help="Stable uppercase gate ID for a newly registered scoped gate")
    args = parser.parse_args()
    gate_supplied = any(v is not None for v in (args.gate_scope, args.gate_accepted, args.gate_total, args.gate_note))
    if not (args.milestone or args.next_gate or gate_supplied):
        parser.error("Provide --milestone, --next-gate or a complete bounded gate")
    if gate_supplied and not all(v is not None for v in (args.gate_scope, args.gate_accepted, args.gate_total, args.gate_note)):
        parser.error("Bounded gate requires --gate-scope, --gate-accepted, --gate-total and --gate-note")
    date = dt.date.fromisoformat(args.date).isoformat()
    if dt.date.fromisoformat(date) > dt.date.today():
        raise ValueError("Evidence review date cannot be in the future.")
    doc = json.loads(DATA.read_text(encoding="utf-8"))
    log = json.loads(EVENTS.read_text(encoding="utf-8"))
    ledger = json.loads(GATES.read_text(encoding="utf-8"))
    if doc.get("schema") != "studio_public_workboard_v1":
        raise ValueError("Unexpected workboard schema")
    if log.get("schema") != "studio_public_workboard_events_v1":
        raise ValueError("Unexpected events schema")
    if ledger.get("schema") != "studio_public_gate_ledger_v1":
        raise ValueError("Unexpected gate ledger schema")
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
    if gate_supplied:
        if args.gate_total <= 0 or not 0 <= args.gate_accepted <= args.gate_total:
            raise ValueError("Invalid bounded gate numerator / denominator")
        metric = {
            "scope": check_public_text(args.gate_scope),
            "accepted": args.gate_accepted,
            "total": args.gate_total,
            "note": check_public_text(args.gate_note),
        }
        existing = [g for g in ledger["records"] if g["project_id"] == args.id]
        if len(existing) > 1:
            raise ValueError("Multiple public gate records in one project")
        if existing:
            gate = existing[0]
            if args.gate_id and args.gate_id != gate["gate_id"]:
                raise ValueError("Existing gate ID cannot change")
            if metric["scope"] != gate["gate_title"] or metric["total"] != gate["total"]:
                raise ValueError("Existing acceptance scope and denominator are frozen")
            if metric["accepted"] < gate["accepted"]:
                raise ValueError("Cannot decrease accepted count without a separately reviewed correction")
            if date < gate["evidence_date"]:
                raise ValueError("Cannot backdate gate evidence")
            gate["accepted"] = metric["accepted"]
            gate["evidence_date"] = date
            gate["evidence_scope"] = metric["note"]
        else:
            if entry.get("gate_metric") is not None:
                raise ValueError("Existing gate metric has no ledger record; review consistency first")
            if not args.gate_id or not re.fullmatch(r"[A-Z0-9-]{5,80}", args.gate_id):
                raise ValueError("New gate requires stable --gate-id")
            if any(g["gate_id"] == args.gate_id for g in ledger["records"]):
                raise ValueError("Gate ID already exists")
            ledger["records"].append({
                "gate_id": args.gate_id, "project_id": args.id,
                "gate_title": metric["scope"], "accepted": metric["accepted"],
                "total": metric["total"], "blocked": None,
                "evidence_date": date, "evidence_scope": metric["note"],
                "verification": "DOCUMENTED_SCOPE_ONLY", "overall_project_percent": False
            })
        ledger["as_of"] = max(ledger["as_of"], date)
        if entry["gate_metric"] != metric:
            entry["gate_metric"] = metric
            changed.append("gate_metric")
    if not changed:
        print("NO CHANGE: public tracker already contains these values.")
        return
    if date < entry["evidence_date"]:
        raise ValueError("Do not backdate below the latest published review.")
    entry["evidence_date"] = date
    doc["as_of"] = max(doc["as_of"], date)
    summary_parts = []
    for key in changed:
        if key == "verified_milestone":
            summary_parts.append("已知成果：" + entry["verified_milestone"])
        elif key == "next_gate":
            summary_parts.append("下一關卡：" + entry["next_gate"])
        elif key == "gate_metric":
            g = entry["gate_metric"]
            summary_parts.append("關卡：" + g["scope"] + " " + str(g["accepted"]) + "/" + str(g["total"]))
    summary = "；".join(summary_parts)
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
    serialized_gates = json.dumps(ledger, ensure_ascii=False, indent=2) + "\n"
    DATA.write_text(serialized_doc, encoding="utf-8")
    EVENTS.write_text(serialized_log, encoding="utf-8")
    if gate_supplied:
        GATES.write_text(serialized_gates, encoding="utf-8")
    print(f"UPDATED: {args.id} ({', '.join(changed)}) on {date}. Validate before committing.")

if __name__ == "__main__":
    main()
