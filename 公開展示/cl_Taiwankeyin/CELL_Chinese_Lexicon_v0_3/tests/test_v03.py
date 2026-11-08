import csv,json,sqlite3,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from build_v03 import build,lookup,ambiguous_forms,export,read_batch,sha,SCHEMA

class TestV03(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory()
        cls.db=Path(cls.tmp.name)/'built.sqlite3'
        cls.manifest=build(output=cls.db)
    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()
    def test_incremental_counts(self):
        m=self.manifest
        self.assertEqual((m['previous_concepts'],m['new_concepts']), (296,127))
        self.assertEqual(m['counts']['concept'],423)
        self.assertEqual(m['counts']['expression'],1269)
    def test_prior_data_not_lost(self):
        for loc,word in [('zh-Hant-TW','演算法'),('zh-Hans-CN','算法'),('en','algorithm')]:
            res=lookup(self.db,loc,word)
            self.assertEqual(len(res),1)
            self.assertEqual(res[0]['concept_id'],'CELL-C0121')
    def test_batch03_bidirectional(self):
        for loc,text in [('zh-Hant-TW','早餐'),('zh-Hans-CN','早餐'),('en','breakfast')]:
            r=lookup(self.db,loc,text)
            self.assertEqual(len(r),1)
            self.assertEqual((r[0]['traditional'],r[0]['simplified'],r[0]['english']),('早餐','早餐','breakfast'))
    def test_terminology(self):
        self.assertEqual(lookup(self.db,'en','wavelength')[0]['traditional'],'波長')
        self.assertEqual(lookup(self.db,'en','blood pressure')[0]['simplified'],'血压')
        self.assertEqual(lookup(self.db,'en','metaphor')[0]['traditional'],'比喻')
    def test_many_to_one_meaning_preserved(self):
        self.assertEqual({x[0] for x in ambiguous_forms(self.db,'发')},{'發','髮'})
        self.assertEqual({x[0] for x in ambiguous_forms(self.db,'后')},{'後','后'})
        self.assertEqual({x[0] for x in ambiguous_forms(self.db,'干')},{'乾','幹'})
        self.assertEqual({x[0] for x in ambiguous_forms(self.db,'里')},{'裡','里'})
    def test_no_automatic_reverse(self):
        with sqlite3.connect(self.db) as c:
            self.assertEqual(c.execute('SELECT count(*) FROM form_candidate WHERE ambiguity="context_needed"').fetchone()[0],8)
    def test_quality_flags(self):
        with sqlite3.connect(self.db) as c:
            self.assertGreaterEqual(c.execute('SELECT count(*) FROM quality_issue').fetchone()[0],1)
            self.assertEqual(c.execute("SELECT count(*) FROM quality_issue WHERE severity='block'").fetchone()[0],0)
    def test_review_status(self):
        self.assertEqual(self.manifest['review_status'],{'draft_review':333,'seed_review_pending':90})
    def test_no_fake_pronunciations(self):
        with sqlite3.connect(self.db) as c:
            self.assertEqual(c.execute("SELECT count(*) FROM pronunciation p JOIN concept c USING(concept_id) WHERE c.status='draft_review'").fetchone()[0],0)
    def test_no_external_dictionary_tables(self):
        with sqlite3.connect(self.db) as c:
            tabs={x[0] for x in c.execute('SELECT name FROM sqlite_master WHERE type="table"')}
            self.assertNotIn('lexicon_mobile',tabs)
            self.assertNotIn('chewing',tabs)
    def test_bare_schema(self):
        with sqlite3.connect(self.db) as c:
            self.assertEqual(c.execute('PRAGMA integrity_check').fetchone()[0],'ok')
            self.assertEqual(c.execute('PRAGMA foreign_key_check').fetchall(),[])
            self.assertEqual(c.execute("SELECT value FROM metadata WHERE key='schema'").fetchone()[0],SCHEMA)
    def test_exports(self):
        target=Path(self.tmp.name)/'export.json'
        self.assertEqual(export(self.db,target),423)
        data=json.loads(target.read_text('utf8'))
        self.assertEqual(len(data['records']),423)
        self.assertEqual(data['schema'],SCHEMA)
    def test_english_not_lost(self):
        for term in ['hello','algorithm','blood pressure','metaphor']:
            self.assertTrue(lookup(self.db,'en',term))
    def test_invalid_locale(self):
        with self.assertRaises(ValueError):lookup(self.db,'zz','book')
    def test_input_not_modified(self):
        self.assertEqual(self.manifest['batch03_sha256'],sha(ROOT/'data/cell_seed_batch03.tsv'))
    def test_bad_batch_dup(self):
        rows=read_batch(ROOT/'data/cell_seed_batch03.tsv')
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'dup.tsv'
            with p.open('w',encoding='utf8',newline='') as f:
                w=csv.DictWriter(f,fieldnames=rows[0].keys(),delimiter='\t');w.writeheader();w.writerow(rows[0]);w.writerow(rows[0])
            with self.assertRaises(ValueError):read_batch(p)
    def test_existing_triple_blocked(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'existing.tsv'
            with p.open('w',encoding='utf8',newline='') as f:
                f.write('domain\ttraditional\tsimplified\tenglish\tpos\n')
                f.write('computing\t電腦\t电脑\tcomputer\tnoun\n')
            with self.assertRaises(ValueError):build(output=Path(d)/'invalid.sqlite3',batch=p)
    def test_tsv_quality(self):
        r=read_batch(ROOT/'data/cell_seed_batch03.tsv')
        self.assertEqual(len(r),127)
        self.assertTrue(all(len(x['english'])>0 for x in r))

if __name__=='__main__':unittest.main()

class TestCLI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory()
        cls.db=Path(cls.tmp.name)/'cli.sqlite3'
        build(output=cls.db)
    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()
    def test_command_line_word(self):
        from query import main
        from contextlib import redirect_stdout
        from io import StringIO
        b=StringIO()
        with redirect_stdout(b):main(['--database',str(self.db),'--locale','en','--word','passport'])
        result=json.loads(b.getvalue());self.assertEqual(result['results'][0]['traditional'],'護照')
    def test_command_line_ambiguous(self):
        from query import main
        from contextlib import redirect_stdout
        from io import StringIO
        b=StringIO()
        with redirect_stdout(b):main(['--database',str(self.db),'--ambiguous','发'])
        self.assertEqual(len(json.loads(b.getvalue())['results']),2)
    def test_command_line_export(self):
        from query import main
        from contextlib import redirect_stdout
        from io import StringIO
        p=Path(self.tmp.name)/'json_out.json'
        with redirect_stdout(StringIO()):main(['--database',str(self.db),'--export',str(p)])
        self.assertEqual(len(json.loads(p.read_text('utf8'))['records']),423)
