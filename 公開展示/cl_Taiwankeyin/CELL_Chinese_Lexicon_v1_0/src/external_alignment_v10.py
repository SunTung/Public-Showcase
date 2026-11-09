#!/usr/bin/env python3
"""Deterministic, non-approving alignment of CELL concepts to an independently supplied TSV.

Input columns: headword, zhuyin, pinyin, source_entry_id. This tool does not
fetch sources or establish authenticity. It never mutates the CELL database.
"""
import argparse,csv,hashlib,json,sqlite3,unicodedata
from pathlib import Path

COLUMNS=('headword','zhuyin','pinyin','source_entry_id')
def sha256(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def align(db,source_tsv,output_json,source_name,source_version):
    if not source_name.strip() or not source_version.strip():raise ValueError('Source identity/version required')
    source_tsv=Path(source_tsv); output_json=Path(output_json)
    with source_tsv.open('r',encoding='utf-8-sig',newline='') as f:
        reader=csv.DictReader(f,delimiter='\t')
        if reader.fieldnames is None or not set(COLUMNS).issubset(reader.fieldnames):raise ValueError('Missing required columns')
        rows=list(reader)
    entries={}; seen_ids=set()
    for i,r in enumerate(rows,2):
        if any(r.get(k) is None or not r[k].strip() for k in COLUMNS):raise ValueError(f'Blank source field at row {i}')
        if any(unicodedata.normalize('NFC',r[k])!=r[k] for k in COLUMNS):raise ValueError(f'Non-NFC row {i}')
        if r['source_entry_id'] in seen_ids:raise ValueError('Duplicate source_entry_id')
        seen_ids.add(r['source_entry_id']);entries.setdefault(r['headword'],[]).append(r)
    uri=Path(db).resolve().as_uri()+'?mode=ro'
    with sqlite3.connect(uri,uri=True) as con:
        concept_rows=con.execute('''SELECT c.concept_id,e.value,
         (SELECT value FROM pronunciation WHERE concept_id=c.concept_id AND scheme='zhuyin' LIMIT 1),
         (SELECT value FROM pronunciation WHERE concept_id=c.concept_id AND scheme='hanyu-pinyin' LIMIT 1)
         FROM concept c JOIN expression e USING(concept_id)
         WHERE e.locale='zh-Hant-TW' ORDER BY c.concept_id''').fetchall()
    findings=[]
    for cid,head,zhuyin,pinyin in concept_rows:
        options=entries.get(head,[])
        if not options:status='NOT_FOUND'
        elif len(options)>1:status='AMBIGUOUS_SOURCE'
        elif not zhuyin or not pinyin:status='MISSING_CELL_PRONUNCIATION'
        elif options[0]['zhuyin']==zhuyin and options[0]['pinyin']==pinyin:status='EXACT_TEXT_MATCH'
        else:status='PRONUNCIATION_DIFFERENCE'
        findings.append({'concept_id':cid,'headword':head,'status':status,
                         'source_entry_ids':[x['source_entry_id'] for x in options],
                         'cell_zhuyin':zhuyin,'cell_pinyin':pinyin,
                         'source_readings':[{'zhuyin':x['zhuyin'],'pinyin':x['pinyin']} for x in options]})
    counts={k:sum(x['status']==k for x in findings) for k in ('EXACT_TEXT_MATCH','PRONUNCIATION_DIFFERENCE','MISSING_CELL_PRONUNCIATION','AMBIGUOUS_SOURCE','NOT_FOUND')}
    result={'schema':'cell.external_alignment.v1.0','source_name':source_name,'source_version':source_version,
            'source_file_sha256':sha256(source_tsv),'source_rows':len(rows),'concepts_checked':len(findings),
            'counts':counts,'approval_events_created':0,'source_authenticity':'NOT_VERIFIED_BY_THIS_TOOL',
            'findings':findings}
    output_json.parent.mkdir(parents=True,exist_ok=True)
    output_json.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return result
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('db');p.add_argument('source_tsv');p.add_argument('output_json');p.add_argument('--source-name',required=True);p.add_argument('--source-version',required=True)
    a=p.parse_args();r=align(a.db,a.source_tsv,a.output_json,a.source_name,a.source_version)
    print(json.dumps({k:v for k,v in r.items() if k!='findings'},ensure_ascii=False,indent=2))
