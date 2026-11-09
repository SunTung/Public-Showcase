#!/usr/bin/env python3
"""CELL concept-first multilingual dictionary v0.2; no legacy lexicon import.

Two CELL-authored seed batches, independent dictionary schema and query APIs.
New rows have deliberately NULL pronunciations until separately verified.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,sqlite3,unicodedata,re
from pathlib import Path

SCHEMA='cell.multilingual.concept.v0.2'
ROOT=Path(__file__).resolve().parents[1]
LOCALES=('zh-Hant-TW','zh-Hans-CN','en')
AMBIGUOUS=[('发','發','development / issuing','CELL-C0022'),('发','髮','hair','CELL-C0023'),('后','後','after / behind','CELL-C0025'),('后','后','queen','CELL-C0026'),('干','乾','dry','CELL-C0029'),('干','幹','cadre','CELL-C0030'),('里','裡','inside','CELL-C0027'),('里','里','unit in place name','CELL-C0028')]

def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()

def read_tsv(path):
    with Path(path).open(encoding='utf-8-sig',newline='') as f:
        return list(csv.DictReader(f,delimiter='\t'))

def validate_text(s):
    if not isinstance(s,str) or not s or s.strip()!=s or '\n' in s or '\t' in s:
        raise ValueError('empty/dirty expression '+repr(s))
    if unicodedata.normalize('NFC',s)!=s: raise ValueError('non-NFC '+s)
    return s

def build(legacy=ROOT/'data/legacy_cell_seed_90.tsv', additions=ROOT/'data/cell_seed_additions.tsv', output=ROOT/'build/cell_concepts.sqlite3'):
    legacy,additions,output=map(Path,(legacy,additions,output))
    output.parent.mkdir(parents=True,exist_ok=True)
    older=read_tsv(legacy); newer=read_tsv(additions)
    if len(older)!=90:raise ValueError('Original CELL seed must contain 90 rows')
    if len(newer)<100:raise ValueError('Missing new CELL concepts')
    records=[]
    for r in older:
        for k in ('concept_id','traditional','simplified','english','pinyin','zhuyin','domain'):validate_text(r[k])
        if r['status']!='curated_seed':raise ValueError('Original seed status changed')
        records.append((r['concept_id'],r['domain'],r['traditional'],r['simplified'],r['english'],r['pinyin'],r['zhuyin'],'seed_review_pending','undetermined','CELL-seed-v0.1'))
    for n,r in enumerate(newer,91):
        for k in ('domain','traditional','simplified','english','pos'):validate_text(r[k])
        if r['pos'] not in ('noun','verb','adjective','adverb','other'):raise ValueError('Invalid POS')
        records.append((f'CELL-C{n:04d}',r['domain'],r['traditional'],r['simplified'],r['english'],None,None,'draft_review',r['pos'],'CELL-original-v0.2'))
    ids=[r[0] for r in records]
    if len(set(ids))!=len(ids):raise ValueError('Duplicate concept ID')
    triplets=[(x[2],x[3],x[4]) for x in records]
    if len(set(triplets))!=len(triplets):raise ValueError('Identical three-language entries need one concept ID')
    pending=output.with_suffix('.pending')
    pending.unlink(missing_ok=True)
    conn=sqlite3.connect(pending)
    try:
        conn.execute('PRAGMA foreign_keys=ON')
        conn.executescript('''PRAGMA journal_mode=DELETE;
            CREATE TABLE metadata(key TEXT PRIMARY KEY,value TEXT NOT NULL);
            CREATE TABLE concept(
              concept_id TEXT PRIMARY KEY,domain TEXT NOT NULL,
              pos TEXT NOT NULL,status TEXT NOT NULL,
              provenance TEXT NOT NULL, definition TEXT,
              created_batch TEXT NOT NULL);
            CREATE TABLE expression(
              concept_id TEXT NOT NULL REFERENCES concept(concept_id),
              locale TEXT NOT NULL CHECK(locale IN('zh-Hant-TW','zh-Hans-CN','en')),
              value TEXT NOT NULL, preferred INTEGER NOT NULL DEFAULT 1,
              review_status TEXT NOT NULL,
              PRIMARY KEY(concept_id,locale,value));
            CREATE TABLE pronunciation(
              concept_id TEXT NOT NULL REFERENCES concept(concept_id),
              scheme TEXT NOT NULL CHECK(scheme IN('zhuyin','hanyu-pinyin')),
              value TEXT NOT NULL,review_status TEXT NOT NULL,
              PRIMARY KEY(concept_id,scheme,value));
            CREATE TABLE form_ambiguity(
              simplified TEXT NOT NULL,traditional TEXT NOT NULL,
              sense_hint TEXT NOT NULL,example_concept_id TEXT REFERENCES concept(concept_id),
              PRIMARY KEY(simplified,traditional,sense_hint));
            CREATE TABLE relation(
              source_id TEXT NOT NULL REFERENCES concept(concept_id),
              relation_type TEXT NOT NULL,
              target_id TEXT NOT NULL REFERENCES concept(concept_id),
              review_status TEXT NOT NULL,
              PRIMARY KEY(source_id,relation_type,target_id));
            CREATE TABLE review_event(
              event_id INTEGER PRIMARY KEY,concept_id TEXT NOT NULL REFERENCES concept(concept_id),
              aspect TEXT NOT NULL,decision TEXT NOT NULL,evidence_ref TEXT,
              note TEXT NOT NULL,created_at TEXT NOT NULL);
            CREATE INDEX ix_expression_locale ON expression(locale,value);
            CREATE INDEX ix_expression_value ON expression(value);
            CREATE INDEX ix_pronunciation ON pronunciation(scheme,value);
            CREATE INDEX ix_concept_domain ON concept(domain,status);
        ''')
        conn.executemany('INSERT INTO concept(concept_id,domain,pos,status,provenance,created_batch) VALUES(?,?,?,?,?,?)',
          [(r[0],r[1],r[8],r[7],r[9],r[9]) for r in records])
        ex=[];pron=[]
        for r in records:
            for locale,value in zip(LOCALES,r[2:5]):ex.append((r[0],locale,value,1,r[7]))
            for scheme,value in [('hanyu-pinyin',r[5]),('zhuyin',r[6])]:
                if value:pron.append((r[0],scheme,value,'seed_review_pending'))
        conn.executemany('INSERT INTO expression VALUES(?,?,?,?,?)',ex)
        conn.executemany('INSERT INTO pronunciation VALUES(?,?,?,?)',pron)
        conn.executemany('INSERT INTO form_ambiguity VALUES(?,?,?,?)',AMBIGUOUS)
        # Relationship links are explicit, not guessed by superficial string resemblance.
        # Explicit semantic links require verified senses and remain empty at this stage.
        metadata={
          'schema':SCHEMA,'project':'CELL multilingual concept lexicon',
          'coverage':'seed and draft only, NOT general dictionary coverage',
          'data_policy':'CELL composed entries; legacy external source not imported',
          'review':'all terms require independent cross-source lexical and phonetic verification',
          'legacy_seed_sha256':digest(legacy),'addition_seed_sha256':digest(additions),
          'new_pronunciation_status':'not populated until separately checked',
        }
        conn.executemany('INSERT INTO metadata VALUES(?,?)',metadata.items())
        result={
          'schema':SCHEMA,'legacy_concepts':len(older),'new_concepts':len(newer),
          'concepts':len(records),'expressions':len(ex),'pronunciations':len(pron),
          'form_ambiguities':len(AMBIGUOUS),'new_terms_without_pronunciation':len(newer),
          'status':'BUILD_PASS; lexical/manual cross-review incomplete'
        }
        for table in ('concept','expression','pronunciation','form_ambiguity','relation','review_event'):
            result[table+'_rows']=conn.execute('SELECT COUNT(*) FROM '+table).fetchone()[0]
        if conn.execute('PRAGMA integrity_check').fetchone()[0]!='ok' or conn.execute('PRAGMA foreign_key_check').fetchall():raise ValueError('DB integrity failure')
        conn.commit()
    finally: conn.close()
    pending.replace(output)
    result.update(database_bytes=output.stat().st_size,database_sha256=digest(output),legacy_sha256=digest(legacy),additions_sha256=digest(additions))
    (output.parent/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    return result

def lookup(db,locale,value):
    if locale not in LOCALES:raise ValueError('Unsupported locale')
    validate_text(value)
    with sqlite3.connect(db) as c:
        c.row_factory=sqlite3.Row
        rs=c.execute('''SELECT DISTINCT x.concept_id,c.domain,c.pos,c.status,
          (SELECT value FROM expression WHERE concept_id=x.concept_id AND locale='zh-Hant-TW' ORDER BY preferred DESC LIMIT 1) AS traditional,
          (SELECT value FROM expression WHERE concept_id=x.concept_id AND locale='zh-Hans-CN' ORDER BY preferred DESC LIMIT 1) AS simplified,
          (SELECT value FROM expression WHERE concept_id=x.concept_id AND locale='en' ORDER BY preferred DESC LIMIT 1) AS english
          FROM expression x JOIN concept c ON x.concept_id=c.concept_id
          WHERE x.locale=? AND x.value=? COLLATE NOCASE
          ORDER BY x.concept_id''',(locale,value)).fetchall()
        return [dict(r) for r in rs]

def search(db,text,limit=20):
    validate_text(text)
    limit=max(1,min(limit,100))
    with sqlite3.connect(db) as c:
        rs=c.execute('''SELECT DISTINCT c.concept_id,c.domain,c.status,e.locale,e.value
           FROM expression e JOIN concept c ON c.concept_id=e.concept_id
           WHERE instr(lower(e.value),lower(?))>0 ORDER BY e.value,c.concept_id LIMIT ?''',(text,limit)).fetchall()
        return [dict(zip(('concept_id','domain','status','locale','value'),row)) for row in rs]

def export(db,destination):
    with sqlite3.connect(db) as c:
        c.row_factory=sqlite3.Row
        records=[dict(x) for x in c.execute('''SELECT c.concept_id,c.domain,c.pos,c.status,
          max(CASE WHEN e.locale='zh-Hant-TW' THEN e.value END) AS traditional,
          max(CASE WHEN e.locale='zh-Hans-CN' THEN e.value END) AS simplified,
          max(CASE WHEN e.locale='en' THEN e.value END) AS english
          FROM concept c JOIN expression e USING(concept_id)
          GROUP BY c.concept_id ORDER BY c.concept_id''')]
    Path(destination).write_text(json.dumps({'schema':SCHEMA,'records':records},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    return len(records)

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--legacy',type=Path,default=ROOT/'data/legacy_cell_seed_90.tsv')
    ap.add_argument('--additions',type=Path,default=ROOT/'data/cell_seed_additions.tsv')
    ap.add_argument('--output',type=Path,default=ROOT/'build/cell_concepts.sqlite3')
    args=ap.parse_args()
    print(json.dumps(build(args.legacy,args.additions,args.output),ensure_ascii=False,indent=2))
