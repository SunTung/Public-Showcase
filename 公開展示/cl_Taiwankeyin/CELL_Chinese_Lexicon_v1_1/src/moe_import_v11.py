#!/usr/bin/env python3
"""Offline, non-mutating MOE XLSX/ZIP -> comparison source and full gap report.

Source files must be acquired separately. Never infer provenance from filenames;
record expected digest and user-supplied acquisition URI/version.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,sqlite3,zipfile
from contextlib import closing
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET

NS={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
FIELDS={'headword':('字詞名','詞目','字詞','詞條','詞目名稱','字詞名稱','headword'),
        'zhuyin':('注音一式','注音','注音符號','注音符號一式','zhuyin'),
        'pinyin':('漢語拼音','漢拼','拼音','pinyin'),
        'source_entry_id':('編號','序號','資料編號','id','source_entry_id')}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def iter_xlsx(data):
    """Read first XLSX worksheet with stdlib, no macros or external resources."""
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        names=z.namelist()
        if any(n.startswith('../') or n.startswith('/') for n in names):raise ValueError('Unsafe XLSX path')
        shared=[]
        if 'xl/sharedStrings.xml' in names:
            node=ET.fromstring(z.read('xl/sharedStrings.xml'))
            shared=[''.join(t.text or '' for t in si.findall('.//m:t',NS)) for si in node.findall('m:si',NS)]
        sheets=sorted(n for n in names if n.startswith('xl/worksheets/sheet') and n.endswith('.xml'))
        if not sheets:raise ValueError('No XLSX sheet')
        # worksheet cell reference may skip columns; do not shift cells left
        for event,el in ET.iterparse(io.BytesIO(z.read(sheets[0])),events=('end',)):
            if el.tag.endswith('}row'):
                cells={}
                for cell in el.findall('m:c',NS):
                    ref=cell.get('r','');letters=''.join(ch for ch in ref if ch.isalpha())
                    if not letters:continue
                    index=0
                    for ch in letters:index=index*26+ord(ch.upper())-64
                    index-=1
                    typ=cell.get('t')
                    v=cell.find('m:v',NS)
                    inline=cell.find('m:is',NS)
                    val=(v.text or '') if v is not None else (''.join(t.text or '' for t in inline.findall('.//m:t',NS)) if inline is not None else '')
                    if typ=='s' and val:val=shared[int(val)]
                    cells[index]=val
                if cells:yield [cells.get(i,'') for i in range(max(cells)+1)]
                el.clear()
def iter_rows(path):
    path=Path(path)
    if path.suffix.lower()=='.xlsx':yield from iter_xlsx(path.read_bytes());return
    if path.suffix.lower()=='.zip':
        with zipfile.ZipFile(path) as z:
            xlsx=[n for n in z.namelist() if n.lower().endswith('.xlsx') and not n.startswith('__MACOSX/')]
            if len(xlsx)!=1:raise ValueError('Expected exactly one XLSX in official ZIP; found '+str(len(xlsx)))
            info=z.getinfo(xlsx[0]);
            if info.file_size>120_000_000:raise ValueError('Excessive XLSX size')
            yield from iter_xlsx(z.read(info));return
    if path.suffix.lower() in ('.tsv','.csv'):
        with path.open(encoding='utf-8-sig',newline='') as f:
            yield from csv.reader(f,delimiter='\t' if path.suffix.lower()=='.tsv' else ',')
        return
    raise ValueError('Supported source: XLSX, ZIP containing XLSX, TSV, CSV')
def normalize_header(x):return ''.join(str(x).strip().lower().split())
def find_columns(header):
    h=[normalize_header(x) for x in header]
    out={}
    for key,aliases in FIELDS.items():
        options=[i for i,x in enumerate(h) if x in [normalize_header(a) for a in aliases]]
        if len(options)>1:raise ValueError('Ambiguous columns for '+key)
        if options:out[key]=options[0]
    if 'headword' not in out:raise ValueError('Missing headword column: '+repr(header[:30]))
    return out
def inspect(db,source,out,source_uri,source_version,expected_sha=None):
    if not source_uri.startswith('https://') or not source_version.strip():raise ValueError('Source URL and version required')
    digest=sha(source)
    if expected_sha and expected_sha.lower()!=digest:raise ValueError('Source SHA-256 mismatch')
    it=iter(iter_rows(source));header=next(it,None)
    if header is None:raise ValueError('Empty source')
    cols=find_columns(header)
    def get(row,k):return str(row[cols[k]]).strip() if k in cols and cols[k]<len(row) else ''
    lookup={};count=0
    for row in it:
        head=get(row,'headword')
        if not head:continue
        count+=1
        # Keep all readings: homographs must not be silently collapsed
        item={'zhuyin':get(row,'zhuyin'),'pinyin':get(row,'pinyin'),
              'source_entry_id':get(row,'source_entry_id') or 'source-row-'+str(count+1)}
        lookup.setdefault(head,[]).append(item)
    uri=Path(db).resolve().as_uri()+'?mode=ro'
    with closing(sqlite3.connect(uri,uri=True)) as c:
        rows=c.execute('''SELECT e.concept_id,e.value,
           (SELECT value FROM pronunciation WHERE concept_id=e.concept_id AND scheme='zhuyin' LIMIT 1),
           (SELECT value FROM pronunciation WHERE concept_id=e.concept_id AND scheme='hanyu-pinyin' LIMIT 1)
           FROM expression e WHERE e.locale='zh-Hant-TW' ORDER BY e.concept_id''').fetchall()
    findings=[]
    for cid,head,z,p in rows:
        options=lookup.get(head,[])
        if not options:status='NOT_FOUND'
        elif len(options)>1:status='MULTIPLE_SOURCE_ENTRIES'
        elif not z or not p:status='CELL_READING_MISSING'
        elif not options[0]['zhuyin'] or not options[0]['pinyin']:status='SOURCE_READING_MISSING'
        elif z==options[0]['zhuyin'] and p==options[0]['pinyin']:status='EXACT_TEXT_MATCH_NOT_APPROVAL'
        else:status='READING_DIFFERENCE'
        findings.append({'concept_id':cid,'headword':head,'status':status,'cell_zhuyin':z,'cell_pinyin':p,'source_entries':options})
    result={'schema':'cell.moe.offline_comparison.v1.1','source_uri':source_uri,'source_version':source_version,
            'source_sha256':digest,'source_rows':count,'source_columns':cols,'concepts_checked':len(findings),
            'counts':dict(Counter(x['status'] for x in findings)),
            'external_authenticity':'NOT_ESTABLISHED_BY_OFFLINE_TOOL',
            'automatic_approvals':0,'findings':findings}
    out=Path(out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return result
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('db');a.add_argument('source');a.add_argument('output');a.add_argument('--source-uri',required=True);a.add_argument('--source-version',required=True);a.add_argument('--expected-sha256');args=a.parse_args()
    r=inspect(args.db,args.source,args.output,args.source_uri,args.source_version,args.expected_sha256)
    print(json.dumps({k:v for k,v in r.items() if k!='findings'},ensure_ascii=False,indent=2))
