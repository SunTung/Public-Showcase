#!/usr/bin/env python3
"""Compare observed dictionary readings against the baseline, WITHOUT approvals.

Observed web-result excerpts aren't authenticated source snapshots. Store only
short independently authored metadata; flag differences for subsequent review.
"""
from __future__ import annotations
import csv,hashlib,json,sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def compare(db, tsv=ROOT/'data/moe_first_comparisons_v10.tsv'):
    with Path(tsv).open(encoding='utf-8',newline='') as f:
        observations=list(csv.DictReader(f,delimiter='\t'))
    results=[]
    with sqlite3.connect(Path(db).resolve().as_uri()+'?mode=ro',uri=True) as c:
        for row in observations:
            cid=row['concept_id']
            matched=c.execute("SELECT value FROM expression WHERE concept_id=? AND locale='zh-Hant-TW'",(cid,)).fetchall()
            if not matched or row['headword'] not in [x[0] for x in matched]:
                raise ValueError('Source word does not match concept '+cid)
            baseline=dict(c.execute('SELECT scheme,value FROM pronunciation WHERE concept_id=?',(cid,)).fetchall())
            if not {'zhuyin','hanyu-pinyin'} <= baseline.keys():
                state='MISSING_BASELINE_READING'
            else:
                state='MATCH' if (baseline['zhuyin']==row['zhuyin'] and baseline['hanyu-pinyin']==row['pinyin']) else 'CONFLICT'
            if not row['source_url'].startswith('https://dict.') or row['retrieval']!='web_result_observation':
                raise ValueError('Unsupported source provenance')
            results.append({'concept_id':cid,'headword':row['headword'],'source':row['source'],
               'source_url':row['source_url'],'baseline_pinyin':baseline.get('hanyu-pinyin'),
               'baseline_zhuyin':baseline.get('zhuyin'),'observed_pinyin':row['pinyin'],
               'observed_zhuyin':row['zhuyin'],'status':state,
               'verification_state':'OBSERVED_NOT_SOURCE_SNAPSHOT_NOT_APPROVED'})
    return results

def export(db,path,tsv=ROOT/'data/moe_first_comparisons_v10.tsv'):
    observations=compare(db,tsv)
    result={'schema':'cell.multilingual.concept.v0.10','records':observations,
      'conflicts':sum(x['status']=='CONFLICT' for x in observations),
      'source_snapshots_verified':0,'lexical_approvals':0}
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return result

if __name__=='__main__':
    print(json.dumps(export(ROOT/'build/cell_concepts.sqlite3',ROOT/'build/comparison_report_v10.json'),ensure_ascii=False,indent=2))
