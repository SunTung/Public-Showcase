#!/usr/bin/env python3
"""Read-only cryptographic snapshot audit; this does not establish source authenticity."""
import hashlib,sqlite3,json
from pathlib import Path

def audit(db):
    issues=[];checked=0
    uri=Path(db).resolve().as_uri()+"?mode=ro"
    try:
        with sqlite3.connect(uri,uri=True) as c:
            for uri,digest,content,state,method in c.execute("SELECT source_uri,digest,captured_text,verification_state,verification_method FROM evidence_snapshot"):
                checked+=1
                if hashlib.sha256(content.encode('utf-8')).hexdigest()!=digest:
                    issues.append({'uri':uri,'issue':'content_digest_mismatch'})
                if not uri.startswith('https://'):
                    issues.append({'uri':uri,'issue':'non_https_source'})
                if method in ('unit-test','test','synthetic',''):
                    issues.append({'uri':uri,'issue':'untrusted_method'})
                if state!='source_confirmed':
                    issues.append({'uri':uri,'issue':'unconfirmed_source'})
            total=c.execute('SELECT COUNT(*) FROM cell_release_v08').fetchone()[0]
    except (sqlite3.Error,OSError) as exc:
        return {'status':'BLOCKED','snapshots':checked,'release_rows':0,'issues':[{'issue':'database_unavailable','detail':type(exc).__name__}]}
    return {'status':'PASS' if not issues else 'BLOCKED','snapshots':checked,'release_rows':total,'issues':issues,'source_authenticity':'NOT_ESTABLISHED_BY_HASH'}

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('db');args=p.parse_args()
 print(json.dumps(audit(args.db),ensure_ascii=False,indent=2))
