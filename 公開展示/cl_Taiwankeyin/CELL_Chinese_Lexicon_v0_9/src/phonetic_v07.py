#!/usr/bin/env python3
"""Inspect pronunciation quality without changing source readings."""
from __future__ import annotations
import argparse,json,sqlite3
from pathlib import Path
from build_v07 import ROOT

def phonetic_report(db,states=None,limit=100):
 allowed={'tone_consistent','tone_mismatch','syllable_count_mismatch','invalid_pinyin_format','invalid_zhuyin_syllable','missing_pair'}
 states=states or sorted(allowed)
 if not set(states)<=allowed:raise ValueError('Unsupported audit state')
 with sqlite3.connect(f'file:{Path(db).resolve()}?mode=ro',uri=True) as c:
  return [{'concept_id':cid,'pinyin':p,'zhuyin':z,'state':s,'note':n} for cid,p,z,s,n in c.execute(
   f"SELECT concept_id,pinyin,zhuyin,state,explanation FROM phonetic_quality_audit WHERE state IN ({','.join('?' for _ in states)}) ORDER BY concept_id LIMIT ?",(*states,max(1,min(int(limit),1000))))]

def review_targets(db,limit=100):
 with sqlite3.connect(f'file:{Path(db).resolve()}?mode=ro',uri=True) as c:
  return [{'concept_id':cid,'aspect':aspect,'source_id':sid,'state':state} for cid,aspect,sid,state in c.execute(
   'SELECT concept_id,aspect,source_id,state FROM lexical_verification_targets ORDER BY concept_id,aspect LIMIT ?', (max(1,min(int(limit),1000)),))]
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--db',type=Path,default=ROOT/'build/cell_concepts.sqlite3')
 p.add_argument('--state',choices=['tone_consistent','tone_mismatch','syllable_count_mismatch','invalid_pinyin_format','invalid_zhuyin_syllable','missing_pair']);p.add_argument('--targets',action='store_true');p.add_argument('--limit',type=int,default=30)
 args=p.parse_args();print(json.dumps(review_targets(args.db,args.limit) if args.targets else phonetic_report(args.db,[args.state] if args.state else None,args.limit),ensure_ascii=False,indent=2))
