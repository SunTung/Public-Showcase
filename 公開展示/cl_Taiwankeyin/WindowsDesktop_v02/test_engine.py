from engine import Engine, MAP
import os,unittest

class TestWinEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db=os.environ['CELL_LEXICON']
    def setUp(self):self.e=Engine(self.db)
    def tearDown(self):self.e.close()
    def test_all_37(self):self.assertEqual(len(MAP),37)
    def test_no_tone(self):
        for c in 'sucl':self.assertTrue(self.e.push(c))
        self.assertEqual(self.e.current_bare(),'ㄋㄧ ㄏㄠ')
        self.assertIn('你好',[x.text for x in self.e.choices])
        self.e.choose(next(i for i,c in enumerate(self.e.choices) if c.text=='你好'))
        self.assertEqual(self.e.context,'你好')
    def test_followups(self):
        self.e.committed('今天')
        self.assertIn('是',self.e.followups(10))
        self.e.committed('。')
        self.assertEqual(self.e.context,'')
    def test_backspace(self):
        self.e.push('s');self.e.push('u');self.assertTrue(self.e.backspace())
        self.assertEqual(self.e.current_bare(),'ㄋ')
    def test_no_duplicate_commit(self):
        self.e.push('s');self.e.push('u');self.assertIsNotNone(self.e.choose(0))
        self.assertIsNone(self.e.choose(0))
if __name__=='__main__':unittest.main()
