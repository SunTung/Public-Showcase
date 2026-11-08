#!/usr/bin/env python3
"""Build an independent CELL concept lexicon from CELL-curated TSV rows.
Legacy input-method dictionaries are NOT imported. No external runtime deps.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,sqlite3,unicodedata
from pathlib import Path

SCHEMA='cell.multilingual.concept.v0.1'
AMBIGUOUS=[
 ('发','發','to develop, emit','CELL-C0022'),
 ('发','髮','hair','CELL-C0023'),
 ('后','後','after, behind','CELL-C0025'),
 ('后','后','queen','CELL-C0026'),
 ('干','乾','dry','CELL-C0029'),
 ('干','幹','cadre','CELL-C0030'),
 ('里','裡','inside','CELL-C0027'),
 ('里','里','unit in place names',''),
]

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def build(tsv,output):
    tsv=Path(tsv);output=Path(output);output.parent.mkdir(parents=True,exist_ok=True)
    with tsv.open(encoding='utf-8',newline='') as stream:
        rows=list(csv.DictReader(stream,delimiter='\t'))
    assert len(rows)>=80
    ids=set();valid=[]
    for row in rows:
        cid=row['concept_id'];assert cid.startswith('CELL-C') and cid not in ids
        ids.add(cid)
        for key in ['traditional','simplified','english','pinyin','zhuyin','domain']:
            assert row[key].strip(),(cid,key)
            assert unicodedata.normalize('NFC',row[key])==row[key],cid
        assert row['status']=='curated_seed'
        valid.append(row)
    pending=output.with_suffix('.pending');pending.unlink(missing_ok=True)
    db=sqlite3.connect(pending)
    try:
        db.executescript('''PRAGMA journal_mode=DELETE;
        CREATE TABLE metadata(key TEXT PRIMARY KEY, value TEXT NOT NULL);
        CREATE TABLE concept(
          concept_id TEXT PRIMARY KEY, domain TEXT NOT NULL, status TEXT NOT NULL);
        CREATE TABLE expression(
          concept_id TEXT NOT NULL REFERENCES concept(concept_id),
          locale TEXT NOT NULL CHECK(locale IN ('zh-Hant-TW','zh-Hans-CN','en')),
          value TEXT NOT NULL, preferred INTEGER NOT NULL DEFAULT 1,
          PRIMARY KEY(concept_id,locale,value));
        CREATE TABLE pronunciation(
          concept_id TEXT NOT NULL REFERENCES concept(concept_id),
          scheme TEXT NOT NULL CHECK(scheme IN ('hanyu-pinyin','zhuyin')),
          value TEXT NOT NULL, PRIMARY KEY(concept_id,scheme,value));
        CREATE TABLE ambiguous_character(
          simplified TEXT NOT NULL, traditional TEXT NOT NULL,
          sense_hint TEXT NOT NULL, example_concept_id TEXT,
          PRIMARY KEY(simplified,traditional,sense_hint));
        CREATE INDEX ix_expression_lookup ON expression(locale,value);
        CREATE INDEX ix_pron_lookup ON pronunciation(scheme,value);
        ''')
        db.executemany('INSERT INTO concept VALUES(?,?,?)',[(r['concept_id'],r['domain'],r['status']) for r in valid])
        expr=[];pron=[]
        for r in valid:
            for loc,k in [('zh-Hant-TW','traditional'),('zh-Hans-CN','simplified'),('en','english')]:expr.append((r['concept_id'],loc,r[k],1))
            for scheme,k in [('hanyu-pinyin','pinyin'),('zhuyin','zhuyin')]:pron.append((r['concept_id'],scheme,r[k]))
        db.executemany('INSERT INTO expression VALUES(?,?,?,?)',expr)
        db.executemany('INSERT INTO pronunciation VALUES(?,?,?)',pron)
        db.executemany('INSERT INTO ambiguous_character VALUES(?,?,?,?)',AMBIGUOUS)
        db.executemany('INSERT INTO metadata VALUES(?,?)',[
          ('schema',SCHEMA),('data_origin','CELL curated concept mapping'),
          ('source_copy','false'),('seed_sha256',sha(tsv)),
          ('coverage','limited curated seed; not a complete dictionary'),
          ('review_stage','bootstrap; phonetic and semantic cross-review pending')])
        db.commit();assert db.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
    finally:db.close()
    pending.replace(output)
    result={'schema':SCHEMA,'concepts':len(valid),'expressions':len(expr),
            'pronunciations':len(pron),'ambiguous_cases':len(AMBIGUOUS),
            'seed_sha256':sha(tsv),'database_sha256':sha(output),
            'database_bytes':output.stat().st_size,
            'review_stage':'bootstrap; review pending'}
    (output.parent/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return result

def lookup(db,locale,value):
    with sqlite3.connect(db) as c:
        return c.execute('''SELECT e.concept_id,
            (SELECT value FROM expression WHERE concept_id=e.concept_id AND locale='zh-Hant-TW' LIMIT 1),
            (SELECT value FROM expression WHERE concept_id=e.concept_id AND locale='zh-Hans-CN' LIMIT 1),
            (SELECT value FROM expression WHERE concept_id=e.concept_id AND locale='en' LIMIT 1)
            FROM expression e WHERE e.locale=? AND lower(e.value)=lower(?)
            ORDER BY e.concept_id''',(locale,value)).fetchall()

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--output',required=True)
 args=p.parse_args();print(json.dumps(build(args.input,args.output),ensure_ascii=False,indent=2))
