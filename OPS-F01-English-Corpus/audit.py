#!/usr/bin/env python3
"""Audit only locally saved public candidates; never assert global dedup."""
import hashlib,json,sys
from pathlib import Path
root=Path(__file__).resolve().parent
ledger_path=root/"indexes"/"ledger.json"
if not ledger_path.exists():
    print(json.dumps({"status":"NO_LEDGER","global_verified_bytes":None}))
    sys.exit(0)
ledger=json.loads(ledger_path.read_text(encoding="utf-8"))
errors=[];total=0;seen=set()
for name,entry in ledger.get("files",{}).items():
    p=root/"corpus"/(name+".txt")
    if not p.is_file():
        errors.append({"name":name,"error":"MISSING"});continue
    data=p.read_bytes();digest=hashlib.sha256(data).hexdigest()
    if digest!=entry.get("sha256"):errors.append({"name":name,"error":"SHA_MISMATCH"})
    if len(data)!=entry.get("candidate_bytes"):errors.append({"name":name,"error":"SIZE_MISMATCH"})
    if digest in seen:errors.append({"name":name,"error":"DUPLICATE"})
    seen.add(digest);total+=len(data)
if total!=ledger.get("candidate_bytes",0):errors.append({"error":"TOTAL_MISMATCH","computed":total})
print(json.dumps({"status":"PASS_LOCAL_CANDIDATES" if not errors else "FAIL","candidate_files":len(ledger.get("files",{})),"candidate_bytes":total,"global_verified_bytes":None,"errors":errors}))
sys.exit(bool(errors))
