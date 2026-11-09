#!/usr/bin/env python3
"""CELL concept lexicon v0.4: additive, sense-safe morphology and review queue.

Never silently equate a character-form mapping with a word translation.
Maintains all previous concept IDs. Does not import a third-party dictionary.
"""
from __future__ import annotations
import csv,hashlib,json,sqlite3,shutil,tempfile
from pathlib import Path
from build_v03 import build as build_v03, lookup as lookup_v03, read_batch

ROOT=Path(__file__).resolve().parents[1]
SCHEMA='cell.multilingual.concept.v0.4'
# Manually reviewed as *candidate mappings*, not production-safe conversion rules.
# A pair is a contextual alternative with a supporting in-project word sense.
VARIANTS=[
 ('发','發','發送','发发送', 'CELL-C0022'),
 ('发','髮','頭髮','头发','CELL-C0023'),
 ('后','後','後面','后面','CELL-C0025'),
 ('后','后','皇后','皇后','CELL-C0026'),
 ('干','乾','乾燥','干燥','CELL-C0029'),
 ('干','幹','幹部','干部','CELL-C0030'),
 ('里','裡','裡面','里面','CELL-C0027'),
 ('里','里','公里','公里','CELL-C0028'),
 ('面','麵','麵條','面条',None),
 ('面','面','見面','见面',None),
]

def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()

def build(output=ROOT/'build/cell_concepts.sqlite3',batch=ROOT/'data/cell_seed_batch04.tsv'):
 output=Path(output);batch=Path(batch);output.parent.mkdir(parents=True,exist_ok=True)
 rows=read_batch(batch)
 with tempfile.TemporaryDirectory() as directory:
  previous=Path(directory)/'v03.sqlite3'
  old=build_v03(output=previous)
  pending=output.with_suffix('.pending');pending.unlink(missing_ok=True)
  shutil.copy2(previous,pending)
 conn=sqlite3.connect(pending)
 try:
  conn.execute('PRAGMA foreign_keys=ON')
  conn.execute('BEGIN IMMEDIATE')
  existing={tuple(x) for x in conn.execute('''SELECT MAX(CASE WHEN locale='zh-Hant-TW' THEN value END),
   MAX(CASE WHEN locale='zh-Hans-CN' THEN value END),MAX(CASE WHEN locale='en' THEN value END)
   FROM expression GROUP BY concept_id''')}
  next_num=max(int(x[0][6:]) for x in conn.execute('SELECT concept_id FROM concept'))+1
  for row in rows:
   vals=(row['traditional'],row['simplified'],row['english'])
   if vals in existing:raise ValueError('duplicate existing concept '+str(vals))
   existing.add(vals)
   cid=f'CELL-C{next_num:04d}';next_num+=1
   conn.execute('INSERT INTO concept VALUES(?,?,?,?,?,?,?)',(cid,row['domain'],row['pos'],'draft_review','CELL-composed-batch04',None,'CELL-v0.4'))
   conn.executemany('INSERT INTO expression VALUES(?,?,?,?,?)',[(cid,locale,value,1,'draft_review') for locale,value in zip(('zh-Hant-TW','zh-Hans-CN','en'),vals)])
  conn.executescript('''CREATE TABLE IF NOT EXISTS form_graph(
   source_locale TEXT NOT NULL,source_form TEXT NOT NULL,
   target_locale TEXT NOT NULL,target_form TEXT NOT NULL,
   context_concept_id TEXT REFERENCES concept(concept_id),
   evidence_example TEXT NOT NULL, status TEXT NOT NULL,
   PRIMARY KEY(source_locale,source_form,target_locale,target_form,evidence_example));
   CREATE INDEX IF NOT EXISTS ix_form_graph_origin ON form_graph(source_locale,source_form);
   CREATE TABLE IF NOT EXISTS lexical_review_queue(
   concept_id TEXT NOT NULL REFERENCES concept(concept_id),
   aspect TEXT NOT NULL,priority INTEGER NOT NULL,
   reason TEXT NOT NULL,state TEXT NOT NULL,
   PRIMARY KEY(concept_id,aspect));
   CREATE INDEX IF NOT EXISTS ix_lexical_review_queue ON lexical_review_queue(state,priority DESC,concept_id);
  ''')
  for simplified,traditional,example,unused,reference in VARIANTS:
   if reference is None:
    match=conn.execute('''SELECT c.concept_id FROM concept c JOIN expression x USING(concept_id)
    WHERE x.locale='zh-Hant-TW' AND x.value=? LIMIT 1''',(example,)).fetchone()
    reference=match[0] if match else None
   if reference is None:raise ValueError('Unknown variant concept '+example)
   conn.execute('INSERT INTO form_graph VALUES(?,?,?,?,?,?,?)',('zh-Hans-CN',simplified,'zh-Hant-TW',traditional,reference,example,'context_required_draft'))
   conn.execute('INSERT INTO form_graph VALUES(?,?,?,?,?,?,?)',('zh-Hant-TW',traditional,'zh-Hans-CN',simplified,reference,example,'context_required_draft'))
  # Review queue is factual state only; nothing is auto-approved.
  conn.execute('''INSERT INTO lexical_review_queue
  SELECT c.concept_id,'meaning',CASE WHEN q.issue_id IS NOT NULL THEN 100 ELSE 40 END,
  CASE WHEN q.issue_id IS NOT NULL THEN 'multiple concepts share a simplified spelling' ELSE 'manual sense verification pending' END,
  'pending' FROM concept c LEFT JOIN
  (SELECT MIN(issue_id) issue_id,concept_id FROM quality_issue GROUP BY concept_id) q ON c.concept_id=q.concept_id''')
  conn.execute('''INSERT INTO lexical_review_queue
  SELECT c.concept_id,'pronunciation',70,'both Mandarin pinyin and Zhuyin require evidence','pending'
  FROM concept c LEFT JOIN pronunciation p ON p.concept_id=c.concept_id
  WHERE p.concept_id IS NULL''')
  conn.execute('''INSERT INTO lexical_review_queue
  SELECT DISTINCT c.concept_id,'glyph_mapping',90,'ambiguous single-character mapping; do not auto-reverse','pending'
  FROM concept c JOIN form_graph g ON c.concept_id=g.context_concept_id''')
  conn.execute('INSERT OR REPLACE INTO metadata VALUES (?,?)',('schema',SCHEMA))
  conn.execute('INSERT OR REPLACE INTO metadata VALUES (?,?)',('batch04_sha256',sha(batch)))
  conn.execute('INSERT OR REPLACE INTO metadata VALUES (?,?)',('review_gate','No human approval recorded; all new entries and mappings are drafts'))
  conn.execute('INSERT OR REPLACE INTO metadata VALUES (?,?)',('previous_concepts',str(old['counts']['concept'])))
  integrity=conn.execute('PRAGMA integrity_check').fetchone()[0]
  fks=conn.execute('PRAGMA foreign_key_check').fetchall()
  if integrity!='ok' or fks:raise ValueError('integrity or foreign key failure')
  conn.commit()
  counts={table:conn.execute('SELECT COUNT(*) FROM '+table).fetchone()[0]
   for table in ['concept','expression','pronunciation','form_graph','lexical_review_queue','form_candidate','quality_issue']}
  by_status=dict(conn.execute('SELECT status,COUNT(*) FROM concept GROUP BY status'))
 except:
  conn.rollback();conn.close();pending.unlink(missing_ok=True);raise
 else:conn.close()
 pending.replace(output)
 result={'schema':SCHEMA,'previous_concepts':old['counts']['concept'],'batch04_concepts':len(rows),
  'counts':counts,'review_status':by_status,'source_batch_sha256':sha(batch),'db_sha256':sha(output),
  'db_bytes':output.stat().st_size,'result':'BUILD_PASS; human lexical approval pending'}
 (output.parent/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 return result

def form_candidates(db,locale,form):
 with sqlite3.connect(db) as c:
  return c.execute('''SELECT target_form,evidence_example,status FROM form_graph
    WHERE source_locale=? AND source_form=? ORDER BY target_form,evidence_example''',(locale,form)).fetchall()

def review_queue(db,aspect=None,limit=30):
 with sqlite3.connect(db) as c:
  sql='SELECT concept_id,aspect,priority,reason,state FROM lexical_review_queue WHERE state=?'
  args=['pending']
  if aspect:sql+=' AND aspect=?';args.append(aspect)
  sql+=' ORDER BY priority DESC,concept_id LIMIT ?';args.append(min(500,max(1,limit)))
  return c.execute(sql,args).fetchall()

if __name__=='__main__':
 r=build()
 print(json.dumps(r,ensure_ascii=False,indent=2))
