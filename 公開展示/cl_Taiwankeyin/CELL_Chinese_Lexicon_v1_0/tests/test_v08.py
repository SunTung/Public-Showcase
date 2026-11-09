import sys,unittest,sqlite3,hashlib,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from build_v08 import build
from dualstore_v08 import lookup
from review_v06 import record_evidence,approve
class TestV08(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();cls.db=Path(cls.tmp.name)/'v08.sqlite3';cls.result=build(cls.db)
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def test_counts(self):self.assertEqual(self.result['counts']['concept'],585)
 def test_expressions(self):self.assertEqual(self.result['counts']['expression'],1755)
 def test_no_promotions(self):self.assertEqual(self.result['counts']['cell_release_v08'],0)
 def test_unreviewed_missing_phonetics(self):self.assertEqual(self.result['counts']['release_gate_issue'],495)
 def test_old_phonetics_remain(self):self.assertEqual(self.result['counts']['pronunciation'],180)
 def test_no_snapshot_fake(self):self.assertEqual(self.result['counts']['evidence_snapshot'],0)
 def test_dual_disabled(self):self.assertEqual(lookup(self.db,'zh-Hant-TW','鍵盤',['鍵盤']),[{'text':'鍵盤','source':'legacy'}])
 def test_dual_enabled_but_unapproved(self):self.assertEqual(lookup(self.db,'zh-Hant-TW','鍵盤',['鍵盤'],True),[{'text':'鍵盤','source':'legacy'}])
 def test_dedupe_legacy(self):self.assertEqual(len(lookup(self.db,'en','keyboard',['keyboard','keyboard'],True)),1)
 def test_unavailable_db_fallback(self):self.assertEqual(len(lookup('/tmp/definitely_missing_cell_v08.sqlite3','en','hello',['hello'],True)),1)
 def test_invalid_locale(self):
  with self.assertRaises(ValueError):lookup(self.db,'not-locale','hello')
 def test_legacy_db_unchanged_readonly(self):
  before=hashlib.sha256(self.db.read_bytes()).hexdigest()
  lookup(self.db,'zh-Hans-CN','键盘',(),True)
  self.assertEqual(before,hashlib.sha256(self.db.read_bytes()).hexdigest())
 def test_reviewer_approval_without_snapshot_cannot_release(self):
  with tempfile.TemporaryDirectory() as d:
   db=Path(d)/'isolated.sqlite';build(db);h=hashlib.sha256(b'structural-test').hexdigest()
   a=record_evidence(db,'CELL-C0017','meaning','https://example.org/a',h,'test only','A','supports')
   b=record_evidence(db,'CELL-C0017','pronunciation','https://example.org/b',h,'test only','B','supports')
   approve(db,'CELL-C0017','A','B',a,b)
   with sqlite3.connect(db) as c:
    self.assertEqual(c.execute('SELECT COUNT(*) FROM cell_release_candidates').fetchone()[0],3)
    self.assertEqual(c.execute('SELECT COUNT(*) FROM cell_release_v08').fetchone()[0],0)
 def test_snapshot_must_have_matching_digest_and_outstanding_targets_block(self):
  with tempfile.TemporaryDirectory() as d:
   db=Path(d)/'isolated.sqlite';build(db);h=hashlib.sha256(b'structural-test').hexdigest()
   a=record_evidence(db,'CELL-C0017','meaning','https://example.org/a',h,'test only','A','supports')
   b=record_evidence(db,'CELL-C0017','pronunciation','https://example.org/b',h,'test only','B','supports')
   approve(db,'CELL-C0017','A','B',a,b)
   with sqlite3.connect(db) as c:
    c.execute('INSERT INTO evidence_snapshot VALUES (?,?,?,?,?,?)',('https://example.org/a','0'*64,'not matching','2026-11-09','unit-test','source_confirmed'))
    c.execute('INSERT INTO evidence_snapshot VALUES (?,?,?,?,?,?)',('https://example.org/b',h,'test only','2026-11-09','unit-test','source_confirmed'))
    self.assertEqual(c.execute('SELECT COUNT(*) FROM cell_release_v08').fetchone()[0],0)
 def test_integrity(self):
  with sqlite3.connect(self.db) as c:self.assertEqual(c.execute('PRAGMA integrity_check').fetchone()[0],'ok')
if __name__=='__main__':unittest.main()
