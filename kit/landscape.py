"""Landscape specials: the house style on a 16:9 frame, for explainers that are not Shorts.

A special lives in specials/<name>/ and sets `format: landscape` in its script front matter;
`vid` then renders it at 960x540 (preview) or 1920x1080 (final). Its scene imports this
module instead of the vertical kit:

    from kit.landscape import *

    class Episode(LandscapeScene):
        def construct(self):
            with self.beat("B1") as b:
                ...

Importing it turns Manim's frame to 16:9 at the series' scale (1 unit = 135 px at 1080p, as
in the Shorts, so every kit size and stroke keeps its pixel size), and re-exports the kit
with the wide-frame geometry under the same names (SAFE_LEFT, STAGE_CENTER, CAPTION_CENTER,
...), so a landscape scene reads like a vertical one. There is no Shorts UI to avoid: the
safe area is the 90% title-safe rectangle, the header runs along its top edge and the
captions sit in a band along its bottom edge.

The Shorts never import this module, and kit/style.py and kit/short.py stay as they are:
both are inputs of the export-QA fingerprint (tools/qa_contract.py).
"""

from __future__ import annotations

import textwrap

import numpy as np
from manim import *  # noqa: F403

# No __all__: like `from kit import *`, a star import of this module gives Manim, the style, the
# parts and the scene classes; the wide geometry below replaces the vertical values of the same
# names from kit/style.py.
from . import parts
from .alignment import AlignmentError, AlignmentLoop, AlignmentSession, Box, alignment_guides  # noqa: F401
from .parts import *  # noqa: F403
from .short import BeatTime, Captions, ShortScene, caption_chunks, colorize, show_caption  # noqa: F401
from .style import *  # noqa: F403

# 16:9 at the Shorts' scale: 8 units tall, so 1 unit = 135 px at 1920x1080.
FRAME_H = 8.0
FRAME_W = FRAME_H * 16 / 9
config.frame_height = FRAME_H
config.frame_width = FRAME_H * config.pixel_width / config.pixel_height

# The 90% title-safe rectangle. Nothing covers a landscape player except its controls, which
# appear on hover along the bottom edge, below the caption band.
SAFE_LEFT, SAFE_RIGHT = -0.45 * FRAME_W, 0.45 * FRAME_W
SAFE_TOP, SAFE_BOTTOM = 0.45 * FRAME_H, -0.45 * FRAME_H
SAFE_CENTER = ORIGIN.copy()
SAFE_BOX = Box(SAFE_LEFT, SAFE_RIGHT, SAFE_BOTTOM, SAFE_TOP)
HEADER_Y = SAFE_TOP - 0.28
CAPTION_CENTER = (SAFE_BOTTOM + 0.55) * UP
# The stage: everything between the header band and the caption band.
STAGE_TOP, STAGE_BOTTOM = HEADER_Y - 0.5, CAPTION_CENTER[1] + 0.62
STAGE_CENTER = (STAGE_TOP + STAGE_BOTTOM) / 2 * UP
STAGE_WIDTH = SAFE_RIGHT - SAFE_LEFT
STAGE_HEIGHT = STAGE_TOP - STAGE_BOTTOM
STAGE_BOX = Box(SAFE_LEFT, SAFE_RIGHT, STAGE_BOTTOM, STAGE_TOP)


def wide_header(number, words, color):
    """Top band: kit.parts' number pill and uppercase label at the left title-safe edge, and
    the faint rule running on to the right edge."""
    pill = RoundedRectangle(
        corner_radius=0.16, width=0.9, height=0.46,
        fill_color=color, fill_opacity=0.15, stroke_color=color, stroke_width=2,
    )
    number_label = parts.text(f"{number:02d}", 21, color, BOLD).move_to(pill)
    label = parts.text(words.upper(), 21, MUTED, BOLD).next_to(pill, RIGHT, buff=0.16)
    head = VGroup(pill, number_label, label)
    head.shift([SAFE_LEFT - pill.get_left()[0], HEADER_Y - pill.get_y(), 0])
    rule = Line(label.get_right() + 0.16 * RIGHT, [SAFE_RIGHT, HEADER_Y, 0], color=FAINT, stroke_width=2)
    return VGroup(pill, number_label, label, rule)


_CAPTION_BOX_H = None


def wide_caption(text: str, colors: dict[str, str]) -> Mobject:
    """kit.short's caption chunk, centered in the wide caption band, with the wide stage's
    width as its limit (a three-word chunk is never squeezed to fit a phone)."""
    global _CAPTION_BOX_H
    if _CAPTION_BOX_H is None:
        _CAPTION_BOX_H = MarkupText("Hg", font=BODY_FONT, weight=BOLD, font_size=CAPTION_SIZE).height + 0.36
    label = MarkupText(colorize(text, colors), font=BODY_FONT, weight=BOLD, font_size=CAPTION_SIZE, color=INK)
    if label.width > STAGE_WIDTH - 0.5:
        label.scale_to_fit_width(STAGE_WIDTH - 0.5)
    box = RoundedRectangle(corner_radius=0.16, width=label.width + 0.5, height=_CAPTION_BOX_H,
                           fill_color=BG, fill_opacity=0.75, stroke_width=0)
    return VGroup(box, label.move_to(box)).move_to(CAPTION_CENTER).set_z_index(100)


class WideCaptions(Captions):
    """kit.short's captions, timed the same way, drawn by wide_caption."""

    def schedule(self, text: str, start: float, duration: float, colors: dict[str, str]):
        self.remove(*self.submobjects)
        self.cues, self.shown = [], None
        chunks = caption_chunks(text)
        total = sum(len(c) for c in chunks)
        t = start
        for chunk in chunks:
            d = duration * len(chunk) / total
            cue = show_caption(wide_caption(chunk, colors), False)
            self.add(cue)
            self.cues.append((t, t + d, cue))
            t += d


def wide_guides() -> Mobject:
    """Overlay for `vid preview --guides`: the title-safe rectangle, the stage and the
    caption band."""
    red = ALERT
    safe = Rectangle(width=SAFE_RIGHT - SAFE_LEFT, height=SAFE_TOP - SAFE_BOTTOM,
                     stroke_color=red, stroke_width=2).move_to(SAFE_CENTER)
    stage = Rectangle(width=STAGE_WIDTH, height=STAGE_HEIGHT, stroke_color=MUTED,
                      stroke_width=1.5).move_to(STAGE_CENTER)
    band = Rectangle(width=STAGE_WIDTH, height=STAGE_BOTTOM - SAFE_BOTTOM, stroke_width=0,
                     fill_color=red, fill_opacity=0.10).align_to(safe, DOWN)
    note = Text("title safe (90%)", font=BODY_FONT, font_size=18, color=red)
    note.next_to(safe, UP, buff=0.06).align_to(safe, RIGHT)
    return VGroup(DashedVMobject(safe, num_dashes=120), DashedVMobject(stage, num_dashes=120),
                  band, note).set_z_index(200)


class LandscapeScene(ShortScene):
    """ShortScene on the wide frame: the same beats, voice, sound cues and alignment loops,
    with wide captions, wide guides and wide animatic cards."""

    def setup(self):
        super().setup()
        self.remove(self.cc)
        self.cc = WideCaptions(self)
        self.add(self.cc)
        if self.guides:
            self.remove(self.guides)
            self.guides = wide_guides()
            self.add(self.guides)
        if self.alignment_guides:
            self.remove(self.alignment_guides)
            self.alignment_guides = alignment_guides(axis_x=float(STAGE_CENTER[0]),
                                                     axis_y=float(STAGE_CENTER[1]), bounds=SAFE_BOX)
            self.add(self.alignment_guides)

    def alignment_loop(self, label: str, **kwargs):
        """A loop measured on the wide frame: its axis is the stage center and inside_safe
        keeps a composition inside the title-safe rectangle."""
        kwargs.setdefault("axis_x", float(STAGE_CENTER[0]))
        kwargs.setdefault("axis_y", float(STAGE_CENTER[1]))
        kwargs.setdefault("safe_bounds", SAFE_BOX)
        return self.alignment.loop(label, **kwargs)

    def placeholder(self, b):
        """Animatic card for a beat that has no animation yet: its VIS and TXT lines."""
        beat = b.beat
        lines = [Text(f"{beat.id} · {beat.label}".upper(), font=TITLE_FONT, font_size=LABEL_SIZE, color=MUTED)]
        if beat.txt:
            lines.append(Text(beat.txt, font=TITLE_FONT, weight=BOLD, font_size=TITLE_SIZE, color=INK))
        if beat.vis:
            wrapped = "\n".join(textwrap.wrap(beat.vis, 64))
            lines.append(Text(wrapped, font=BODY_FONT, font_size=BODY_SIZE - 8, color=MUTED))
        card = VGroup(*lines).arrange(DOWN, buff=0.4)
        if card.width > STAGE_WIDTH - 0.8:
            card.scale_to_fit_width(STAGE_WIDTH - 0.8)
        if card.height > STAGE_HEIGHT - 0.8:
            card.scale_to_fit_height(STAGE_HEIGHT - 0.8)
        frame = DashedVMobject(
            RoundedRectangle(corner_radius=0.25, width=card.width + 0.8, height=card.height + 0.6,
                             stroke_color=MUTED, stroke_width=2),
            num_dashes=72,
        )
        group = VGroup(frame, card).move_to(STAGE_CENTER)
        fade = max(min(0.3, b.duration / 4), 1 / config.frame_rate)
        self.play(FadeIn(group, shift=0.15 * UP), run_time=fade)
        self.hold(b, leave=fade)
        self.play(FadeOut(group), run_time=fade)
