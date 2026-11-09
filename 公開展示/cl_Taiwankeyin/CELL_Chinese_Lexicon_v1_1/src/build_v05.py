#!/usr/bin/env python3
"""CELL v0.5: preserve v0.4, append reviewed-as-draft batch, validate glyph evidence,
create immutable provenance-oriented review and dual-store candidate views.
No automatic human approval, pronunciation invention, or legacy wordlist import.
"""
import csv, hashlib, json, shutil, sqlite3, tempfile, unicodedata
from pathlib import Path
from build_v04 import build as build_v04

ROOT=Path(__file__).resolve().parents[1]
SCHEMA='cell.multilingual.concept.v0.5'
LOCALES=('zh-Hant-TW','zh-Hans-CN','en')

def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for chunk in iter(lambda:f.read(1<<20),b''):h.update(chunk)
 return h.hexdigest()

def read_batch(path):
 with Path(path).open(encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f,delimiter='\t'))
 required=('domain','traditional','simplified','english','pos')
 if not rows or not all(k in rows[0] for k in required):raise ValueError('Missing seed headers')
 triples=set()
 for row in rows:
  for k in required:
   v=row[k]
   if not v or v.strip()!=v or unicodedata.normalize('NFC',v)!=v or '\n' in v:raise ValueError('Invalid '+k)
  if row['pos'] not in ('noun','verb','adjective','adverb','other'):raise ValueError('Invalid POS')
  t=tuple(row[k] for k in ('traditional','simplified','english'))
  if t in triples:raise ValueError('Duplicate seed triple')
  triples.add(t)
 return rows

def build(output=ROOT/'build/cell_concepts.sqlite3',batch=ROOT/'data/cell_seed_batch05.tsv'):
 output=Path(output);batch=Path(batch);output.parent.mkdir(parents=True,exist_ok=True)
 rows=read_batch(batch)
 with tempfile.TemporaryDirectory() as d:
  previous=Path(d)/'v04.sqlite3';old=build_v04(output=previous)
  pending=output.with_suffix('.pending');pending.unlink(missing_ok=True);shutil.copy2(previous,pending)
 conn=sqlite3.connect(pending)
 try:
  conn.execute('PRAGMA foreign_keys=ON')
  conn.execute('BEGIN IMMEDIATE')
  previous_ids={r[0] for r in conn.execute('SELECT concept_id FROM concept')}
  known={tuple(row) for row in conn.execute('''SELECT MAX(CASE WHEN locale='zh-Hant-TW' THEN value END), MAX(CASE WHEN locale='zh-Hans-CN' THEN value END),MAX(CASE WHEN locale='en' THEN value END) FROM expression GROUP BY concept_id''')}
  next_id=max(int(cid[6:]) for cid in previous_ids)+1
  for row in rows:
   triple=tuple(row[x] for x in ('traditional','simplified','english'))
   if triple in known:raise ValueError('Existing triple '+str(triple))
   known.add(triple);cid=f'CELL-C{next_id:04d}';next_id+=1
   conn.execute('''INSERT INTO concept(concept_id,domain,pos,status,provenance,definition,created_batch) VALUES (?,?,?,?,?,?,?)''',(cid,row['domain'],row['pos'],'draft_review','CELL-composed-batch05',None,'CELL-v0.5'))
   conn.executemany('INSERT INTO expression VALUES(?,?,?,?,?)',[(cid,locale,value,1,'draft_review') for locale,value in zip(LOCALES,triple)])
   conn.executemany('INSERT INTO lexical_review_queue VALUES(?,?,?,?,?)',[(cid,'meaning',40,'independent bilingual lexical review required','pending'),(cid,'pronunciation',70,'both pinyin and Zhuyin missing; evidence required','pending')])
  # Prevent legacy mismatched context IDs from being mistaken for verified glyph evidence.
  conn.execute('''CREATE TABLE IF NOT EXISTS glyph_evidence_audit(
   source_locale TEXT NOT NULL,source_form TEXT NOT NULL,target_locale TEXT NOT NULL,target_form TEXT NOT NULL,
   evidence_example TEXT NOT NULL,context_concept_id TEXT NOT NULL REFERENCES concept(concept_id),
   audit_state TEXT NOT NULL CHECK(audit_state IN ('consistent_example','mismatched_example','ambiguous_context')),
   explanation TEXT NOT NULL,PRIMARY KEY(source_locale,source_form,target_locale,target_form,evidence_example))''')
  graph=conn.execute('SELECT source_locale,source_form,target_locale,target_form,evidence_example,context_concept_id FROM form_graph ORDER BY source_locale,source_form,target_locale,target_form').fetchall()
  # Fix a historic bad reference *only when exact expression evidence exists*.
  for origin,src,destination,dst,example,ref in graph:
   expected=conn.execute('SELECT concept_id FROM expression WHERE locale=? AND value=? ORDER BY concept_id',(destination,example)).fetchall()
   if not expected and origin=='zh-Hant-TW':
    expected=conn.execute('SELECT concept_id FROM expression WHERE locale=? AND value=? ORDER BY concept_id',('zh-Hant-TW',example)).fetchall()
   if expected and ref not in {x[0] for x in expected}:
    # Preserve original decision in audit; explicitly repair reference to a matching word sense.
    replacement=expected[0][0]
    conn.execute('UPDATE form_graph SET context_concept_id=? WHERE source_locale=? AND source_form=? AND target_locale=? AND target_form=? AND evidence_example=?',(replacement,origin,src,destination,dst,example))
  # Audit every graph edge without granting conversion approval.
  for origin,src,destination,dst,example,ref in conn.execute('SELECT source_locale,source_form,target_locale,target_form,evidence_example,context_concept_id FROM form_graph').fetchall():
   correct_locale='zh-Hant-TW'
   expr=conn.execute('SELECT value FROM expression WHERE concept_id=? AND locale=?',(ref,correct_locale)).fetchone()
   matches=bool(expr and expr[0]==example)
   state='consistent_example' if matches else 'mismatched_example'
   note='Context concept has matching traditional word example; conversion not approved' if matches else 'Example differs from concept text; human review required'
   conn.execute('INSERT INTO glyph_evidence_audit VALUES(?,?,?,?,?,?,?,?)',(origin,src,destination,dst,example,ref,state,note))
  conn.execute('''CREATE VIEW IF NOT EXISTS cell_candidate_view AS
   SELECT e.locale,e.value,e.concept_id,c.status,c.domain,'CELL' AS source
   FROM expression e JOIN concept c USING(concept_id)''')
  conn.execute('INSERT OR REPLACE INTO metadata VALUES (?,?)',('schema',SCHEMA))
  conn.execute('INSERT OR REPLACE INTO metadata VALUES (?,?)',('batch05_sha256',sha(batch)))
  conn.execute('INSERT OR REPLACE INTO metadata VALUES (?,?)',('promotion_gate','Drafts must not override legacy keyboard candidates until manual evidence approval'))
  if conn.execute('PRAGMA integrity_check').fetchone()[0]!='ok' or conn.execute('PRAGMA foreign_key_check').fetchall():raise ValueError('DB integrity failure')
  count=conn.execute('SELECT COUNT(*) FROM concept').fetchone()[0]
  prev_ids_in_db={r[0] for r in conn.execute('SELECT concept_id FROM concept') if r[0] in previous_ids}
  if prev_ids_in_db!=previous_ids or count!=old['counts']['concept']+len(rows):raise ValueError('Changed prior concept IDs')
  conn.commit()
  stats={t:conn.execute('SELECT COUNT(*) FROM '+t).fetchone()[0] for t in ('concept','expression','pronunciation','form_graph','glyph_evidence_audit','lexical_review_queue','review_event')}
  audit=dict(conn.execute('SELECT audit_state,COUNT(*) FROM glyph_evidence_audit GROUP BY audit_state'))
 except:
  conn.rollback();conn.close();pending.unlink(missing_ok=True);raise
 else:conn.close()
 pending.replace(output)
 result={'schema':SCHEMA,'previous_concepts':old['counts']['concept'],'batch05_concepts':len(rows),'counts':stats,'audit':audit,'batch05_sha256':sha(batch),'db_sha256':sha(output),'status':'BUILD_PASS / REVIEW_PENDING / DUAL_LOOKUP_READY'}
 (output.parent/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 return result

def lookup(db,locale,form,allow_drafts=False):
 if locale not in LOCALES or not isinstance(form,str) or not form.strip():raise ValueError('Invalid query')
 with sqlite3.connect(db) as c:
  c.row_factory=sqlite3.Row
  sql='SELECT concept_id,value,status,domain,source FROM cell_candidate_view WHERE locale=? AND value=?'
  if not allow_drafts:sql+=" AND status='approved'"
  return [dict(x) for x in c.execute(sql+' ORDER BY concept_id',(locale,form))]

def dual_lookup(cell_db,locale,form,legacy_candidates=(),allow_drafts=False):
 """Stable legacy-first candidates; no file writes or edits to the legacy dictionary."""
 out=[];seen=set()
 for term in legacy_candidates:
  if term not in seen:out.append({'form':term,'source':'legacy'});seen.add(term)
 for item in lookup(cell_db,locale,form,allow_drafts):
  if item['value'] not in seen:out.append({'form':item['value'],'source':'CELL','status':item['status']});seen.add(item['value'])
 return out

if __name__=='__main__':
 print(json.dumps(build(),ensure_ascii=False,indent=2))
