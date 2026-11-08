#!/usr/bin/env python3
"""Build an indexed Android-only lexicon from the exact verified public data inputs.

The original full RGOS SQLite is held in a private repository. CI must never
receive private credentials. Instead reconstruct the same 158,905 Chewing/OpenCC
rows from pinned public input blobs, verify source hashes and accepted counts.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from pathlib import Path
import sqlite3
import urllib.request
from collections import Counter

UPSTREAM_COMMIT = 'c44e81aef24b06f1509f19e1be54c99812d0c43f'
SOURCE_REPO = 'chewing/libchewing-data'
SOURCES = {
    'word.csv': '04308dd3b31ead3a61d9210ec3fd427dabced12a',
    'tsi.csv': 'a13b3dd87c1c5205d3250ef296d76d2bb23f1900',
}
EXPECTED_ROWS = 158905
EXPECTED_MULTI = 133505
EXPECTED_READINGS = 121377
TONES = 'ˉˊˇˋ˙'
VALID = frozenset('ㄅㄆㄇㄈㄉㄊㄋㄌㄍㄎㄏㄐㄑㄒㄓㄔㄕㄖㄗㄘㄙㄧㄨㄩㄚㄛㄜㄝㄞㄟㄠㄡㄢㄣㄤㄥㄦ'+TONES+' ')
SOURCE_URL = ('https://raw.githubusercontent.com/chewing/libchewing-data/'
              +UPSTREAM_COMMIT+'/dict/chewing/')


def digest(path:Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for part in iter(lambda:stream.read(1024 * 1024),b''):h.update(part)
    return h.hexdigest()


def blob_hash(data:bytes) -> str:
    return hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()


def fetch_pinned(folder:Path):
    folder.mkdir(parents=True,exist_ok=True)
    for name,sha in SOURCES.items():
        file=folder/name
        if file.exists() and blob_hash(file.read_bytes())==sha:continue
        with urllib.request.urlopen(SOURCE_URL+name,timeout=90) as response:
            content=response.read(25_000_001)
        if len(content)>25_000_000 or blob_hash(content)!=sha:
            raise ValueError('Official Chewing source SHA mismatch or oversize: '+name)
        file.write_bytes(content)


def build(source_dir:Path,dest:Path,allow_fixture:bool=False):
    from opencc import OpenCC
    cc=OpenCC('s2twp')
    if not allow_fixture:
        for name,sha in SOURCES.items():
            file=source_dir/name
            if blob_hash(file.read_bytes())!=sha:raise ValueError('Source identity mismatch '+name)
    dest.parent.mkdir(parents=True,exist_ok=True)
    pending=dest.with_suffix('.partial')
    pending.unlink(missing_ok=True)
    db=sqlite3.connect(pending)
    stats=Counter()
    try:
        db.executescript('''PRAGMA journal_mode=DELETE; PRAGMA synchronous=FULL;
          CREATE TABLE lexicon_mobile (
            bare TEXT NOT NULL, reading TEXT NOT NULL, word TEXT NOT NULL,
            frequency INTEGER NOT NULL,
            PRIMARY KEY (bare,reading,word)
          ) WITHOUT ROWID;''')
        for name in SOURCES:
            buf=[]
            with (source_dir/name).open(encoding='utf-8-sig',newline='') as f:
                for parts in csv.reader(f):
                    if not parts or parts[0].lstrip().startswith('#'):continue
                    if len(parts)<3:continue
                    word,freq,reading=(p.strip() for p in parts[:3])
                    if not word or not reading or not freq.isascii() or not freq.isdecimal():continue
                    if any(ch not in VALID for ch in reading):continue
                    syllables=reading.split()
                    if not syllables:continue
                    normalized=' '.join(syllables)
                    new_word=cc.convert(word)
                    if not new_word:continue
                    stats[name+'_parsed']+=1
                    if new_word != word:stats[name+'_converted']+=1
                    bare=''.join(ch for ch in normalized if ch not in TONES)
                    buf.append((bare,normalized,new_word,int(freq)))
                    if len(buf)>=5000:
                        db.executemany('''INSERT INTO lexicon_mobile VALUES (?,?,?,?)
                          ON CONFLICT(bare,reading,word) DO UPDATE SET frequency=max(lexicon_mobile.frequency,excluded.frequency)''',buf)
                        buf.clear()
            if buf:
                db.executemany('''INSERT INTO lexicon_mobile VALUES (?,?,?,?)
                   ON CONFLICT(bare,reading,word) DO UPDATE SET frequency=max(lexicon_mobile.frequency,excluded.frequency)''',buf)
        db.executescript('''
          CREATE INDEX idx_mobile_bare_freq ON lexicon_mobile (bare,frequency DESC);
          CREATE INDEX idx_mobile_reading_freq ON lexicon_mobile (reading,frequency DESC);
          CREATE INDEX idx_mobile_word_prefix ON lexicon_mobile (word,frequency DESC);
        ''')
        totals=db.execute('''SELECT COUNT(*),SUM(CASE WHEN instr(reading,' ')>0 THEN 1 ELSE 0 END),
                         COUNT(DISTINCT reading) FROM lexicon_mobile''').fetchone()
        if not allow_fixture and totals!=(EXPECTED_ROWS,EXPECTED_MULTI,EXPECTED_READINGS):
            raise ValueError(f'Full-corpus row counts disagree with verified Drive baseline: {totals}')
        for bare,word in [('ㄋㄧ','你'),('ㄏㄠ','好'),('ㄓㄨㄥ ㄨㄣ','中文')]:
            if not allow_fixture and not db.execute('SELECT 1 FROM lexicon_mobile WHERE bare=? AND word=?',(bare,word)).fetchone():
                raise ValueError('Known common character/word missing from corpus: '+word)
        if db.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise RuntimeError('Bad SQLite mobile image')
        db.commit()
    finally:
        db.close()
    pending.replace(dest)
    manifest={
        'schema':'cell.taiwankeyin.mobile.full_lexicon.v1',
        'source':SOURCE_REPO,
        'source_commit':UPSTREAM_COMMIT,
        'source_sha_git_blobs':SOURCES,
        'source_data_license':'LGPL-2.1-or-later (source metadata)',
        'normalization':'OpenCC 1.4.2 s2twp (Taiwan variants and phrases)',
        'prior_verified_rgos_rows':EXPECTED_ROWS,
        'prior_verified_rgos_sha256':'57d3d3f332710d6dcab0bbef997407edeb56ca5e9483652fd42fb7404cc01586',
        'data_counts':dict(stats),'mobile_rows':totals[0],
        'multi_syllable_rows':totals[1], 'unique_readings':totals[2],
        'output_bytes':dest.stat().st_size,'output_sha256':digest(dest)
    }
    (dest.parent/'full_lexicon_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('CELL_ANDROID_FULL_LEXICON_PASS '+json.dumps(manifest,ensure_ascii=False))
    return manifest


def main():
    p=argparse.ArgumentParser(description='Exact-source full traditional Chinese dictionary for CELL Android')
    p.add_argument('--source-dir',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--download',action='store_true')
    args=p.parse_args()
    if args.download:fetch_pinned(args.source_dir)
    build(args.source_dir,args.output)

if __name__=='__main__':main()
