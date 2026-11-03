"""Draws every drawn part into gallery.png and pins their shapes in frozen.json.

    vid uv run python -m resources.gallery          redraw gallery.png
    vid uv run python -m resources.gallery --pin    also rewrite frozen.json

Pinning a changed shape needs the creator's approval: a part's look is part of the house style,
and a re-render of a finished video would pick up the change. tests/test_resources.py fails while
a shape differs from its pin. A part with words pins its structure only, since fonts differ between
machines.
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

from manim import BOLD, RIGHT, Scene, VGroup, tempconfig

from kit.parts import text
from kit.style import A_COLOR, B_COLOR, BG, LINK_COLOR, MUTED

from . import icons
from .parts import Flow, bridge, panel, phase_pill, phase_pills, stamp

HERE = Path(__file__).parent
GALLERY = HERE / "gallery.png"
FROZEN = HERE / "frozen.json"
COLUMNS = 7
TILE = (2.3, 1.95)
ROOM = (2.0, 1.2)  # the largest width and height of a part in its tile


def _plate():
    return icons.plate(icons.person(A_COLOR), A_COLOR)


def _bridge():
    start, end = panel(0.7, 0.7, A_COLOR), panel(0.7, 0.7, B_COLOR).shift(2.6 * RIGHT)
    return VGroup(start, bridge(start, end, color=MUTED), end)


def _flow():
    return Flow([-1, 0, 0], [1, 0, 0], spacing=0.4, phase=0.1).stop()


def catalogue() -> dict[str, tuple]:
    """Every drawn part: name -> (builder, has words). The gallery and the pins both use it."""
    colors = (A_COLOR, B_COLOR, LINK_COLOR)
    parts = {name: ((lambda f=getattr(icons, name), c=colors[i % 3]: f(c)), False)
             for i, name in enumerate(n for n in icons.__all__ if n != "plate")}
    parts["plate"] = (_plate, False)
    parts["panel"] = (lambda: panel(1.6, 1.0, A_COLOR), False)
    parts["bridge"] = (_bridge, False)
    parts["Flow"] = (_flow, False)
    parts["phase_pill"] = (lambda: phase_pill(1, "WORD"), True)
    parts["phase_pills"] = (lambda: phase_pills(("ONE", "TWO")), True)
    parts["stamp"] = (lambda: stamp("WORD", B_COLOR, tilt=0.1), True)
    return parts


def measure(mob, has_words: bool) -> dict:
    """What a pin holds. Family counts are stable; sizes only without words, as fonts differ."""
    pin = {"parts": len(mob.submobjects), "family": len(mob.get_family())}
    if not has_words:
        pin |= {"width": round(mob.width, 3), "height": round(mob.height, 3), "points": len(mob.get_all_points())}
    return pin


def pins() -> dict:
    return {name: measure(build(), words) for name, (build, words) in catalogue().items()}


class Sheet(Scene):
    def construct(self):
        names = catalogue()
        rows = -(-len(names) // COLUMNS)
        for i, (name, (build, _)) in enumerate(names.items()):
            x = (i % COLUMNS + 0.5 - COLUMNS / 2) * TILE[0]
            y = (rows / 2 - i // COLUMNS - 0.5) * TILE[1]
            part = build()
            part.scale(min(1.0, ROOM[0] / part.width, ROOM[1] / part.height)).move_to([x, y + 0.2, 0])
            self.add(part, text(name, 20, MUTED, BOLD).move_to([x, y - 0.74, 0]))


def draw() -> Path:
    rows = -(-len(catalogue()) // COLUMNS)
    width, height = COLUMNS * TILE[0], rows * TILE[1]
    settings = {
        "pixel_width": 1400, "pixel_height": round(1400 * height / width), "frame_width": width, "frame_height": height,
        "background_color": BG, "save_last_frame": True, "write_to_movie": False, "disable_caching": True,
        "verbosity": "ERROR", "progress_bar": "none",
    }
    with tempfile.TemporaryDirectory() as scratch, tempconfig({**settings, "media_dir": scratch}):
        sheet = Sheet()
        sheet.render()
        sheet.renderer.camera.get_image().convert("RGB").save(GALLERY, optimize=True)
    return GALLERY


if __name__ == "__main__":
    print(draw())
    if "--pin" in sys.argv[1:]:
        FROZEN.write_text(json.dumps(pins(), indent=1, sort_keys=True) + "\n", encoding="utf-8")
        print(FROZEN)
