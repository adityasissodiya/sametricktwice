"""Recurring house-style parts: type helpers, the top-band beat header, date badges, pills.

Every episode uses these, so they live in the kit rather than in an episode's scene.py.
See STYLE_GUIDE.md ("Canvas and composition") for where each one goes.
"""

from manim import BOLD, DOWN, NORMAL, RIGHT, Line, RoundedRectangle, Text, VGroup

from .style import BODY_FONT, BODY_SIZE, FAINT, INK, MUTED, TITLE_FONT, TITLE_SIZE


def text(words, size=BODY_SIZE, color=INK, weight=NORMAL):
    return Text(words, font=BODY_FONT, font_size=size, color=color, weight=weight)


def title(words, size=TITLE_SIZE, color=INK):
    return Text(words, font=TITLE_FONT, font_size=size, color=color, weight=BOLD)


def beat_header(number, words, color):
    """Top band: a colored number pill, an uppercase beat label and a faint rule."""
    pill = RoundedRectangle(
        corner_radius=0.16, width=0.9, height=0.46,
        fill_color=color, fill_opacity=0.15, stroke_color=color, stroke_width=2,
    )
    number_label = text(f"{number:02d}", 21, color, BOLD).move_to(pill)
    label = text(words.upper(), 21, MUTED, BOLD).next_to(pill, RIGHT, buff=0.16)
    rule = Line(label.get_right() + 0.16 * RIGHT, [2.60, label.get_y(), 0], color=FAINT, stroke_width=2)
    return VGroup(pill, number_label, label, rule).move_to([-0.45, 5.0, 0])


def date_badge(year, color):
    box = RoundedRectangle(
        corner_radius=0.16, width=2.0, height=0.72,
        fill_color=color, fill_opacity=0.12, stroke_color=color, stroke_width=2,
    )
    return VGroup(box, title(year, 34, color).move_to(box))


def pill(words, color, size=20, pad=0.42):
    """A label in a rounded box that is always sized to its text."""
    label = text(words, size, color, BOLD)
    box = RoundedRectangle(
        corner_radius=0.15, width=label.width + pad, height=label.height + 0.42,
        fill_color=color, fill_opacity=0.14, stroke_color=color, stroke_width=2,
    )
    return VGroup(box, label.move_to(box))


def phone(height=5.0, color=FAINT):
    """A modern phone: VGroup(body, screen, speaker slot). Draw content on index 1."""
    width = height * 0.5
    body = RoundedRectangle(
        corner_radius=height * 0.075, width=width, height=height,
        fill_color="#131722", fill_opacity=1, stroke_color=color, stroke_width=5,
    )
    screen = RoundedRectangle(
        corner_radius=height * 0.05, width=width - 0.26, height=height - 0.62,
        fill_color="#0B0E14", fill_opacity=1, stroke_width=0,
    ).move_to(body).shift(0.05 * DOWN)
    speaker = RoundedRectangle(
        corner_radius=0.04, width=width * 0.22, height=0.08,
        fill_color=color, fill_opacity=1, stroke_width=0,
    ).move_to(body.get_top() + 0.16 * DOWN)
    return VGroup(body, screen, speaker)


__all__ = ["text", "title", "beat_header", "date_badge", "pill", "phone"]
