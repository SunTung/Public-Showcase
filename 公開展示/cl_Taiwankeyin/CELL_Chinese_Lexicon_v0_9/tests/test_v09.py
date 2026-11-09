import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from source_observation_v09 import analyze,export
class TestObservedSources(unittest.TestCase):
 def test_five_real_observations(self):self.assertEqual(len(analyze()),5)
 def test_all_heads_match(self):self.assertTrue(all(x['headword_match'] for x in analyze()))
 def test_all_pinyin_match(self):self.assertTrue(all(x['pinyin_match'] for x in analyze()))
 def test_neutral_tone_comparison(self):self.assertTrue(next(x for x in analyze() if x['headword']=='謝謝')['zhuyin_match'])
 def test_all_zhuyin_match(self):self.assertTrue(all(x['zhuyin_match'] for x in analyze()))
 def test_no_approval_from_observation(self):
  self.assertEqual(export()['human_approved_count'],0)
  self.assertEqual(export()['verified_snapshot_count'],0)
 def test_immutable_baseline_count(self):
  import sqlite3
  with sqlite3.connect(ROOT/'build/cell_concepts.sqlite3') as c:
   self.assertEqual(c.execute('SELECT COUNT(*) FROM concept').fetchone()[0],585)
   self.assertEqual(c.execute('SELECT COUNT(*) FROM cell_release_v08').fetchone()[0],0)
