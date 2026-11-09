#!/usr/bin/env python3
"""v0.8 release gate hardening: truth of evidence linkages is checked at query time.

Raw evidence from v0.6 remains a *claim*, not a verified source snapshot.
"""
import hashlib,json,sqlite3,shutil,tempfile
from pathlib import Path
from build_v07 import build as build_v07
ROOT=Path(__file__).resolve().parents[1]
SCHEMA='cell.multilingual.concept.v0.8'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def build(output=ROOT/'build/cell_concepts.sqlite3'):
 output=Path(output);output.parent.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory() as d:
  previous=Path(d)/'v07.sqlite3';old=build_v07(previous)
  pending=output.with_suffix('.pending');pending.unlink(missing_ok=True);shutil.copyfile(previous,pending)
 con=sqlite3.connect(pending)
 try:
  con.execute('PRAGMA foreign_keys=ON')
  con.executescript('''
   CREATE TABLE evidence_snapshot (
    source_uri TEXT NOT NULL, digest TEXT NOT NULL,
    captured_text TEXT NOT NULL CHECK(length(captured_text)>0),
    verified_at TEXT NOT NULL, verification_method TEXT NOT NULL,
    verification_state TEXT NOT NULL CHECK(verification_state IN ('source_confirmed','rejected')),
    PRIMARY KEY(source_uri,digest));
   CREATE TABLE release_gate_issue (
    issue_id INTEGER PRIMARY KEY, concept_id TEXT NOT NULL REFERENCES concept(concept_id),
    rule TEXT NOT NULL, details TEXT NOT NULL,
    UNIQUE(concept_id,rule,details));
   DROP VIEW IF EXISTS cell_release_v08;
   CREATE VIEW cell_release_v08 AS
    SELECT e.locale,e.value,e.concept_id,c.domain
    FROM expression e JOIN concept c USING(concept_id)
    JOIN lexical_approval a USING(concept_id)
    JOIN lexical_evidence m ON m.evidence_id=a.meaning_evidence_id
    JOIN lexical_evidence p ON p.evidence_id=a.pronunciation_evidence_id
    JOIN evidence_snapshot sm ON sm.source_uri=m.source_uri AND sm.digest=m.evidence_digest
    JOIN evidence_snapshot sp ON sp.source_uri=p.source_uri AND sp.digest=p.evidence_digest
    JOIN phonetic_quality_audit qa ON qa.concept_id=c.concept_id
    WHERE a.approval_state='approved'
      AND m.concept_id=c.concept_id AND p.concept_id=c.concept_id
      AND m.aspect='meaning' AND p.aspect='pronunciation'
      AND m.decision='supports' AND p.decision='supports'
      AND m.reviewer_id<>p.reviewer_id
      AND ((m.reviewer_id=a.reviewer_primary AND p.reviewer_id=a.reviewer_secondary)
        OR (m.reviewer_id=a.reviewer_secondary AND p.reviewer_id=a.reviewer_primary))
      AND sm.verification_state='source_confirmed' AND sp.verification_state='source_confirmed'
      AND qa.state='tone_consistent'
      AND NOT EXISTS (SELECT 1 FROM lexical_verification_targets t
                      WHERE t.concept_id=c.concept_id AND t.state<>'supported');
   CREATE INDEX IF NOT EXISTS ix_review_targets_state ON lexical_verification_targets(state,aspect);
   CREATE INDEX IF NOT EXISTS ix_expression_locale_value ON expression(locale,value);
  ''')
  # The audit queue is explicitly informational: it never changes an approval state.
  for cid, in con.execute('SELECT concept_id FROM concept ORDER BY concept_id'):
   p=con.execute('SELECT COUNT(*) FROM pronunciation WHERE concept_id=?',(cid,)).fetchone()[0]
   if p<2:
    con.execute('INSERT INTO release_gate_issue(concept_id,rule,details) VALUES (?,?,?)',
      (cid,'missing_pronunciation_pair','Needs independently reviewed Pinyin and Zhuyin'))
  con.execute("INSERT OR REPLACE INTO metadata VALUES (?,?)",('schema',SCHEMA))
  con.execute("INSERT OR REPLACE INTO metadata VALUES (?,?)",('release_gate_v08','Views require evidence snapshots and independent reviewer agreement, with no outstanding targets'))
  assert con.execute('PRAGMA foreign_key_check').fetchall()==[]
  assert con.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
  con.commit()
  counts={t:con.execute('SELECT COUNT(*) FROM '+t).fetchone()[0] for t in ('concept','expression','pronunciation','lexical_approval','evidence_snapshot','cell_release_v08','release_gate_issue','lexical_verification_targets')}
  if counts['concept']!=585 or counts['expression']!=1755 or counts['cell_release_v08']!=0:raise ValueError('Baseline mismatch')
 finally:con.close()
 pending.replace(output)
 result={'schema':SCHEMA,'prior_schema':old['schema'],'counts':counts,'database_sha256':sha(output),'release_gate':'SOURCE_SNAPSHOT_REQUIRED','status':'BUILD_PASS / EXTERNAL_LEXICAL_REVIEW_PENDING'}
 (output.parent/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 return result
if __name__=='__main__':print(json.dumps(build(),ensure_ascii=False,indent=2))
