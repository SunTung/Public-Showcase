#!/usr/bin/env python3
"""Synthetic release tests; uses temporary public-like directories, never private corpora."""
import hashlib
import importlib.util
import json
import pathlib
import tempfile
import unittest
from unittest.mock import patch

ROOT = pathlib.Path(__file__).resolve().parents[2]
MODULE = ROOT / "public-training-corpus" / "validate_public_corpus.py"
spec = importlib.util.spec_from_file_location("public_corpus_validator", MODULE)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)

class ReleaseBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = pathlib.Path(self.tmp.name)
        (self.base/"texts").mkdir()
        self.sample = b"Sample public domain history text.\n"
        (self.base/"texts"/"history.txt").write_bytes(self.sample)
        sha=hashlib.sha1(b"blob "+str(len(self.sample)).encode("ascii")+b"\0"+self.sample).hexdigest()
        self.doc={"schema":"public_training_corpus_v1","auto_publish":False,
                  "entries":[{"id":"history","path":"texts/history.txt","status":"published",
                              "training_approved_for_external_ingestion":True,
                              "rights_basis":"original historical work public domain",
                              "source_urls":["https://www.gutenberg.org/ebooks/5"],
                              "git_blob_sha":sha}]}
        self.write_catalog()
        self.patch=patch.object(validator,"BASE",self.base)
        self.patch.start()
        self.addCleanup(self.patch.stop)

    def write_catalog(self):
        (self.base/"catalog.json").write_text(json.dumps(self.doc),encoding="utf-8")

    def test_valid_release(self):
        self.assertEqual(validator.validate(),1)

    def test_unlisted_file_fails_closed(self):
        (self.base/"texts"/"unreviewed.txt").write_text("unreviewed",encoding="utf-8")
        with self.assertRaisesRegex(ValueError,"do not exactly match"):
            validator.validate()

    def test_modified_source_hash_fails(self):
        (self.base/"texts"/"history.txt").write_bytes(b"tampered\n")
        with self.assertRaisesRegex(ValueError,"Git blob mismatch"):
            validator.validate()

    def test_missing_rights_evidence_fails(self):
        self.doc["entries"][0].pop("rights_basis")
        self.write_catalog()
        with self.assertRaisesRegex(ValueError,"Missing public origin"):
            validator.validate()

    def test_unapproved_source_fails(self):
        self.doc["entries"][0]["training_approved_for_external_ingestion"]=False
        self.write_catalog()
        with self.assertRaisesRegex(ValueError,"Not approved"):
            validator.validate()

if __name__=="__main__":
    unittest.main()
