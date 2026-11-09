#!/usr/bin/env python3
"""CELL v0.4 read-only JSON queries for three-language expressions and glyph candidates."""
import argparse,json
from pathlib import Path
from build_v03 import lookup,export
from build_v04 import form_candidates,review_queue
ROOT=Path(__file__).resolve().parents[1]
def main(argv=None):
 p=argparse.ArgumentParser()
 p.add_argument('--database',type=Path,default=ROOT/'build/cell_concepts.sqlite3')
 g=p.add_mutually_exclusive_group(required=True)
 g.add_argument('--word');g.add_argument('--form');g.add_argument('--review',choices=['meaning','pronunciation','glyph_mapping']);g.add_argument('--export',type=Path)
 p.add_argument('--locale',choices=['en','zh-Hans-CN','zh-Hant-TW'],default='zh-Hant-TW')
 a=p.parse_args(argv)
 if not a.database.is_file():p.error('first build the v0.4 SQLite database')
 if a.word is not None:result={'kind':'concept','results':lookup(a.database,a.locale,a.word)}
 elif a.form is not None:result={'kind':'glyph_candidates','results':[{'target_form':t,'context_example':e,'status':s} for t,e,s in form_candidates(a.database,a.locale,a.form)]}
 elif a.review is not None:result={'kind':'review_queue','results':[{'concept_id':i,'aspect':x,'priority':p,'reason':r,'state':s} for i,x,p,r,s in review_queue(a.database,a.review)]}
 else:result={'kind':'export','records':export(a.database,a.export),'path':str(a.export)}
 print(json.dumps(result,ensure_ascii=False,indent=2));return result
if __name__=='__main__':main()
