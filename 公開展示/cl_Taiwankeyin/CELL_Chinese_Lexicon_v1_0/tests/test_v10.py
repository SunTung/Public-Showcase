import sys,unittest,tempfile,csv,sqlite3,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from build_v08 import build
from external_alignment_v10 import align
class TestV10(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();cls.db=Path(cls.tmp.name)/'dict.sqlite3';build(cls.db)
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def prepare(self,rows,header=('headword','zhuyin','pinyin','source_entry_id')):
  d=tempfile.TemporaryDirectory();p=Path(d.name)/'source.tsv'
  with p.open('w',encoding='utf-8',newline='') as f:
   w=csv.writer(f,delimiter='\t');w.writerow(header);w.writerows(rows)
  return d,p,Path(d.name)/'out.json'
 def runalign(self,rows):
  d,p,o=self.prepare(rows)
  try:return align(self.db,p,o,'Independent Source','2026-11-09'),json.loads(o.read_text())
  finally:d.cleanup()
 def test_match(self):
  r,_=self.runalign([('你好','ㄋㄧˇ ㄏㄠˇ','ni3 hao3','x1')]);self.assertEqual(r['counts']['EXACT_TEXT_MATCH'],1)
 def test_difference(self):
  r,_=self.runalign([('你好','ㄋㄧˇ ㄏㄠˋ','ni3 hao4','x1')]);self.assertEqual(r['counts']['PRONUNCIATION_DIFFERENCE'],1)
 def test_ambiguous(self):
  r,_=self.runalign([('你好','ㄋㄧˇ ㄏㄠˇ','ni3 hao3','x1'),('你好','ㄋㄧˇ ㄏㄠˋ','ni3 hao4','x2')]);self.assertEqual(r['counts']['AMBIGUOUS_SOURCE'],1)
 def test_missing_reading(self):
  r,_=self.runalign([('演算法','ㄧㄢˇ ㄙㄨㄢˋ ㄈㄚˇ','yan3 suan4 fa3','x1')]);self.assertGreaterEqual(r['counts']['MISSING_CELL_PRONUNCIATION'],1)
 def test_unmatched(self):
  r,_=self.runalign([]);self.assertEqual(r['counts']['NOT_FOUND'],585)
 def test_no_approval(self):
  r,_=self.runalign([('你好','ㄋㄧˇ ㄏㄠˇ','ni3 hao3','x1')]);self.assertEqual(r['approval_events_created'],0)
 def test_no_mutation(self):
  before=hashlib.sha256(self.db.read_bytes()).hexdigest();self.runalign([]);self.assertEqual(before,hashlib.sha256(self.db.read_bytes()).hexdigest())
 def test_bad_header(self):
  d,p,o=self.prepare([],('headword','pinyin'))
  try:
   with self.assertRaises(ValueError):align(self.db,p,o,'x','v')
  finally:d.cleanup()
 def test_duplicate_source_id(self):
  d,p,o=self.prepare([('你好','a','b','id'),('再見','c','d','id')])
  try:
   with self.assertRaises(ValueError):align(self.db,p,o,'x','v')
  finally:d.cleanup()
 def test_missing_source_identity(self):
  d,p,o=self.prepare([])
  try:
   with self.assertRaises(ValueError):align(self.db,p,o,'','v')
  finally:d.cleanup()
 def test_output_schema(self):
  r,data=self.runalign([]);self.assertEqual(data['schema'],'cell.external_alignment.v1.0');self.assertEqual(len(data['findings']),585)
 def test_source_digest(self):
  d,p,o=self.prepare([])
  try:self.assertEqual(align(self.db,p,o,'x','v')['source_file_sha256'],hashlib.sha256(p.read_bytes()).hexdigest())
  finally:d.cleanup()
 def test_status_totals(self):
  r,_=self.runalign([('你好','ㄋㄧˇ ㄏㄠˇ','ni3 hao3','x1')]);self.assertEqual(sum(r['counts'].values()),585)
