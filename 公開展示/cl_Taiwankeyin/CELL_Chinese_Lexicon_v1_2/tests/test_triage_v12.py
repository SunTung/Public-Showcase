import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from triage_v12 import triage
class TestTriage(unittest.TestCase):
 def test_difference(self):self.assertEqual(triage([{'concept_id':'CELL-C1','status':'DIFFERENT_ZHUYIN'}])['queue'][0]['priority'],'P0_READING_CONFLICT')
 def test_ambiguous(self):self.assertEqual(triage([{'concept_id':'CELL-C1','status':'MULTIPLE_SOURCE_ENTRIES'}])['queue'][0]['priority'],'P1_AMBIGUOUS_SOURCE')
 def test_match(self):self.assertEqual(triage([{'concept_id':'CELL-C1','status':'EXACT_ZHUYIN'}])['queue'][0]['priority'],'P3_MATCH_NEEDS_REVIEW')
 def test_approval(self):self.assertEqual(triage([{'concept_id':'CELL-C1','status':'MATCH'}])['approved_count'],0)
