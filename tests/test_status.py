"""Tests for the walkthrough tracker (tools/status.py) and the Learn report (tools/report.py)."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tests.episode_fixture import make_episode
from tools import qa_contract, report, status

ROOT = Path(__file__).resolve().parents[1]


class StatusTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.exports, self.media, self.results = root / "exports", root / "media", root / "results.csv"
        self.exports.mkdir()
        self.patch = mock.patch.multiple(status, EXPORTS=self.exports, MEDIA=self.media, RESULTS=self.results)
        self.patch.start()

    def tearDown(self):
        self.patch.stop()
        self.tmp.cleanup()

    def step_now(self, ep: Path) -> str:
        return status.current(status.steps(ep, full=False)).name

    def test_a_new_episode_starts_with_the_brief(self):
        ep = Path(self.tmp.name) / "episodes" / "010-new-pair"
        ep.mkdir(parents=True)
        for template in (ROOT / "templates").glob("*.md"):
            (ep / template.name).write_text(template.read_text(encoding="utf-8").replace("{slug}", ep.name),
                                            encoding="utf-8")
        self.assertEqual(self.step_now(ep), "Brief")

    def test_steps_advance_with_the_files_and_stale_exports_count_as_undone(self):
        ep = make_episode(Path(self.tmp.name) / "episodes")
        self.assertEqual(self.step_now(ep), "Alignment")
        report_file = self.media / ep.name / "alignment-report.json"
        report_file.parent.mkdir(parents=True)
        report_file.write_text(json.dumps({"passed": True, "reports": [{}]}), encoding="utf-8")
        self.assertEqual(self.step_now(ep), "Final")
        video, qa_file = self.exports / f"{ep.name}.mp4", self.exports / f"{ep.name}.qa.json"
        video.write_bytes(b"mp4")
        qa_file.write_text(json.dumps({
            "episode": ep.name,
            "video": video.name,
            "passed": True,
            "pipeline_fingerprint": qa_contract.pipeline_fingerprint(),
            "results": [],
        }), encoding="utf-8")
        self.assertEqual(self.step_now(ep), "Publish")
        later = video.stat().st_mtime + 60
        os.utime(ep / "scene.py", (later, later))
        final = next(s for s in status.steps(ep, full=False) if s.name == "Final")
        self.assertFalse(final.done)
        self.assertIn("export older than scene.py", final.detail)

    def test_old_qa_report_cannot_mark_a_new_pipeline_as_done(self):
        ep = make_episode(Path(self.tmp.name) / "episodes")
        report_file = self.media / ep.name / "alignment-report.json"
        report_file.parent.mkdir(parents=True)
        report_file.write_text(json.dumps({"passed": True, "reports": [{}]}), encoding="utf-8")
        video, qa_file = self.exports / f"{ep.name}.mp4", self.exports / f"{ep.name}.qa.json"
        video.write_bytes(b"mp4")
        qa_file.write_text(json.dumps({
            "episode": ep.name,
            "video": video.name,
            "passed": True,
            "pipeline_fingerprint": "from-an-older-pipeline",
            "results": [],
        }), encoding="utf-8")

        final = next(s for s in status.steps(ep, full=False) if s.name == "Final")
        self.assertFalse(final.done)
        self.assertIn("rules changed", final.detail)

    def test_qa_report_copied_from_another_export_is_rejected(self):
        ep = make_episode(Path(self.tmp.name) / "episodes")
        report_file = self.media / ep.name / "alignment-report.json"
        report_file.parent.mkdir(parents=True)
        report_file.write_text(json.dumps({"passed": True, "reports": [{}]}), encoding="utf-8")
        video, qa_file = self.exports / f"{ep.name}.mp4", self.exports / f"{ep.name}.qa.json"
        video.write_bytes(b"mp4")
        qa_file.write_text(json.dumps({
            "episode": "008-some-other-pair",
            "video": "008-some-other-pair.mp4",
            "passed": True,
            "pipeline_fingerprint": qa_contract.pipeline_fingerprint(),
            "results": [],
        }), encoding="utf-8")

        final = next(s for s in status.steps(ep, full=False) if s.name == "Final")
        self.assertFalse(final.done)
        self.assertIn("another export", final.detail)

    def test_legacy_qa_report_without_fingerprint_is_stale(self):
        ep = make_episode(Path(self.tmp.name) / "episodes")
        report_file = self.media / ep.name / "alignment-report.json"
        report_file.parent.mkdir(parents=True)
        report_file.write_text(json.dumps({"passed": True, "reports": [{}]}), encoding="utf-8")
        video, qa_file = self.exports / f"{ep.name}.mp4", self.exports / f"{ep.name}.qa.json"
        video.write_bytes(b"mp4")
        qa_file.write_text(json.dumps({
            "episode": ep.name,
            "video": video.name,
            "passed": True,
            "results": [],
        }), encoding="utf-8")

        final = next(s for s in status.steps(ep, full=False) if s.name == "Final")
        self.assertFalse(final.done)
        self.assertIn("rules changed", final.detail)

    def test_publish_and_learn_need_ticks_and_results(self):
        ep = make_episode(Path(self.tmp.name) / "episodes")
        (ep / "publish.md").write_text("- [x] uploaded\n- [ ] captions\n", encoding="utf-8")
        self.assertEqual(status.boxes((ep / "publish.md").read_text(encoding="utf-8")), (1, 2))
        self.results.write_text("episode,days_live,views\n009-kettle-x-rocket,7,1200\n", encoding="utf-8")
        self.assertEqual(status.result_rows("009", self.results), 1)
        self.assertEqual(status.result_rows("010", self.results), 0)

    def test_publish_template_keeps_both_manual_delivery_reviews(self):
        template = (ROOT / "templates" / "publish.md").read_text(encoding="utf-8")
        self.assertIn("Watched on a phone by the creator, with sound and muted", template)
        self.assertIn("Listened once without watching", template)
        self.assertIn("without sounding rushed or flat", template)


class ReportTests(unittest.TestCase):
    def test_latest_reading_wins_and_cells_are_formatted(self):
        with tempfile.TemporaryDirectory() as tmp:
            csv_path = Path(tmp) / "results.csv"
            csv_path.write_text("episode,days_live,views\n001,1,100\n001,28,9000\n001,7,4000\n002,1,50\n",
                                encoding="utf-8")
            latest = report.latest_results(csv_path)
        self.assertEqual(latest["001"]["views"], "9000")
        self.assertEqual(latest["002"]["days_live"], "1")
        self.assertEqual(report.cell(0.218, "answer_share"), "22%")
        self.assertEqual(report.cell(0.504, "sentence_pause_s"), "0.5")
        self.assertEqual(report.cell(61.099, "duration_s"), "61.1")
        self.assertEqual(report.cell(None), "-")


if __name__ == "__main__":
    unittest.main()
