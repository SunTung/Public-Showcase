#!/usr/bin/env python3
"""Bounded public-domain Gutenberg text collector; local candidates only."""
import hashlib,json,re,urllib.request,datetime
from pathlib import Path
from catalog import discover_page
ROOT=Path(__file__).resolve().parent
OUT=ROOT/"corpus";OUT.mkdir(exist_ok=True)
LEDGER=ROOT/"indexes"/"ledger.json";LEDGER.parent.mkdir(exist_ok=True)
state=json.loads(LEDGER.read_text(encoding="utf-8")) if LEDGER.exists() else {"files":{},"candidate_bytes":0,"runs":[]}
# Source identifiers are public-domain classics; never copy private repository data.
BOOKS=[11,84,1342,1661,2701,345,98,158,1400,1260,768,12,1727,6130,1513,1524,74,76,5200,4300]
done={v["source_id"] for v in state["files"].values()}
state.setdefault('catalog_page',1)
state.setdefault('blocked_sources',{})
# Rotate subject searches so literature does not monopolize the corpus.
TOPICS=["science","mathematics","medicine","biology","history","law","technology","philosophy","education","literature"]
state.setdefault("topic_cursor",0)
state.setdefault("topic_pages",{})
topic=TOPICS[state["topic_cursor"]%len(TOPICS)]
state["topic_cursor"]+=1
page=state["topic_pages"].get(topic,1)
queue=[]
state.setdefault("discovery_runs",[])
discovery={"topic":topic,"page":page,"mode":"topic","found":0,"error":None}
try:
    found,has_next=discover_page(page,timeout=10,topic=topic)
    queue=[(int(name.split("-")[-1]),url) for name,url,kind in found if int(name.split("-")[-1]) not in done]
    state["topic_pages"][topic]=page+1 if has_next else 1
    discovery["found"]=len(queue)
except Exception as exc:
    discovery["error"]=str(exc)[:200]
    # A second bounded discovery strategy; do not confuse metadata with downloaded text.
    try:
        found,has_next=discover_page(page,timeout=10,search=topic)
        queue=[(int(name.split("-")[-1]),url) for name,url,kind in found if int(name.split("-")[-1]) not in done]
        state["topic_pages"][topic]=page+1 if has_next else 1
        discovery["mode"]="search_fallback"
        discovery["found"]=len(queue)
    except Exception as second:
        discovery["mode"]="catalog_unavailable"
        discovery["error"]+="; fallback: "+str(second)[:150]
state["discovery_runs"]=(state["discovery_runs"]+[discovery])[-200:]
# Seed texts are fallback only, not the primary search direction.
if not queue:
    discovery["mode"]="seed_fallback"
    queue=[(book,f"https://www.gutenberg.org/ebooks/{book}.txt.utf-8") for book in BOOKS if book not in done]
result={"at":datetime.datetime.now(datetime.timezone.utc).isoformat(),"status":"NO_NEW_SOURCE"}
for book,url in queue:
    if book in done:continue
    if state['blocked_sources'].get(str(book),0)>=3:continue
    try:
        req=urllib.request.Request(url,headers={"User-Agent":"OPS-F01-research-collector/1.0"})
        with urllib.request.urlopen(req,timeout=25) as resp:
            if resp.status!=200:raise ValueError("HTTP_NOT_200")
            raw=resp.read(5_000_001)
        if len(raw)>5_000_000 or len(raw)<2000 or b"\x00" in raw:raise ValueError("SIZE_OR_BINARY")
        body=raw.decode("utf-8-sig")
        a=re.search(r"\*\*\* START OF (?:THE|THIS) PROJECT GUTENBERG EBOOK[^\n]*\*\*\*",body,re.I)
        b=re.search(r"\*\*\* END OF (?:THE|THIS) PROJECT GUTENBERG EBOOK[^\n]*\*\*\*",body,re.I)
        if not a or not b or b.start()<=a.end():raise ValueError("NO_GUTENBERG_BODY_MARKERS")
        body=body[a.end():b.start()].strip()+"\n"
        data=body.encode("utf-8")
        words=re.findall(r"[A-Za-z]{3,}",body)
        if len(words)<400:raise ValueError("INSUFFICIENT_ENGLISH")
        sha=hashlib.sha256(data).hexdigest()
        if any(x["sha256"]==sha for x in state["files"].values()):
            result={"at":result["at"],"status":"DUPLICATE_SHA","source_id":book}
            continue
        name=f"gutenberg-{book}"
        (OUT/(name+".txt")).write_bytes(data)
        state["files"][name]={"source_id":book,"source_url":url,"sha256":sha,"candidate_bytes":len(data),"language_candidate":"en","global_verified":False,"search_topic":topic if discovery["mode"] in ("topic","search_fallback") else "literature","content_category":"literature_unverified_subgenre","category_verified":False,"discovery_mode":discovery["mode"]}
        state["candidate_bytes"]=sum(v["candidate_bytes"] for v in state["files"].values())
        result={"at":result["at"],"status":"LOCAL_CANDIDATE_ADDED","source_id":book,"candidate_bytes":len(data)}
        break
    except Exception as exc:
        state['blocked_sources'][str(book)]=state['blocked_sources'].get(str(book),0)+1
        result={"at":result["at"],"status":"SOURCE_ERROR","source_id":book,"error":str(exc)[:150]}
        continue
state["runs"]=(state["runs"]+[result])[-200:]
LEDGER.write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"result":result,"total_public_candidate_bytes":state["candidate_bytes"],"global_verified_bytes":None}))
