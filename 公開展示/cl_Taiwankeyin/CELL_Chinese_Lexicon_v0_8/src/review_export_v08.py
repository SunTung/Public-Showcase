#!/usr/bin/env python3
"""Export outstanding cross-check targets without claiming verification."""
import argparse,csv,sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def export(db,dest):
 with sqlite3.connect('file:'+str(Path(db).resolve())+'?mode=ro',uri=True) as c:
  rows=c.execute('''SELECT t.concept_id,t.aspect,s.authority,s.source_url,
   t.state,t.note,
   MAX(CASE WHEN e.locale='zh-Hant-TW' THEN e.value END) AS traditional,
   MAX(CASE WHEN e.locale='zh-Hans-CN' THEN e.value END) AS simplified,
   MAX(CASE WHEN e.locale='en' THEN e.value END) AS english
   FROM lexical_verification_targets t JOIN verification_sources s USING(source_id)
   JOIN expression e ON e.concept_id=t.concept_id
   GROUP BY t.concept_id,t.aspect,s.authority,s.source_url,t.state,t.note
   ORDER BY t.concept_id,t.aspect''').fetchall()
 target=Path(dest);target.parent.mkdir(parents=True,exist_ok=True)
 with target.open('w',encoding='utf-8-sig',newline='') as f:
  out=csv.writer(f,delimiter='\t');out.writerow(['concept_id','aspect','authority','source_url','state','note','traditional','simplified','english']);out.writerows(rows)
 return len(rows)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--database',type=Path,default=ROOT/'build/cell_concepts.sqlite3');p.add_argument('--output',type=Path,default=ROOT/'build/review_targets.tsv');a=p.parse_args();print(export(a.database,a.output))
