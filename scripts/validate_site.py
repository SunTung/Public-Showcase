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
    assert estimates["reviewed_count"] == 19 and estimates["total_count"] == 37
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
    assert all(mapping[e["id"]]["confidence"] == "low" for e in portfolio["items"][19:])
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

    print(f"PASS: HTML, {len(months)} month(s), {len(current['projects'])} monthly progress entries, {len(portfolio['items'])} public portfolio items, {len(products['products'])} products")

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        sys.exit(1)
