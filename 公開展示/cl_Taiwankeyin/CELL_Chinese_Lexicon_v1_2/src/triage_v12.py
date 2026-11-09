"""CELL v1.2 read-only review triage, supports v1.1 findings."""
import json,sys
from pathlib import Path
from collections import defaultdict,Counter
VALID={'CONFLICT','MATCH','MISSING_BASELINE_READING','EXACT_TEXT_MATCH','PRONUNCIATION_DIFFERENCE','MISSING_CELL_PRONUNCIATION','AMBIGUOUS_SOURCE','NOT_FOUND','MULTIPLE_SOURCE_ENTRIES','EXACT_ZHUYIN','DIFFERENT_ZHUYIN'}
def triage(rows):
 groups=defaultdict(list)
 for r in rows:
  cid=r.get('concept_id','')
  if not cid.startswith('CELL-C') or r.get('status') not in VALID:raise ValueError('Invalid concept/status')
  groups[cid].append(r)
 queue=[]
 for cid,records in sorted(groups.items()):
  states={r['status'] for r in records}
  if states&{'CONFLICT','PRONUNCIATION_DIFFERENCE','DIFFERENT_ZHUYIN'}:priority='P0_READING_CONFLICT'
  elif states&{'AMBIGUOUS_SOURCE','MULTIPLE_SOURCE_ENTRIES'}:priority='P1_AMBIGUOUS_SOURCE'
  elif states&{'MISSING_BASELINE_READING','MISSING_CELL_PRONUNCIATION'}:priority='P1_MISSING_PRONUNCIATION'
  elif 'NOT_FOUND' in states:priority='P2_NOT_FOUND'
  else:priority='P3_MATCH_NEEDS_REVIEW'
  queue.append({'concept_id':cid,'priority':priority,'statuses':sorted(states),'approval':'PENDING_HUMAN_REVIEW'})
 return {'schema':'cell.lexicon.triage.v1.2','total_concepts_reviewed':len(queue),'priority_counts':dict(Counter(r['priority'] for r in queue)),'approved_count':0,'queue':queue}
def export(src,dst):
 data=json.loads(Path(src).read_text(encoding='utf8'))
 rows=data.get('records',data.get('findings')) if isinstance(data,dict) else data
 if not isinstance(rows,list):raise ValueError('Expected records/findings')
 result=triage(rows);Path(dst).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8');return result
if __name__=='__main__':print(export(sys.argv[1],sys.argv[2])['priority_counts'])
