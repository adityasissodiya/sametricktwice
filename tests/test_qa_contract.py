"""Tests for invalidating saved QA reports when the production checks change."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools import qa_contract


class QaContractTests(unittest.TestCase):
    def test_fingerprint_is_stable_for_unchanged_inputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "rule.py"
            path.write_text("LIMIT = 1\n", encoding="utf-8")
            self.assertEqual(
                qa_contract.pipeline_fingerprint([path]),
                qa_contract.pipeline_fingerprint([path]),
            )

    def test_fingerprint_changes_when_a_rule_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "rule.py"
            path.write_text("LIMIT = 1\n", encoding="utf-8")
            before = qa_contract.pipeline_fingerprint([path])
            path.write_text("LIMIT = 2\n", encoding="utf-8")
            self.assertNotEqual(before, qa_contract.pipeline_fingerprint([path]))

    def test_fingerprint_ignores_line_endings(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "rule.py"
            path.write_bytes(b"LIMIT = 1\nNAME = 'x'\n")
            unix = qa_contract.pipeline_fingerprint([path])
            path.write_bytes(b"LIMIT = 1\r\nNAME = 'x'\r\n")
            self.assertEqual(unix, qa_contract.pipeline_fingerprint([path]))

    def test_report_must_contain_the_current_fingerprint(self):
        current = qa_contract.pipeline_fingerprint()
        self.assertTrue(qa_contract.report_is_current({"pipeline_fingerprint": current}))
        self.assertFalse(qa_contract.report_is_current({}))
        self.assertFalse(qa_contract.report_is_current({"pipeline_fingerprint": "old"}))

    def test_report_identity_must_match_the_requested_export(self):
        report = {
            "episode": "009-kettle-x-rocket",
            "video": "009-kettle-x-rocket.mp4",
            "pipeline_fingerprint": qa_contract.pipeline_fingerprint(),
        }
        self.assertTrue(qa_contract.report_is_current(
            report, episode=report["episode"], video=report["video"]
        ))
        self.assertFalse(qa_contract.report_is_current(
            report, episode="010-other", video=report["video"]
        ))

    def test_transitive_qa_sources_are_fingerprinted(self):
        names = {path.name for path in qa_contract.QA_DEPENDENCIES}
        self.assertTrue({"qa.py", "qa_contract.py", "sfxqa.py", "visual_quality.py",
                         "design.py", "scriptfile.py"}.issubset(names))


if __name__ == "__main__":
    unittest.main()
