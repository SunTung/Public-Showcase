import csv,importlib.util,json,sqlite3,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('batch_intake_v11',ROOT/'src/batch_intake_v11.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class TestV11(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.db=ROOT/'build/cell_concepts.sqlite3'
  assert cls.db.exists()
 def make(self,rows,columns=None):
  tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup)
  p=Path(tmp.name)/'external.tsv'
  with p.open('w',encoding='utf-8',newline='') as f:
   w=csv.DictWriter(f,fieldnames=columns or ['headword','zhuyin','pinyin','source_entry_id','definition'],delimiter='\t');w.writeheader();w.writerows(rows)
  return p,Path(tmp.name)/'report.json'
 def run_report(self,rows):
  p,out=self.make(rows)
  return m.inspect(self.db,p,out,name='fixture',version='test',source_url='https://example.org/fixture')
 def test_exact(self):
  r=self.run_report([dict(headword='你好',zhuyin='ㄋㄧˇ ㄏㄠˇ',pinyin='ni3 hao3',source_entry_id='a',definition='greeting')]);self.assertEqual(r['counts']['EXACT_ZHUYIN'],1)
 def test_diff(self):
  r=self.run_report([dict(headword='你好',zhuyin='ㄋㄧˋ ㄏㄠˇ',pinyin='ni4 hao3',source_entry_id='a',definition='')]);self.assertEqual(r['counts']['DIFFERENT_ZHUYIN'],1)
 def test_missing(self):
  r=self.run_report([dict(headword='早餐',zhuyin='ㄗㄠˇ ㄘㄢ',pinyin='zao3 can1',source_entry_id='a',definition='')]);self.assertEqual(r['counts']['MISSING_CELL_PRONUNCIATION'],1)
 def test_multiple(self):
  r=self.run_report([dict(headword='你好',zhuyin='ㄋㄧˇ ㄏㄠˇ',pinyin='',source_entry_id='a',definition=''),dict(headword='你好',zhuyin='ㄋㄧˊ ㄏㄠˇ',pinyin='',source_entry_id='b',definition='')]);self.assertEqual(r['counts']['MULTIPLE_SOURCE_ENTRIES'],1)
 def test_not_found(self):
  r=self.run_report([dict(headword='測試外部詞',zhuyin='ㄘㄜˋ',pinyin='',source_entry_id='a',definition='')]);self.assertEqual(r['counts']['NOT_FOUND'],585)
 def test_no_approval(self):
  r=self.run_report([dict(headword='你好',zhuyin='ㄋㄧˇ ㄏㄠˇ',pinyin='',source_entry_id='a',definition='')]);self.assertEqual(r['release_candidates_added'],0);self.assertFalse(r['db_modified'])
 def test_counts(self):
  r=self.run_report([dict(headword='你好',zhuyin='ㄋㄧˇ ㄏㄠˇ',pinyin='',source_entry_id='a',definition='')]);self.assertEqual(sum(r['counts'].values()),585)
 def test_digest(self):
  p,out=self.make([dict(headword='你好',zhuyin='ㄋㄧˇ ㄏㄠˇ',pinyin='',source_entry_id='a',definition='')]);r=m.inspect(self.db,p,out,name='fixture',version='test',source_url='https://example.org/fixture');self.assertEqual(r['source']['file_sha256'],m.sha256(p))
 def test_duplicate_id_rejected(self):
  p,out=self.make([dict(headword='你好',zhuyin='ㄋㄧˇ ㄏㄠˇ',pinyin='',source_entry_id='a',definition=''),dict(headword='再見',zhuyin='ㄗㄞˋ',pinyin='',source_entry_id='a',definition='')]);self.assertRaises(ValueError,m.load_rows,p)
 def test_non_https_rejected(self):
  p,out=self.make([dict(headword='你好',zhuyin='ㄋㄧˇ ㄏㄠˇ',pinyin='',source_entry_id='a',definition='')]);self.assertRaises(ValueError,m.inspect,self.db,p,out,name='x',version='v',source_url='http://bad')
 def test_missing_field_rejected(self):
  p,out=self.make([dict(headword='你好',zhuyin='ㄋㄧˇ ㄏㄠˇ',pinyin='',source_entry_id='a',definition='')]);self.assertRaises(ValueError,m.load_rows,p,{'headword':'missing','zhuyin':'zhuyin','source_entry_id':'source_entry_id'})
 def test_empty_rejected(self):
  p,out=self.make([]);self.assertRaises(ValueError,m.inspect,self.db,p,out,name='x',version='v',source_url='https://example.org')
 def test_db_unchanged(self):
  before=m.sha256(self.db);self.run_report([dict(headword='你好',zhuyin='ㄋㄧˇ ㄏㄠˇ',pinyin='',source_entry_id='a',definition='')]);self.assertEqual(m.sha256(self.db),before)
 def test_report_persisted(self):
  p,out=self.make([dict(headword='你好',zhuyin='ㄋㄧˇ ㄏㄠˇ',pinyin='',source_entry_id='a',definition='')]);m.inspect(self.db,p,out,name='x',version='v',source_url='https://example.org');self.assertEqual(len(json.loads(out.read_text())['findings']),585)
if __name__=='__main__':unittest.main()
