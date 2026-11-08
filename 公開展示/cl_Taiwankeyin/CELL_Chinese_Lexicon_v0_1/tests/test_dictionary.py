import unittest,sqlite3,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from build_dictionary import build,lookup
class DictionaryTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.db=ROOT/'build'/'cell_concepts.sqlite3'
  build(ROOT/'data'/'cell_seed.tsv',cls.db)
 def test_size(self):
  with sqlite3.connect(self.db) as c:
   self.assertEqual(c.execute('SELECT count(*) FROM concept').fetchone()[0],90)
   self.assertEqual(c.execute('SELECT count(*) FROM expression').fetchone()[0],270)
   self.assertEqual(c.execute('PRAGMA integrity_check').fetchone()[0],'ok')
 def test_three_direction_lookup(self):
  for loc,word in [('zh-Hant-TW','鍵盤'),('zh-Hans-CN','键盘'),('en','keyboard')]:
   found=lookup(self.db,loc,word)
   self.assertTrue(found)
   self.assertEqual(found[0][1:],('鍵盤','键盘','keyboard'))
 def test_ambiguous_not_collapsed(self):
  with sqlite3.connect(self.db) as c:
   self.assertEqual(c.execute("SELECT COUNT(DISTINCT traditional) FROM ambiguous_character WHERE simplified='发'").fetchone()[0],2)
   self.assertEqual(c.execute("SELECT COUNT(DISTINCT traditional) FROM ambiguous_character WHERE simplified='后'").fetchone()[0],2)
   self.assertTrue(any(x[1]=='頭髮' for x in lookup(self.db,'en','hair')))
   self.assertTrue(any(x[1]=='發展' for x in lookup(self.db,'en','development')))
 def test_locale_specific_technical_words(self):
  self.assertEqual(lookup(self.db,'en','computer memory')[0][1:3],('記憶體','内存'))
  self.assertEqual(lookup(self.db,'en','hard disk')[0][1:3],('硬碟','硬盘'))
 def test_no_legacy_schema(self):
  with sqlite3.connect(self.db) as c:
   tables={x[0] for x in c.execute("SELECT name FROM sqlite_master WHERE type='table'")}
   self.assertNotIn('lexicon_mobile',tables)
   self.assertNotIn('phrase_stat',tables)
 def test_gloss_not_invertible(self):
  self.assertGreaterEqual(len(lookup(self.db,'en','mobile phone')),2)
if __name__=='__main__':unittest.main()
