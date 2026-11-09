import unittest,sys,sqlite3,tempfile,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from build_v04 import build,form_candidates,review_queue,SCHEMA
from build_v03 import lookup
class TestV04(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();cls.db=Path(cls.tmp.name)/'lex.sqlite3';cls.report=build(cls.db)
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def test_counts(self):
  self.assertEqual(self.report['previous_concepts'],423)
  self.assertEqual(self.report['counts']['concept'],423+self.report['batch04_concepts'])
  self.assertEqual(self.report['counts']['expression'],3*self.report['counts']['concept'])
 def test_prior_id(self):self.assertEqual(lookup(self.db,'en','algorithm')[0]['concept_id'],'CELL-C0121')
 def test_new_triple(self):
  self.assertEqual(lookup(self.db,'en','speech synthesis')[0]['traditional'],'語音合成')
  self.assertEqual(lookup(self.db,'zh-Hans-CN','电池')[0]['english'],'battery')
 def test_ambiguity(self):
  self.assertEqual({x[0] for x in form_candidates(self.db,'zh-Hans-CN','发')},{'發','髮'})
  self.assertEqual({x[0] for x in form_candidates(self.db,'zh-Hans-CN','面')},{'面','麵'})
 def test_bidirection(self):
  self.assertEqual({x[0] for x in form_candidates(self.db,'zh-Hant-TW','髮')},{'发'})
 def test_no_auto_conversion(self):
  with sqlite3.connect(self.db) as c:self.assertEqual(c.execute("SELECT COUNT(*) FROM form_graph WHERE status!='context_required_draft'").fetchone()[0],0)
 def test_quality_queue(self):
  self.assertTrue(review_queue(self.db,aspect='glyph_mapping'))
  with sqlite3.connect(self.db) as c:
   self.assertEqual(c.execute("SELECT COUNT(*) FROM lexical_review_queue WHERE aspect='meaning'").fetchone()[0],self.report['counts']['concept'])
 def test_no_approved_reviews(self):
  with sqlite3.connect(self.db) as c:self.assertEqual(c.execute("SELECT COUNT(*) FROM lexical_review_queue WHERE state!='pending'").fetchone()[0],0)
 def test_new_no_synthetic_pronunciations(self):
  with sqlite3.connect(self.db) as c:self.assertEqual(c.execute("SELECT COUNT(*) FROM pronunciation p JOIN concept c USING(concept_id) WHERE c.created_batch='CELL-v0.4'").fetchone()[0],0)
 def test_integrity(self):
  with sqlite3.connect(self.db) as c:
   self.assertEqual(c.execute('PRAGMA integrity_check').fetchone()[0],'ok')
   self.assertEqual(c.execute('PRAGMA foreign_key_check').fetchall(),[])
 def test_schema(self):
  with sqlite3.connect(self.db) as c:self.assertEqual(c.execute("SELECT value FROM metadata WHERE key='schema'").fetchone()[0],SCHEMA)
 def test_deterministic(self):
  with tempfile.TemporaryDirectory() as d:
   other=Path(d)/'lex.sqlite3';m=build(other)
   self.assertEqual(m['counts'],self.report['counts'])
   self.assertEqual(m['source_batch_sha256'],self.report['source_batch_sha256'])
if __name__=='__main__':unittest.main()
