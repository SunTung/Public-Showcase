#!/usr/bin/env python3
"""Evidence capture and two-reviewer release gate, fail-closed by default."""
import sqlite3, hashlib, json, argparse
from pathlib import Path
from datetime import datetime, timezone
from build_v06 import ROOT

def evidence_id(concept_id,aspect,uri,digest,reviewer):
 return hashlib.sha256('\0'.join([concept_id,aspect,uri,digest,reviewer]).encode()).hexdigest()[:32]
def record_evidence(db,concept_id,aspect,source_uri,evidence_digest,note,reviewer,decision,when=None):
 if aspect not in {'meaning','pronunciation','form','regional_usage'} or decision not in {'supports','contradicts','unclear'}:raise ValueError('invalid aspect/decision')
 if not source_uri.startswith(('https://','http://','urn:')) or len(evidence_digest)!=64 or any(c not in '0123456789abcdef' for c in evidence_digest):raise ValueError('evidence URI and SHA256 required')
 if not reviewer.strip() or not note.strip():raise ValueError('nonempty reviewer and evidence note required')
 eid=evidence_id(concept_id,aspect,source_uri,evidence_digest,reviewer)
 with sqlite3.connect(db) as c:
  c.execute('PRAGMA foreign_keys=ON')
  c.execute('INSERT INTO lexical_evidence VALUES (?,?,?,?,?,?,?,?,?)',(eid,concept_id,aspect,source_uri,evidence_digest,note,reviewer,decision,when or datetime.now(timezone.utc).isoformat()))
 return eid

def approve(db,concept_id,first,second,meaning_id,pronunciation_id,when=None):
 if not first.strip() or not second.strip() or first==second:raise ValueError('independent reviewers required')
 with sqlite3.connect(db) as c:
  c.execute('PRAGMA foreign_keys=ON')
  pairs=c.execute('SELECT evidence_id,aspect,reviewer_id,decision FROM lexical_evidence WHERE evidence_id IN (?,?) AND concept_id=?',(meaning_id,pronunciation_id,concept_id)).fetchall()
  evidence={r[0]:r for r in pairs}
  if len(evidence)!=2:raise ValueError('both evidence records required for this concept')
  a=evidence.get(meaning_id);b=evidence.get(pronunciation_id)
  if not a or not b or a[1]!='meaning' or b[1]!='pronunciation' or a[3]!='supports' or b[3]!='supports':raise ValueError('supporting evidence for meaning and pronunciation required')
  if {a[2],b[2]}!={first,second}:raise ValueError('both named reviewers must provide the evidence')
  c.execute('INSERT INTO lexical_approval VALUES (?,?,?,?,?,?,?)',(concept_id,first,second,meaning_id,pronunciation_id,'approved',when or datetime.now(timezone.utc).isoformat()))
  c.execute("UPDATE lexical_review_queue SET state='completed' WHERE concept_id=? AND aspect IN ('meaning','pronunciation')",(concept_id,))
  # Released words only via view; original drafts and input methods remain untouched.

def candidates(db,locale,form):
 if locale not in {'zh-Hant-TW','zh-Hans-CN','en'}:raise ValueError('invalid locale')
 with sqlite3.connect(db) as c:
  return c.execute('SELECT concept_id,value FROM cell_release_candidates WHERE locale=? AND value=? ORDER BY concept_id',(locale,form)).fetchall()

def review_queue(db,limit=25):
 with sqlite3.connect(db) as c:
  return [dict(zip(('concept_id','aspect','priority','detail'),r)) for r in c.execute("SELECT concept_id,aspect,priority,reason FROM lexical_review_queue WHERE state='pending' ORDER BY priority,concept_id LIMIT ?",(max(1,min(limit,1000)),))]
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--db',type=Path,default=ROOT/'build/cell_concepts.sqlite3');p.add_argument('--queue',action='store_true');p.add_argument('--limit',type=int,default=25);args=p.parse_args()
 print(json.dumps(review_queue(args.db,args.limit) if args.queue else {'release_count':len(candidates(args.db,'zh-Hant-TW','鍵盤'))},ensure_ascii=False,indent=2))
