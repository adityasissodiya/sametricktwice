"""Optional building blocks harvested from finished videos. Start at resources/README.md.

`from resources import *` gives the names below and `icons`. It never imports kit.landscape,
so it works in a Short and in a landscape special alike: import your kit first.
"""

from . import icons
from .moves import between, pop, route, swap, tween
from .parts import PANEL_OPACITY, Flow, backdrop, bridge, dim, light, panel, phase_pill, phase_pills, stamp
from .stage import BREATH, LONG_BREATH, StageTools, stage_box

__all__ = [
    "BREATH", "LONG_BREATH", "PANEL_OPACITY", "Flow", "StageTools", "backdrop", "between", "bridge", "dim", "icons", "light",
    "panel", "phase_pill", "phase_pills", "pop", "route", "stage_box", "stamp", "swap", "tween",
]
