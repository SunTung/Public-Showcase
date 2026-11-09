#!/usr/bin/env python3
"""CELL v0.6: audit-ready evidence ledger, no unverified lexical promotion."""
import json, sqlite3, shutil, tempfile, hashlib
from pathlib import Path
from build_v05 import build as build_v05
ROOT=Path(__file__).resolve().parents[1]
SCHEMA='cell.multilingual.concept.v0.6'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def build(output=ROOT/'build/cell_concepts.sqlite3'):
 output=Path(output);output.parent.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory() as d:
  source=Path(d)/'prior.sqlite3';prior=build_v05(source)
  pending=output.with_suffix('.pending');pending.unlink(missing_ok=True);shutil.copy2(source,pending)
 c=sqlite3.connect(pending)
 try:
  c.execute('PRAGMA foreign_keys=ON')
  c.executescript('''
  CREATE TABLE IF NOT EXISTS lexical_evidence(
    evidence_id TEXT PRIMARY KEY,
    concept_id TEXT NOT NULL REFERENCES concept(concept_id),
    aspect TEXT NOT NULL CHECK(aspect IN ('meaning','pronunciation','form','regional_usage')),
    source_uri TEXT NOT NULL, evidence_digest TEXT NOT NULL,
    excerpt_note TEXT NOT NULL, reviewer_id TEXT NOT NULL,
    decision TEXT NOT NULL CHECK(decision IN ('supports','contradicts','unclear')),
    recorded_at TEXT NOT NULL
  );
  CREATE TABLE IF NOT EXISTS lexical_approval(
    concept_id TEXT PRIMARY KEY REFERENCES concept(concept_id),
    reviewer_primary TEXT NOT NULL, reviewer_secondary TEXT NOT NULL,
    meaning_evidence_id TEXT NOT NULL REFERENCES lexical_evidence(evidence_id),
    pronunciation_evidence_id TEXT NOT NULL REFERENCES lexical_evidence(evidence_id),
    approval_state TEXT NOT NULL CHECK(approval_state IN ('approved','revoked')),
    approved_at TEXT NOT NULL,
    CHECK(reviewer_primary<>reviewer_secondary)
  );
  CREATE INDEX IF NOT EXISTS ix_evidence_concept ON lexical_evidence(concept_id,aspect);
  CREATE VIEW IF NOT EXISTS cell_release_candidates AS
    SELECT e.locale,e.value,e.concept_id,c.domain
    FROM expression e JOIN concept c USING(concept_id)
    JOIN lexical_approval a USING(concept_id)
    WHERE a.approval_state='approved';
  ''')
  c.execute("INSERT OR REPLACE INTO metadata VALUES (?,?)",('schema',SCHEMA))
  c.execute("INSERT OR REPLACE INTO metadata VALUES (?,?)",('release_gate','lexical_approval with 2 distinct reviewers and linked evidence; fail-closed'))
  assert c.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
  assert c.execute('PRAGMA foreign_key_check').fetchall()==[]
  counts={t:c.execute('SELECT COUNT(*) FROM '+t).fetchone()[0] for t in ['concept','expression','pronunciation','lexical_review_queue','lexical_evidence','lexical_approval','cell_release_candidates']}
  assert counts['concept']==585 and counts['expression']==1755 and counts['lexical_approval']==0
  c.commit()
 finally:c.close()
 pending.replace(output)
 result={'schema':SCHEMA,'previous_db_sha256':prior['db_sha256'],'counts':counts,'database_sha256':sha(output),'status':'BUILD_PASS / EVIDENCE_WORKFLOW_READY / NO_APPROVED_TERMS'}
 (output.parent/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 return result
if __name__=='__main__':print(json.dumps(build(),ensure_ascii=False,indent=2))
