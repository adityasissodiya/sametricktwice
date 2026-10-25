"""Deterministic alignment and symmetry checks for vertical episode layouts.

This module treats layout as a small set of explicit constraints instead of a
visual guess.  Build a keyframe, register only the relationships that are
supposed to be symmetric, then leave the context before animating it::

    with AlignmentLoop("B4 process cards", on_failure="raise") as align:
        align.even_row(cards, y=1.3, gap=0.30)
        align.inside_safe(cards)

    self.play(LaggedStart(*[FadeIn(card) for card in cards]))

The loop corrects the registered mobjects, measures them again, and repeats
until every measurement is within tolerance.  Conflicting constraints are
reported rather than silently oscillating.  Use ``mirror_pair`` for genuinely
matching left/right objects; use ``even_row`` (or ``balanced_pair``) for unlike
objects whose *combined visual bounds* should be centered.

Manim coordinates are used throughout.  The default 0.04-unit tolerance is
about 5.4 pixels in the 1080-pixel-wide final render.
"""

from __future__ import annotations

import json
import os
import statistics
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable, Literal, Sequence

import numpy as np
from manim import (
    DOWN,
    DashedLine,
    Dot,
    Mobject,
    Rectangle,
    Text,
    VGroup,
)

from .style import (
    BODY_FONT,
    LINK_COLOR,
    SAFE_BOTTOM,
    SAFE_LEFT,
    SAFE_RIGHT,
    SAFE_TOP,
    STAGE_CENTER,
)

DEFAULT_TOLERANCE = 0.04
DEFAULT_MAX_PASSES = 6


class AlignmentError(RuntimeError):
    """Raised when a refinement loop cannot satisfy all of its constraints."""


@dataclass(frozen=True)
class Box:
    """Axis-aligned visual bounds in Manim scene units."""

    left: float
    right: float
    bottom: float
    top: float

    @property
    def width(self) -> float:
        return self.right - self.left

    @property
    def height(self) -> float:
        return self.top - self.bottom

    @property
    def center_x(self) -> float:
        return (self.left + self.right) / 2

    @property
    def center_y(self) -> float:
        return (self.bottom + self.top) / 2


def visual_box(mobject: Mobject) -> Box:
    """Return the rendered bounding box used by all alignment measurements."""

    return Box(
        left=float(mobject.get_left()[0]),
        right=float(mobject.get_right()[0]),
        bottom=float(mobject.get_bottom()[1]),
        top=float(mobject.get_top()[1]),
    )


def _combined_box(mobjects: Sequence[Mobject]) -> Box:
    if not mobjects:
        raise ValueError("an alignment constraint needs at least one mobject")
    boxes = [visual_box(mobject) for mobject in mobjects]
    return Box(
        left=min(box.left for box in boxes),
        right=max(box.right for box in boxes),
        bottom=min(box.bottom for box in boxes),
        top=max(box.top for box in boxes),
    )


def _name(mobject: Mobject, fallback: str) -> str:
    explicit = getattr(mobject, "alignment_name", None)
    return str(explicit or fallback)


@dataclass(frozen=True)
class AlignmentIssue:
    """One failed numeric measurement."""

    constraint: str
    kind: str
    metric: str
    measured: float
    target: float
    error: float
    tolerance: float
    detail: str

    def as_dict(self) -> dict[str, object]:
        return {
            "constraint": self.constraint,
            "kind": self.kind,
            "metric": self.metric,
            "measured": round(self.measured, 6),
            "target": round(self.target, 6),
            "error": round(self.error, 6),
            "tolerance": round(self.tolerance, 6),
            "detail": self.detail,
        }


def _failed_issue(
    *,
    constraint: str,
    kind: str,
    metric: str,
    measured: float,
    target: float,
    tolerance: float,
    detail: str,
) -> AlignmentIssue | None:
    error = abs(measured - target)
    if error <= tolerance:
        return None
    return AlignmentIssue(
        constraint=constraint,
        kind=kind,
        metric=metric,
        measured=float(measured),
        target=float(target),
        error=float(error),
        tolerance=float(tolerance),
        detail=detail,
    )


class _Constraint:
    kind = "constraint"
    priority = 50

    def __init__(self, name: str, tolerance: float):
        self.name = name
        self.tolerance = tolerance

    def inspect(self) -> list[AlignmentIssue]:
        raise NotImplementedError

    def correct(self) -> None:
        raise NotImplementedError


class _Centered(_Constraint):
    kind = "centered"
    priority = 40

    def __init__(
        self,
        mobject: Mobject,
        name: str,
        tolerance: float,
        axis_x: float | None,
        axis_y: float | None,
    ):
        super().__init__(name, tolerance)
        if axis_x is None and axis_y is None:
            raise ValueError("centered() needs axis_x, axis_y, or both")
        self.mobject = mobject
        self.axis_x = axis_x
        self.axis_y = axis_y

    def inspect(self) -> list[AlignmentIssue]:
        box = visual_box(self.mobject)
        issues = []
        if self.axis_x is not None:
            issue = _failed_issue(
                constraint=self.name,
                kind=self.kind,
                metric="center_x",
                measured=box.center_x,
                target=self.axis_x,
                tolerance=self.tolerance,
                detail="the visual bounding box is not centered on the vertical stage axis",
            )
            if issue:
                issues.append(issue)
        if self.axis_y is not None:
            issue = _failed_issue(
                constraint=self.name,
                kind=self.kind,
                metric="center_y",
                measured=box.center_y,
                target=self.axis_y,
                tolerance=self.tolerance,
                detail="the visual bounding box is not centered on the requested horizontal axis",
            )
            if issue:
                issues.append(issue)
        return issues

    def correct(self) -> None:
        box = visual_box(self.mobject)
        delta = np.zeros(3)
        if self.axis_x is not None:
            delta[0] = self.axis_x - box.center_x
        if self.axis_y is not None:
            delta[1] = self.axis_y - box.center_y
        self.mobject.shift(delta)


class _MirrorPair(_Constraint):
    kind = "mirror_pair"
    priority = 30

    def __init__(
        self,
        left: Mobject,
        right: Mobject,
        name: str,
        tolerance: float,
        axis_x: float,
        y: float | None,
        align_y: bool,
        min_gap: float,
    ):
        super().__init__(name, tolerance)
        if min_gap < 0:
            raise ValueError("min_gap cannot be negative")
        self.left = left
        self.right = right
        self.axis_x = axis_x
        self.y = y
        self.align_y = align_y
        self.min_gap = min_gap

    def inspect(self) -> list[AlignmentIssue]:
        left, right = visual_box(self.left), visual_box(self.right)
        issues = []
        midpoint = (left.center_x + right.center_x) / 2
        issue = _failed_issue(
            constraint=self.name,
            kind=self.kind,
            metric="pair_midpoint_x",
            measured=midpoint,
            target=self.axis_x,
            tolerance=self.tolerance,
            detail="left and right centers are not equally distant from the stage axis",
        )
        if issue:
            issues.append(issue)
        if self.align_y:
            target_y = self.y if self.y is not None else (left.center_y + right.center_y) / 2
            for side, measured in (("left_center_y", left.center_y), ("right_center_y", right.center_y)):
                issue = _failed_issue(
                    constraint=self.name,
                    kind=self.kind,
                    metric=side,
                    measured=measured,
                    target=target_y,
                    tolerance=self.tolerance,
                    detail="the mirrored objects do not share a baseline",
                )
                if issue:
                    issues.append(issue)
        gap = right.left - left.right
        if gap < self.min_gap - self.tolerance:
            issues.append(
                AlignmentIssue(
                    constraint=self.name,
                    kind=self.kind,
                    metric="inner_gap",
                    measured=gap,
                    target=self.min_gap,
                    error=self.min_gap - gap,
                    tolerance=self.tolerance,
                    detail="the mirrored objects overlap or are too close together",
                )
            )
        if left.center_x > self.axis_x + self.tolerance or right.center_x < self.axis_x - self.tolerance:
            issues.append(
                AlignmentIssue(
                    constraint=self.name,
                    kind=self.kind,
                    metric="side_order",
                    measured=left.center_x - right.center_x,
                    target=-abs(left.center_x - right.center_x),
                    error=abs(left.center_x - right.center_x),
                    tolerance=self.tolerance,
                    detail="the declared left/right pair is on the wrong side of the axis",
                )
            )
        return issues

    def correct(self) -> None:
        left, right = visual_box(self.left), visual_box(self.right)
        separation = max(
            abs(right.center_x - left.center_x),
            (left.width + right.width) / 2 + self.min_gap,
        )
        half = separation / 2
        target_y = self.y if self.y is not None else (left.center_y + right.center_y) / 2
        self.left.set_x(self.axis_x - half)
        self.right.set_x(self.axis_x + half)
        if self.align_y:
            self.left.set_y(target_y)
            self.right.set_y(target_y)


class _EvenRow(_Constraint):
    kind = "even_row"
    priority = 20

    def __init__(
        self,
        mobjects: Sequence[Mobject],
        name: str,
        tolerance: float,
        center_x: float | None,
        y: float | None,
        gap: float | None,
        min_gap: float,
    ):
        super().__init__(name, tolerance)
        if not mobjects:
            raise ValueError("even_row() needs at least one mobject")
        if gap is not None and gap < 0:
            raise ValueError("gap cannot be negative")
        if min_gap < 0:
            raise ValueError("min_gap cannot be negative")
        self.mobjects = list(mobjects)
        self.center_x = center_x
        self.y = y
        self.gap = gap
        self.min_gap = min_gap

    def _gaps(self, boxes: Sequence[Box]) -> list[float]:
        return [boxes[i + 1].left - boxes[i].right for i in range(len(boxes) - 1)]

    def _target_gap(self, gaps: Sequence[float]) -> float:
        if self.gap is not None:
            return self.gap
        return max(self.min_gap, statistics.median(gaps)) if gaps else self.min_gap

    def inspect(self) -> list[AlignmentIssue]:
        boxes = [visual_box(mobject) for mobject in self.mobjects]
        issues = []
        target_y = self.y if self.y is not None else statistics.fmean(box.center_y for box in boxes)
        for index, box in enumerate(boxes):
            issue = _failed_issue(
                constraint=self.name,
                kind=self.kind,
                metric=f"item_{index}_center_y",
                measured=box.center_y,
                target=target_y,
                tolerance=self.tolerance,
                detail="row items do not share a horizontal centerline",
            )
            if issue:
                issues.append(issue)
        gaps = self._gaps(boxes)
        target_gap = self._target_gap(gaps)
        for index, measured in enumerate(gaps):
            issue = _failed_issue(
                constraint=self.name,
                kind=self.kind,
                metric=f"gap_{index}_{index + 1}",
                measured=measured,
                target=target_gap,
                tolerance=self.tolerance,
                detail="row edge gaps are not equal",
            )
            if issue:
                issues.append(issue)
        if self.center_x is not None:
            box = _combined_box(self.mobjects)
            issue = _failed_issue(
                constraint=self.name,
                kind=self.kind,
                metric="row_center_x",
                measured=box.center_x,
                target=self.center_x,
                tolerance=self.tolerance,
                detail="the row's outer visual bounds are not centered on the stage axis",
            )
            if issue:
                issues.append(issue)
        return issues

    def correct(self) -> None:
        boxes = [visual_box(mobject) for mobject in self.mobjects]
        gaps = self._gaps(boxes)
        gap = self._target_gap(gaps)
        target_y = self.y if self.y is not None else statistics.fmean(box.center_y for box in boxes)
        total_width = sum(box.width for box in boxes) + gap * (len(boxes) - 1)
        center_x = self.center_x if self.center_x is not None else _combined_box(self.mobjects).center_x
        cursor = center_x - total_width / 2
        for mobject, box in zip(self.mobjects, boxes, strict=True):
            mobject.set_x(cursor + box.width / 2)
            mobject.set_y(target_y)
            cursor += box.width + gap


class _EvenColumn(_Constraint):
    kind = "even_column"
    priority = 20

    def __init__(
        self,
        mobjects: Sequence[Mobject],
        name: str,
        tolerance: float,
        x: float | None,
        center_y: float | None,
        gap: float | None,
        min_gap: float,
    ):
        super().__init__(name, tolerance)
        if not mobjects:
            raise ValueError("even_column() needs at least one mobject")
        if gap is not None and gap < 0:
            raise ValueError("gap cannot be negative")
        if min_gap < 0:
            raise ValueError("min_gap cannot be negative")
        self.mobjects = list(mobjects)
        self.x = x
        self.center_y = center_y
        self.gap = gap
        self.min_gap = min_gap

    def _gaps(self, boxes: Sequence[Box]) -> list[float]:
        return [boxes[i].bottom - boxes[i + 1].top for i in range(len(boxes) - 1)]

    def _target_gap(self, gaps: Sequence[float]) -> float:
        if self.gap is not None:
            return self.gap
        return max(self.min_gap, statistics.median(gaps)) if gaps else self.min_gap

    def inspect(self) -> list[AlignmentIssue]:
        boxes = [visual_box(mobject) for mobject in self.mobjects]
        issues = []
        target_x = self.x if self.x is not None else statistics.fmean(box.center_x for box in boxes)
        for index, box in enumerate(boxes):
            issue = _failed_issue(
                constraint=self.name,
                kind=self.kind,
                metric=f"item_{index}_center_x",
                measured=box.center_x,
                target=target_x,
                tolerance=self.tolerance,
                detail="column items do not share a vertical centerline",
            )
            if issue:
                issues.append(issue)
        gaps = self._gaps(boxes)
        target_gap = self._target_gap(gaps)
        for index, measured in enumerate(gaps):
            issue = _failed_issue(
                constraint=self.name,
                kind=self.kind,
                metric=f"gap_{index}_{index + 1}",
                measured=measured,
                target=target_gap,
                tolerance=self.tolerance,
                detail="column edge gaps are not equal",
            )
            if issue:
                issues.append(issue)
        if self.center_y is not None:
            box = _combined_box(self.mobjects)
            issue = _failed_issue(
                constraint=self.name,
                kind=self.kind,
                metric="column_center_y",
                measured=box.center_y,
                target=self.center_y,
                tolerance=self.tolerance,
                detail="the column's outer visual bounds are not centered on the requested axis",
            )
            if issue:
                issues.append(issue)
        return issues

    def correct(self) -> None:
        boxes = [visual_box(mobject) for mobject in self.mobjects]
        gaps = self._gaps(boxes)
        gap = self._target_gap(gaps)
        target_x = self.x if self.x is not None else statistics.fmean(box.center_x for box in boxes)
        total_height = sum(box.height for box in boxes) + gap * (len(boxes) - 1)
        center_y = self.center_y if self.center_y is not None else _combined_box(self.mobjects).center_y
        cursor = center_y + total_height / 2
        for mobject, box in zip(self.mobjects, boxes, strict=True):
            mobject.set_x(target_x)
            mobject.set_y(cursor - box.height / 2)
            cursor -= box.height + gap


class _InsideBounds(_Constraint):
    kind = "inside_bounds"
    priority = 10

    def __init__(
        self,
        mobject: Mobject,
        name: str,
        tolerance: float,
        bounds: Box,
        padding: float,
        allow_scale: bool,
    ):
        super().__init__(name, tolerance)
        if padding < 0:
            raise ValueError("padding cannot be negative")
        if bounds.width <= 2 * padding or bounds.height <= 2 * padding:
            raise ValueError("padding leaves no usable area inside the bounds")
        self.mobject = mobject
        self.bounds = bounds
        self.padding = padding
        self.allow_scale = allow_scale

    def inspect(self) -> list[AlignmentIssue]:
        box = visual_box(self.mobject)
        targets = {
            "left": (box.left, self.bounds.left + self.padding, max(0.0, self.bounds.left + self.padding - box.left)),
            "right": (box.right, self.bounds.right - self.padding, max(0.0, box.right - (self.bounds.right - self.padding))),
            "bottom": (box.bottom, self.bounds.bottom + self.padding, max(0.0, self.bounds.bottom + self.padding - box.bottom)),
            "top": (box.top, self.bounds.top - self.padding, max(0.0, box.top - (self.bounds.top - self.padding))),
        }
        issues = []
        for metric, (measured, target, overflow) in targets.items():
            if overflow > self.tolerance:
                issues.append(
                    AlignmentIssue(
                        constraint=self.name,
                        kind=self.kind,
                        metric=f"{metric}_overflow",
                        measured=measured,
                        target=target,
                        error=overflow,
                        tolerance=self.tolerance,
                        detail="visual content extends outside its allowed safe area",
                    )
                )
        return issues

    def correct(self) -> None:
        box = visual_box(self.mobject)
        available_width = self.bounds.width - 2 * self.padding
        available_height = self.bounds.height - 2 * self.padding
        if self.allow_scale and box.width > 0 and box.height > 0:
            scale = min(1.0, available_width / box.width, available_height / box.height)
            if scale < 1.0:
                self.mobject.scale(scale)
                box = visual_box(self.mobject)
        delta = np.zeros(3)
        min_x, max_x = self.bounds.left + self.padding, self.bounds.right - self.padding
        min_y, max_y = self.bounds.bottom + self.padding, self.bounds.top - self.padding
        if box.left < min_x:
            delta[0] += min_x - box.left
        if box.right + delta[0] > max_x:
            delta[0] += max_x - (box.right + delta[0])
        if box.bottom < min_y:
            delta[1] += min_y - box.bottom
        if box.top + delta[1] > max_y:
            delta[1] += max_y - (box.top + delta[1])
        self.mobject.shift(delta)


@dataclass
class AlignmentReport:
    """Result of one refinement loop, suitable for a CI/report artifact."""

    label: str
    passes: int
    converged: bool
    initial_issues: list[AlignmentIssue] = field(default_factory=list)
    issues: list[AlignmentIssue] = field(default_factory=list)
    corrections: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return self.converged and not self.issues

    def as_dict(self) -> dict[str, object]:
        return {
            "label": self.label,
            "passed": self.passed,
            "passes": self.passes,
            "initial_issue_count": len(self.initial_issues),
            "remaining_issue_count": len(self.issues),
            "corrections": self.corrections,
            "issues": [issue.as_dict() for issue in self.issues],
        }

    def summary(self) -> str:
        if self.passed:
            suffix = "no correction needed" if not self.initial_issues else f"refined in {self.passes} pass(es)"
            return f"{self.label}: aligned ({suffix})"
        details = "; ".join(
            f"{issue.constraint}.{issue.metric} off by {issue.error:.3f}u"
            for issue in self.issues[:5]
        )
        if len(self.issues) > 5:
            details += f"; plus {len(self.issues) - 5} more"
        return f"{self.label}: alignment failed after {self.passes} pass(es): {details}"


FailureMode = Literal["return", "warn", "raise"]


class AlignmentLoop:
    """Register, refine, and verify a single animation keyframe.

    Constraints are intentionally opt-in.  An intentionally asymmetric
    composition should not be declared symmetric merely to make a gate pass.
    """

    def __init__(
        self,
        label: str,
        *,
        axis_x: float = float(STAGE_CENTER[0]),
        axis_y: float = float(STAGE_CENTER[1]),
        tolerance: float = DEFAULT_TOLERANCE,
        max_passes: int = DEFAULT_MAX_PASSES,
        on_failure: FailureMode = "raise",
        reporter: Callable[[AlignmentReport], None] | None = None,
    ):
        if tolerance <= 0:
            raise ValueError("tolerance must be positive")
        if max_passes < 1:
            raise ValueError("max_passes must be at least 1")
        if on_failure not in {"return", "warn", "raise"}:
            raise ValueError("on_failure must be 'return', 'warn', or 'raise'")
        self.label = label
        self.axis_x = float(axis_x)
        self.axis_y = float(axis_y)
        self.tolerance = float(tolerance)
        self.max_passes = int(max_passes)
        self.on_failure = on_failure
        self.reporter = reporter
        self.constraints: list[_Constraint] = []
        self.report: AlignmentReport | None = None

    def _tol(self, tolerance: float | None) -> float:
        result = self.tolerance if tolerance is None else float(tolerance)
        if result <= 0:
            raise ValueError("tolerance must be positive")
        return result

    def centered(
        self,
        mobject: Mobject,
        *,
        name: str | None = None,
        horizontal: bool = True,
        vertical: bool = False,
        axis_x: float | None = None,
        axis_y: float | None = None,
        tolerance: float | None = None,
    ) -> Mobject:
        """Center a visual bounding box on one or both requested axes."""

        target_x = (self.axis_x if axis_x is None else float(axis_x)) if horizontal else None
        target_y = (self.axis_y if axis_y is None else float(axis_y)) if vertical else None
        self.constraints.append(
            _Centered(
                mobject,
                name or _name(mobject, "centered object"),
                self._tol(tolerance),
                target_x,
                target_y,
            )
        )
        return mobject

    def mirror_pair(
        self,
        left: Mobject,
        right: Mobject,
        *,
        name: str | None = None,
        axis_x: float | None = None,
        y: float | None = None,
        align_y: bool = True,
        min_gap: float = 0.0,
        tolerance: float | None = None,
    ) -> tuple[Mobject, Mobject]:
        """Place two matching objects at equal center distances from an axis."""

        self.constraints.append(
            _MirrorPair(
                left,
                right,
                name or f"{_name(left, 'left')} / {_name(right, 'right')}",
                self._tol(tolerance),
                self.axis_x if axis_x is None else float(axis_x),
                y,
                align_y,
                float(min_gap),
            )
        )
        return left, right

    def even_row(
        self,
        mobjects: Iterable[Mobject] | Mobject,
        *,
        name: str = "row",
        center_x: float | None = None,
        y: float | None = None,
        gap: float | None = None,
        min_gap: float = 0.0,
        tolerance: float | None = None,
    ) -> Sequence[Mobject]:
        """Equalize edge gaps, share a baseline, and center the row's bounds."""

        items = _as_items(mobjects)
        target_x = self.axis_x if center_x is None else float(center_x)
        self.constraints.append(
            _EvenRow(items, name, self._tol(tolerance), target_x, y, gap, float(min_gap))
        )
        return items

    def balanced_pair(self, left: Mobject, right: Mobject, **kwargs) -> tuple[Mobject, Mobject]:
        """Center the combined outer bounds of two unlike objects with an even gap."""

        self.even_row([left, right], **kwargs)
        return left, right

    def even_column(
        self,
        mobjects: Iterable[Mobject] | Mobject,
        *,
        name: str = "column",
        x: float | None = None,
        center_y: float | None = None,
        gap: float | None = None,
        min_gap: float = 0.0,
        tolerance: float | None = None,
    ) -> Sequence[Mobject]:
        """Equalize edge gaps and align a top-to-bottom list on one x-axis."""

        items = _as_items(mobjects)
        target_x = self.axis_x if x is None else float(x)
        self.constraints.append(
            _EvenColumn(items, name, self._tol(tolerance), target_x, center_y, gap, float(min_gap))
        )
        return items

    def inside_safe(
        self,
        mobject: Mobject,
        *,
        name: str | None = None,
        padding: float = 0.12,
        allow_scale: bool = True,
        bounds: Box | None = None,
        tolerance: float | None = None,
    ) -> Mobject:
        """Keep a composition inside the Shorts-safe rectangle, scaling if needed."""

        self.constraints.append(
            _InsideBounds(
                mobject,
                name or _name(mobject, "safe-area object"),
                self._tol(tolerance),
                bounds or Box(SAFE_LEFT, SAFE_RIGHT, SAFE_BOTTOM, SAFE_TOP),
                float(padding),
                allow_scale,
            )
        )
        return mobject

    def check(self) -> list[AlignmentIssue]:
        """Measure every constraint without moving anything."""

        return [issue for constraint in self.constraints for issue in constraint.inspect()]

    def refine(self) -> AlignmentReport:
        """Iteratively correct all constraints, then warn or fail if any remain."""

        if not self.constraints:
            raise ValueError(f"{self.label!r} has no alignment constraints")
        initial = self.check()
        corrections: list[str] = []
        passes = 0
        seen: set[tuple[tuple[str, str, int], ...]] = set()

        while passes < self.max_passes:
            issues = self.check()
            if not issues:
                break
            signature = tuple(
                sorted(
                    (issue.constraint, issue.metric, round(issue.error / issue.tolerance * 1000))
                    for issue in issues
                )
            )
            if signature in seen:
                break
            seen.add(signature)
            passes += 1
            for constraint in sorted(self.constraints, key=lambda item: item.priority):
                if constraint.inspect():
                    constraint.correct()
                    corrections.append(f"pass {passes}: {constraint.kind} · {constraint.name}")

        remaining = self.check()
        report = AlignmentReport(
            label=self.label,
            passes=passes,
            converged=not remaining,
            initial_issues=initial,
            issues=remaining,
            corrections=corrections,
        )
        self.report = report
        if self.reporter:
            self.reporter(report)
        if remaining and self.on_failure == "warn":
            warnings.warn(report.summary(), stacklevel=2)
        elif remaining and self.on_failure == "raise":
            raise AlignmentError(report.summary())
        return report

    def __enter__(self) -> AlignmentLoop:
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        if exc_type is None:
            self.refine()
        return False


def _as_items(mobjects: Iterable[Mobject] | Mobject) -> list[Mobject]:
    if isinstance(mobjects, Mobject):
        items = list(mobjects.submobjects)
    else:
        items = list(mobjects)
    if not items:
        raise ValueError("the mobject collection is empty")
    if not all(isinstance(item, Mobject) for item in items):
        raise TypeError("alignment collections may contain only Manim mobjects")
    return items


class AlignmentSession:
    """Collect beat-level reports and enforce preview/final policy in one place.

    ``VID_ALIGN=warn`` is suitable for previews; ``VID_ALIGN=strict`` turns any
    unresolved constraint into a failing final-render gate.  ``VID_ALIGN_REPORT``
    may point to a JSON output file.  A scene should call ``finish()`` once after
    constructing its final beat.
    """

    def __init__(
        self,
        *,
        mode: Literal["off", "warn", "strict"] = "warn",
        report_path: str | Path | None = None,
        tolerance: float = DEFAULT_TOLERANCE,
        max_passes: int = DEFAULT_MAX_PASSES,
    ):
        if mode not in {"off", "warn", "strict"}:
            raise ValueError("alignment mode must be 'off', 'warn', or 'strict'")
        self.mode = mode
        self.report_path = Path(report_path) if report_path else None
        self.tolerance = tolerance
        self.max_passes = max_passes
        self.reports: list[AlignmentReport] = []

    @classmethod
    def from_environment(cls, *, default: Literal["off", "warn", "strict"] = "warn") -> AlignmentSession:
        raw = os.environ.get("VID_ALIGN", default).strip().lower()
        aliases = {"0": "off", "false": "off", "1": "warn", "true": "warn", "error": "strict"}
        mode = aliases.get(raw, raw)
        if mode not in {"off", "warn", "strict"}:
            raise ValueError(f"invalid VID_ALIGN value {raw!r}; use off, warn, or strict")
        return cls(mode=mode, report_path=os.environ.get("VID_ALIGN_REPORT"))

    def loop(self, label: str, **kwargs) -> AlignmentLoop:
        """Create a loop that records its report in this session."""

        kwargs.setdefault("tolerance", self.tolerance)
        kwargs.setdefault("max_passes", self.max_passes)
        kwargs.setdefault("on_failure", {"off": "return", "warn": "warn", "strict": "raise"}[self.mode])
        kwargs["reporter"] = self._record
        return AlignmentLoop(label, **kwargs)

    def _record(self, report: AlignmentReport) -> None:
        self.reports.append(report)
        # Persist after every loop so a strict failure during construct still
        # leaves a useful machine-readable report behind.
        self._write_report()

    def _write_report(self) -> None:
        if not self.report_path:
            return
        failed = [report for report in self.reports if not report.passed]
        missing_checks = self.mode != "off" and not self.reports
        self.report_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "passed": not failed and not missing_checks,
            "missing_checks": missing_checks,
            "loop_count": len(self.reports),
            "failed_loop_count": len(failed),
            "reports": [report.as_dict() for report in self.reports],
        }
        self.report_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    def finish(self) -> list[AlignmentReport]:
        """Write the report and enforce that audited scenes registered a check."""

        self._write_report()
        if self.mode != "off" and not self.reports:
            message = "No alignment loops were registered; every finished episode needs measured layout checks."
            if self.mode == "warn":
                warnings.warn(message, stacklevel=2)
            elif self.mode == "strict":
                raise AlignmentError(message)
        return self.reports


def alignment_guides(
    *,
    axis_x: float = float(STAGE_CENTER[0]),
    axis_y: float = float(STAGE_CENTER[1]),
) -> Mobject:
    """Debug overlay for the safe-area symmetry axis and stage center."""

    safe = Rectangle(
        width=SAFE_RIGHT - SAFE_LEFT,
        height=SAFE_TOP - SAFE_BOTTOM,
        stroke_color=LINK_COLOR,
        stroke_width=1.5,
    ).move_to([(SAFE_LEFT + SAFE_RIGHT) / 2, (SAFE_BOTTOM + SAFE_TOP) / 2, 0])
    axis = DashedLine(
        [axis_x, SAFE_BOTTOM, 0],
        [axis_x, SAFE_TOP, 0],
        dash_length=0.10,
        color=LINK_COLOR,
        stroke_width=2,
    )
    cross = VGroup(
        DashedLine([SAFE_LEFT, axis_y, 0], [SAFE_RIGHT, axis_y, 0], dash_length=0.10, color=LINK_COLOR),
        Dot([axis_x, axis_y, 0], radius=0.06, color=LINK_COLOR),
    )
    label = Text("SYMMETRY AXIS", font=BODY_FONT, font_size=16, color=LINK_COLOR)
    label.next_to(axis.get_top(), DOWN, buff=0.08)
    return VGroup(safe, axis, cross, label).set_z_index(201)


__all__ = [
    "AlignmentError",
    "AlignmentIssue",
    "AlignmentLoop",
    "AlignmentReport",
    "AlignmentSession",
    "Box",
    "DEFAULT_MAX_PASSES",
    "DEFAULT_TOLERANCE",
    "alignment_guides",
    "visual_box",
]
