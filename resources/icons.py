"""Small generic pictograms from finished videos: open gallery.png to see them all.

Each function returns a mobject centered on the origin in the house style (tinted fill, thick
stroke) and scaled by `size`, which leaves strokes as thick as they are. None has words of its
own. Docstrings list the parts a scene may animate, by index.

Add a drawing only if two different videos could use it, and only if it shows a kind of thing,
not one subject. Diagrams of a topic belong in that video's scene.py: repeated subjects are
what YouTube's "inauthentic content" rule demonetizes, and AGENTS.md bans carry-over.
"""

from __future__ import annotations

import numpy as np
from manim import (DOWN, LEFT, ORIGIN, PI, RIGHT, TAU, UP, AnnularSector, Arc, ArcBetweenPoints, Circle, Dot, Line, Polygon,
                   Rectangle, RoundedRectangle, Square, Star, VGroup, VMobject)

from kit.style import ALERT, BG, INK, MUTED


def _placed(mob, size):
    return mob.move_to(ORIGIN).scale(size)


def person(color=INK, size=1.0):
    """Head (0) and shoulders (1)."""
    head = Circle(radius=0.17, fill_color=color, fill_opacity=0.9, stroke_width=0)
    body = RoundedRectangle(corner_radius=0.17, width=0.62, height=0.38, fill_color=color, fill_opacity=0.25,
                            stroke_color=color, stroke_width=4).next_to(head, DOWN, buff=0.05)
    return _placed(VGroup(head, body), size)


def doc(color=INK, size=1.0, rows=3):
    """A page (0) with a folded corner (1) and rows of text (2)."""
    w, h, f = 0.39, 0.49, 0.2
    page = Polygon([-w, h, 0], [w - f, h, 0], [w, h - f, 0], [w, -h, 0], [-w, -h, 0], fill_color=BG, fill_opacity=1,
                   stroke_color=color, stroke_width=3)
    fold = Polygon([w - f, h, 0], [w - f, h - f, 0], [w, h - f, 0], fill_color=color, fill_opacity=0.6, stroke_width=0)
    lines = VGroup(*[Line([-w + 0.13, h - 0.32 - 0.19 * i, 0], [w - 0.15, h - 0.32 - 0.19 * i, 0], color=color,
                          stroke_width=3, stroke_opacity=0.6) for i in range(rows)])
    return _placed(VGroup(page, fold, lines), size)


def key(color=INK, size=1.0, length=1.0):
    """Bow (0), hole (1), shaft (2), teeth (3). `length` sets the shaft, so keys can differ visibly."""
    bow = Circle(radius=0.26, fill_color=color, fill_opacity=0.3, stroke_color=color, stroke_width=5)
    hole = Circle(radius=0.09, fill_color=BG, fill_opacity=1, stroke_color=color, stroke_width=3)
    shaft = Rectangle(width=length, height=0.13, fill_color=color, fill_opacity=0.9, stroke_width=0)
    shaft.next_to(bow, RIGHT, buff=-0.02)
    teeth = VGroup(*[Rectangle(width=0.11, height=h, fill_color=color, fill_opacity=0.9, stroke_width=0)
                     for h in (0.26, 0.18)]).arrange(RIGHT, buff=0.08, aligned_edge=UP)
    teeth.next_to(shaft, DOWN, buff=0).align_to(shaft, RIGHT).shift(0.06 * LEFT)
    return _placed(VGroup(bow, hole, shaft, teeth), size)


class Padlock(VGroup):
    """Open it with Rotate(lock.shackle, angle=0.8, about_point=lock.hinge()); recolor() returns
    the lock, so it can go in lock.animate.recolor(color)."""

    def __init__(self, color=INK):
        super().__init__()
        self.body = RoundedRectangle(corner_radius=0.05, width=0.42, height=0.32, fill_color=color, fill_opacity=1,
                                     stroke_width=0)
        top = self.body.get_top()
        self.shackle = VGroup(Line(top + 0.12 * LEFT, top + 0.12 * LEFT + 0.09 * UP),
                              Arc(radius=0.12, start_angle=0, angle=PI, arc_center=top + 0.09 * UP),
                              Line(top + 0.12 * RIGHT + 0.09 * UP, top + 0.12 * RIGHT)).set_stroke(color, width=6)
        keyhole = Circle(radius=0.05, fill_color=BG, fill_opacity=1, stroke_width=0).move_to(self.body)
        self.add(self.shackle, self.body, keyhole)

    def recolor(self, color):
        self.body.set_fill(color)
        self.shackle.set_stroke(color)
        return self

    def hinge(self):
        return self.shackle[0].get_start()


def padlock(color=INK, size=1.0):
    """A Padlock whose shackle (.shackle) can swing open about .hinge()."""
    return _placed(Padlock(color), size)


def tick(color=INK, size=1.0):
    return _placed(VMobject(stroke_color=color, stroke_width=6).set_points_as_corners(
        [[-0.16, 0.0, 0], [-0.05, -0.12, 0], [0.18, 0.15, 0]]), size)


def cross(color=ALERT, size=1.0):
    return _placed(VGroup(Line([-0.16, -0.16, 0], [0.16, 0.16, 0]), Line([-0.16, 0.16, 0], [0.16, -0.16, 0])).set_stroke(
        color, width=6), size)


def ring(color=INK, size=1.0):
    """An opaque disc to put a tick or a cross on."""
    return _placed(Circle(radius=0.27, fill_color=BG, fill_opacity=1, stroke_color=color, stroke_width=4), size)


def seal(color=INK, size=1.0):
    """A small mark of signature or approval."""
    return _placed(VGroup(Circle(radius=0.085, fill_color=color, fill_opacity=1, stroke_color=BG, stroke_width=2),
                          Dot(radius=0.025, color=BG)), size)


def star(color=INK, size=1.0):
    return _placed(Star(5, outer_radius=0.24, inner_radius=0.1, fill_color=color, fill_opacity=0.95, stroke_color=color,
                        stroke_width=2), size)


def flame(color=INK, size=1.0):
    """An outer tongue (0) and a brighter core (1). The side notch keeps it from reading as a drop."""
    outer = VMobject(fill_color=color, fill_opacity=0.30, stroke_color=color, stroke_width=4)
    outer.set_points_as_corners([[0.04, 0.62, 0], [0.2, 0.3, 0], [0.34, 0.1, 0], [0.32, -0.18, 0], [0.16, -0.42, 0],
                                 [0, -0.48, 0], [-0.16, -0.42, 0], [-0.32, -0.18, 0], [-0.34, 0.06, 0], [-0.24, 0.3, 0],
                                 [-0.14, 0.14, 0], [-0.06, 0.34, 0], [0.04, 0.62, 0]])
    outer.make_smooth()
    inner = outer.copy().scale(0.48).shift(0.17 * DOWN).set_fill(color, opacity=0.65)
    return _placed(VGroup(outer, inner), size)


def clock(color=INK, size=1.0):
    """Face (0), ticks (1), minute hand (2), hour hand (3). Turn a hand with
    Rotate(c[2], angle=-0.95 * TAU, about_point=c[0].get_center()): a full TAU draws no path."""
    radius = 0.5
    face = Circle(radius=radius, fill_color=color, fill_opacity=0.1, stroke_color=color, stroke_width=4)
    ticks = VGroup(*[Line(0.78 * radius * np.array([np.cos(a), np.sin(a), 0]),
                          0.92 * radius * np.array([np.cos(a), np.sin(a), 0]), color=color, stroke_width=3)
                     for a in np.arange(0, TAU, TAU / 12)])
    minute = Line(ORIGIN, 0.72 * radius * UP, color=color, stroke_width=4)
    hour = Line(ORIGIN, 0.45 * radius * RIGHT, color=color, stroke_width=5)
    return _placed(VGroup(face, ticks, minute, hour), size)


def gear(color=INK, size=1.0, teeth=10):
    """Wheel (0) and hole (1). Spin it about its hole:
    g.add_updater(lambda m, dt: m.rotate(-dt, about_point=m[1].get_center()))."""
    radius, points = 0.44, []
    for i in range(teeth):
        for offset, r in ((-0.30, 0.76), (-0.15, 1.0), (0.15, 1.0), (0.30, 0.76)):
            angle = (i + offset) * TAU / teeth
            points.append([radius * r * np.cos(angle), radius * r * np.sin(angle), 0])
    wheel = Polygon(*points, fill_color=color, fill_opacity=1, stroke_width=0)
    hole = Circle(radius=radius * 0.3, fill_color=BG, fill_opacity=1, stroke_width=0)
    return _placed(VGroup(wheel, hole), size)


def server(color=INK, size=1.0):
    """A rack (0) with three bays (1) and three lights (2)."""
    box = RoundedRectangle(corner_radius=0.08, width=0.62, height=0.84, fill_color=color, fill_opacity=0.16,
                           stroke_color=color, stroke_width=4)
    bays = VGroup(*[Line([-0.19, y, 0], [0.1, y, 0], color=color, stroke_width=4) for y in (0.22, 0.0, -0.22)])
    lights = VGroup(*[Dot([0.19, y, 0], radius=0.04, color=color) for y in (0.22, 0.0, -0.22)])
    return _placed(VGroup(box, bays, lights), size)


def laptop(color=INK, size=1.0):
    """Lid (0) and base (1)."""
    lid = RoundedRectangle(corner_radius=0.05, width=0.72, height=0.46, fill_color=color, fill_opacity=0.18,
                           stroke_color=color, stroke_width=4)
    base = Polygon([-0.48, -0.3, 0], [0.48, -0.3, 0], [0.4, -0.23, 0], [-0.4, -0.23, 0], fill_color=color,
                   fill_opacity=0.7, stroke_color=color, stroke_width=3)
    return _placed(VGroup(lid, base), size)


def monitor(color=INK, size=1.0):
    """Screen (0), lines of text (1), neck (2), foot (3)."""
    screen = RoundedRectangle(corner_radius=0.08, width=1.0, height=0.68, fill_color=BG, fill_opacity=1,
                              stroke_color=color, stroke_width=4).move_to([0, 0.12, 0])
    lines = VGroup(*[Rectangle(width=w, height=0.07, fill_color=color, fill_opacity=1, stroke_width=0)
                     .move_to([w / 2 - 0.34, y, 0]) for w, y in ((0.60, 0.28), (0.38, 0.12), (0.50, -0.04))])
    neck = Rectangle(width=0.15, height=0.14, fill_color=color, fill_opacity=1, stroke_width=0).move_to([0, -0.29, 0])
    foot = RoundedRectangle(corner_radius=0.04, width=0.54, height=0.09, fill_color=color, fill_opacity=1,
                            stroke_width=0).move_to([0, -0.40, 0])
    return _placed(VGroup(screen, lines, neck, foot), size)


def house(color=INK, size=1.0):
    """Body (0), roof (1), a lit window (2) that can go dark."""
    body = Rectangle(width=0.34, height=0.24, fill_color=color, fill_opacity=0.15, stroke_color=color, stroke_width=3)
    roof = Polygon([-0.22, 0.12, 0], [0.22, 0.12, 0], [0, 0.3, 0], fill_color=color, fill_opacity=0.35, stroke_color=color,
                   stroke_width=3)
    window = Square(0.1, fill_color=INK, fill_opacity=0.95, stroke_width=0).move_to(body)
    return _placed(VGroup(body, roof, window), size)


def building(color=INK, size=1.0):
    """A block (0) with two rows of windows (1)."""
    block = RoundedRectangle(corner_radius=0.06, width=1.3, height=1.0, fill_color=color, fill_opacity=0.14,
                             stroke_color=color, stroke_width=4)
    panes = VGroup(*[Square(0.12, fill_color=color, fill_opacity=0.6, stroke_width=0) for _ in range(6)])
    panes.arrange_in_grid(rows=2, cols=3, buff=0.14).move_to(block)
    return _placed(VGroup(block, panes), size)


def truck(color=INK, size=1.0):
    """Body (0), cab (1), wheels (2)."""
    body = RoundedRectangle(corner_radius=0.06, width=0.8, height=0.44, fill_color=color, fill_opacity=0.18,
                            stroke_color=color, stroke_width=4)
    cab = RoundedRectangle(corner_radius=0.06, width=0.3, height=0.3, fill_color=color, fill_opacity=0.35,
                           stroke_color=color, stroke_width=4).next_to(body, RIGHT, buff=0.03).align_to(body, DOWN)
    wheels = VGroup(*[Circle(radius=0.085, fill_color=BG, fill_opacity=1, stroke_color=color, stroke_width=3)
                      .move_to([x, body.get_bottom()[1], 0]) for x in (-0.22, 0.58)])
    return _placed(VGroup(body, cab, wheels), size)


def flag(color=INK, size=1.0):
    """Pole (0) and cloth (1)."""
    pole = Line([0, -0.45, 0], [0, 0.45, 0], color=MUTED, stroke_width=4)
    cloth = Polygon([0, 0.45, 0], [0.46, 0.3, 0], [0, 0.15, 0], fill_color=color, fill_opacity=0.85, stroke_width=0)
    return _placed(VGroup(pole, cloth), size)


def coin(color=INK, size=1.0):
    rim = Circle(radius=0.22, fill_color=color, fill_opacity=0.85, stroke_color=color, stroke_width=3)
    inner = Circle(radius=0.13, stroke_color=BG, stroke_width=3)
    return _placed(VGroup(rim, inner), size)


def eye(color=INK, size=1.0):
    """Two lids (0) and a pupil (1)."""
    lids = VGroup(ArcBetweenPoints([-0.42, 0, 0], [0.42, 0, 0], angle=-PI / 2.2),
                  ArcBetweenPoints([-0.42, 0, 0], [0.42, 0, 0], angle=PI / 2.2)).set_stroke(color, width=4)
    pupil = Circle(radius=0.12, fill_color=color, fill_opacity=1, stroke_width=0)
    return _placed(VGroup(lids, pupil), size)


def lens(color=INK, size=1.0):
    """Glass (0) and handle (1): a magnifier that says "look closer"."""
    glass = Circle(radius=0.32, fill_color=color, fill_opacity=0.15, stroke_color=color, stroke_width=6)
    rim = glass.point_at_angle(-PI / 4)
    handle = Line(rim, rim + 0.3 * np.array([1, -1, 0]), color=color, stroke_width=9)
    return _placed(VGroup(glass, handle), size)


def gauge(color=INK, size=1.0):
    """Face (0), dial (1), needle (2) pointing left, hub (3). Move the needle with
    Rotate(g[2], angle=-share * PI, about_point=g[3].get_center())."""
    face = AnnularSector(inner_radius=0.0, outer_radius=0.95, angle=PI, start_angle=0, fill_color=color, fill_opacity=0.06,
                         stroke_width=0)
    dial = Arc(radius=0.95, start_angle=PI, angle=-PI, stroke_color=MUTED, stroke_width=6)
    needle = Line(ORIGIN, 0.82 * LEFT, stroke_color=color, stroke_width=6)
    hub = Dot(radius=0.08, color=color)
    return _placed(VGroup(face, dial, needle, hub), size)


def battery(color=INK, size=1.0):
    """Body (0), cap (1), plus (2), minus (3)."""
    body = RoundedRectangle(corner_radius=0.08, width=0.62, height=1.0, fill_color=color, fill_opacity=0.25,
                            stroke_color=color, stroke_width=4)
    cap = Rectangle(width=0.24, height=0.12, fill_color=color, fill_opacity=0.8, stroke_width=0).next_to(body, UP, buff=0)
    plus = VGroup(Line([-0.11, 0.2, 0], [0.11, 0.2, 0]), Line([0, 0.09, 0], [0, 0.31, 0])).set_stroke(INK, 4)
    minus = Line([-0.11, -0.22, 0], [0.11, -0.22, 0]).set_stroke(INK, 4)
    return _placed(VGroup(body, cap, plus, minus), size)


def plate(drawing, color=INK, side=2.3):
    """A square plate (0) around a drawing (1), so two worlds' icons read as a matched pair."""
    board = RoundedRectangle(corner_radius=0.26, width=side, height=side, fill_color=color, fill_opacity=0.10,
                             stroke_color=color, stroke_width=4)
    room = 0.66 * side
    drawing.scale(room / max(drawing.width, drawing.height)).move_to(board)
    return VGroup(board, drawing)


__all__ = ["battery", "building", "clock", "coin", "cross", "doc", "eye", "flag", "flame", "gauge", "gear", "house", "key",
           "laptop", "lens", "monitor", "padlock", "person", "plate", "ring", "seal", "server", "star", "tick", "truck"]
