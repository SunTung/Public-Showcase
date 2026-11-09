import unittest,sys,tempfile,csv
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from comparison_v10 import compare,export
from build_v08 import build

class TestV10(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();cls.db=Path(cls.tmp.name)/'test.sqlite3';build(cls.db)
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def test_conflict_detected(self):
  rows=compare(self.db);self.assertEqual([x['status'] for x in rows],['CONFLICT','CONFLICT','MATCH'])
 def test_no_fake_approval(self):
  x=export(self.db,Path(self.tmp.name)/'report.json');self.assertEqual(x['lexical_approvals'],0)
  self.assertEqual(x['source_snapshots_verified'],0)
 def test_readonly(self):
  import hashlib
  a=hashlib.sha256(self.db.read_bytes()).digest();compare(self.db)
  self.assertEqual(a,hashlib.sha256(self.db.read_bytes()).digest())
 def test_preserves_baseline(self):
  import sqlite3
  with sqlite3.connect(self.db) as c:
   self.assertEqual(c.execute('select count(*) from concept').fetchone()[0],585)
   self.assertEqual(c.execute('select count(*) from expression').fetchone()[0],1755)
   self.assertEqual(c.execute('select count(*) from lexical_approval').fetchone()[0],0)
 def test_reject_mismatched_concept(self):
  with tempfile.TemporaryDirectory() as d:
   t=Path(d)/'bad.tsv';t.write_text('concept_id\theadword\tsource\tsource_url\tpinyin\tzhuyin\tmeaning_note\tretrieval\tstatus\nCELL-C0023\t錯字\tx\thttps://dict.concised.moe.edu.tw/x\ta\tb\tx\tweb_result_observation\tpending\n',encoding='utf8')
   with self.assertRaises(ValueError):compare(self.db,t)
