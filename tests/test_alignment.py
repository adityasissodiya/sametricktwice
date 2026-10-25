"""Regression tests for the reusable Manim alignment refinement loop."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

try:
    import manim  # noqa: F401
except ImportError:  # e.g. the CI runner, which has no render stack
    raise unittest.SkipTest("needs the render stack (manim)")

from manim import Rectangle, VGroup

from kit.alignment import AlignmentError, AlignmentLoop, AlignmentSession, visual_box
from kit.style import SAFE_BOTTOM, SAFE_LEFT, SAFE_RIGHT, SAFE_TOP, STAGE_CENTER


class AlignmentLoopTests(unittest.TestCase):
    def test_centers_visual_bounds_on_safe_stage_axis(self):
        card = Rectangle(width=2.0, height=1.0).move_to([1.4, 0.2, 0])
        loop = AlignmentLoop("center", on_failure="return")
        loop.centered(card)

        report = loop.refine()

        self.assertTrue(report.passed, report.summary())
        self.assertAlmostEqual(visual_box(card).center_x, float(STAGE_CENTER[0]))

    def test_mirror_pair_shares_baseline_and_axis(self):
        left = Rectangle(width=1.0, height=0.8).move_to([-2.2, 1.0, 0])
        right = Rectangle(width=1.0, height=0.8).move_to([0.2, 1.6, 0])
        loop = AlignmentLoop("mirror", on_failure="return")
        loop.mirror_pair(left, right, y=1.25, min_gap=0.3)

        report = loop.refine()
        left_box, right_box = visual_box(left), visual_box(right)

        self.assertTrue(report.passed, report.summary())
        self.assertAlmostEqual((left_box.center_x + right_box.center_x) / 2, float(STAGE_CENTER[0]))
        self.assertAlmostEqual(left_box.center_y, 1.25)
        self.assertAlmostEqual(right_box.center_y, 1.25)
        self.assertGreaterEqual(right_box.left - left_box.right, 0.3 - loop.tolerance)

    def test_even_row_uses_equal_edge_gaps_and_outer_center(self):
        cards = [
            Rectangle(width=0.8, height=0.7).move_to([-2.5, 0.8, 0]),
            Rectangle(width=1.4, height=1.0).move_to([-0.1, 1.5, 0]),
            Rectangle(width=1.0, height=0.9).move_to([1.8, 0.4, 0]),
        ]
        loop = AlignmentLoop("row", on_failure="return")
        loop.even_row(cards, y=1.1, gap=0.25)

        report = loop.refine()
        boxes = [visual_box(card) for card in cards]
        gaps = [boxes[index + 1].left - boxes[index].right for index in range(2)]

        self.assertTrue(report.passed, report.summary())
        self.assertAlmostEqual(gaps[0], 0.25)
        self.assertAlmostEqual(gaps[1], 0.25)
        self.assertAlmostEqual((boxes[0].left + boxes[-1].right) / 2, float(STAGE_CENTER[0]))
        self.assertTrue(all(abs(box.center_y - 1.1) < 1e-8 for box in boxes))

    def test_inside_safe_scales_and_shifts_oversized_group(self):
        group = VGroup(Rectangle(width=10.0, height=12.0)).move_to([1.0, 1.0, 0])
        loop = AlignmentLoop("safe", on_failure="return")
        loop.inside_safe(group, padding=0.12)

        report = loop.refine()
        box = visual_box(group)

        self.assertTrue(report.passed, report.summary())
        self.assertGreaterEqual(box.left, SAFE_LEFT + 0.12 - loop.tolerance)
        self.assertLessEqual(box.right, SAFE_RIGHT - 0.12 + loop.tolerance)
        self.assertGreaterEqual(box.bottom, SAFE_BOTTOM + 0.12 - loop.tolerance)
        self.assertLessEqual(box.top, SAFE_TOP - 0.12 + loop.tolerance)

    def test_conflicting_constraints_fail_instead_of_oscillating_forever(self):
        card = Rectangle(width=1.0, height=1.0)
        loop = AlignmentLoop("conflict", max_passes=6, on_failure="return")
        loop.centered(card, axis_x=-1.0)
        loop.centered(card, axis_x=1.0)

        report = loop.refine()

        self.assertFalse(report.passed)
        self.assertLessEqual(report.passes, 6)
        self.assertTrue(report.issues)

    def test_strict_session_rejects_a_finished_scene_without_checks(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            report_path = Path(temp_dir) / "alignment-report.json"
            session = AlignmentSession(mode="strict", report_path=report_path)

            with self.assertRaises(AlignmentError):
                session.finish()

            payload = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertFalse(payload["passed"])
            self.assertTrue(payload["missing_checks"])
            self.assertEqual(payload["loop_count"], 0)

    def test_strict_session_persists_a_failed_loop_before_raising(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            report_path = Path(temp_dir) / "alignment-report.json"
            session = AlignmentSession(mode="strict", report_path=report_path, max_passes=2)
            card = Rectangle(width=1.0, height=1.0)
            loop = session.loop("conflict")
            loop.centered(card, axis_x=-1.0)
            loop.centered(card, axis_x=1.0)

            with self.assertRaises(AlignmentError):
                loop.refine()

            payload = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertFalse(payload["passed"])
            self.assertFalse(payload["missing_checks"])
            self.assertEqual(payload["failed_loop_count"], 1)


if __name__ == "__main__":
    unittest.main()
