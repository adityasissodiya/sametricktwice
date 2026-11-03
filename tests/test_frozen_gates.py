"""Freezes what makes the videos pass: the limits and the list of rules (resources/GATES.md)."""

from __future__ import annotations

import dataclasses
import re
import tempfile
import tomllib
import unittest
from pathlib import Path

from tests.episode_fixture import make_episode
from tests.test_qa import GOOD
from tools import design, qa

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "resources" / "GATES.md"
APPROVAL = ("resources/GATES.md froze this value, and the finished videos passed with it. It changes only "
            "with the creator's approval (AGENTS.md, 'Ask the creator first'); then update the page too.")


def frozen() -> dict:
    return tomllib.loads(re.search(r"```toml\n(.*?)```", PAGE.read_text(encoding="utf-8"), re.S)[1])


def toml(name: str) -> dict:
    return tomllib.loads((ROOT / name).read_text(encoding="utf-8"))


def listed(heading: str) -> set[str]:
    """The rule names in the table under one heading of the page."""
    page = PAGE.read_text(encoding="utf-8")
    section = page[page.index(f"## {heading}"):]
    section = section[:section.index("\n## ", 3)]
    return set(re.findall(r"^\| `([a-z-]+)` \|", section, re.M))


class FrozenNumberTests(unittest.TestCase):
    def test_check_limits(self):
        self.assertEqual(dataclasses.asdict(design.load_section(design.Limits, "check")), frozen()["check"], APPROVAL)

    def test_qa_limits(self):
        self.assertEqual(dataclasses.asdict(design.load_section(qa.Limits, "qa")), frozen()["qa"], APPROVAL)

    def test_plain_english_limits(self):
        self.assertEqual(toml("ste.toml"), frozen()["ste"], APPROVAL)

    def test_the_narrator(self):
        self.assertEqual(toml("voice.toml"), frozen()["voice"], APPROVAL)

    def test_the_series_constants(self):
        self.assertEqual(toml("series.toml"), frozen()["series"], APPROVAL)

    def test_the_alignment_tolerance(self):
        source = (ROOT / "kit" / "alignment.py").read_text(encoding="utf-8")
        live = {"tolerance": float(re.search(r"^DEFAULT_TOLERANCE = (.+)$", source, re.M)[1]),
                "max_passes": int(re.search(r"^DEFAULT_MAX_PASSES = (.+)$", source, re.M)[1])}
        self.assertEqual(live, frozen()["alignment"], APPROVAL)


class RosterTests(unittest.TestCase):
    """A rule the page does not explain sends the next agent back to reading tools/."""

    def test_the_page_lists_exactly_the_source_rules(self):
        with tempfile.TemporaryDirectory() as tmp:
            live = {r.rule for r in design.check(make_episode(Path(tmp)), final=True)}
        self.assertEqual(listed("Source rules"), live, "add or remove the rule in resources/GATES.md")

    def test_the_page_lists_exactly_the_export_rules(self):
        live = {r.rule for r in qa.judge(GOOD, [], qa.Limits())}
        self.assertEqual(listed("Export rules"), live, "add or remove the rule in resources/GATES.md")


if __name__ == "__main__":
    unittest.main()
