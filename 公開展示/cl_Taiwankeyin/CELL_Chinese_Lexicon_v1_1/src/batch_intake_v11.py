#!/usr/bin/env python3
"""Fail-closed, read-only batch intake of independently supplied official lexicon data.

No network access, no automatic approvals, no mutations to CELL SQLite.
Source file is retained separately, with digest and provenance in output.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,sqlite3,unicodedata,datetime
from collections import Counter,defaultdict
from pathlib import Path

REQUIRED=('headword','zhuyin','source_entry_id')
OPTIONAL=('pinyin','definition')
STATUSES=('NOT_FOUND','MULTIPLE_SOURCE_ENTRIES','MISSING_CELL_PRONUNCIATION','EXACT_ZHUYIN','DIFFERENT_ZHUYIN')

def sha256(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()

def load_rows(path,columns=None):
 path=Path(path)
 if path.suffix.lower()=='.tsv':
  with path.open(encoding='utf-8-sig',newline='') as f:
   reader=csv.DictReader(f,delimiter='\t')
   if reader.fieldnames is None:raise ValueError('No header')
   fields=reader.fieldnames
   rows=list(reader)
 elif path.suffix.lower()=='.xlsx':
  from openpyxl import load_workbook
  wb=load_workbook(path,read_only=True,data_only=True)
  try:
   sheet=wb.active
   iterator=sheet.iter_rows(values_only=True)
   fields=[str(x).strip() if x is not None else '' for x in next(iterator)]
   rows=[dict(zip(fields,['' if x is None else str(x) for x in values])) for values in iterator]
  finally:wb.close()
 else:raise ValueError('Only TSV or XLSX source supported')
 mapping=columns or {x:x for x in REQUIRED+OPTIONAL}
 if not all(mapping.get(x) in fields for x in REQUIRED):raise ValueError('Missing required source columns')
 seen=set(); result=[]
 for line,row in enumerate(rows,2):
  record={key:str(row.get(mapping.get(key,''),'') or '').strip() for key in REQUIRED+OPTIONAL}
  if not any(record.values()):continue
  if any(not record[x] for x in REQUIRED):raise ValueError(f'Missing required field at row {line}')
  if any(unicodedata.normalize('NFC',v)!=v for v in record.values()):raise ValueError(f'Non-NFC at row {line}')
  if record['source_entry_id'] in seen:raise ValueError(f'Duplicate source ID: {record["source_entry_id"]}')
  seen.add(record['source_entry_id']);result.append(record)
 return result

def inspect(db,source,output,*,name,version,source_url,columns=None):
 if not all(isinstance(x,str) and x.strip() for x in (name,version,source_url)):
  raise ValueError('Explicit source name, version and URL required')
 if not source_url.startswith('https://'):raise ValueError('Source URL must be HTTPS')
 rows=load_rows(source,columns)
 if not rows:raise ValueError('Source file has no entries')
 by_head=defaultdict(list)
 for row in rows:by_head[row['headword']].append(row)
 uri=Path(db).resolve().as_uri()+'?mode=ro'
 with sqlite3.connect(uri,uri=True) as con:
  concepts=con.execute('''SELECT c.concept_id,e.value,
   (SELECT value FROM pronunciation p WHERE p.concept_id=c.concept_id AND scheme='zhuyin' ORDER BY value LIMIT 1),
   (SELECT value FROM pronunciation p WHERE p.concept_id=c.concept_id AND scheme='hanyu-pinyin' ORDER BY value LIMIT 1)
   FROM concept c JOIN expression e USING(concept_id) WHERE e.locale='zh-Hant-TW' ORDER BY c.concept_id''').fetchall()
  if len(concepts)!=585:raise ValueError('Expected 585 CELL concepts; baseline mismatch')
 findings=[]
 for cid,head,zh,pin in concepts:
  options=by_head.get(head,[])
  if not options:status='NOT_FOUND'
  elif len(options)>1:status='MULTIPLE_SOURCE_ENTRIES'
  elif not zh:status='MISSING_CELL_PRONUNCIATION'
  elif zh==options[0]['zhuyin']:status='EXACT_ZHUYIN'
  else:status='DIFFERENT_ZHUYIN'
  findings.append({'concept_id':cid,'headword':head,'status':status,'cell_zhuyin':zh,'cell_pinyin':pin,
                   'source_matches':[{'source_entry_id':x['source_entry_id'],'zhuyin':x['zhuyin'],
                    'pinyin':x['pinyin'],'has_definition':bool(x['definition'])} for x in options]})
 counts=dict(Counter(x['status'] for x in findings))
 report={'schema':'cell.batch_intake.v1.1','source':{'name':name,'version':version,'url':source_url,
         'file_sha256':sha256(source),'file_bytes':Path(source).stat().st_size,'row_count':len(rows)},
         'concepts_checked':len(findings),'counts':{x:counts.get(x,0) for x in STATUSES},
         'source_authenticity':'UNVERIFIED_OFFLINE_INPUT','semantic_review':'NOT_PERFORMED',
         'phonetic_approval':'NOT_PERFORMED','release_candidates_added':0,
         'db_modified':False,'findings':findings}
 output=Path(output);output.parent.mkdir(parents=True,exist_ok=True)
 pending=output.with_suffix(output.suffix+'.pending')
 pending.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 pending.replace(output)
 return report

if __name__=='__main__':
 ap=argparse.ArgumentParser()
 ap.add_argument('db');ap.add_argument('source');ap.add_argument('output')
 ap.add_argument('--name',required=True);ap.add_argument('--version',required=True);ap.add_argument('--source-url',required=True)
 ap.add_argument('--column-map',help='JSON map from canonical field names to source column names')
 args=ap.parse_args()
 mapping=json.loads(args.column_map) if args.column_map else None
 result=inspect(args.db,args.source,args.output,name=args.name,version=args.version,source_url=args.source_url,columns=mapping)
 print(json.dumps({k:v for k,v in result.items() if k!='findings'},ensure_ascii=False,indent=2))
