"""A small synthetic episode that passes every design rule, for tests to break one rule at a time."""

from __future__ import annotations

import textwrap
from pathlib import Path

BEATS = {
    "B1": "Every rocket uses an idea from a 1900 kettle.",
    "B2": "In 1900, a cook watched the lid of her kettle jump. The steam inside pushed it up again and again.",
    "B3": "Hot water makes steam. The steam needs much more room than the water. So it pushes the lid away.",
    "B4": "That is the trick: heat, steam, push.",
    "B5": "Rocket makers needed a strong push to lift heavy loads from the ground into the sky.",
    "B6": "They used the same trick. Hot gas needs much more room than the fuel, so it pushes the rocket up.",
    "B7": "Then rockets helped kettles in return. Strong rocket metals now make many kettles safe and light.",
    "B8": "Today, every launch and every kettle on a stove uses the same push from hot gas.",
    "B9": "A kettle taught rockets how to fly. Then rockets made kettles better. Same trick, two worlds.",
}
TXT = {"B1": "Kettle × Rocket", "B4": "Heat · Steam · Push"}
FRONT = {
    "title": "Every rocket uses an idea from a kettle",
    "a": "Kettle | kettle, kettles, lid",
    "b": "Rocket | rocket, rockets, launch",
    "link": "Steam | steam, gas, push",
    "glossary": "",
}


def write_script(ep: Path, beats: dict[str, str] | None = None, txt: dict[str, str] | None = None,
                 front: dict[str, str] | None = None) -> None:
    beats = BEATS if beats is None else beats
    txt = TXT if txt is None else txt
    meta = {**FRONT, **(front or {})}
    lines = ["---", *(f"{k}: {v}" for k, v in meta.items()), "---", ""]
    for beat_id, vo in beats.items():
        lines += [f"## {beat_id} · Beat", f"VO: {vo}", "VIS: Shapes.",
                  "NOTE: Keep the line clear; shape its pace and emphasis."]
        if beat_id in txt:
            lines.append(f"TXT: {txt[beat_id]}")
        lines.append("")
    (ep / "script.md").write_text("\n".join(lines), encoding="utf-8")


def write_brief(ep: Path, bridge: str = "Rockets fly with the push of hot gas that lifts a kettle lid.",
                rows: list[str] | None = None) -> None:
    rows = rows if rows is not None else [
        "| C1 | A cook saw a kettle lid jump in 1900 (B1, B2) | [museum](https://example.org/kettle) | | high |",
        "| C2 | Steam needs more room than water (B3, B6) | [physics](https://example.org/steam) | | high |",
        "| C3 | Rockets lift loads with hot gas (B5-B8) | [agency](https://example.org/rocket) | | high |",
        "| F1 | Trick name and kicker (B4, B9) | framing, not a fact claim (C2) | | n/a |",
    ]
    text = textwrap.dedent(f"""\
        # fixture · brief

        **Pair:** A = Kettle · B = Rocket
        **The bridge (one sentence):** {bridge}
        **A helped B by:** steam.

        ## Claim ledger

        | # | Claim, as said (beat) | Source 1 | Source 2 | Confidence |
        |---|---|---|---|---|
        """) + "\n".join(rows) + "\n"
    (ep / "brief.md").write_text(text, encoding="utf-8")


def write_scene(ep: Path, body: str | None = None, beats: list[str] | None = None) -> None:
    if body is None:
        calls = []
        for beat_id in beats or list(BEATS):
            if beat_id == "B3":
                action = ('            self.replay_time = b.duration * 0.80\n'
                          '            self.mechanism(A_COLOR, self.replay_time)\n'
                          '            self.hold(b)')
            elif beat_id == "B6":
                action = ('            self.mechanism(B_COLOR, self.replay_time)\n'
                          '            self.hold(b)')
            else:
                action = (f'            mark = text("{beat_id} label", 24, A_COLOR)\n'
                          '            self.play(mark.animate.shift(0.2 * RIGHT), run_time=b.duration * 0.80)\n'
                          '            self.hold(b)')
            calls.append(f'        with self.beat("{beat_id}") as b:\n{action}')
        body = "\n".join(calls)
    scene = ("from kit import *\n\n\nclass Episode(ShortScene):\n"
             "    def mechanism(self, skin, run_time):\n"
             "        mark = Circle(color=skin)\n"
             "        self.play(mark.animate.shift(0.2 * RIGHT), run_time=run_time)\n\n"
             "    def construct(self):\n"
             + body + "\n")
    (ep / "scene.py").write_text(scene, encoding="utf-8")


def make_episode(root: Path, slug: str = "009-kettle-x-rocket") -> Path:
    ep = root / slug
    ep.mkdir(parents=True)
    write_script(ep)
    write_brief(ep)
    write_scene(ep)
    return ep
