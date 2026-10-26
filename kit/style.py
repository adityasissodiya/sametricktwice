"""The Episode 001 house style: vertical frame, palette, type and phone-safe geometry.

Color carries meaning in the finished Episode 001 house style, and it stays the same in every episode:
world A is always blue, world B is always orange, the shared trick is always violet.
Primary compositions use the Shorts-safe axis ``SAFE_CENTER[0]`` (-0.4), not x=0.
See STYLE_GUIDE.md before adding or changing visual constants.
"""

from pathlib import Path

import manimpango
from manim import RIGHT, UP, config

# Vertical 9:16 frame, 8 units wide, so 1 unit = 135 px at 1080x1920.
FRAME_W = 8.0
config.frame_width = FRAME_W
config.frame_height = FRAME_W * config.pixel_height / config.pixel_width
FRAME_H = config.frame_height

# Palette
BG = "#0F1117"
INK = "#ECEFF4"
MUTED = "#7D869C"
FAINT = "#2A2F3A"
A_COLOR = "#58B4FF"  # world A
B_COLOR = "#FF9F45"  # world B
LINK_COLOR = "#C792EA"  # the shared trick
ALERT = "#FF5C5C"  # a problem: too big, blocked, wrong. Use it rarely, for that meaning only

# The house fonts ship with Windows. On Linux and macOS, which lack them, the open-licence
# look-alikes in kit/fonts (OFL, see the licence files there) are registered and used instead,
# so a render looks the same on every machine without installing anything.
FONT_DIR = Path(__file__).with_name("fonts")


def _pick_font(house: str, stand_in: str) -> str:
    if house in manimpango.list_fonts():
        return house
    for font in sorted(FONT_DIR.glob("*.ttf")):
        manimpango.register_font(str(font))
    return stand_in


TITLE_FONT = _pick_font("Bahnschrift", "Barlow Semi Condensed")
BODY_FONT = _pick_font("Segoe UI", "Open Sans")

TITLE_SIZE = 64
BODY_SIZE = 34
LABEL_SIZE = 28
CAPTION_SIZE = 40
STROKE = 5  # thicker than Manim's default 4: thin lines vanish on a phone

# Shorts UI covers the top bar, the right-hand buttons and the bottom title area.
# These edges are approximate. Check with: vid preview <ep> --guides
SAFE_LEFT, SAFE_RIGHT = -3.55, 2.75
SAFE_TOP, SAFE_BOTTOM = 5.45, -4.0
SAFE_CENTER = ((SAFE_LEFT + SAFE_RIGHT) / 2) * RIGHT + ((SAFE_TOP + SAFE_BOTTOM) / 2) * UP
CAPTION_CENTER = ((SAFE_LEFT + SAFE_RIGHT) / 2) * RIGHT + (SAFE_BOTTOM + 0.7) * UP
STAGE_CENTER = SAFE_CENTER + 0.6 * UP  # main animation area, clear of the captions
STAGE_WIDTH = SAFE_RIGHT - SAFE_LEFT

__all__ = [
    "FRAME_W", "FRAME_H", "BG", "INK", "MUTED", "FAINT", "A_COLOR", "B_COLOR", "LINK_COLOR", "ALERT",
    "TITLE_FONT", "BODY_FONT", "TITLE_SIZE", "BODY_SIZE", "LABEL_SIZE", "CAPTION_SIZE", "STROKE",
    "SAFE_LEFT", "SAFE_RIGHT", "SAFE_TOP", "SAFE_BOTTOM", "SAFE_CENTER", "CAPTION_CENTER",
    "STAGE_CENTER", "STAGE_WIDTH",
]
