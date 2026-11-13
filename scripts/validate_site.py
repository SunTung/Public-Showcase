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
    p0 = read_json("workboard-p0-tasks.json")
    assert set(p0) == {"schema", "as_of", "source_snapshot", "scope", "project_count", "task_count", "overall_completion_pct", "records", "release"}
    assert p0["schema"] == "studio_public_p0_task_audit_v1"
    assert p0["project_count"] == 4 and p0["task_count"] == len(p0["records"]) == 20
    assert p0["overall_completion_pct"] is None
    p0_ids = {"CELL-CORE", "CELL-EN", "RL-GAME-STUDIO", "ENDLESS"}
    assert {x["project_id"] for x in p0["records"]} == p0_ids
    assert len({x["task_id"] for x in p0["records"]}) == len(p0["records"])
    allowed_status = {"VERIFIED_BOUNDED", "OPEN", "PLANNED", "BLOCKED_EXTERNAL"}
    for task in p0["records"]:
        assert set(task) == {"task_id", "project_id", "title", "status", "evidence_summary",
                             "evidence_date", "counts_toward_overall_completion", "acceptance_criterion", "dependency", "execution_class", "acceptance_receipt_state"}
        assert task["status"] in allowed_status
        assert task["counts_toward_overall_completion"] is False
        assert task["execution_class"] in {"ARCHIVED_CHECK", "NATIVE_RUNNER", "EVALUATION_RUNNER", "DESIGN_REVIEW", "ENVIRONMENT_CHECK", "WINDOWS_GUI"}
        assert task["acceptance_receipt_state"] == ("BASELINE_RECORDED" if task["status"] == "VERIFIED_BOUNDED" else "NOT_ACCEPTED")
        assert 10 <= len(task["acceptance_criterion"]) <= 180
        assert 6 <= len(task["dependency"]) <= 180

        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", task["evidence_date"])
        assert 5 <= len(task["title"]) <= 180 and 12 <= len(task["evidence_summary"]) <= 180
        assert not re.search(r"(?:github\.com|drive\.google\.com|/mnt/|token|password|secret|source_path|sha256)",
                             json.dumps(task, ensure_ascii=False), re.I)
    assert "workboard-p0-tasks.json" in (ROOT / "workboard.html").read_text(encoding="utf-8")
    latest = read_json("workboard-latest.json")
    assert set(latest) == {"schema", "checked_on", "private_base_snapshot", "scope",
                           "registered_count", "category_counts", "unregistered_candidate_count",
                           "unregistered_candidate_public_note", "records"}
    assert latest["schema"] == "studio_public_all_project_latest_v1"
    assert latest["registered_count"] == len(latest["records"]) == len(board["items"]) == 38
    expected_classes = {"NEW_BOUNDED_SOURCE_REPORT", "SOURCE_ACTIVITY_ONLY",
                        "NO_NEW_GATE_CONFIRMED", "SOURCE_EVIDENCE_PENDING"}
    assert set(latest["category_counts"]) == expected_classes
    assert sum(latest["category_counts"].values()) == 38
    assert len({r["project_id"] for r in latest["records"]}) == 38
    assert {r["project_id"] for r in latest["records"]} == {r["id"] for r in board["items"]}
    assert latest["unregistered_candidate_count"] == 1
    assert latest["private_base_snapshot"] <= latest["checked_on"]
    for item in latest["records"]:
        assert set(item) == {"project_id", "project_name", "review_class",
                             "latest_summary", "evidence_boundary", "whole_project_completion_pct"}
        assert item["review_class"] in expected_classes
        assert item["whole_project_completion_pct"] is None
        assert 8 <= len(item["latest_summary"]) <= 180
        assert 8 <= len(item["evidence_boundary"]) <= 180
        assert not re.search(r"(?:github\\.com|drive\\.google\\.com|/mnt/|token|password|secret|source_path|sha256)",
                             json.dumps(item, ensure_ascii=False), re.I)
        match = next(row for row in board["items"] if row["id"] == item["project_id"])
        assert item["project_name"] == match["name"]
    for key in expected_classes:
        assert latest["category_counts"][key] == sum(r["review_class"] == key for r in latest["records"])
    assert "workboard-latest.json" in (ROOT / "workboard.html").read_text(encoding="utf-8")
    events = read_json("workboard-events.json")
    assert set(events) == {"schema", "events"}
    assert events["schema"] == "studio_public_workboard_events_v1"
    assert isinstance(events["events"], list) and events["events"]
    valid_event_kinds = {"REGISTRY_SYNC", "CURATED_MILESTONE_UPDATE", "PORTFOLIO_TAXONOMY_R10", "OPS_R8_SOURCE_INGEST", "REPO_ACTIVITY_R10", "RESEARCH_INVENTORY_R10"}
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
    inv = read_json("workboard-repositories.json")
    assert inv["schema"] == "studio_github_cross_repo_inventory_v1"
    assert inv["privacy_policy"] == "PUBLIC_REPOSITORIES_ONLY"
    PUBLIC_REPOSITORIES = {"Public-Showcase", "CELL-DEFENDER"}
    assert inv["repo_count"] == len(inv["repository_statuses"]) == len(PUBLIC_REPOSITORIES)
    assert {r["repository"] for r in inv["repository_statuses"]} == PUBLIC_REPOSITORIES
    assert inv["aggregate"]["files"] == sum(r["file_count"] for r in inv["repository_statuses"])
    assert inv["aggregate"]["markdown_files"] == sum(r["markdown_count"] for r in inv["repository_statuses"])
    assert inv["aggregate"]["paper_named_file_candidates"] == sum(r["paper_named_file_candidates"] for r in inv["repository_statuses"])
    assert inv["aggregate"]["experiment_related_file_candidates"] == sum(r["experiment_related_file_candidates"] for r in inv["repository_statuses"])
    assert inv["aggregate"]["pdf_files"] == sum(r["pdf_count"] for r in inv["repository_statuses"])
    assert len(inv["families"]) == 12 and len(set(inv["families"])) == 12
    for row in inv["repository_statuses"]:
        assert row["tree_complete"]
        assert row["file_count"] >= 0
        assert row["last_action"] is None or row["last_action"]["conclusion"] in {"success", "failure", "cancelled", "skipped", "timed_out", "action_required", None}
        assert set(row["domain_path_hits"]) == set(inv["families"])
    for key in inv["families"]:
        assert inv["aggregate"]["domain_path_hits"][key] == sum(r["domain_path_hits"][key] for r in inv["repository_statuses"])
    research = read_json("workboard-research-topics.json")
    assert research["schema"] == "studio_research_topic_directory_v1"
    assert research["privacy_policy"] == "PUBLIC_ONLY_NO_PRIVATE_DERIVED_METRICS"
    assert research["topic_count"] == len(research["records"]) == 12
    assert research["repo_count"] == inv["repo_count"]
    assert research["project_count"] == 0
    assert research["paper_named_candidate_files"] == inv["aggregate"]["paper_named_file_candidates"]
    assert research["verified_unique_papers"] is None and research["verified_independent_research_topics"] is None
    assert research["private_topic_directory_clusters"] is None
    assert research["unknown_topic_directory_candidates"] is None
    assert research["unknown_paper_named_candidate_files"] is None
    assert research["unregistered_candidate"] is None
    for topic in research["records"]:
        assert topic["id"] in inv["families"]
        assert topic["path_hit_files"] == inv["aggregate"]["domain_path_hits"][topic["id"]]
        assert topic["matching_repository_count"] == sum(r["domain_path_hits"][topic["id"]] > 0 for r in inv["repository_statuses"])
        assert topic["topic_directory_candidates"] == 0
        assert topic["paper_named_candidate_files"] == 0
        assert topic["leading_repositories"] == []
        assert topic["project_count"] == 0
        assert topic["related_registered_project_ids"] == []
    # The public research index must never expose private repository identifiers.
    for forbidden in ("HF_TOKEN", "RGOS-RGSS", "CELL-NERVE-Interleaved-Memory",
                      "research_tracking/20261114", "private_projects/", "file_trees/"):
        assert forbidden not in json.dumps(inv, ensure_ascii=False)
        assert forbidden not in json.dumps(research, ensure_ascii=False)
        assert forbidden not in (ROOT / "research-index.html").read_text(encoding="utf-8")
    research_html = (ROOT / "research-index.html").read_text(encoding="utf-8")
    for filename in ("workboard-repositories.json", "workboard-research-topics.json", "workboard-latest.json"):
        assert filename in research_html
    parser_research = PageParser()
    parser_research.feed(research_html)
    assert {"repoCount","topics","repoQuery","repos","projects"}.issubset(parser_research.ids)
    assert "research-index.html" in page
    assert "research-index.html" in (ROOT / "workboard.html").read_text(encoding="utf-8")
    print(f"PASS: HTML, {len(months)} month(s), {len(current['projects'])} monthly progress entries, {len(portfolio['items'])} public portfolio items, {len(products['products'])} products")

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        import traceback
        traceback.print_exc()
        print(f"FAIL: {type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(1)
