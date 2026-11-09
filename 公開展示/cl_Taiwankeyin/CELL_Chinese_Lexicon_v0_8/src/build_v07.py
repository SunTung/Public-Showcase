#!/usr/bin/env python3
"""CELL 0.7: phonetic QA and independent-reference triage; no automatic approvals."""
from __future__ import annotations
import hashlib, json, re, shutil, sqlite3, tempfile
from pathlib import Path
from build_v06 import build as build_v06
ROOT=Path(__file__).resolve().parents[1]
SCHEMA='cell.multilingual.concept.v0.7'
TONE_MARKS={'1':'','2':'ˊ','3':'ˇ','4':'ˋ','5':'˙'}
RE_PINYIN=re.compile(r"^[a-züv]+[1-5]$")

def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for chunk in iter(lambda:f.read(1048576),b''):h.update(chunk)
 return h.hexdigest()

def syllable_tones(pinyin,zhuyin):
 """Check tone count and placement, not exact syllabic sound equivalence."""
 p=pinyin.split(' '); z=zhuyin.split(' ')
 if len(p)!=len(z):return 'syllable_count_mismatch',f'{len(p)} pinyin / {len(z)} zhuyin'
 if not all(RE_PINYIN.fullmatch(s) for s in p):return 'invalid_pinyin_format','Pinyin syllable requires numbered tone'
 for n,(ps,zs) in enumerate(zip(p,z),1):
  tone=ps[-1];expected=TONE_MARKS[tone]
  marks=[x for x in zs if x in 'ˊˇˋ˙']
  if tone=='1':ok=not marks
  elif tone=='5':ok=marks==['˙'] and zs.startswith('˙') or marks==['˙'] and zs.endswith('˙')
  else:ok=marks==[expected]
  if not ok:return 'tone_mismatch',f'syllable {n}: pinyin tone={tone}, zhuyin={zs}'
  if not any('ㄅ'<=x<='ㄩ' for x in zs):return 'invalid_zhuyin_syllable',f'syllable {n}: {zs}'
 return 'tone_consistent','Tone sequence and syllable count match (not full phonetic validation)'

def build(output=ROOT/'build/cell_concepts.sqlite3'):
 output=Path(output);output.parent.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory() as tmp:
  prior_db=Path(tmp)/'v06.sqlite3';prev=build_v06(prior_db)
  pending=output.with_suffix('.pending');pending.unlink(missing_ok=True)
  shutil.copyfile(prior_db,pending)
 c=sqlite3.connect(pending)
 try:
  c.execute('PRAGMA foreign_keys=ON')
  c.executescript("""
    CREATE TABLE phonetic_quality_audit (
      concept_id TEXT PRIMARY KEY REFERENCES concept(concept_id),
      pinyin TEXT, zhuyin TEXT,
      state TEXT NOT NULL CHECK(state IN ('tone_consistent','tone_mismatch','syllable_count_mismatch', 'invalid_pinyin_format','invalid_zhuyin_syllable','missing_pair')),
      explanation TEXT NOT NULL,
      review_status TEXT NOT NULL DEFAULT 'automated_check_only');
    CREATE TABLE verification_sources (
      source_id TEXT PRIMARY KEY, authority TEXT NOT NULL, source_url TEXT NOT NULL,
      verification_scope TEXT NOT NULL, fetched_sha256 TEXT, fetched_at TEXT,
      status TEXT NOT NULL CHECK(status IN ('reference_registered','snapshot_verified')));
    CREATE TABLE lexical_verification_targets (
      concept_id TEXT NOT NULL REFERENCES concept(concept_id),
      aspect TEXT NOT NULL CHECK(aspect IN ('meaning','pronunciation','form')),
      source_id TEXT NOT NULL REFERENCES verification_sources(source_id),
      state TEXT NOT NULL CHECK(state IN ('awaiting_comparison','supported','contradicted','inconclusive')),
      note TEXT NOT NULL,
      PRIMARY KEY(concept_id,aspect,source_id));
    CREATE VIEW cell_release_v07 AS
      SELECT r.locale,r.value,r.concept_id,r.domain FROM cell_release_candidates r
      WHERE EXISTS (SELECT 1 FROM phonetic_quality_audit a
                    WHERE a.concept_id=r.concept_id AND a.state='tone_consistent')
      AND NOT EXISTS(SELECT 1 FROM lexical_verification_targets t
                    WHERE t.concept_id=r.concept_id AND t.state<>'supported');
  """)
  c.executemany('INSERT INTO verification_sources VALUES (?,?,?,?,?,?,?)',[
   ('unicode-unihan','Unicode Consortium','https://www.unicode.org/reports/tr38/',
    'Character-form variant relationships; not lexical sense or pronunciation proof',None,None,'reference_registered'),
   ('tw-moe-dictionary','Taiwan Ministry of Education','https://dict.revised.moe.edu.tw/',
    'Chinese word meaning and Taiwanese Mandarin Zhuyin lookup; manual verification pending',None,None,'reference_registered'),
  ])
  records=c.execute("""SELECT x.concept_id,
      MAX(CASE WHEN x.scheme='hanyu-pinyin' THEN x.value END),
      MAX(CASE WHEN x.scheme='zhuyin' THEN x.value END)
      FROM pronunciation x GROUP BY x.concept_id ORDER BY x.concept_id""").fetchall()
  counts={}
  for cid,p,z in records:
   state,why=syllable_tones(p,z) if p and z else ('missing_pair','Pronunciation pair incomplete')
   counts[state]=counts.get(state,0)+1
   c.execute('INSERT INTO phonetic_quality_audit VALUES (?,?,?,?,?,?)',(cid,p,z,state,why,'automated_check_only'))
   c.execute('INSERT INTO lexical_verification_targets VALUES (?,?,?,?,?)',
             (cid,'pronunciation','tw-moe-dictionary','awaiting_comparison','Manual comparison of both representations required'))
  # Prioritize lexically ambiguous words for evidence-based human review.
  ambiguous_ids=[r[0] for r in c.execute("""SELECT DISTINCT context_concept_id FROM form_graph
                                WHERE context_concept_id IS NOT NULL""")]
  for cid in ambiguous_ids:
   c.execute('INSERT OR IGNORE INTO lexical_verification_targets VALUES (?,?,?,?,?)',
     (cid,'form','unicode-unihan','awaiting_comparison','Check glyph candidate and word context independently'))
  c.execute('INSERT OR REPLACE INTO metadata VALUES (?,?)',('schema',SCHEMA))
  c.execute('INSERT OR REPLACE INTO metadata VALUES (?,?)',('v07_policy','Phonetic audit is formal/tonal only; evidence URLs are catalog references, not verified sources'))
  if c.execute('PRAGMA integrity_check').fetchone()[0]!='ok' or c.execute('PRAGMA foreign_key_check').fetchall():raise ValueError('DB integrity failure')
  c.commit()
  totals={name:c.execute('SELECT COUNT(*) FROM '+name).fetchone()[0] for name in
    ('concept','expression','pronunciation','lexical_review_queue','lexical_approval','cell_release_v07','phonetic_quality_audit','lexical_verification_targets')}
 finally:c.close()
 pending.replace(output)
 manifest={'schema':SCHEMA,'previous_concepts':prev['counts']['concept'],'counts':totals,
   'tone_audit':counts,'reference_status':'two source registries, no fetched snapshots, no human approvals',
   'database_sha256':sha(output),'status':'BUILD_PASS / FORMAL_PHONETIC_AUDIT / EXTERNAL_REVIEW_PENDING'}
 (output.parent/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 return manifest
if __name__=='__main__':print(json.dumps(build(),ensure_ascii=False,indent=2))
