"""Tests for the contact-sheet tool (tools/frames.py) without decoding a real video."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from PIL import Image

from tools import frames


def fake_grab(video: Path, t: float, out: Path, size=frames.PHONE) -> Path:
    Image.new("RGB", size or frames.PHONE, "#123456").save(out)
    return out


class PartialSheetTests(unittest.TestCase):
    TIMES = {"B1": (0.0, 3.0), "B2": (3.0, 6.0), "B3": (6.0, 9.0), "B4": (9.0, 12.0)}

    def sheets(self, media: Path, **kwargs) -> list[Path]:
        with (mock.patch.object(frames, "MEDIA", media),
              mock.patch.object(frames, "timed", return_value=(Path("v.mp4"), self.TIMES)),
              mock.patch.object(frames, "grab", side_effect=fake_grab)):
            return frames.contact_sheets(Path("009-kettle-x-rocket"), **kwargs)

    def test_all_beats_make_full_sheets_and_a_cover(self):
        with tempfile.TemporaryDirectory() as tmp:
            names = [p.name for p in self.sheets(Path(tmp))]
        self.assertEqual(names, ["sheet-1.png", "sheet-2.png", "cover.png"])

    def test_chosen_beats_cannot_pass_for_the_full_sheets(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths = self.sheets(Path(tmp), beats=["B3", "B1"])
            names = [p.name for p in paths]
            w, h = frames.PHONE
            with Image.open(paths[0]) as sheet:
                self.assertEqual(sheet.size, (3 * (w + 10) + 10, 2 * (h + 26 + 10) + 10))  # two beats, three frames each
            frames_made = sorted(p.name for p in paths[0].parent.glob("B*.png"))
        self.assertEqual(names, ["beats-1.png"])
        self.assertEqual(frames_made, [f"{b}-{m}.png" for b in ("B1", "B3") for m in sorted(frames.MOMENTS)])

    def test_an_unknown_beat_is_an_error_that_lists_the_real_ones(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(SystemExit, "B9.*B1, B2, B3, B4"):
                self.sheets(Path(tmp), beats=["B9"])


class MomentSheetTests(unittest.TestCase):
    def test_one_labeled_frame_per_second_four_to_a_row(self):
        with tempfile.TemporaryDirectory() as tmp:
            media = Path(tmp)
            with (mock.patch.object(frames, "MEDIA", media),
                  mock.patch.object(frames, "grab", side_effect=fake_grab)):
                path = frames.moment_sheet(Path("009-kettle-x-rocket"), Path("v.mp4"), [1.0, 2.5, 3.0, 4.0, 5.5])
            w, h = frames.PHONE
            with Image.open(path) as sheet:
                self.assertEqual(sheet.size, (4 * (w + 10) + 10, 2 * (h + 26 + 10) + 10))
            self.assertEqual(len(list(path.parent.glob("at-*.png"))), 5)

    def test_a_new_request_replaces_the_old_moment_frames(self):
        with tempfile.TemporaryDirectory() as tmp:
            media = Path(tmp)
            with (mock.patch.object(frames, "MEDIA", media),
                  mock.patch.object(frames, "grab", side_effect=fake_grab)):
                frames.moment_sheet(Path("009-kettle-x-rocket"), Path("v.mp4"), [1.0, 2.0, 3.0])
                path = frames.moment_sheet(Path("009-kettle-x-rocket"), Path("v.mp4"), [4.0])
            self.assertEqual([p.name for p in path.parent.glob("at-*.png")], ["at-0004.00.png"])


class PictureCheckTests(unittest.TestCase):
    def test_the_render_is_judged_with_the_export_rules_and_limits(self):
        metrics = {"opening_motion_min": 1.0, "opening_motion_mean": 1.0, "visual_density_median": 0.3,
                   "stage_height_median": 0.7,
                   "beat_visuals": {"B1": {"foreground_share": 0.3, "width_share": 0.9, "height_share": 0.7}}}
        with (mock.patch.object(frames.visual_quality, "measure_video", return_value=metrics) as measure,
              mock.patch.object(frames, "show", return_value=True) as show):
            self.assertTrue(frames.picture_check(Path("v.mp4"), {"B1": (0.0, 4.25)}))
        measure.assert_called_once_with(Path("v.mp4"), {"B1": [0.0, 4.25]})
        results = show.call_args.args[1]
        self.assertEqual([(r.rule, r.status) for r in results],
                         [("opening-quality", "pass"), ("stage-coverage", "pass"), ("layout-variety", "pass")])


if __name__ == "__main__":
    unittest.main()
