#!/usr/bin/env python3
"""Synthetic leak fixtures; never fetch or read private repositories."""
import importlib.util
import unittest
from pathlib import Path

SCRIPT=Path(__file__).with_name("check_public_privacy.py")
spec=importlib.util.spec_from_file_location("check_public_privacy",SCRIPT)
gate=importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

class PublicPrivacyTests(unittest.TestCase):
    def test_public_repository_allowed(self):
        self.assertEqual(gate.scan_text("https://github.com/SunTung/Public-Showcase","sample"),[])
        self.assertEqual(gate.scan_text("SunTung/CELL-DEFENDER","sample"),[])
    def test_private_repo_reference_rejected(self):
        self.assertTrue(gate.scan_text("https://github.com/SunTung/private-example","sample"))
        self.assertTrue(gate.scan_text("SunTung/private-example","sample"))
    def test_private_source_path_rejected(self):
        self.assertTrue(gate.scan_text("private_projects/research/demo","sample"))
        self.assertTrue(gate.scan_text("research_tracking/20261114/detail.json","sample"))
    def test_private_drive_url_rejected(self):
        self.assertTrue(gate.scan_text("https://drive.google.com/file/d/example","sample"))
    def test_json_secret_fields_rejected(self):
        self.assertTrue(gate.scan_object({"ok":{"private_path":"foo"}},"sample"))
        self.assertFalse(gate.scan_object({"public_label":"generic"},"sample"))
    def test_token_patterns_rejected(self):
        self.assertTrue(gate.scan_text("ghp_"+("x"*20),"sample"))
    def test_no_false_positive_on_private_word(self):
        self.assertFalse(gate.scan_text("Private materials are not published.","sample"))

if __name__ == "__main__":
    unittest.main()
