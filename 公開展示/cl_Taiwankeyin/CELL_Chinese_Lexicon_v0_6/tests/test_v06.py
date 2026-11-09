import unittest, tempfile, sqlite3, sys, hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from build_v06 import build
from review_v06 import record_evidence,approve,candidates,review_queue
class TestV06(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.temp=tempfile.TemporaryDirectory();cls.db=Path(cls.temp.name)/'v06.sqlite3';cls.report=build(cls.db)
 @classmethod
 def tearDownClass(cls):cls.temp.cleanup()
 def test_legacy_counts(self):self.assertEqual(self.report['counts']['concept'],585)
 def test_expression_counts(self):self.assertEqual(self.report['counts']['expression'],1755)
 def test_review_queue_preserved(self):self.assertGreaterEqual(self.report['counts']['lexical_review_queue'],1090)
 def test_fail_closed(self):self.assertEqual(candidates(self.db,'zh-Hant-TW','鍵盤'),[])
 def test_no_automatic_approval(self):self.assertEqual(self.report['counts']['lexical_approval'],0)
 def test_queue_available(self):self.assertTrue(review_queue(self.db,5))
 def test_bogus_evidence_rejected(self):
  with self.assertRaises(ValueError):record_evidence(self.db,'CELL-C0017','meaning','', 'x'*64,'note','reviewer','supports')
 def test_single_reviewer_blocked(self):
  with self.assertRaises(ValueError):approve(self.db,'CELL-C0017','same','same','x','y')
 def test_missing_evidence_blocked(self):
  with self.assertRaises(ValueError):approve(self.db,'CELL-C0017','a','b','x','y')
 def test_fk(self):
  with sqlite3.connect(self.db) as c:self.assertEqual(c.execute('PRAGMA foreign_key_check').fetchall(),[])
 def test_integrity(self):
  with sqlite3.connect(self.db) as c:self.assertEqual(c.execute('PRAGMA integrity_check').fetchone()[0],'ok')
 def test_review_approval_transaction(self):
  with tempfile.TemporaryDirectory() as d:
   db=Path(d)/'isolated.sqlite3';build(db);h=hashlib.sha256(b'independent short evidence').hexdigest()
   x=record_evidence(db,'CELL-C0017','meaning','https://example.org/meaning',h,'meaning evidence','reviewer-A','supports')
   y=record_evidence(db,'CELL-C0017','pronunciation','https://example.org/pron',h,'pronunciation evidence','reviewer-B','supports')
   # Structural approval test only: illustrative URLs are NOT factual verification.
   approve(db,'CELL-C0017','reviewer-A','reviewer-B',x,y)
   self.assertEqual(candidates(db,'zh-Hant-TW','鍵盤')[0][1],'鍵盤')
   self.assertEqual(candidates(self.db,'zh-Hant-TW','鍵盤'),[])
 def test_unsupported_locale(self):
  with self.assertRaises(ValueError):candidates(self.db,'invalid','鍵盤')
if __name__=='__main__':unittest.main()
