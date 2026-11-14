#!/usr/bin/env python3
"""Public candidate domain report. No global verified totals are inferred."""
import collections,json
from pathlib import Path
root=Path(__file__).resolve().parent
p=root/"indexes"/"ledger.json"
d=json.loads(p.read_text(encoding="utf-8"))
by=collections.defaultdict(lambda:{"files":0,"candidate_bytes":0})
for entry in d.get("files",{}).values():
    # Historical fixed-list Gutenberg items were tagged with the rotating search topic.\n    # Their category is unknown until content classification, never the attempted topic.\n    category=entry.get("search_topic","unclassified")\n    if isinstance(entry.get("source_id"),int) and entry["source_id"] in {11,84,1342,1661,2701,345,98,158,1400,1260,768,12,1727,6130,1513,1524,74,76,5200,4300}:\n        category="legacy_seed_unclassified"
    by[category]["files"]+=1
    by[category]["candidate_bytes"]+=int(entry.get("candidate_bytes",0))
result={"status":"CANDIDATE_ONLY","total_candidate_bytes":d.get("candidate_bytes",0),"files":len(d.get("files",{})),"categories":dict(sorted(by.items())),"global_verified_bytes":None,"cross_repository_dedup":"NOT_COMPLETE"}
out=root/"reports"/"category_status.json"
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(result,ensure_ascii=False))
