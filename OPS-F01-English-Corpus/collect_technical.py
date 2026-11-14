#!/usr/bin/env python3
"""Bounded public technical Markdown collector. Candidate-only, never globally verified."""
import datetime,hashlib,json,re,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent
LEDGER=ROOT/"indexes"/"ledger.json"
SOURCES=[
("python-devguide-contributing","https://raw.githubusercontent.com/python/devguide/main/contributing/index.rst","technology"),
("python-devguide-documentation","https://raw.githubusercontent.com/python/devguide/main/documentation/markup.rst","technology"),
("python-peps-pep8","https://raw.githubusercontent.com/python/peps/main/peps/pep-0008.rst","technology"),
("python-peps-pep20","https://raw.githubusercontent.com/python/peps/main/peps/pep-0020.rst","technology"),
("python-peps-pep257","https://raw.githubusercontent.com/python/peps/main/peps/pep-0257.rst","technology"),
]
def run():
    state=json.loads(LEDGER.read_text(encoding="utf-8")) if LEDGER.exists() else {"files":{},"candidate_bytes":0,"runs":[]}
    state.setdefault("technical_runs",[])
    existing={x.get("sha256") for x in state["files"].values()}
    report={"at":datetime.datetime.now(datetime.timezone.utc).isoformat(),"status":"NO_NEW_TECHNICAL_SOURCE"}
    for key,url,topic in SOURCES:
        if key in state["files"]:continue
        try:
            request=urllib.request.Request(url,headers={"User-Agent":"OPS-F01-research-collector/0.4"})
            with urllib.request.urlopen(request,timeout=15) as response:
                if response.status!=200:raise ValueError("HTTP_NOT_200")
                raw=response.read(750001)
            if not 1500<=len(raw)<=750000 or b"\x00" in raw:raise ValueError("SIZE_OR_BINARY")
            body=raw.decode("utf-8-sig")
            if len(re.findall(r"[A-Za-z]{3,}",body))<250:raise ValueError("INSUFFICIENT_ENGLISH")
            data=body.encode("utf-8")
            sha=hashlib.sha256(data).hexdigest()
            if sha in existing:
                report={"at":report["at"],"status":"DUPLICATE_LOCAL_SHA","source":key}
                continue
            folder=ROOT/"corpus";folder.mkdir(exist_ok=True)
            (folder/(key+".txt")).write_bytes(data)
            state["files"][key]={"source_id":key,"source_url":url,"sha256":sha,"candidate_bytes":len(data),"language_candidate":"en","global_verified":False,"search_topic":topic,"source_format":"rst","discovery_mode":"curated_public_technical"}
            state["candidate_bytes"]=sum(x["candidate_bytes"] for x in state["files"].values())
            report={"at":report["at"],"status":"LOCAL_TECHNICAL_CANDIDATE_ADDED","source":key,"candidate_bytes":len(data)}
            break
        except Exception as exc:
            report={"at":report["at"],"status":"SOURCE_ERROR","source":key,"error":str(exc)[:160]}
            continue
    state["technical_runs"]=(state["technical_runs"]+[report])[-200:]
    LEDGER.parent.mkdir(exist_ok=True)
    LEDGER.write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report))
if __name__=="__main__":run()
