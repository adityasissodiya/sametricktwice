"""Tests for specials (tools/special.py): format, limits overlay, length, format rule, lookup."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tests.episode_fixture import write_script
from tools import special, vid
from tools.scriptfile import load_script


def make_special(root: Path, name: str = "explainer", front: dict[str, str] | None = None,
                 limits: str | None = None) -> Path:
    ep = root / name
    ep.mkdir(parents=True)
    write_script(ep, front=front)
    if limits is not None:
        (ep / "limits.toml").write_text(limits, encoding="utf-8")
    return ep


class FormatTests(unittest.TestCase):
    def test_format_defaults_to_short(self):
        with tempfile.TemporaryDirectory() as tmp:
            ep = make_special(Path(tmp))
            self.assertEqual(special.video_format(ep), "short")
            self.assertEqual(special.frame_size(ep, final=False), (540, 960))
            self.assertEqual(special.frame_size(ep, final=True), (1080, 1920))

    def test_landscape_renders_wide(self):
        with tempfile.TemporaryDirectory() as tmp:
            ep = make_special(Path(tmp), front={"format": "Landscape"})
            self.assertEqual(special.video_format(ep), "landscape")
            self.assertEqual(special.frame_size(ep, final=False), (960, 540))
            self.assertEqual(special.frame_size(ep, final=True), (1920, 1080))
            self.assertEqual(special.thumb_size(ep), (640, 360))

    def test_unknown_format_is_an_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            ep = make_special(Path(tmp), front={"format": "square"})
            with self.assertRaises(SystemExit):
                special.video_format(ep)


class LimitsTests(unittest.TestCase):
    def test_overlay_changes_only_the_named_keys(self):
        with tempfile.TemporaryDirectory() as tmp:
            ep = make_special(Path(tmp), limits="[qa]\nseconds = [150, 240]\n")
            series = special.design.load_section(special.qa.Limits, "qa")
            mine = special.qa_limits(ep)
            self.assertEqual(mine.seconds, [150, 240])
            self.assertEqual(mine.wpm, series.wpm)
            self.assertEqual(mine.hook_end_max, series.hook_end_max)

    def test_no_limits_file_keeps_the_series_limits(self):
        with tempfile.TemporaryDirectory() as tmp:
            ep = make_special(Path(tmp))
            self.assertEqual(special.qa_limits(ep), special.design.load_section(special.qa.Limits, "qa"))
            self.assertEqual(special.ste_config(ep), special.ste.load_config())

    def test_misspelled_key_or_unknown_section_is_an_error(self):
        for text in ("[qa]\nsecond = [150, 240]\n", "[check]\nhook_max_words = 40\n"):
            with tempfile.TemporaryDirectory() as tmp:
                ep = make_special(Path(tmp), limits=text)
                with self.assertRaises(SystemExit, msg=text):
                    special.qa_limits(ep)

    def test_length_uses_the_special_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            ep = make_special(Path(tmp), limits="[ste]\nseconds = [150, 240]\n")
            script = load_script(ep / "script.md")  # the fixture is a Short: about 50 s
            self.assertEqual(special.length(script, ep).status, "fail")
            (ep / "limits.toml").write_text("[ste]\nseconds = [30, 90]\n", encoding="utf-8")
            self.assertEqual(special.length(script, ep).status, "pass")


class FormatRuleTests(unittest.TestCase):
    METRICS = {"width": 1920, "height": 1080, "fps": 60.0, "video_codec": "h264", "audio_codec": "aac",
               "sample_rate": 48000}

    def test_landscape_master_is_1920x1080(self):
        self.assertEqual(special.format_result(self.METRICS, "landscape").status, "pass")
        tall = {**self.METRICS, "width": 1080, "height": 1920}
        self.assertEqual(special.format_result(tall, "landscape").status, "fail")
        self.assertEqual(special.format_result(tall, "short").status, "pass")


class LookupTests(unittest.TestCase):
    def test_vid_finds_specials_by_name_and_tells_them_apart(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            episodes, specials = root / "episodes", root / "specials"
            (episodes / "001-kettle-x-rocket").mkdir(parents=True)
            ep = make_special(specials, "wide-explainer")
            with (mock.patch.object(vid, "EPISODES", episodes), mock.patch.object(vid, "SPECIALS", specials),
                  mock.patch.object(special, "SPECIALS", specials)):
                self.assertEqual(vid.episode("wide-explainer"), ep)
                self.assertEqual(vid.episode("wide"), ep)
                self.assertEqual(vid.episode("001"), episodes / "001-kettle-x-rocket")
                self.assertTrue(special.is_special(ep))
                self.assertFalse(special.is_special(episodes / "001-kettle-x-rocket"))
                self.assertEqual(vid.ref(ep), "wide-explainer")
                self.assertEqual(vid.ref(episodes / "001-kettle-x-rocket"), "001")


if __name__ == "__main__":
    unittest.main()
