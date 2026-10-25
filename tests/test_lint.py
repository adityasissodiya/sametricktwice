"""Tests for the carry-over check (tools/lint.py) on synthetic episodes."""

from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from tools import lint

SCRIPT = """---
a: {a}
b: {b}
link: Trick | trick
glossary:
---
## B1 · Hook
VO: {vo}
VIS: {vis}
"""


def make_episode(root: Path, slug: str, scene: str, a: str, b: str, vo: str, vis: str = "Shapes.",
                 sounds: dict[str, bytes] | None = None) -> Path:
    ep = root / slug
    ep.mkdir(parents=True)
    (ep / "scene.py").write_text(textwrap.dedent(scene), encoding="utf-8")
    (ep / "script.md").write_text(SCRIPT.format(a=a, b=b, vo=vo, vis=vis), encoding="utf-8")
    for name, data in (sounds or {}).items():
        (ep / "audio").mkdir(exist_ok=True)
        (ep / "audio" / name).write_bytes(data)
    return ep


class ScreenStringTests(unittest.TestCase):
    def test_only_text_that_can_reach_the_screen_is_collected(self):
        scene = '''
            """Docstring is not on screen."""
            LABELS = ("FLT 12",)

            def f(self, x):
                with self.alignment_loop("B1 opening composition") as align:
                    align.even_row(x, name="device row")
                with self.beat("B1") as b:
                    self.sfx("tap.wav", -9)
                text("HELLO", 20, "#ECEFF4")
                title(f"{x} piece")
                self.end_card(tagline=("SAME TRICK", "TWO WORLDS"), sound="spark.wav")
        '''
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "scene.py"
            path.write_text(textwrap.dedent(scene), encoding="utf-8")
            self.assertEqual(lint.screen_strings(path), {"FLT 12", "HELLO", "SAME TRICK", "TWO WORLDS"})


class CarryOverTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.episodes, kit = root / "episodes", root / "sfx"
        kit.mkdir()
        (kit / "tap.wav").write_bytes(b"kit-tap")
        self.patch = mock.patch.multiple(lint, EPISODES=self.episodes, KIT_SFX=kit)
        self.patch.start()
        self.first = make_episode(self.episodes, "001-camera-x-chip",
                                  'text("Remember this")\ntext("CAMERA")\n',
                                  "Camera | camera", "Chip | chip", "Old line about chips.",
                                  sounds={"whoosh.wav": b"whoosh-bytes"})

    def tearDown(self):
        self.patch.stop()
        self.tmp.cleanup()

    def kinds(self, ep: Path) -> list[str]:
        return sorted(f.kind for f in lint.lint(ep))

    def test_first_episode_has_nothing_to_carry_over(self):
        self.assertEqual(lint.lint(self.first), [])

    def test_carry_over_of_every_kind_is_reported(self):
        second = make_episode(
            self.episodes, "002-radar-x-phone",
            'text("Remember this")\ntext("Connection map")\ntext("Fresh label")\n',
            "Radar | radar", "Phone | phone", "A camera appears.", vis="Camera and Chip from 001 stay faint.",
            sounds={"copied.wav": b"whoosh-bytes", "tap.wav": b"kit-tap", "a.wav": b"same", "b.wav": b"same"},
        )
        findings = lint.lint(second)
        messages = " | ".join(f.message for f in findings)
        self.assertIn("'Remember this' is on screen in 001", messages)
        self.assertNotIn("Connection map", messages)
        self.assertIn("topic word 'camera' in B1 VO", messages)
        self.assertIn("topic word 'chip' in B1 VIS", messages)
        self.assertIn("script.md:", messages)
        self.assertIn("copy of 001/audio/whoosh.wav", messages)
        self.assertIn("copy of kit/sfx/tap.wav", messages)
        self.assertIn("are the same sound", messages)

    def test_a_topic_this_episode_declares_is_allowed(self):
        second = make_episode(self.episodes, "002-film-x-camera", 'text("Reel")\n',
                              "Film | film", "Camera | camera", "A camera turns film into light.")
        self.assertEqual(self.kinds(second), [])


if __name__ == "__main__":
    unittest.main()
