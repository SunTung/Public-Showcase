#!/usr/bin/env python3
"""Offline tests: use synthetic private inputs; never fetch private repositories in CI."""
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("reconcile_workboard", ROOT / "scripts/reconcile_workboard.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

def fixtures():
    reg = {"records": [
        {"id":"A","audit_round2":{"status":"SOURCE_REVIEWED"},"overall_completion_pct":None},
        {"id":"B","audit_round2":{"status":"SOURCE_ONLY_PENDING"},"overall_completion_pct":None},
    ]}
    wbs = {"work_packages":[
        {"project_id":"A","priority":"P0"},
        {"project_id":"B","priority":"P2"},
    ]}
    pub = {"items":[
        {"id":"A","priority":"P0","source_reviewed":True},
        {"id":"B","priority":"P2","source_reviewed":False},
    ]}
    return reg,wbs,pub

class ReconcileTests(unittest.TestCase):
    def test_unchanged(self):
        r,w,p = fixtures()
        result=MODULE.summarize(r,w,p)
        self.assertEqual(result["review_required_count"],0)
        self.assertFalse(result["automatic_publication"])
        self.assertNotIn("source_path",json.dumps(result))

    def test_priority_source_and_new_project(self):
        r,w,p=fixtures()
        p["items"][0]["priority"]="P1"
        p["items"][1]["source_reviewed"]=True
        p["items"].append({"id":"C","priority":"P0","source_reviewed":False})
        result=MODULE.summarize(r,w,p)
        self.assertEqual(result["review_required_count"],3)
        issues={x["id"]:x["reasons"] for x in result["review_items"]}
        self.assertIn("PRIORITY_CHANGED",issues["A"])
        self.assertIn("SOURCE_REVIEW_STATUS_CHANGED",issues["B"])
        self.assertIn("PUBLIC_ONLY_PROJECT_REQUIRES_REVIEW",issues["C"])

    def test_new_registry_project(self):
        r,w,p=fixtures()
        r["records"].append({"id":"D","audit_round2":{},"overall_completion_pct":None,"source":{"path":"/PRIVATE"}})
        w["work_packages"].append({"project_id":"D","priority":"P1"})
        result=MODULE.summarize(r,w,p)
        self.assertEqual(result["review_items"][0]["id"],"D")
        self.assertNotIn("/PRIVATE",json.dumps(result))

    def test_mismatched_registry_wbs_rejected(self):
        r,w,p=fixtures()
        w["work_packages"].pop()
        with self.assertRaises(ValueError): MODULE.summarize(r,w,p)

    def test_duplicate_rejected(self):
        r,w,p=fixtures()
        r["records"].append(r["records"][0])
        with self.assertRaises(ValueError): MODULE.summarize(r,w,p)

    def test_private_output_only(self):
        r,w,p=fixtures()
        with tempfile.TemporaryDirectory() as temp:
            tmp=Path(temp)
            for name,d in (("r.json",r),("w.json",w),("p.json",p)):
                (tmp/name).write_text(json.dumps(d),encoding="utf-8")
            out=tmp/"review.json"
            cmd=[sys.executable,str(ROOT/"scripts/reconcile_workboard.py"),
                 "--registry",str(tmp/"r.json"),"--wbs",str(tmp/"w.json"),
                 "--public",str(tmp/"p.json"),"--output",str(out)]
            proc=subprocess.run(cmd,text=True,capture_output=True)
            self.assertEqual(proc.returncode,0,proc.stderr)
            self.assertEqual(json.loads(out.read_text())["review_required_count"],0)

if __name__=="__main__":
    unittest.main()
