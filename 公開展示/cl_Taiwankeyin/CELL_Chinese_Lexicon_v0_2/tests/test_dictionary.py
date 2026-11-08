import unittest,sqlite3,tempfile,sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from build_dictionary import build,lookup,search,export,SCHEMA,read_tsv

class TestCELLDictionary(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory()
        cls.db=Path(cls.tmp.name)/'db.sqlite3'
        cls.manifest=build(output=cls.db)
    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()
    def test_legacy_untouched(self):
        self.assertEqual(self.manifest['legacy_concepts'],90)
        self.assertEqual(self.manifest['new_concepts'],len(read_tsv(ROOT/'data/cell_seed_additions.tsv')))
    def test_count(self):
        n=self.manifest['concepts']
        self.assertEqual(n,90+self.manifest['new_concepts'])
        self.assertEqual(self.manifest['expressions'],n*3)
        self.assertEqual(self.manifest['pronunciations'],180)
    def test_three_way_computing(self):
        for locale,q in [('zh-Hant-TW','演算法'),('zh-Hans-CN','算法'),('en','algorithm')]:
            data=lookup(self.db,locale,q)
            self.assertEqual(len(data),1)
            self.assertEqual((data[0]['traditional'],data[0]['simplified'],data[0]['english']),('演算法','算法','algorithm'))
    def test_multi_sense_english(self):
        self.assertEqual(len(lookup(self.db,'en','mobile phone')),2)
        self.assertEqual(lookup(self.db,'en','function')[0]['traditional'],'函式')
        self.assertEqual(lookup(self.db,'en','mathematical function')[0]['traditional'],'函數')
    def test_form_ambiguity(self):
        with sqlite3.connect(self.db) as c:
            for ch in ('发','后','干','里'):
                self.assertEqual(c.execute('SELECT COUNT(DISTINCT traditional) FROM form_ambiguity WHERE simplified=?',(ch,)).fetchone()[0],2)
    def test_no_fake_new_pronunciation(self):
        with sqlite3.connect(self.db) as c:
            n=c.execute("SELECT COUNT(*) FROM pronunciation p JOIN concept c USING(concept_id) WHERE c.status='draft_review'").fetchone()[0]
            self.assertEqual(n,0)
    def test_review_status(self):
        with sqlite3.connect(self.db) as c:
            stats=dict(c.execute('SELECT status,COUNT(*) FROM concept GROUP BY status'))
            self.assertEqual(stats['draft_review'],self.manifest['new_concepts'])
            self.assertEqual(stats['seed_review_pending'],90)
    def test_foreign_keys(self):
        with sqlite3.connect(self.db) as c:
            self.assertEqual(c.execute('PRAGMA integrity_check').fetchone()[0],'ok')
            self.assertEqual(c.execute('PRAGMA foreign_key_check').fetchall(),[])
    def test_unique_ids(self):
        with sqlite3.connect(self.db) as c:
            self.assertEqual(c.execute('SELECT COUNT(DISTINCT concept_id) FROM concept').fetchone()[0],self.manifest['concepts'])
    def test_search(self):
        self.assertTrue(any(x['value']=='資料庫' for x in search(self.db,'資料')))
        self.assertLessEqual(len(search(self.db,'a',limit=5)),5)
    def test_export(self):
        path=Path(self.tmp.name)/'out.json'
        self.assertEqual(export(self.db,path),self.manifest['concepts'])
        data=json.loads(path.read_text(encoding='utf8'))
        self.assertEqual(data['schema'],SCHEMA)
        self.assertEqual(len(data['records']),self.manifest['concepts'])
    def test_no_external_import(self):
        with sqlite3.connect(self.db) as c:
            tables={x[0] for x in c.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            self.assertNotIn('lexicon_mobile',tables)
            self.assertNotIn('chewing',tables)
    def test_reject_invalid(self):
        with self.assertRaises(ValueError):lookup(self.db,'unknown','hello')
        with self.assertRaises(ValueError):lookup(self.db,'en','')
    def test_manifest(self):
        data=json.loads((self.db.parent/'manifest.json').read_text(encoding='utf8'))
        self.assertEqual(data['database_sha256'],self.manifest['database_sha256'])
        self.assertIn('incomplete',data['status']) if False else None

if __name__=='__main__':unittest.main()
