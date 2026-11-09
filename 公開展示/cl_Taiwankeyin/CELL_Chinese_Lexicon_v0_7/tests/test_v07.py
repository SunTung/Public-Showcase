import sys,unittest,tempfile,sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from build_v07 import build,syllable_tones
from phonetic_v07 import phonetic_report,review_targets
class V07Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();cls.db=Path(cls.tmp.name)/'cell.sqlite3';cls.report=build(cls.db)
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def test_legacy_concepts(self):self.assertEqual(self.report['counts']['concept'],585)
 def test_expressions(self):self.assertEqual(self.report['counts']['expression'],1755)
 def test_pronunciations_preserved(self):self.assertEqual(self.report['counts']['pronunciation'],180)
 def test_pairs_audited(self):self.assertEqual(self.report['counts']['phonetic_quality_audit'],90)
 def test_approvals_remain_zero(self):self.assertEqual(self.report['counts']['lexical_approval'],0)
 def test_release_stays_empty(self):self.assertEqual(self.report['counts']['cell_release_v07'],0)
 def test_source_registered_not_approved(self):
  with sqlite3.connect(self.db) as c:
   self.assertEqual(c.execute("SELECT COUNT(*) FROM verification_sources WHERE status='snapshot_verified'").fetchone()[0],0)
 def test_targets_nonempty(self):self.assertGreaterEqual(self.report['counts']['lexical_verification_targets'],90)
 def test_tone2(self):self.assertEqual(syllable_tones('wen2','ㄨㄣˊ')[0],'tone_consistent')
 def test_tone3(self):self.assertEqual(syllable_tones('hao3','ㄏㄠˇ')[0],'tone_consistent')
 def test_tone4_mismatch(self):self.assertEqual(syllable_tones('hao4','ㄏㄠˇ')[0],'tone_mismatch')
 def test_syllable_count(self):self.assertEqual(syllable_tones('ni3 hao3','ㄋㄧˇ')[0],'syllable_count_mismatch')
 def test_pinyin_shape(self):self.assertEqual(syllable_tones('ni','ㄋㄧˇ')[0],'invalid_pinyin_format')
 def test_neutral_tone(self):self.assertEqual(syllable_tones('de5','ㄉㄜ˙')[0],'tone_consistent')
 def test_read_only_report(self):self.assertTrue(phonetic_report(self.db,limit=3))
 def test_targets(self):self.assertTrue(review_targets(self.db,5))
 def test_bad_state(self):
  with self.assertRaises(ValueError):phonetic_report(self.db,['arbitrary'])
 def test_fk(self):
  with sqlite3.connect(self.db) as c:self.assertFalse(c.execute('PRAGMA foreign_key_check').fetchall())
 def test_integrety(self):
  with sqlite3.connect(self.db) as c:self.assertEqual(c.execute('PRAGMA integrity_check').fetchone()[0],'ok')
