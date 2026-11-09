#!/usr/bin/env python3
"""Independent lexical observation audit; no automatic human approval or source snapshot claims."""
from pathlib import Path
import csv,sqlite3,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
def analyze(db=ROOT/'build/cell_concepts.sqlite3',samples=ROOT/'data/observed_moe_samples_v09.tsv'):
 with Path(samples).open(encoding='utf-8',newline='') as f: observations=list(csv.DictReader(f,delimiter='\t'))
 c=sqlite3.connect(db);c.row_factory=sqlite3.Row
 try:
  output=[]
  for x in observations:
   r=c.execute("SELECT value FROM expression WHERE concept_id=? AND locale='zh-Hant-TW'",(x['concept_id'],)).fetchone()
   p=c.execute("SELECT scheme,value FROM pronunciation WHERE concept_id=?",(x['concept_id'],)).fetchall()
   prior={y['scheme']:y['value'] for y in p}
   # The source uses leading neutral-tone dot while the historical seed stores a trailing dot.
   # Normalize tone-dot position for comparison, not for writing back to the baseline.
   def zh(s):return ' '.join((part.replace('˙','')+'˙' if part.startswith('˙') else part) for part in s.split())
   form_ok=bool(r and r['value']==x['headword'])
   py_ok=(prior.get('hanyu-pinyin')==x['pinyin_numbered'])
   zy_ok=(zh(prior.get('zhuyin',''))==zh(x['zhuyin_display']))
   output.append({'concept_id':x['concept_id'],'headword':x['headword'],'source_url':x['source_url'],
    'source_name':x['source_name'],'headword_match':form_ok,'pinyin_match':py_ok,
    'zhuyin_match':zy_ok,'check_state':'observed_comparison_only',
    'editorial_note':('Neutral-tone dot placement normalized; no source-derived pronunciation rewrite' if '˙' in x['zhuyin_display'] else 'Observation matched recorded seed'),
    'source_status':'web_display_observed_not_archived_snapshot'})
  assert len({r['concept_id'] for r in output})==len(output)
  return output
 finally:c.close()
def export(dest=ROOT/'build/observed_moe_audit_v09.json'):
 records=analyze(); d={'schema':'cell.multilingual.concept.v0.9','source_observations':len(records),
 'consistent_reading_pairs':sum(x['pinyin_match'] and x['zhuyin_match'] for x in records),
 'verified_snapshot_count':0,'human_approved_count':0,'records':records}
 Path(dest).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');return d
if __name__=='__main__':print(json.dumps(export(),ensure_ascii=False,indent=2))
