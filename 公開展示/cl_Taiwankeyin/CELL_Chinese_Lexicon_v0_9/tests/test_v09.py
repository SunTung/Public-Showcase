import unittest,sys,sqlite3,hashlib,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from build_v08 import build
from snapshot_audit_v09 import audit
from dualstore_v09 import lookup
class TestV09(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();cls.db=Path(cls.tmp.name)/'db.sqlite';build(cls.db)
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def test_clean(self):self.assertEqual(audit(self.db)['status'],'PASS')
 def test_no_claims(self):self.assertEqual(audit(self.db)['snapshots'],0)
 def test_zero_release(self):self.assertEqual(audit(self.db)['release_rows'],0)
 def test_no_source_authenticity_claim(self):self.assertEqual(audit(self.db)['source_authenticity'],'NOT_ESTABLISHED_BY_HASH')
 def test_legacy(self):self.assertEqual(lookup(self.db,'en','hello',['hello'],True)[0]['source'],'legacy')
 def test_no_candidate(self):self.assertEqual(lookup(self.db,'en','hello',[],True),[])
 def test_disabled(self):self.assertEqual(lookup(self.db,'en','hello',['hello'],False)[0]['source'],'legacy')
 def test_missing(self):self.assertEqual(lookup(self.db.parent/'missing.sqlite','en','hello',['hello'],True)[0]['source'],'legacy')
 def test_invalid_locale(self):
  with self.assertRaises(ValueError):lookup(self.db,'fr','hello')
 def test_digest_mismatch_blocks(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'db.sqlite';build(p)
   with sqlite3.connect(p) as c:c.execute('INSERT INTO evidence_snapshot VALUES(?,?,?,?,?,?)',('https://example.org/a','0'*64,'actual content','2026-11-09','manual','source_confirmed'))
   self.assertEqual(audit(p)['status'],'BLOCKED')
   self.assertEqual(lookup(p,'en','hello',['hello'],True)[0]['source'],'legacy')
 def test_test_method_blocks(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'db.sqlite';build(p);content='test content'
   with sqlite3.connect(p) as c:c.execute('INSERT INTO evidence_snapshot VALUES(?,?,?,?,?,?)',('https://example.org/a',hashlib.sha256(content.encode()).hexdigest(),content,'2026-11-09','unit-test','source_confirmed'))
   self.assertEqual(audit(p)['status'],'BLOCKED')
 def test_non_https_blocks(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'db.sqlite';build(p);content='content'
   with sqlite3.connect(p) as c:c.execute('INSERT INTO evidence_snapshot VALUES(?,?,?,?,?,?)',('http://example.org/a',hashlib.sha256(content.encode()).hexdigest(),content,'2026-11-09','manual','source_confirmed'))
   self.assertEqual(audit(p)['status'],'BLOCKED')
 def test_readonly(self):
  before=hashlib.sha256(self.db.read_bytes()).hexdigest();lookup(self.db,'en','hello',[],True)
  self.assertEqual(before,hashlib.sha256(self.db.read_bytes()).hexdigest())
