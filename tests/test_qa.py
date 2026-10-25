"""Tests for the export QA (tools/qa.py) on synthetic captions, logs and measurements."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tests.episode_fixture import BEATS, write_script
from tools import qa
from tools.scriptfile import load_script

SRT = """1
00:00:00,000 --> 00:00:01,500
Every rocket uses an idea

2
00:00:01,600 --> 00:00:03,000
from a 1900 kettle.

3
00:00:03,300 --> 00:00:09,000
In 1900, a cook watched the lid of her kettle jump. The steam inside pushed it up again and again.
"""

LOG = """[blackdetect @ 0x1] black_start:4.2 black_end:4.9 black_duration:0.7
[freezedetect @ 0x2] lavfi.freezedetect.freeze_start: 10.5
[freezedetect @ 0x2] lavfi.freezedetect.freeze_duration: 1.2
[freezedetect @ 0x2] lavfi.freezedetect.freeze_end: 11.7
[freezedetect @ 0x2] lavfi.freezedetect.freeze_start: 52.0
[Parsed_ebur128_0 @ 0x3] Summary:

  Integrated loudness:
    I:         -14.3 LUFS
    Threshold: -24.4 LUFS

  True peak:
    Peak:       -2.4 dBFS
"""

GOOD = {
    "width": 1080, "height": 1920, "fps": 60.0, "video_codec": "h264", "audio_codec": "aac",
    "sample_rate": 48000, "duration_s": 55.0, "narration_start_s": 0.0, "first_frame_contrast": 20.0,
    "first_frame_motion": 1.0, "hook_end_s": 4.0, "mechanism_beat": "B3", "answer_start_s": 12.0,
    "answer_share": 12 / 55, "words": 150, "wpm": 170.0, "sentence_pause_s": 0.5,
    "sentence_pauses_measured": 6, "beats": {f"B{i}": [0, 1] for i in range(1, 10)},
    "black_max_s": 0.6, "freeze_max_s": 1.1, "lufs": -14.2, "true_peak_db": -2.5,
}


class CaptionTimingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        ep = Path(self.tmp.name)
        write_script(ep, {"B1": BEATS["B1"], "B2": BEATS["B2"]})
        self.script = load_script(ep / "script.md")

    def tearDown(self):
        self.tmp.cleanup()

    def test_srt_cues_are_parsed(self):
        cues = qa.parse_srt(SRT)
        self.assertEqual(len(cues), 3)
        self.assertEqual(cues[1], qa.Cue(1.6, 3.0, "from a 1900 kettle."))

    def test_beats_are_timed_from_the_cues_that_say_them(self):
        times, problems = qa.beat_times(self.script, qa.parse_srt(SRT))
        self.assertEqual(problems, [])
        self.assertEqual(times, {"B1": (0.0, 3.0), "B2": (3.3, 9.0)})

    def test_changed_words_or_extra_cues_are_reported(self):
        _, problems = qa.beat_times(self.script, qa.parse_srt(SRT.replace("1900 kettle", "1901 kettle")))
        self.assertTrue(problems and problems[0].startswith("B1: the captions say"), problems)
        _, problems = qa.beat_times(self.script, qa.parse_srt(SRT + "\n4\n00:00:09,100 --> 00:00:10,000\nBonus line.\n"))
        self.assertEqual(problems, ["1 caption cue(s) after the last beat"])


class MeasurementTests(unittest.TestCase):
    def test_scan_log_gives_black_freeze_and_loudness(self):
        m = qa.parse_scan(LOG, duration=55.0)
        self.assertEqual(m, {"black_max_s": 0.7, "freeze_max_s": 3.0, "lufs": -14.3, "true_peak_db": -2.4})

    def test_frame_contrast_and_motion(self):
        flat, varied = bytes([16] * 100), bytes([16, 200] * 50)
        self.assertEqual(qa.contrast(flat), 0.0)
        self.assertGreater(qa.contrast(varied), 50)
        self.assertEqual(qa.motion(flat, flat), 0.0)
        self.assertAlmostEqual(qa.motion(flat, varied), 92.0)

    def test_sentence_pauses_take_the_longest_inner_silences(self):
        script = mock.Mock(beats={"B2": mock.Mock(vo=BEATS["B2"]), "B4": mock.Mock(vo=BEATS["B4"])})
        spans = ([(0.0, 0.05), (1.2, 1.35), (3.1, 3.62), (8.0, 8.4)], 8.4)
        with mock.patch.object(qa, "silences", return_value=spans):
            pauses = qa.sentence_pauses(script, {BEATS["B2"]: Path("b2.wav"), BEATS["B4"]: Path("b4.wav")})
        self.assertEqual([round(p, 2) for p in pauses], [0.52])


class ReportContractTests(unittest.TestCase):
    def test_run_writes_export_identity_and_current_pipeline_fingerprint(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ep = root / "episodes" / "009-kettle-x-rocket"
            video = root / "exports" / f"{ep.name}.mp4"
            ep.mkdir(parents=True)
            video.parent.mkdir(parents=True)
            video.write_bytes(b"mp4")

            with (mock.patch.object(qa, "load_section", return_value=qa.Limits()),
                  mock.patch.object(qa, "measure", return_value=({"duration_s": 50.0}, [])),
                  mock.patch.object(qa, "judge", return_value=[]),
                  mock.patch.object(qa, "show", return_value=True)):
                self.assertTrue(qa.run(ep, video))

            report = json.loads(video.with_suffix(".qa.json").read_text(encoding="utf-8"))
            self.assertEqual(report["episode"], ep.name)
            self.assertEqual(report["video"], video.name)
            self.assertEqual(report["pipeline_fingerprint"], qa.qa_contract.pipeline_fingerprint())
            self.assertTrue(qa.qa_contract.report_is_current(
                report, episode=ep.name, video=video.name
            ))


class JudgeTests(unittest.TestCase):
    lim = qa.Limits()

    def failed(self, problems=(), **changes) -> dict[str, list[str]]:
        results = qa.judge({**GOOD, **changes}, list(problems), self.lim)
        return {r.rule: r.issues for r in results if r.status == "fail"}

    def test_a_good_export_passes(self):
        self.assertEqual(self.failed(), {})

    def test_each_measurement_has_its_limit(self):
        self.assertIn("length", self.failed(duration_s=61.1))
        self.assertIn("format", self.failed(fps=30.0))
        self.assertIn("cold-open", self.failed(narration_start_s=0.8))
        self.assertIn("cold-open", self.failed(first_frame_contrast=1.0))
        self.assertIn("cold-open", self.failed(first_frame_motion=0.0))
        self.assertIn("hook-time", self.failed(hook_end_s=7.5))
        self.assertIn("early-answer", self.failed(answer_share=0.5))
        self.assertIn("speech-rate", self.failed(wpm=205.0))
        self.assertIn("speech-rate", self.failed(wpm=110.0))
        self.assertIn("delivery-pace", self.failed(wpm=147.0))
        self.assertIn("pauses", self.failed(sentence_pause_s=0.2))
        self.assertIn("loudness", self.failed(lufs=-18.0))
        self.assertIn("loudness", self.failed(true_peak_db=-0.5))
        self.assertIn("dead-air", self.failed(black_max_s=1.4))
        self.assertIn("dead-air", self.failed(freeze_max_s=3.5))

    def test_delivery_pace_is_stricter_than_the_comprehension_safety_band(self):
        failed = self.failed(wpm=147.0)
        self.assertNotIn("speech-rate", failed)
        self.assertIn("delivery-pace", failed)
        self.assertIn("sound-only", failed["delivery-pace"][0])

    def test_delivery_band_preserves_both_references_and_flags_episode_003(self):
        self.assertNotIn("delivery-pace", self.failed(wpm=163.2))
        self.assertNotIn("delivery-pace", self.failed(wpm=177.3))
        self.assertIn("delivery-pace", self.failed(wpm=147.0))

    def test_rendered_visual_quality_is_an_export_gate(self):
        good_profiles = {
            f"B{i}": {"foreground_share": .20, "width_share": .70, "height_share": .70}
            for i in range(1, 10)
        }
        good = {
            "opening_motion_min": .48,
            "opening_motion_mean": .50,
            "visual_density_median": .20,
            "stage_height_median": .70,
            "beat_visuals": good_profiles,
        }
        failures = self.failed(**good)
        for rule in ("opening-quality", "stage-coverage", "layout-variety"):
            self.assertNotIn(rule, failures)

        weak = {
            **good,
            "opening_motion_min": .08,
            "opening_motion_mean": .10,
            "visual_density_median": .12,
            "stage_height_median": .35,
            "beat_visuals": {
                f"B{i}": {"foreground_share": .08, "width_share": .85, "height_share": .30}
                for i in range(1, 10)
            },
        }
        failures = self.failed(**weak)
        self.assertIn("opening-quality", failures)
        self.assertIn("stage-coverage", failures)
        self.assertIn("layout-variety", failures)

    def test_rendered_visual_quality_skips_for_legacy_metric_dictionaries(self):
        statuses = {r.rule: r.status for r in qa.judge(GOOD, [], self.lim)}
        for rule in ("opening-quality", "stage-coverage", "layout-variety"):
            self.assertEqual(statuses[rule], "skip")

    def test_timing_waits_for_matching_captions(self):
        results = {r.rule: r for r in qa.judge(GOOD, ["B2: the captions say ..."], self.lim)}
        self.assertEqual(results["captions"].status, "fail")
        for rule in ("hook-time", "early-answer", "speech-rate", "delivery-pace"):
            self.assertEqual(results[rule].status, "skip")

    def test_pauses_are_skipped_without_cached_voice_audio(self):
        results = {r.rule: r.status for r in qa.judge({**GOOD, "sentence_pause_s": None}, [], self.lim)}
        self.assertEqual(results["pauses"], "skip")


class PreviewPaceTests(unittest.TestCase):
    """`vid preview` prints the pace with the export's own formula, before any final render."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ep = Path(self.tmp.name)
        write_script(self.ep, {"B1": BEATS["B1"], "B2": BEATS["B2"]})

    def tearDown(self):
        self.tmp.cleanup()

    def test_pace_uses_the_export_formula_once_every_beat_is_voiced(self):
        files = {BEATS["B1"]: Path("b1.wav"), BEATS["B2"]: Path("b2.wav")}
        with (mock.patch.object(qa, "voice_files", return_value=files),
              mock.patch.object(qa, "media_seconds", side_effect=[3.0, 6.0])):
            words, talk, wpm = qa.narration_pace(self.ep)
        expected = len(qa.tokens(BEATS["B1"])) + len(qa.tokens(BEATS["B2"]))
        self.assertEqual((words, talk), (expected, 9.0))
        self.assertEqual(wpm, round(expected / 9.0 * 60, 1))

    def test_no_pace_until_every_beat_has_its_voice(self):
        with mock.patch.object(qa, "voice_files", return_value={BEATS["B1"]: Path("b1.wav")}):
            self.assertIsNone(qa.narration_pace(self.ep))


class PictureRuleTests(unittest.TestCase):
    """The picture rules `vid qa` and `vid frames` share."""

    lim = qa.Limits()

    @staticmethod
    def metrics(density=0.3, height=0.7, opening=1.0) -> dict:
        beats = {f"B{i}": {"foreground_share": density, "width_share": 0.9, "height_share": height}
                 for i in range(1, 10)}
        return {"opening_motion_min": opening, "opening_motion_mean": opening, "beat_visuals": beats,
                "visual_density_median": density, "stage_height_median": height}

    def status(self, m: dict) -> dict[str, str]:
        return {r.rule: r.status for r in qa.picture_results(m, self.lim)}

    def test_a_full_tall_moving_composition_passes(self):
        self.assertEqual(self.status(self.metrics()),
                         {"opening-quality": "pass", "stage-coverage": "pass", "layout-variety": "pass"})

    def test_sparse_flat_or_still_compositions_fail_their_own_rule(self):
        self.assertEqual(self.status(self.metrics(density=0.05))["stage-coverage"], "fail")
        self.assertEqual(self.status(self.metrics(height=0.3))["layout-variety"], "fail")
        self.assertEqual(self.status(self.metrics(opening=0.0))["opening-quality"], "fail")

    def test_without_rendered_samples_the_rules_skip(self):
        self.assertEqual(set(self.status({}).values()), {"skip"})


if __name__ == "__main__":
    unittest.main()
