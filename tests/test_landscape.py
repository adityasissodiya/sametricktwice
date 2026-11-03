"""Tests for landscape specials: kit/landscape.py's geometry and the alignment loop's bounds."""

from __future__ import annotations

import json
import subprocess
import sys
import textwrap
import unittest
from pathlib import Path

try:
    import manim  # noqa: F401
except ImportError:  # e.g. the CI runner, which has no render stack
    raise unittest.SkipTest("needs the render stack (manim)")

from manim import Rectangle

from kit.alignment import AlignmentLoop, Box, visual_box
from tools import special

ROOT = Path(__file__).resolve().parents[1]

# kit.landscape changes Manim's global frame when imported, so it is measured in a child
# process: the other tests keep the vertical frame.
PROBE = textwrap.dedent("""
    import json
    from manim import config
    import kit.landscape as L

    header = L.wide_header(7, "a wide header", L.A_COLOR)
    caption = L.wide_caption("three short words", {})
    print(json.dumps({
        "frame": [config.frame_width, config.frame_height],
        "safe": [L.SAFE_LEFT, L.SAFE_RIGHT, L.SAFE_BOTTOM, L.SAFE_TOP],
        "stage": [L.STAGE_BOX.left, L.STAGE_BOX.right, L.STAGE_BOX.bottom, L.STAGE_BOX.top],
        "header": [header.get_left()[0], header.get_right()[0], header.get_bottom()[1], header.get_top()[1]],
        "caption": [caption.get_left()[0], caption.get_right()[0], caption.get_bottom()[1], caption.get_top()[1]],
        "caption_center": list(map(float, L.CAPTION_CENTER[:2])),
        "frame_wh": [L.FRAME_W, L.FRAME_H],
    }))
""")


# A scene's own import line: everything `from kit import *` gives, with the wide geometry.
STAR_PROBE = textwrap.dedent("""
    import json
    from kit.landscape import *

    print(json.dumps({
        "manim": all(name in globals() for name in ("VGroup", "Create", "Transform", "UP", "config")),
        "kit": all(name in globals() for name in ("text", "pill", "BeatTime", "AlignmentLoop", "A_COLOR")),
        "scene": "LandscapeScene" in globals() and "wide_header" in globals(),
        "stage_width": STAGE_WIDTH,
        "safe_width": SAFE_RIGHT - SAFE_LEFT,
    }))
""")


def probe(code: str = PROBE) -> dict:
    out = subprocess.run([sys.executable, "-c", code], cwd=ROOT, capture_output=True, text=True, check=True)
    return json.loads(out.stdout.strip().splitlines()[-1])


class LandscapeGeometryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.g = probe()

    def test_frame_is_16_9_at_the_shorts_scale(self):
        width, height = self.g["frame"]
        self.assertAlmostEqual(height, 8.0)
        self.assertAlmostEqual(width / height, 16 / 9, places=3)
        self.assertAlmostEqual(1080 / height, 1080 / 8.0)  # 135 px per unit, as in the Shorts

    def test_bands_nest_inside_the_title_safe_area(self):
        left, right, bottom, top = self.g["safe"]
        width, height = self.g["frame_wh"]
        self.assertAlmostEqual(right - left, 0.9 * width)
        self.assertAlmostEqual(top - bottom, 0.9 * height)
        s_left, s_right, s_bottom, s_top = self.g["stage"]
        h_left, h_right, h_bottom, h_top = self.g["header"]
        c_left, c_right, c_bottom, c_top = self.g["caption"]
        self.assertAlmostEqual(h_left, left, places=2)   # header: the full title-safe width
        self.assertAlmostEqual(h_right, right, places=2)
        self.assertLessEqual(h_top, top)
        self.assertGreater(h_bottom, s_top)               # header above the stage
        self.assertLess(c_top, s_bottom)                  # captions below the stage
        self.assertGreaterEqual(c_bottom, bottom)
        self.assertAlmostEqual((c_left + c_right) / 2, self.g["caption_center"][0], places=3)

    def test_a_scene_star_import_gets_manim_the_kit_and_the_wide_geometry(self):
        g = probe(STAR_PROBE)
        self.assertTrue(g["manim"] and g["kit"] and g["scene"], g)
        self.assertAlmostEqual(g["stage_width"], 0.9 * self.g["frame_wh"][0])  # not the 9:16 stage
        self.assertAlmostEqual(g["safe_width"], g["stage_width"])

    def test_qa_samples_the_same_stage_the_kit_draws(self):
        width, height = self.g["frame_wh"]
        s_left, s_right, s_bottom, s_top = self.g["stage"]
        x, y, w, h = special.WIDE_STAGE_CROP
        self.assertAlmostEqual(x, (s_left + width / 2) / width, places=3)
        self.assertAlmostEqual(w, (s_right - s_left) / width, places=3)
        self.assertAlmostEqual(y, (height / 2 - s_top) / height, places=3)
        self.assertAlmostEqual(h, (s_top - s_bottom) / height, places=3)


class SafeBoundsTests(unittest.TestCase):
    def test_a_loop_keeps_content_inside_its_own_safe_rectangle(self):
        wide = Box(-6.4, 6.4, -3.6, 3.6)
        card = Rectangle(width=2.0, height=1.0).move_to([5.0, 0.0, 0])  # outside the 9:16 safe area
        loop = AlignmentLoop("wide", axis_x=0.0, axis_y=0.0, safe_bounds=wide, on_failure="return")
        loop.inside_safe(card)
        report = loop.refine()
        self.assertTrue(report.passed, report.summary())
        self.assertAlmostEqual(visual_box(card).center_x, 5.0)  # inside the wide frame: untouched

    def test_without_safe_bounds_the_shorts_rectangle_applies(self):
        card = Rectangle(width=2.0, height=1.0).move_to([5.0, 0.0, 0])
        loop = AlignmentLoop("tall", on_failure="return")
        loop.inside_safe(card)
        loop.refine()
        self.assertLess(visual_box(card).right, 2.75 + 1e-6)


if __name__ == "__main__":
    unittest.main()
