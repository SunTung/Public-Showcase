#!/usr/bin/env python3
"""Platform-neutral CELL vocabulary query: JSON output, no network or dependencies."""
import argparse,json
from pathlib import Path
from build_v03 import lookup,ambiguous_forms,export
ROOT=Path(__file__).resolve().parents[1]
def main(argv=None):
    p=argparse.ArgumentParser(description='CELL vocabulary concept lookup')
    p.add_argument('--database',type=Path,default=ROOT/'build/cell_concepts.sqlite3')
    mode=p.add_mutually_exclusive_group(required=True)
    mode.add_argument('--word',type=str)
    mode.add_argument('--ambiguous',type=str)
    mode.add_argument('--export',type=Path)
    p.add_argument('--locale',choices=['zh-Hant-TW','zh-Hans-CN','en'],default='zh-Hant-TW')
    args=p.parse_args(argv)
    if not args.database.is_file():p.error('No CELL database; first run python src/build_v03.py')
    if args.word is not None:
        data={'query':args.word,'locale':args.locale,'results':lookup(args.database,args.locale,args.word)}
    elif args.ambiguous is not None:
        data={'query':args.ambiguous,'results':[{'traditional':r[0],'ambiguity':r[1],'status':r[2]} for r in ambiguous_forms(args.database,args.ambiguous)]}
    else:
        n=export(args.database,args.export);data={'export':str(args.export),'concepts':n}
    print(json.dumps(data,ensure_ascii=False,indent=2))
    return data
if __name__=='__main__':main()
