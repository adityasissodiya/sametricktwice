"""Channel art for YouTube: the profile picture, the banner and the video watermark.

The mark is a T-junction. World A (blue) and world B (orange) are the two arms; they meet at
one shared trick (the violet stem and node). In the banner a small violet 2 makes it "T²":
the same trick, twice. The profile picture and the watermark drop the 2, because YouTube
shows them as small as 32 px, where a superscript is a speck. Colors and fonts come from
kit/style.py, so the channel art always matches the videos.

Run:  vid uv run python brand/make.py

Writes to exports/brand/:
  avatar.png     800x800    profile picture (YouTube crops it to a circle, shown at 98 px)
  banner.png     2560x1440  banner; every word stays in the central 1546x423 px phone area
  watermark.png  300x300    video watermark (transparent corners, well under 1 MB)
  preview.png               the three at real size, and where the banner crops
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from manim import (BOLD, DOWN, LEFT, ORIGIN, RIGHT, UP, Circle, Dot, Line, MarkupText,  # noqa: E402
                   RoundedRectangle, Scene, Text, VGroup, tempconfig)
from PIL import Image, ImageDraw  # noqa: E402

from kit.style import A_COLOR, B_COLOR, BG, BODY_FONT, FAINT, INK, LINK_COLOR, MUTED, TITLE_FONT  # noqa: E402

OUT = ROOT / "exports" / "brand"
SCRATCH = ROOT / ".cache" / "brand"  # Manim's own render files
PX = 100  # pixels per Manim unit in every image, so stroke_width 1 is 1 px

# YouTube's banner: TV shows all of it, desktop a full-width strip, phones only the center.
BANNER = (2560, 1440)
STRIP_H = 423 / PX  # the strip every device shows
PHONE_W = 1546 / PX  # the part phones show; every word must fit inside it

# The T, in units of its stem: bar thickness, arm length and node radius, from the junction.
THICK, ARM, STEM, NODE = 0.26, 0.66, 1.0, 0.19


def _bar(start: tuple[float, float], end: tuple[float, float], color: str) -> RoundedRectangle:
    """A filled bar with round ends, horizontal or vertical, from start to end."""
    (x0, y0), (x1, y1) = start, end
    bar = RoundedRectangle(width=abs(x1 - x0) + THICK, height=abs(y1 - y0) + THICK,
                           corner_radius=THICK / 2)
    bar.set_fill(color, 1).set_stroke(width=0)
    return bar.move_to(((x0 + x1) / 2, (y0 + y1) / 2, 0))


def mark(scale: float = 1.0, squared: bool = True) -> VGroup:
    """The channel mark with its junction at the origin; the stem is `scale` units long."""
    parts = VGroup(
        _bar((-ARM, 0), (0, 0), A_COLOR),
        _bar((0, 0), (ARM, 0), B_COLOR),
        _bar((0, 0), (0, -STEM), LINK_COLOR),
        Circle(radius=NODE).set_fill(LINK_COLOR, 1).set_stroke(width=0),
    )
    if squared:
        two = Text("2", font=TITLE_FONT, weight=BOLD, color=LINK_COLOR).scale_to_fit_height(0.42)
        two.next_to(parts[1], RIGHT, buff=0.06).align_to(parts[1], UP).shift(0.14 * UP)
        parts.add(two)
    return parts.scale(scale, about_point=ORIGIN)


def badge(radius: float, fill: float = 0.82) -> VGroup:
    """The mark without the 2, centered on the smallest circle around the T and sized so
    that circle is `fill` of a circle of `radius`: as big as a round crop allows."""
    tip, foot = ARM + THICK / 2, STEM + THICK / 2  # crossbar tip and stem foot, from the junction
    center = (tip ** 2 - foot ** 2) / (2 * foot)  # that circle's center, below the junction
    scale = fill * radius / (foot + center)
    return mark(scale, squared=False).shift(-center * scale * UP)


def _web(seed: int, side: int, color: str, count: int = 15) -> VGroup:
    """A loose web of nodes on one side of the banner, outside the phone area."""
    rng = random.Random(seed)
    half_w, half_h = BANNER[0] / PX / 2, BANNER[1] / PX / 2
    inner = PHONE_W / 2 + 0.3
    points: list[tuple[float, float]] = []
    while len(points) < count:
        x = side * rng.uniform(inner, half_w - 0.5)
        y = rng.uniform(-half_h + 0.6, half_h - 0.6)
        if all((x - px) ** 2 + (y - py) ** 2 > 1.5 ** 2 for px, py in points):
            points.append((x, y))

    def glow(x: float) -> float:  # dimmer toward the words
        return 0.4 + 0.6 * min(1.0, (abs(x) - inner) / 3.0)

    edges = set()
    for i, (x, y) in enumerate(points):
        nearest = sorted(range(count), key=lambda j: (points[j][0] - x) ** 2 + (points[j][1] - y) ** 2)
        edges.update(frozenset((i, j)) for j in nearest[1:3])  # each node joins its two nearest
    web = VGroup()
    for i, j in sorted(tuple(sorted(edge)) for edge in edges):
        (x, y), (qx, qy) = points[i], points[j]
        web.add(Line((x, y, 0), (qx, qy, 0), stroke_width=3, color=color)
                .set_stroke(opacity=0.45 * min(glow(x), glow(qx))))
    for x, y in points:
        web.add(Dot((x, y, 0), radius=rng.uniform(0.07, 0.15), color=color).set_opacity(glow(x)))
    return web


class Avatar(Scene):
    def construct(self):
        self.add(badge(4.0))


class Watermark(Scene):
    def construct(self):
        disc = Circle(radius=1.48).set_fill(BG, 1).set_stroke(FAINT, width=4)
        self.add(disc, badge(1.48))


class Banner(Scene):
    def construct(self):
        half_w, half_h = BANNER[0] / PX / 2, BANNER[1] / PX / 2
        grid = VGroup(*[Dot((x * 0.6, y * 0.6, 0), radius=0.022, color=FAINT)
                        for x in range(-int(half_w / 0.6), int(half_w / 0.6) + 1)
                        for y in range(-int(half_h / 0.6), int(half_h / 0.6) + 1)])
        title = MarkupText(f'SAME <span foreground="{LINK_COLOR}">TRICK</span> TWICE',
                           font=TITLE_FONT, weight=BOLD, color=INK).scale_to_fit_height(0.82)
        tagline = MarkupText(f'Two worlds. <span foreground="{LINK_COLOR}">One trick.</span>',
                             font=BODY_FONT, color=MUTED).scale_to_fit_height(0.5)
        words = VGroup(title, tagline).arrange(DOWN, aligned_edge=LEFT, buff=0.38)
        block = VGroup(mark(1.9), words).arrange(RIGHT, buff=0.8)
        block.scale_to_fit_width(min(block.width, PHONE_W - 1.6)).move_to(ORIGIN)
        assert block.height < STRIP_H - 0.6, "the words must stay inside the strip every device shows"
        self.add(grid, _web(7, -1, A_COLOR), _web(11, 1, B_COLOR), block)


def render(scene: type[Scene], name: str, size: tuple[int, int], transparent: bool = False) -> Path:
    """Render one still frame of `scene` at exactly `size` pixels into exports/brand/."""
    width, height = size
    settings = {
        "pixel_width": width, "pixel_height": height,
        "frame_width": width / PX, "frame_height": height / PX,
        "background_color": BG, "transparent": transparent,
        "background_opacity": 0.0 if transparent else 1.0,
        "save_last_frame": True, "write_to_movie": False, "disable_caching": True,
        "media_dir": str(SCRATCH), "verbosity": "ERROR", "progress_bar": "none",
    }
    with tempconfig(settings):
        instance = scene()
        instance.render()
        image = instance.renderer.camera.get_image()
    if not transparent:
        image = image.convert("RGB")
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"{name}.png"
    image.save(path, optimize=True)
    return path


def _circle(image: Image.Image, size: int) -> Image.Image:
    """The avatar as YouTube crops it: a circle, `size` px across."""
    big = image.convert("RGBA").resize((size * 4, size * 4), Image.LANCZOS)
    mask = Image.new("L", big.size, 0)
    ImageDraw.Draw(mask).ellipse((0, 0, big.width - 1, big.height - 1), fill=255)
    big.putalpha(mask)
    return big.resize((size, size), Image.LANCZOS)


def preview(avatar: Path, banner: Path, watermark: Path) -> Path:
    """One sheet: the avatar at 98, 40 and 32 px on YouTube's dark and light pages, the
    watermark on a video-colored frame, and the banner with the desktop strip (white) and
    the phone crop (yellow) marked."""
    sheet = Image.new("RGB", (1400, 1180), "#202124")
    draw = ImageDraw.Draw(sheet)
    art = Image.open(avatar)
    sizes = [(_circle(art, s), s) for s in (98, 40, 32)]
    for i, page in enumerate(("#0F0F0F", "#FFFFFF")):
        x = 40 + i * 300
        draw.rectangle((x, 40, x + 260, 180), fill=page)
        left = x + 20
        for circle, size in sizes:
            sheet.paste(circle, (left, 110 - size // 2), circle)
            left += size + 24
    frame = Image.new("RGB", (480, 270), BG)
    mark_img = Image.open(watermark).resize((60, 60), Image.LANCZOS)
    frame.paste(mark_img, (480 - 60 - 16, 270 - 60 - 16), mark_img)
    sheet.paste(frame, (880, 40))
    full = Image.open(banner)
    scale = 1320 / full.width
    sheet.paste(full.resize((1320, round(full.height * scale)), Image.LANCZOS), (40, 340))
    top = 340 + round((full.height - 423) / 2 * scale)
    bottom = top + round(423 * scale)
    left = 40 + round((full.width - 1546) / 2 * scale)
    draw.rectangle((40, top, 40 + 1320, bottom), outline="#FFFFFF", width=2)
    draw.rectangle((left, top, left + round(1546 * scale), bottom), outline="#FFD54F", width=3)
    path = OUT / "preview.png"
    sheet.save(path)
    return path


if __name__ == "__main__":
    avatar = render(Avatar, "avatar", (800, 800))
    banner = render(Banner, "banner", BANNER)
    watermark = render(Watermark, "watermark", (300, 300), transparent=True)
    for path in (avatar, banner, watermark, preview(avatar, banner, watermark)):
        print(f"{path.relative_to(ROOT)}  {path.stat().st_size / 1024:.0f} KB")
