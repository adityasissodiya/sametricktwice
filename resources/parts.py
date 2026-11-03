"""House grammar shared by the long videos: panels, phase pills, flows, stamps, links.

Words are always arguments, so lint and the on-screen rules see them in scene.py.
"""

from __future__ import annotations

import numpy as np
from manim import BOLD, DOWN, RIGHT, AnimationGroup, Dot, Line, RoundedRectangle, VGroup

from kit.parts import text, title
from kit.style import BG, FAINT, INK, LINK_COLOR, MUTED

from .stage import stage_box

# The faintest tint that still counts as picture in stage-coverage for every house color but
# FAINT, which is too dark to tint with. MUTED falls short at 0.08; the world colors pass at 0.06.
PANEL_OPACITY = 0.10


def panel(width, height, color, opacity=PANEL_OPACITY):
    """A tinted panel behind one part of the story; it stays behind everything drawn on it."""
    return RoundedRectangle(corner_radius=0.26, width=width, height=height, fill_color=color, fill_opacity=opacity,
                            stroke_color=color, stroke_width=2, stroke_opacity=0.55).set_z_index(-1)


def backdrop(color, opacity=PANEL_OPACITY):
    """One world's color across the whole stage, so the viewer knows where they are."""
    box = stage_box()
    return panel(box.width - 0.1, box.height - 0.19, color, opacity).set_stroke(opacity=0.2).move_to(
        [box.center_x, box.center_y, 0])


def phase_pill(number, word, width=2.7, height=0.74, size=24):
    """A step of a process, unlit: box (0), digit (1), word (2)."""
    box = RoundedRectangle(corner_radius=0.16, width=width, height=height, fill_color=MUTED, fill_opacity=0.1,
                           stroke_color=MUTED, stroke_width=2)
    digit = text(str(number), size - 2, MUTED, BOLD).move_to(box.get_left() + 0.36 * RIGHT)
    label = text(word, size, MUTED, BOLD).move_to(box).shift(0.2 * RIGHT)
    return VGroup(box, digit, label)


def phase_pills(words, direction=RIGHT, buff=0.3, **kwargs):
    """One numbered pill per word, in a row or a column. Keeps the viewer's place in a process."""
    pills = [phase_pill(number, word, **kwargs) for number, word in enumerate(words, 1)]
    return VGroup(*pills).arrange(direction, buff=buff)


def light(pill, color):
    """A step begins: its pill fills with the color of the step."""
    box, digit, label = pill
    return AnimationGroup(box.animate.set_stroke(color, width=4).set_fill(color, opacity=0.3),
                          digit.animate.set_color(color), label.animate.set_color(INK))


def dim(pill):
    """A step is over: its pill keeps its color but steps back."""
    box, _, label = pill
    return AnimationGroup(box.animate.set_fill(opacity=0.1), label.animate.set_color(MUTED))


class Flow(VGroup):
    """Dots that run along a line while the scene plays. Set `hold_at` (a share of the line) to
    stop them in a queue behind a gate, and None to let them go. Add it with self.add. Call
    stop() before you fade it: while it runs it resets its dots' opacity on every frame."""

    def __init__(self, start, end, color=LINK_COLOR, radius=0.09, spacing=0.9, pace=2.2, phase=0.0):
        self.line_start, self.line_end = np.array(start, dtype=float), np.array(end, dtype=float)
        length = float(np.linalg.norm(self.line_end - self.line_start))
        count = max(2, int(length / spacing))
        super().__init__(*[Dot(radius=radius, color=color) for _ in range(count)])
        self.rate, self.queue_gap, self.hold_at = pace / length, 0.24 / length, None
        self.alphas = [(phase + i / count) % 1 for i in range(count)]
        self.place()
        self.add_updater(Flow.advance)

    def advance(self, dt):
        step = self.rate * dt
        if self.hold_at is None:
            self.alphas = [(a + step) % 1 for a in self.alphas]
        else:
            queue = sorted((i for i, a in enumerate(self.alphas) if a <= self.hold_at), key=lambda i: -self.alphas[i])
            for rank, i in enumerate(queue):
                limit = self.hold_at - rank * self.queue_gap
                self.alphas[i] = max(self.alphas[i], min(self.alphas[i] + step, limit))
            self.alphas = [a + step if a > self.hold_at else a for a in self.alphas]
        self.place()

    def place(self):
        for dot, a in zip(self.submobjects, self.alphas):
            dot.move_to(self.line_start + (self.line_end - self.line_start) * min(a, 1.0))
            dot.set_opacity(0 if a >= 1 else min(1.0, a / 0.05, (1 - a) / 0.05))

    def stop(self):
        self.clear_updaters()
        return self


def stamp(words, color, tilt=0.0, size=66):
    """A decision in big words on an opaque tag, above everything else on stage."""
    label = title(words, size, color)
    box = RoundedRectangle(corner_radius=0.16, width=label.width + 0.6, height=label.height + 0.6, fill_color=BG,
                           fill_opacity=0.92, stroke_color=color, stroke_width=8)
    return VGroup(box, label.move_to(box)).rotate(tilt).set_z_index(5)


def bridge(start, end, gap=0.08, color=FAINT, width=7):
    """A straight link between two mobjects that starts and ends at their borders, so it never
    runs through a card or a label."""
    p, q = start.get_center(), end.get_center()
    d = q - p

    def leave(mob):  # the share of p->q that lies inside mob's box, plus the gap
        w, h = mob.width / 2 + gap, mob.height / 2 + gap
        return min(w / abs(d[0]) if d[0] else np.inf, h / abs(d[1]) if d[1] else np.inf)

    return Line(p + leave(start) * d, q - leave(end) * d, color=color, stroke_width=width)


__all__ = ["Flow", "PANEL_OPACITY", "backdrop", "bridge", "dim", "light", "panel", "phase_pill", "phase_pills", "stamp"]
