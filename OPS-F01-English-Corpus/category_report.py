#!/usr/bin/env python3
"""Public candidate domain report. No global verified totals are inferred."""
import collections,json
from pathlib import Path
root=Path(__file__).resolve().parent
p=root/"indexes"/"ledger.json"
d=json.loads(p.read_text(encoding="utf-8"))
by=collections.defaultdict(lambda:{"files":0,"candidate_bytes":0})
for entry in d.get("files",{}).values():
    category=entry.get("search_topic","unclassified")
    by[category]["files"]+=1
    by[category]["candidate_bytes"]+=int(entry.get("candidate_bytes",0))
result={"status":"CANDIDATE_ONLY","total_candidate_bytes":d.get("candidate_bytes",0),"files":len(d.get("files",{})),"categories":dict(sorted(by.items())),"global_verified_bytes":None,"cross_repository_dedup":"NOT_COMPLETE"}
out=root/"reports"/"category_status.json"
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(result,ensure_ascii=False))
