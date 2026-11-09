import csv,json,sqlite3,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from build_v05 import build,lookup,dual_lookup,read_batch
class TestV05(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();cls.db=Path(cls.tmp.name)/'v05.sqlite3';cls.report=build(cls.db)
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def test_legacy_preserved(self):self.assertEqual(self.report['previous_concepts'],525)
 def test_batch_size(self):self.assertEqual(self.report['batch05_concepts'],60)
 def test_count(self):self.assertEqual(self.report['counts']['concept'],585)
 def test_expressions(self):self.assertEqual(self.report['counts']['expression'],1755)
 def test_integrity(self):
  with sqlite3.connect(self.db) as c:
   self.assertEqual(c.execute('PRAGMA integrity_check').fetchone()[0],'ok')
   self.assertFalse(c.execute('PRAGMA foreign_key_check').fetchall())
 def test_graph_audit(self):self.assertEqual(self.report['counts']['glyph_evidence_audit'],20)
 def test_known_wrong_reference_repaired(self):
  with sqlite3.connect(self.db) as c:
   x=c.execute("SELECT context_concept_id FROM form_graph WHERE source_locale='zh-Hans-CN' AND source_form='发' AND target_form='發'").fetchone()[0]
   self.assertEqual(x,'CELL-C0485')
 def test_no_unsafe_promotion(self):self.assertEqual(lookup(self.db,'zh-Hant-TW','知道'),[])
 def test_draft_optin(self):self.assertEqual(lookup(self.db,'zh-Hant-TW','知道',True)[0]['status'],'draft_review')
 def test_legacy_first(self):
  rows=dual_lookup(self.db,'zh-Hant-TW','知道',['知道','曉得'],True)
  self.assertEqual([(r['form'],r['source']) for r in rows],[('知道','legacy'),('曉得','legacy')])
 def test_invalid_locale(self):
  with self.assertRaises(ValueError):lookup(self.db,'XX','知道')
 def test_no_phony_pronunciation(self):self.assertEqual(self.report['counts']['pronunciation'],180)
 def test_reviews_increase(self):self.assertGreaterEqual(self.report['counts']['lexical_review_queue'],1090)
 def test_manifest(self):self.assertEqual(json.loads((self.db.parent/'manifest.json').read_text())['db_sha256'],self.report['db_sha256'])
 def test_missing_data(self):
  with self.assertRaises(FileNotFoundError):read_batch(ROOT/'tests'/'not_here.tsv')
if __name__=='__main__':unittest.main()
