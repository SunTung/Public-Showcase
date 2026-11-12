#!/usr/bin/env python3
"""Validate only explicitly approved public website artifacts."""
import json
import pathlib
import re
import sys
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parents[1]
MONTH = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")
ALLOWED = {"month", "projects"}
PROJECT_FIELDS = {"name", "progress", "status"}
PRODUCT_FIELDS = {"title", "title_en", "category", "description", "description_en", "public", "url"}
PORTFOLIO_FIELDS = {"number", "id", "name", "name_en", "goal", "goal_en", "category", "monthly_progress_pct", "progress_basis"}
PORTFOLIO_CATEGORIES = {"ai", "software", "game", "data", "medical", "research", "paper", "literature", "business"}

def read_json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

def assert_progress(data, month):
    assert set(data) == ALLOWED, "Unexpected top-level progress fields"
    assert data["month"] == month
    assert isinstance(data["projects"], list) and len(data["projects"]) > 0
    for p in data["projects"]:
        assert set(p).issubset(PROJECT_FIELDS), "Unapproved project field"
        assert isinstance(p.get("name"), str) and p["name"].strip()
        assert type(p.get("progress")) in (int, float) and 0 <= p["progress"] <= 100
        assert isinstance(p.get("status"), str)
        assert not re.search(r"(?:token|secret|password|private_repo|model_path)", str(p), re.I)

class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if "id" in d:
            assert d["id"] not in self.ids, "Duplicate HTML id"
            self.ids.add(d["id"])

def main():
    page = (ROOT / "index.html").read_text(encoding="utf-8")
    parser = PageParser()
    parser.feed(page)
    for name in ("progress", "research", "software", "about", "products", "list", "monthSelect", "langToggle", "portfolio", "portfolioList", "portfolioSearch", "portfolioCategory"):
        assert name in parser.ids, f"Missing element: {name}"
    months = read_json("history/index.json")["months"]
    assert len(months) == len(set(months)) and months
    for month in months:
        assert MONTH.fullmatch(month), f"Invalid month: {month}"
        assert_progress(read_json(f"history/{month}.json"), month)
    current = read_json("progress.json")
    assert_progress(current, current["month"])
    assert current == read_json(f"history/{current['month']}.json"), "Current month differs from archive"
    products = read_json("products.json")
    assert set(products) == {"products"}
    for p in products["products"]:
        assert set(p).issubset(PRODUCT_FIELDS), "Unapproved product field"
        assert p.get("public") is True, "Only approved public entries may be listed"
        if "url" in p:
            assert p["url"].startswith("https://github.com/SunTung/"), "Unapproved public link"
    portfolio = read_json("portfolio.json")
    assert set(portfolio) == {"schema", "month", "progress_meaning", "items"}
    assert portfolio["schema"] == "studio_public_portfolio_v1"
    assert portfolio["month"] == current["month"], "Portfolio must match current displayed month"
    assert isinstance(portfolio["items"], list) and len(portfolio["items"]) >= 1
    seen_ids = set()
    for i, entry in enumerate(portfolio["items"], start=1):
        assert set(entry) == PORTFOLIO_FIELDS, "Unexpected portfolio field; possible private data exposure"
        assert entry["number"] == f"{i:03d}", "Public project numbering must be stable"
        assert isinstance(entry["id"], str) and re.fullmatch(r"[A-Z0-9-]+", entry["id"])
        assert entry["id"] not in seen_ids, "Duplicate project ID"
        seen_ids.add(entry["id"])
        for key in ("name", "name_en", "goal", "goal_en"):
            assert isinstance(entry[key], str) and 3 <= len(entry[key]) <= 250
        assert entry["category"] in PORTFOLIO_CATEGORIES
        pct = entry["monthly_progress_pct"]
        assert pct is None or (type(pct) in (float, int) and 0 <= pct <= 100)
        assert entry["progress_basis"] == ("not_assessed" if pct is None else "user_supplied_monthly_plan")
        serialized = json.dumps(entry, ensure_ascii=False)
        assert not re.search(r"(?:github\.com|drive\.google\.com|/mnt/|[a-zA-Z]:\\\\|token|password|private_repo|model_path|source\.repository|source\.path|sha256|commit_sha)", serialized, re.I), "Potential private source or credential in portfolio"
    estimates = read_json("estimates.json")
    assert set(estimates) == {"schema", "as_of", "method", "scope_note_zh", "scope_note_en", "reviewed_count", "total_count", "items"}
    assert estimates["schema"] == "public_stage_estimates_v1"
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", estimates["as_of"])
    assert estimates["reviewed_count"] == 26 and estimates["total_count"] == 37
    assert len(estimates["items"]) == len(portfolio["items"]) == 37
    estimate_fields = {"id", "low", "high", "confidence", "scope", "note_zh", "note_en"}
    mapping = {x["id"]: x for x in estimates["items"]}
    assert len(mapping) == 37 and set(mapping) == seen_ids
    for row in estimates["items"]:
        assert set(row) == estimate_fields, "Unexpected estimate field"
        assert type(row["low"]) is int and type(row["high"]) is int
        assert 0 <= row["low"] <= row["high"] <= 100
        assert row["low"] % 5 == row["high"] % 5 == 0, "Do not imply false numeric precision"
        assert row["confidence"] in {"low", "medium", "high"}
        assert re.fullmatch(r"[a-z_]+", row["scope"])
        for key in ("note_zh", "note_en"):
            assert isinstance(row[key], str) and 10 <= len(row[key]) <= 160
        serialized = json.dumps(row, ensure_ascii=False)
        assert not re.search(r"(?:github\\.com|drive\\.google\\.com|/mnt/|[a-zA-Z]:\\\\|token|password|private_repo|model_path|sha256|commit_sha)", serialized, re.I)
    assert all(mapping[e["id"]]["confidence"] == "low" for e in portfolio["items"][26:])
    assert sum(e["monthly_progress_pct"] is not None for e in portfolio["items"]) == len(current["projects"]), "Mismatch with monthly dashboard"
    # Featured dashboard cards must share portfolio IDs and estimates with the overview.
    public_names = {entry["name"]: entry["id"] for entry in portfolio["items"]}
    assert len(public_names) == len(portfolio["items"]), "Duplicate public display names"
    for featured in current["projects"]:
        assert featured["name"] in public_names, "Featured project has no linked portfolio item"
        assert public_names[featured["name"]] in mapping, "Featured project has no linked estimate"
    assert 'const project=portfolio.find(x=>x.name===p.name)' in page, "Dashboard is not linked to portfolio identity"
    assert 'const estimate=project&&estimates[project.id]' in page, "Dashboard does not use shared estimates"
    assert 'text(monthly,(language==="zh"?"原本本月計畫："' in page, "Monthly plan must stay distinct from estimate"

    board = read_json("workboard.json")
    assert board["schema"] == "studio_public_workboard_v1"
    assert board["registered_projects"] == board["work_packages"] == len(board["items"]) == 38
    assert board["source_reviewed"] == 35 and board["source_pending"] == 3
    assert sum(board["priority_counts"].values()) == 38
    assert len({r["id"] for r in board["items"]}) == 38
    for r in board["items"]:
        assert set(r) == {"number", "id", "name", "category", "goal", "priority", "source_reviewed", "work_status", "overall_completion_pct", "monthly_plan_pct", "next_gate", "verified_milestone", "evidence_date", "status_kind", "gate_metric"}
        assert r["priority"] in {"P0", "P1", "P2", "P_RESEARCH", "P_BLOCKED"}
        assert isinstance(r["source_reviewed"], bool)
        assert r["overall_completion_pct"] is None, "No fabricated completion percentage"
        metric = r["gate_metric"]
        if metric is not None:
            assert set(metric) == {"scope", "accepted", "total", "note"}
            assert type(metric["accepted"]) is int and type(metric["total"]) is int
            assert 0 <= metric["accepted"] <= metric["total"] and metric["total"] > 0
            assert len(metric["scope"]) >= 5 and len(metric["note"]) >= 10
            assert not re.search(r"(?:github\\.com|drive\\.google\\.com|/mnt/|token|password|secret|source_path|sha256)", json.dumps(metric, ensure_ascii=False), re.I)

        assert r["status_kind"] in {"NEXT_GATE_OPEN", "EVIDENCE_PENDING"}
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", r["evidence_date"])
        assert 8 <= len(r["verified_milestone"]) <= 180
        assert 8 <= len(r["next_gate"]) <= 180
        assert r["monthly_plan_pct"] is None or isinstance(r["monthly_plan_pct"], (int, float))
        assert not re.search(r"(?:github\\.com|drive\\.google\\.com|/mnt/|token|password|secret|source_path|owner_repository|SHA256)", json.dumps(r, ensure_ascii=False), re.I)
    assert sum(r["source_reviewed"] for r in board["items"]) == 35
    gates = read_json("workboard-gates.json")
    assert set(gates) == {"schema", "as_of", "scope", "records"}
    assert gates["schema"] == "studio_public_gate_ledger_v1"
    assert isinstance(gates["records"], list)
    gate_ids = set()
    gate_project_ids = set()
    for gate in gates["records"]:
        assert set(gate) == {"gate_id", "project_id", "gate_title", "accepted", "total",
                            "blocked", "evidence_date", "evidence_scope", "verification",
                            "overall_project_percent"}
        assert gate["gate_id"] not in gate_ids
        gate_ids.add(gate["gate_id"])
        assert gate["project_id"] in {r["id"] for r in board["items"]}
        assert gate["project_id"] not in gate_project_ids, "Only one public scoped metric per project in R6"
        gate_project_ids.add(gate["project_id"])
        assert type(gate["accepted"]) is int and type(gate["total"]) is int
        assert 0 <= gate["accepted"] <= gate["total"] and gate["total"] > 0
        assert gate["blocked"] is None or (type(gate["blocked"]) is int and 0 <= gate["blocked"] <= gate["total"] - gate["accepted"])
        assert gate["overall_project_percent"] is False
        assert gate["verification"] == "DOCUMENTED_SCOPE_ONLY"
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", gate["evidence_date"])
        for k in ("gate_title", "evidence_scope"):
            assert isinstance(gate[k], str) and 5 <= len(gate[k]) <= 180
        assert not re.search(r"(?:github\\.com|drive\\.google\\.com|/mnt/|token|password|secret|source_path|sha256)",
                             json.dumps(gate, ensure_ascii=False), re.I)
        match = next(r for r in board["items"] if r["id"] == gate["project_id"])
        assert match["gate_metric"] is not None
        assert match["gate_metric"]["accepted"] == gate["accepted"]
        assert match["gate_metric"]["total"] == gate["total"]
        assert match["gate_metric"]["scope"] == gate["gate_title"]
    assert sum(r["gate_metric"] is not None for r in board["items"]) == len(gates["records"])
    events = read_json("workboard-events.json")
    assert set(events) == {"schema", "events"}
    assert events["schema"] == "studio_public_workboard_events_v1"
    assert isinstance(events["events"], list) and events["events"]
    valid_event_kinds = {"REGISTRY_SYNC", "CURATED_MILESTONE_UPDATE"}
    for event in events["events"]:
        assert set(event) == {"date", "project_id", "kind", "summary"}
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", event["date"])
        assert event["project_id"] == "ALL" or event["project_id"] in {r["id"] for r in board["items"]}
        assert event["kind"] in valid_event_kinds
        assert 8 <= len(event["summary"]) <= 360
        assert not re.search(r"(?:github\.com|drive\.google\.com|/mnt/|token|password|secret|source_path|sha256)", event["summary"], re.I)
    assert "workboard-events.json" in (ROOT / "workboard.html").read_text(encoding="utf-8")
    sync = read_json("workboard-sync-status.json")
    assert set(sync) == {"schema", "checked_on", "private_registry_snapshot_date",
                         "scope", "private_registry_count", "private_wbs_count",
                         "public_tracker_count", "mismatch_count", "all_functional_gates_verified",
                         "automatic_private_sync_enabled", "publication_method", "summary_zh"}
    assert sync["schema"] == "studio_public_reconciliation_status_v1"
    assert sync["private_registry_count"] == sync["private_wbs_count"] == sync["public_tracker_count"] == 38
    assert type(sync["mismatch_count"]) is int and 0 <= sync["mismatch_count"] <= 38
    assert sync["automatic_private_sync_enabled"] is False
    assert sync["all_functional_gates_verified"] is False
    assert "workboard-sync-status.json" in (ROOT / "workboard.html").read_text(encoding="utf-8")
    assert "workboard.html" in page
    assert 'workboard.json' in (ROOT / "workboard.html").read_text(encoding="utf-8")
    print(f"PASS: HTML, {len(months)} month(s), {len(current['projects'])} monthly progress entries, {len(portfolio['items'])} public portfolio items, {len(products['products'])} products")

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        sys.exit(1)
