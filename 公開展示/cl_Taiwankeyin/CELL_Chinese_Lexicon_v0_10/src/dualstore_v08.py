#!/usr/bin/env python3
"""Read-only, fail-closed, testable cross-platform CELL adjunct lookup."""
import sqlite3
from pathlib import Path
VALID={'zh-Hant-TW','zh-Hans-CN','en'}

def lookup(cell_db,locale,form,legacy_candidates=(),enabled=False,limit=20):
 if locale not in VALID or not isinstance(form,str) or not form.strip():raise ValueError('invalid query')
 out=[];seen=set()
 for word in legacy_candidates:
  if word not in seen:
   out.append({'text':word,'source':'legacy'});seen.add(word)
 if not enabled:return out[:limit]
 try:
  uri='file:'+str(Path(cell_db).resolve())+'?mode=ro'
  with sqlite3.connect(uri,uri=True,timeout=0.25) as c:
   # query against audited release view, never against draft candidate tables
   matches=c.execute('SELECT value FROM cell_release_v08 WHERE locale=? AND value=? LIMIT ?', (locale,form,max(1,min(100,limit)))).fetchall()
  for word, in matches:
   if word not in seen:
    out.append({'text':word,'source':'CELL-approved'});seen.add(word)
 except (sqlite3.Error,OSError,ValueError):
  # invalid/unreadable CELL DB must not affect existing keyboard output
  pass
 return out[:limit]
