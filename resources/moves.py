"""Motion helpers: each returns a rate function, a path or an animation for self.play in scene.py.

The causal names the gates look for (MoveAlongPath, Transform, .animate.shift) stay in scene.py:
write MoveAlongPath(token, route(a, b)), not a helper that hides it.
"""

from __future__ import annotations

import numpy as np
from manim import AnimationGroup, ArcBetweenPoints, FadeIn, FadeOut, Line, Mobject, UpdateFromAlphaFunc, smooth, there_and_back


def between(start, end):
    """A rate function that runs only inside one part of an animation, for several steps in one
    self.play: FadeOut(old, rate_func=between(0, 0.4)), Create(link, rate_func=between(0.7, 1))."""
    return lambda t: smooth(min(1.0, max(0.0, (t - start) / (end - start))))


def swap(old, new, at=0.4):
    """Replace one word or part with another in two steps. A plain crossfade overlaps them, and
    two sets of words on top of each other read as a smudge."""
    return AnimationGroup(FadeOut(old, rate_func=between(0.0, at)), FadeIn(new, rate_func=between(at, 1.0)))


def pop(mobject, factor=1.12):
    """A short swell and return that says "this one, now"."""
    return mobject.animate(rate_func=there_and_back).scale(factor)


def _point(target):
    return target.get_center() if isinstance(target, Mobject) else np.array(target, dtype=float)


def route(start, end, angle=0.0):
    """The path for MoveAlongPath(token, route(a, b)), between points or mobjects: straight, or
    an arc when `angle` is set. Build it after the alignment loop, which may move its ends."""
    a, z = _point(start), _point(end)
    return ArcBetweenPoints(a, z, angle=angle) if angle else Line(a, z)


def tween(mobject, setter, start, end, **kwargs):
    """Animate any state, not just a position: setter(mobject, value) runs on each frame with a
    value from start to end. Both may be numbers or equal-length sequences."""
    first, last = np.asarray(start, dtype=float), np.asarray(end, dtype=float)

    def update(mob, share):
        value = first + (last - first) * share
        setter(mob, value.tolist() if value.ndim else float(value))

    return UpdateFromAlphaFunc(mobject, update, **kwargs)


__all__ = ["between", "pop", "route", "swap", "tween"]
