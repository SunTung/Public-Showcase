#!/usr/bin/env python3
"""v0.9: legacy-first, read-only; reject CELL if snapshot integrity fails."""
import sqlite3
from pathlib import Path
from snapshot_audit_v09 import audit
VALID={'zh-Hant-TW','zh-Hans-CN','en'}

def lookup(cell_db,locale,form,legacy_candidates=(),enabled=False,limit=20):
    if locale not in VALID or not isinstance(form,str) or not form.strip():
        raise ValueError('invalid query')
    limit=max(1,min(100,int(limit)))
    out=[];seen=set()
    for word in legacy_candidates:
        if word not in seen:
            out.append({'text':word,'source':'legacy'});seen.add(word)
    if not enabled:return out[:limit]
    report=audit(cell_db)
    if report['status']!='PASS':return out[:limit]
    try:
        with sqlite3.connect(Path(cell_db).resolve().as_uri()+'?mode=ro',uri=True,timeout=0.25) as c:
            matches=c.execute('SELECT value FROM cell_release_v08 WHERE locale=? AND value=? LIMIT ?', (locale,form,limit)).fetchall()
        for word, in matches:
            if word not in seen:
                out.append({'text':word,'source':'CELL-approved'});seen.add(word)
    except (sqlite3.Error,OSError,ValueError):pass
    return out[:limit]
