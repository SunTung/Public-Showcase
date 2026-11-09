#!/usr/bin/env python3
"""CELL v0.3: deterministic incremental concept database; no Chewing/OpenCC bulk import.

The prior v0.2 source is invoked unmodified, then extended under a SQLite transaction.
All new terms are draft and have NO fabricated pronunciation.
"""
from __future__ import annotations
import csv,hashlib,importlib.util,json,sqlite3,shutil,tempfile,unicodedata
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'src/build_dictionary.py'
SCHEMA='cell.multilingual.concept.v0.3'


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for c in iter(lambda:f.read(1024*1024),b''):h.update(c)
    return h.hexdigest()


def import_v02():
    spec=importlib.util.spec_from_file_location('cell_legacy_builder_v02',SRC)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def read_batch(path):
    with Path(path).open(encoding='utf-8',newline='') as f:
        records=list(csv.DictReader(f,delimiter='\t'))
    assert records, 'Missing new batch'
    required={'domain','traditional','simplified','english','pos'}
    if not required.issubset(records[0]):raise ValueError('Missing columns')
    for r in records:
        for k in required:
            s=r[k]
            if not s or s!=s.strip() or '\n' in s or unicodedata.normalize('NFC',s)!=s:
                raise ValueError('Non-normalized field '+k+': '+repr(s))
        if r['pos'] not in {'noun','verb','adjective','adverb','other'}:raise ValueError('Unsupported POS')
    if len({(r['traditional'],r['simplified'],r['english']) for r in records})!=len(records):
        raise ValueError('Same semantic triple repeated in new batch')
    return records


def build(output=ROOT/'build/cell_concepts.sqlite3',batch=ROOT/'data/cell_seed_batch03.tsv'):
    output=Path(output);output.parent.mkdir(parents=True,exist_ok=True)
    v02=import_v02()
    rows=read_batch(batch)
    with tempfile.TemporaryDirectory() as d:
        previous=Path(d)/'prior.sqlite3'
        meta02=v02.build(output=previous)
        pending=output.with_suffix('.pending')
        pending.unlink(missing_ok=True)
        shutil.copyfile(previous,pending)
    conn=sqlite3.connect(pending)
    try:
        conn.execute('PRAGMA foreign_keys=ON')
        conn.execute('BEGIN IMMEDIATE')
        existing={tuple(x) for x in conn.execute('''SELECT
            MAX(CASE WHEN locale='zh-Hant-TW' THEN value END),
            MAX(CASE WHEN locale='zh-Hans-CN' THEN value END),
            MAX(CASE WHEN locale='en' THEN value END)
            FROM expression GROUP BY concept_id''')}
        ids=[int(row[0][6:]) for row in conn.execute('SELECT concept_id FROM concept').fetchall() if row[0].startswith('CELL-C')]
        # `x` is a one-column SQLite row; keep IDs monotonically increasing.
        next_id=max(ids)+1
        for r in rows:
            triple=(r['traditional'],r['simplified'],r['english'])
            if triple in existing:raise ValueError('Duplicate existing triple '+repr(triple))
            existing.add(triple)
            cid=f'CELL-C{next_id:04d}';next_id+=1
            conn.execute('''INSERT INTO concept(concept_id,domain,pos,status,provenance,definition,created_batch)
                            VALUES(?,?,?,?,?,?,?)''',
                         (cid,r['domain'],r['pos'],'draft_review','CELL-composed-batch03',None,'CELL-v0.3'))
            conn.executemany('''INSERT INTO expression(concept_id,locale,value,preferred,review_status)
                                VALUES(?,?,?,?,?)''',[(cid,k,v,1,'draft_review') for k,v in zip(v02.LOCALES,triple)])
        conn.executescript('''CREATE TABLE IF NOT EXISTS form_candidate(
                 candidate_id INTEGER PRIMARY KEY,
                 source_form TEXT NOT NULL,target_form TEXT NOT NULL,
                 source_locale TEXT NOT NULL,target_locale TEXT NOT NULL,
                 ambiguity TEXT NOT NULL CHECK(ambiguity IN ('unambiguous_example','context_needed')),
                 example_concept_id TEXT REFERENCES concept(concept_id),
                 review_status TEXT NOT NULL,
                 UNIQUE(source_form,target_form,source_locale,target_locale,example_concept_id)
             );
             CREATE INDEX IF NOT EXISTS ix_form_candidate_source ON form_candidate(source_locale,source_form);
             CREATE TABLE IF NOT EXISTS quality_issue(
                 issue_id INTEGER PRIMARY KEY,
                 concept_id TEXT REFERENCES concept(concept_id),
                 issue_type TEXT NOT NULL,
                 detail TEXT NOT NULL,
                 severity TEXT NOT NULL CHECK(severity IN ('info','review','block')),
                 UNIQUE(concept_id,issue_type,detail)
             );''')
        # Character-level variants are examples, NOT automatic whole-text conversion rules.
        for simple,traditional,hint,example in conn.execute('SELECT simplified,traditional,sense_hint,example_concept_id FROM form_ambiguity'):
            conn.execute('''INSERT INTO form_candidate(source_form,target_form,source_locale,target_locale,ambiguity,example_concept_id,review_status)
                       VALUES(?,?,?,?,?,?,?)''',(simple,traditional,'zh-Hans-CN','zh-Hant-TW','context_needed',example,'example_requires_review'))
        # Critically, we flag suspicious 1-to-many mapping rather than force a translation.
        conflicts=conn.execute('''SELECT zh.value,COUNT(DISTINCT zh.concept_id) FROM expression zh
                 WHERE zh.locale='zh-Hans-CN' GROUP BY zh.value HAVING COUNT(DISTINCT zh.concept_id)>1''').fetchall()
        for value,n in conflicts:
            matches=conn.execute("SELECT DISTINCT concept_id FROM expression WHERE locale='zh-Hans-CN' AND value=?",(value,)).fetchall()
            for (cid,) in matches:
                conn.execute('''INSERT INTO quality_issue(concept_id,issue_type,detail,severity) VALUES(?,?,?,?)''',
                             (cid,'shared_simplified_form',f'{value}: {n} separate concepts; must inspect sense','review'))
        conn.execute("UPDATE metadata SET value=? WHERE key='schema'",(SCHEMA,))
        conn.execute("INSERT OR REPLACE INTO metadata VALUES(?,?)",('batch03_sha256',sha(batch)))
        conn.execute("INSERT OR REPLACE INTO metadata VALUES(?,?)",('quality_policy','No automatic sense merging; manual approval required'))
        conn.execute("INSERT OR REPLACE INTO metadata VALUES(?,?)",('v02_concepts',str(meta02['concepts'])))
        if conn.execute('PRAGMA foreign_key_check').fetchall():raise AssertionError('Foreign key violation')
        if conn.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise AssertionError('SQLite integrity failure')
        conn.commit()
        counts={n:conn.execute(f'SELECT COUNT(*) FROM {n}').fetchone()[0]
                for n in ['concept','expression','pronunciation','form_ambiguity','form_candidate','quality_issue','relation','review_event']}
        stage=conn.execute('SELECT status,COUNT(*) FROM concept GROUP BY status ORDER BY status').fetchall()
    except:
        conn.rollback();conn.close();pending.unlink(missing_ok=True);raise
    else:conn.close()
    pending.replace(output)
    report=dict(schema=SCHEMA,previous_concepts=meta02['concepts'],new_concepts=len(rows),
                counts=counts,review_status=dict(stage),db_sha256=sha(output),db_bytes=output.stat().st_size,
                batch03_sha256=sha(batch),status='BUILD_VERIFIED; semantic/phonetic review incomplete')
    (output.parent/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return report


def lookup(db,locale,form):
    if locale not in ('zh-Hant-TW','zh-Hans-CN','en'):raise ValueError('Unsupported locale')
    with sqlite3.connect(db) as con:
        con.row_factory=sqlite3.Row
        return [dict(r) for r in con.execute('''SELECT c.concept_id,c.domain,c.pos,c.status,
                   MAX(CASE WHEN e.locale='zh-Hant-TW' THEN e.value END) traditional,
                   MAX(CASE WHEN e.locale='zh-Hans-CN' THEN e.value END) simplified,
                   MAX(CASE WHEN e.locale='en' THEN e.value END) english
                   FROM expression match JOIN concept c ON match.concept_id=c.concept_id
                   JOIN expression e ON e.concept_id=c.concept_id
                   WHERE match.locale=? AND match.value=? COLLATE NOCASE
                   GROUP BY c.concept_id ORDER BY c.concept_id''',(locale,form))]


def ambiguous_forms(db,simplified):
    with sqlite3.connect(db) as c:
        return c.execute('''SELECT DISTINCT target_form,ambiguity,review_status
                   FROM form_candidate WHERE source_locale='zh-Hans-CN' AND source_form=?
                   ORDER BY target_form''',(simplified,)).fetchall()


def export(db,path):
    with sqlite3.connect(db) as c:
        c.row_factory=sqlite3.Row
        rows=[dict(r) for r in c.execute('''SELECT c.concept_id,c.domain,c.pos,c.status,
                  max(CASE WHEN e.locale='zh-Hant-TW' THEN e.value END) traditional,
                  max(CASE WHEN e.locale='zh-Hans-CN' THEN e.value END) simplified,
                  max(CASE WHEN e.locale='en' THEN e.value END) english
                  FROM concept c JOIN expression e USING(concept_id)
                  GROUP BY c.concept_id ORDER BY c.concept_id''')]
    Path(path).write_text(json.dumps({'schema':SCHEMA,'concept_count':len(rows),'records':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return len(rows)

if __name__=='__main__':
    print(json.dumps(build(),ensure_ascii=False,indent=2))
    export(ROOT/'build/cell_concepts.sqlite3',ROOT/'build/cell_concepts.json')
