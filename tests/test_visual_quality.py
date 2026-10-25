"""Regression tests for rendered composition and causal-motion quality gates."""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from tools import visual_quality as vq


def rgb_frame(width: int, height: int, points: set[tuple[int, int]], color=(236, 239, 244)) -> bytes:
    pixels = bytearray(vq.BG_RGB * (width * height))
    for x, y in points:
        i = (y * width + x) * 3
        pixels[i:i + 3] = bytes(color)
    return bytes(pixels)


class FrameProfileTests(unittest.TestCase):
    def test_profile_reports_density_and_two_dimensional_coverage(self):
        frame = rgb_frame(10, 10, {(x, y) for x in range(2, 8) for y in range(3, 7)})
        profile = vq.frame_profile(frame, (10, 10))
        self.assertAlmostEqual(profile.foreground_share, 0.24)
        self.assertAlmostEqual(profile.width_share, 0.60)
        self.assertAlmostEqual(profile.height_share, 0.40)

    def test_h264_sized_background_noise_is_not_content(self):
        noisy_bg = bytes((20, 21, 27)) * 16
        self.assertEqual(vq.frame_profile(noisy_bg, (4, 4)), vq.FrameProfile(0.0, 0.0, 0.0))

    def test_bad_rgb_buffer_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "expected 48 RGB bytes"):
            vq.frame_profile(b"short", (4, 4))

    def test_motion_uses_luma_change(self):
        dark = bytes((15, 17, 23)) * 4
        light = bytes((235, 237, 243)) * 4
        self.assertEqual(vq.gray_motion(dark, dark), 0.0)
        self.assertGreater(vq.gray_motion(dark, light), 200)
        with self.assertRaisesRegex(ValueError, "same RGB dimensions"):
            vq.gray_motion(dark, light[:-3])

    def test_representative_sample_is_inside_each_beat(self):
        self.assertEqual(
            vq.representative_times({"B1": [0.0, 4.0], "B2": [4.5, 10.5]}),
            {"B1": 2.8, "B2": 8.7},
        )


class RenderedQualityJudgeTests(unittest.TestCase):
    def test_reference_like_metrics_pass(self):
        metrics = {
            "opening_motion_min": 0.45,
            "visual_density_median": 0.20,
            "stage_height_median": 0.70,
            "beat_visuals": {
                f"B{i}": {"foreground_share": 0.20, "width_share": 0.72, "height_share": 0.55}
                for i in range(1, 10)
            },
        }
        self.assertEqual(
            vq.judge_rendered(metrics, existing_opening_motion_floor=0.15),
            {"opening-quality": [], "stage-coverage": [], "layout-variety": []},
        )

    def test_barely_clearing_old_opening_floor_fails_quality_margin(self):
        issues = vq.judge_rendered(
            {"opening_motion_min": 0.153, "beat_visuals": {}},
            existing_opening_motion_floor=0.15,
        )
        self.assertTrue(issues["opening-quality"])
        self.assertIn("quality floor 0.300", issues["opening-quality"][0])

    def test_too_many_sparse_beats_fail(self):
        profiles = {
            f"B{i}": {"foreground_share": 0.01 if i <= 3 else 0.08,
                       "width_share": 0.50, "height_share": 0.50}
            for i in range(1, 10)
        }
        issues = vq.judge_rendered(
            {"opening_motion_min": 1.0, "visual_density_median": 0.08,
             "stage_height_median": 0.50, "beat_visuals": profiles},
            existing_opening_motion_floor=0.15,
        )
        self.assertEqual(issues["opening-quality"], [])
        self.assertIn("B1, B2, B3", issues["stage-coverage"][0])

    def test_repetitive_wide_shallow_compositions_fail(self):
        profiles = {
            f"B{i}": {"foreground_share": 0.07, "width_share": 0.80,
                       "height_share": 0.20 if i <= 4 else 0.50}
            for i in range(1, 10)
        }
        issues = vq.judge_rendered(
            {"opening_motion_min": 1.0, "visual_density_median": 0.20,
             "stage_height_median": 0.40, "beat_visuals": profiles},
            existing_opening_motion_floor=0.15,
        )
        self.assertIn("4 beats collapse into wide horizontal strips", issues["layout-variety"][0])

    def test_thresholds_preserve_both_reference_exports_and_reject_episode_003(self):
        """Lock the limits to measurements from the three 2026-10-07 master exports."""

        def measured(opening, density_median, height_median, profiles):
            return {
                "opening_motion_min": opening,
                "visual_density_median": density_median,
                "stage_height_median": height_median,
                "beat_visuals": {
                    f"B{i}": {"foreground_share": density, "width_share": width,
                              "height_share": height}
                    for i, (density, width, height) in enumerate(profiles, 1)
                },
            }

        episode_001 = measured(0.552, 0.2230, 0.77, [
            (.1514, 1.0000, .98), (.2008, .9583, .71), (.2230, .8854, .77),
            (.2880, .9375, .33), (.1416, .7604, .96), (.2720, .8750, .97),
            (.2553, .8542, .75), (.2845, .9583, .82), (.1502, .9583, .42),
        ])
        episode_002 = measured(0.479, 0.3178, 0.79, [
            (.1629, .7500, .92), (.3535, .8750, .87), (.4758, .9583, .79),
            (.2818, .9271, .33), (.3178, .6771, .91), (.5469, .9583, .99),
            (.4509, .9167, .59), (.1747, .7500, .71), (.1013, .9271, .29),
        ])
        episode_003 = measured(0.077, 0.1665, 0.53, [
            (.1211, .9688, .24), (.2577, .6667, .59), (.2327, .8542, .67),
            (.1194, .6979, .43), (.1665, .8438, .61), (.2529, .8542, .72),
            (.2828, .8333, .53), (.0826, .8750, .22), (.1437, .9896, .41),
        ])

        for reference in (episode_001, episode_002):
            with self.subTest(reference=reference["opening_motion_min"]):
                issues = vq.judge_rendered(reference, existing_opening_motion_floor=0.15)
                self.assertFalse(any(issues.values()), issues)
        issues = vq.judge_rendered(episode_003, existing_opening_motion_floor=0.15)
        self.assertTrue(issues["opening-quality"])
        self.assertTrue(issues["stage-coverage"])
        self.assertTrue(issues["layout-variety"])


class RenderedMeasurementTests(unittest.TestCase):
    def test_measure_video_samples_the_whole_opening_and_one_settled_frame_per_beat(self):
        width, height = vq.SAMPLE_SIZE
        dark = rgb_frame(width, height, set())
        light = rgb_frame(width, height, {(x, y) for x in range(width) for y in range(height)})
        half = rgb_frame(width, height, {(x, y) for x in range(width // 2) for y in range(height)})
        with mock.patch.object(
            vq, "rgb_frame", side_effect=[dark, half, light, half, dark, half, light]
        ) as decode:
            metrics = vq.measure_video(Path("episode.mp4"), {"B1": [0.0, 4.0], "B2": [4.0, 8.0]})
        self.assertEqual(decode.call_count, 7)
        self.assertEqual([call.args[1] for call in decode.call_args_list[:5]], [0.0, .25, .5, .75, 1.0])
        self.assertEqual([call.args[1] for call in decode.call_args_list[5:]], [2.8, 6.8])
        self.assertEqual(set(metrics["beat_visuals"]), {"B1", "B2"})


class SourceMotionTests(unittest.TestCase):
    def inspect(self, source: str) -> vq.SceneMotionReport:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "scene.py"
            path.write_text(textwrap.dedent(source), encoding="utf-8")
            return vq.inspect_scene_motion(path)

    def test_generic_fades_pulses_and_highlights_do_not_count_as_causal(self):
        report = self.inspect("""
            class Episode:
                def construct(self):
                    with self.beat("B1") as b:
                        self.play(FadeIn(card), Indicate(card), card.animate.scale(1.1))
                    with self.beat("B2") as b:
                        self.play(FadeOut(card), GrowFromCenter(label))
        """)
        self.assertEqual(report.beats, {"B1": 0, "B2": 0})

    def test_geometry_changes_and_transformations_count(self):
        report = self.inspect("""
            class Episode:
                def construct(self):
                    with self.beat("B1") as b:
                        self.play(token.animate.shift(RIGHT), FadeIn(label))
                    with self.beat("B2") as b:
                        self.play(ReplacementTransform(old, new))
                    with self.beat("B3") as b:
                        self.play(MoveAlongPath(dot, route))
        """)
        self.assertEqual(report.beats, {"B1": 1, "B2": 1, "B3": 1})

    def test_reusable_mechanism_helper_is_credited_to_both_beats(self):
        report = self.inspect("""
            class Episode:
                def trick(self):
                    self.play(surface.animate.stretch_to_fit_width(4))

                def construct(self):
                    with self.beat("B3") as b:
                        self.trick()
                    with self.beat("B6") as b:
                        self.trick()
        """)
        self.assertEqual(report.beats, {"B3": 1, "B6": 1})
        self.assertIn("animate.stretch_to_fit_width", report.evidence["B3"][0])

    def test_seven_story_beats_and_both_mechanism_replays_are_required(self):
        beats = {f"B{i}": (1 if i <= 7 else 0) for i in range(1, 10)}
        report = vq.SceneMotionReport(beats, {beat: [] for beat in beats})
        self.assertEqual(vq.judge_scene_motion(report), [])
        beats["B6"] = 0
        beats["B8"] = 1
        issues = vq.judge_scene_motion(vq.SceneMotionReport(beats, {}))
        self.assertIn("B6", issues[0] if len(issues) == 1 else " ".join(issues))


class DeliveryNoteTests(unittest.TestCase):
    def test_notes_are_explicitly_marked_as_manual_not_synthesis_input(self):
        audit = vq.delivery_note_audit({"B1": "Stress the hook.", "B2": ""})
        self.assertEqual(audit["notes_present"], ["B1"])
        self.assertFalse(audit["notes_drive_synthesis"])
        self.assertTrue(audit["manual_listen_required"])


if __name__ == "__main__":
    unittest.main()
