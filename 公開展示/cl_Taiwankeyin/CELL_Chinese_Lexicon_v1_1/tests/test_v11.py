import sys,tempfile,unittest,csv,json,zipfile,io
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from moe_import_v11 import inspect,find_columns,iter_rows,sha
DB=ROOT/'build/cell_concepts.sqlite3'
class TestV11(unittest.TestCase):
 def source(self,rows):
  d=tempfile.TemporaryDirectory();p=Path(d.name)/'source.tsv'
  with p.open('w',encoding='utf8',newline='') as f:
   w=csv.writer(f,delimiter='\t');w.writerows(rows)
  return d,p
 def test_all_concepts_reported(self):
  d,p=self.source([['詞目','注音','漢語拼音'],['你好','ㄋㄧˇ ㄏㄠˇ','ni3 hao3']])
  with d:
   r=inspect(DB,p,Path(d.name)/'report.json','https://example.org/download','test')
   self.assertEqual(r['concepts_checked'],585);self.assertEqual(r['automatic_approvals'],0)
   self.assertEqual(sum(r['counts'].values()),585)
 def test_exact_not_approval(self):
  d,p=self.source([['詞目','注音','漢語拼音'],['你好','ㄋㄧˇ ㄏㄠˇ','ni3 hao3']])
  with d:
   r=inspect(DB,p,Path(d.name)/'r.json','https://example.org','v')
   self.assertEqual(r['findings'][0]['status'],'EXACT_TEXT_MATCH_NOT_APPROVAL')
 def test_multiple_readings(self):
  d,p=self.source([['詞目','注音','漢語拼音'],['你好','a','a'],['你好','b','b']])
  with d:self.assertEqual(inspect(DB,p,Path(d.name)/'r.json','https://example.org','v')['findings'][0]['status'],'MULTIPLE_SOURCE_ENTRIES')
 def test_missing_source_pinyin(self):
  d,p=self.source([['詞目','注音'],['你好','ㄋㄧˇ ㄏㄠˇ']])
  with d:self.assertEqual(inspect(DB,p,Path(d.name)/'r.json','https://example.org','v')['findings'][0]['status'],'SOURCE_READING_MISSING')
 def test_sha_reject(self):
  d,p=self.source([['詞目'],['你好']])
  with d,self.assertRaises(ValueError):inspect(DB,p,Path(d.name)/'r.json','https://example.org','v','0'*64)
 def test_url_reject(self):
  d,p=self.source([['詞目'],['你好']])
  with d,self.assertRaises(ValueError):inspect(DB,p,Path(d.name)/'r.json','file:///fake','v')
 def test_missing_headword_reject(self):
  d,p=self.source([['something'],['你好']])
  with d,self.assertRaises(ValueError):inspect(DB,p,Path(d.name)/'r.json','https://example.org','v')
 def test_alias(self):self.assertEqual(find_columns(['編號','詞目','注音一式','漢語拼音']),{'headword':1,'zhuyin':2,'pinyin':3,'source_entry_id':0})
 def test_duplicate_columns(self):
  with self.assertRaises(ValueError):find_columns(['詞目','字詞'])
 def test_tsv_rows(self):
  d,p=self.source([['詞目'],['字典']])
  with d:self.assertEqual(list(iter_rows(p)),[['詞目'],['字典']])
 def test_empty_source(self):
  d,p=self.source([])
  with d,self.assertRaises(ValueError):inspect(DB,p,Path(d.name)/'r.json','https://example.org','v')
 def test_no_db_mutation(self):
  import hashlib
  before=sha(DB);d,p=self.source([['詞目'],['你好']])
  with d:inspect(DB,p,Path(d.name)/'r.json','https://example.org','v')
  self.assertEqual(sha(DB),before)
 def test_unknown_extension(self):
  d=tempfile.TemporaryDirectory()
  with d:
   p=Path(d.name)/'a.exe';p.write_bytes(b'')
   with self.assertRaises(ValueError):list(iter_rows(p))
if __name__=='__main__':unittest.main()
