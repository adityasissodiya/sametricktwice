"""Stage housekeeping for a scene: class Episode(StageTools, LandscapeScene).

Nothing here calls self.play. The source gates read motion in scene.py only, and they give a
helper credit only if it is a method of the Episode class itself, so all motion stays there.
This module must never import kit.landscape, which turns Manim's frame to 16:9 on import: it
looks at call time for the module the scene chose.
"""

from __future__ import annotations

import sys

from manim import VGroup

from kit.alignment import Box
from kit.parts import beat_header, title
from kit.style import INK, SAFE_LEFT, SAFE_RIGHT

BREATH = 1.4         # seconds of silence after a beat, when a video should feel slow
LONG_BREATH = 2.2    # the same, after the end of a part
TOP_LINE = 0.4       # how far below the stage's top edge a beat's on-screen words sit

# The vertical stage: below the beat header, above the caption band. kit.style has no such box.
_TALL_STAGE = Box(SAFE_LEFT, SAFE_RIGHT, -2.68, 4.5)


def _wide():
    """kit.landscape if this scene imported it, else None."""
    return sys.modules.get("kit.landscape")


def stage_box() -> Box:
    """The stage of the format being rendered, as a kit.alignment.Box."""
    wide = _wide()
    return wide.STAGE_BOX if wide else _TALL_STAGE


class StageTools:
    """Mix in before the scene class. Needs only what ShortScene already provides."""

    top = None  # the beat label now on screen

    def header(self, number, words, color):
        """Swap the beat label at once: a crossfade garbles text this small."""
        if self.top is not None:
            self.remove(self.top)
        wide = _wide()
        self.top = (wide.wide_header if wide else beat_header)(number, words, color)
        self.add(self.top)
        return self.top

    def onscreen(self, words, color=INK, size=40):
        """A beat's on-screen words on the stage's top line. The scene plays them in."""
        box = stage_box()
        return title(words, size, color).move_to([box.center_x, box.top - TOP_LINE, 0])

    def on_stage(self, *keep):
        """Everything on stage but the captions, the guides, the header and `keep`: pass the
        result to FadeOut. Animation groups gather mobjects into one new group, so each kept
        mobject is first made top-level again; a fade of the rest then never takes a part that
        a transform still needs."""
        for mob in keep:
            if not any(mob is m for m in self.mobjects):
                self.add(mob)
        fixed = [self.cc, self.guides, self.alignment_guides, self.top, *keep]
        return [m for m in self.mobjects if not any(m is f for f in fixed)]

    def cut(self):
        """A hard cut between story units: the old picture leaves in one frame. A fade to clear
        the stage would make near-black frames."""
        self.remove(*self.on_stage())

    def fits(self, label, *mobjects):
        """Register a layout keyframe: everything named must already sit on the stage. Nothing
        rescales, so `vid align` reports a slip instead of quietly shrinking the picture."""
        with self.alignment_loop(label) as align:
            align.inside_safe(VGroup(*mobjects), bounds=stage_box(), padding=0.04, allow_scale=False)

    def breath(self, seconds=BREATH):
        """Silence after a beat. The frozen narrator sets the word speed; slowness lives here."""
        self.wait(seconds)


__all__ = ["BREATH", "LONG_BREATH", "StageTools", "stage_box"]
