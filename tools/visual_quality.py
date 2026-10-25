"""Rendered and source-level visual-quality checks for a finished Short.

The ordinary export QA protects delivery facts such as resolution, duration and loudness.
This module protects a different failure mode: a technically valid video whose compositions
are mostly empty horizontal strips and whose scene uses fades or pulses where a causal change
should be shown.

The pixel functions are deliberately small and dependency-free.  ``measure_video`` asks
ffmpeg for tiny RGB samples of only the usable stage; the pure functions beneath it are easy
to regression-test with synthetic frames.  ``inspect_scene_motion`` reads scene.py without
executing Manim.
"""

from __future__ import annotations

import ast
import shutil
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence


# The main-diagram portion of the Shorts-safe area, excluding the beat header and captions.
# Values are fractions of the 9:16 frame and follow kit/style.py's geometry.
STAGE_CROP = (0.05625, 0.2012, 0.7875, 0.4605)
SAMPLE_SIZE = (96, 100)
BG_RGB = (15, 17, 23)  # kit.style.BG = #0F1117
FOREGROUND_DELTA = 12

# House-quality floors.  These intentionally describe the reference treatment, not mere
# decodability.  They are arguments on the public judging functions so the production
# configuration can own them without changing the measurement code.
DEFAULT_OPENING_MOTION_MARGIN = 2.0
DEFAULT_MIN_DENSITY = 0.13
DEFAULT_MIN_MEDIAN_DENSITY = 0.18
DEFAULT_MIN_HEIGHT = 0.45
DEFAULT_MIN_MEDIAN_HEIGHT = 0.60
DEFAULT_STRIP_MIN_WIDTH = 0.62
DEFAULT_MAX_LOW_DENSITY_BEATS = 2
DEFAULT_MAX_HORIZONTAL_STRIP_BEATS = 2
DEFAULT_MIN_CAUSAL_BEATS = 7


@dataclass(frozen=True)
class FrameProfile:
    foreground_share: float
    width_share: float
    height_share: float


@dataclass(frozen=True)
class SceneMotionReport:
    beats: dict[str, int]
    evidence: dict[str, list[str]]

    @property
    def causal_beats(self) -> list[str]:
        return [beat for beat, count in self.beats.items() if count]


def foreground_mask(
    rgb: bytes,
    size: tuple[int, int],
    *,
    background: tuple[int, int, int] = BG_RGB,
    delta: int = FOREGROUND_DELTA,
) -> list[bool]:
    """Return pixels visibly different from the house background.

    H.264 moves nominally flat background values by a few integer levels.  A maximum-channel
    distance is more stable than exact RGB equality and still sees muted gray strokes.
    """

    width, height = size
    expected = width * height * 3
    if len(rgb) != expected:
        raise ValueError(f"expected {expected} RGB bytes for {width}x{height}, got {len(rgb)}")
    return [
        max(abs(rgb[i + channel] - background[channel]) for channel in range(3)) >= delta
        for i in range(0, len(rgb), 3)
    ]


def frame_profile(rgb: bytes, size: tuple[int, int] = SAMPLE_SIZE) -> FrameProfile:
    """Measure foreground density and its bounding-box coverage of the usable stage."""

    width, height = size
    mask = foreground_mask(rgb, size)
    points = [(i % width, i // width) for i, on in enumerate(mask) if on]
    if not points:
        return FrameProfile(0.0, 0.0, 0.0)
    xs, ys = zip(*points)
    return FrameProfile(
        foreground_share=len(points) / (width * height),
        width_share=(max(xs) - min(xs) + 1) / width,
        height_share=(max(ys) - min(ys) + 1) / height,
    )


def gray_motion(a: bytes, b: bytes) -> float:
    """Mean absolute luma change between same-sized RGB frames."""

    if len(a) != len(b) or len(a) % 3:
        raise ValueError("motion frames must have the same RGB dimensions")
    if not a:
        return 0.0
    total = 0.0
    for i in range(0, len(a), 3):
        # Integer-friendly Rec. 709 approximation.  Absolute scale remains 0..255.
        ya = (54 * a[i] + 183 * a[i + 1] + 19 * a[i + 2]) / 256
        yb = (54 * b[i] + 183 * b[i + 1] + 19 * b[i + 2]) / 256
        total += abs(ya - yb)
    return total / (len(a) // 3)


def _ffmpeg() -> str:
    exe = shutil.which("ffmpeg")
    if not exe:
        raise FileNotFoundError("ffmpeg is not on PATH; run this check through vid")
    return exe


def rgb_frame(
    video: Path,
    time_s: float,
    *,
    size: tuple[int, int] = SAMPLE_SIZE,
    crop: tuple[float, float, float, float] = STAGE_CROP,
) -> bytes:
    """Decode one tiny RGB frame from the main-diagram stage."""

    width, height = size
    x, y, w, h = crop
    vf = (
        f"crop=iw*{w}:ih*{h}:iw*{x}:ih*{y},"
        f"scale={width}:{height}:flags=area,format=rgb24"
    )
    return subprocess.run(
        [_ffmpeg(), "-v", "error", "-ss", f"{max(0.0, time_s):.3f}", "-i", str(video),
         "-frames:v", "1", "-vf", vf, "-f", "rawvideo", "-"],
        capture_output=True,
        check=True,
    ).stdout


def representative_times(beats: Mapping[str, Sequence[float]], at: float = 0.70) -> dict[str, float]:
    """Choose the settled composition in each narrated beat, before its transition."""

    return {
        beat: float(span[0]) + (float(span[1]) - float(span[0])) * at
        for beat, span in beats.items()
        if len(span) == 2 and float(span[1]) > float(span[0])
    }


def measure_video(video: Path, beats: Mapping[str, Sequence[float]]) -> dict:
    """Return rendered visual metrics for QA JSON.

    Five opening samples avoid treating one lucky 0/0.5-second pair as a strong hook.  One
    settled sample per beat profiles composition without making rendering slower.
    """

    opening_times = (0.0, 0.25, 0.50, 0.75, 1.0)
    opening = [rgb_frame(video, t) for t in opening_times]
    opening_steps = [gray_motion(a, b) for a, b in zip(opening, opening[1:])]

    times = representative_times(beats)
    profiles = {beat: frame_profile(rgb_frame(video, t)) for beat, t in times.items()}
    densities = [p.foreground_share for p in profiles.values()]
    heights = [p.height_share for p in profiles.values()]
    return {
        "opening_motion_steps": [round(value, 3) for value in opening_steps],
        "opening_motion_min": round(min(opening_steps, default=0.0), 3),
        "opening_motion_mean": round(sum(opening_steps) / len(opening_steps), 3) if opening_steps else 0.0,
        "beat_visuals": {beat: {key: round(value, 4) for key, value in asdict(profile).items()}
                         for beat, profile in profiles.items()},
        "visual_density_median": round(_median(densities), 4),
        "stage_height_median": round(_median(heights), 4),
    }


def judge_rendered(
    metrics: Mapping,
    *,
    existing_opening_motion_floor: float,
    opening_motion_margin: float = DEFAULT_OPENING_MOTION_MARGIN,
    min_density: float = DEFAULT_MIN_DENSITY,
    min_median_density: float = DEFAULT_MIN_MEDIAN_DENSITY,
    min_height: float = DEFAULT_MIN_HEIGHT,
    min_median_height: float = DEFAULT_MIN_MEDIAN_HEIGHT,
    strip_min_width: float = DEFAULT_STRIP_MIN_WIDTH,
    max_low_density_beats: int = DEFAULT_MAX_LOW_DENSITY_BEATS,
    max_horizontal_strip_beats: int = DEFAULT_MAX_HORIZONTAL_STRIP_BEATS,
) -> dict[str, list[str]]:
    """Return issues keyed by production-rule name for rendered visual quality."""

    issues: dict[str, list[str]] = {"opening-quality": [], "stage-coverage": [], "layout-variety": []}
    opening = float(metrics.get("opening_motion_min", 0.0))
    target = existing_opening_motion_floor * opening_motion_margin
    if opening < target:
        issues["opening-quality"].append(
            f"weakest opening quarter-second changes {opening:.3f} gray levels "
            f"(quality floor {target:.3f}); keep meaningful motion alive through the first second"
        )

    profiles = metrics.get("beat_visuals", {})
    low = [beat for beat, p in profiles.items() if float(p.get("foreground_share", 0.0)) < min_density]
    if len(low) > max_low_density_beats:
        issues["stage-coverage"].append(
            f"{len(low)} beat compositions are visually sparse ({', '.join(low)}; max "
            f"{max_low_density_beats} below {min_density:.1%} foreground)"
        )
    density_median = float(metrics.get("visual_density_median", 0.0))
    if profiles and density_median < min_median_density:
        issues["stage-coverage"].append(
            f"median foreground coverage is {density_median:.1%} (minimum "
            f"{min_median_density:.1%}); enlarge the hero diagrams and use the safe stage"
        )

    strips = [
        beat for beat, p in profiles.items()
        if float(p.get("width_share", 0.0)) >= strip_min_width
        and float(p.get("height_share", 0.0)) < min_height
    ]
    if len(strips) > max_horizontal_strip_beats:
        issues["layout-variety"].append(
            f"{len(strips)} beats collapse into wide horizontal strips ({', '.join(strips)}; max "
            f"{max_horizontal_strip_beats}); vary scale and use the stage vertically"
        )
    height_median = float(metrics.get("stage_height_median", 0.0))
    if profiles and height_median < min_median_height:
        issues["layout-variety"].append(
            f"median composition height is {height_median:.0%} of the stage (minimum "
            f"{min_median_height:.0%}); too many beats occupy the same shallow band"
        )
    return issues


def _median(values: Sequence[float]) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    middle = len(ordered) // 2
    return ordered[middle] if len(ordered) % 2 else (ordered[middle - 1] + ordered[middle]) / 2


_NAMED_CAUSAL = {
    "Transform",
    "ReplacementTransform",
    "TransformFromCopy",
    "FadeTransform",
    "MoveAlongPath",
    "Rotate",
    "GrowArrow",
}
_GEOMETRY_CHANGES = {
    "shift",
    "move_to",
    "next_to",
    "align_to",
    "rotate",
    "stretch",
    "stretch_to_fit_height",
    "stretch_to_fit_width",
}
_SELF_INFRASTRUCTURE = {
    "alignment_loop", "beat", "clear_stage", "hold", "placeholder", "sfx", "wait",
}


def _call_name(call: ast.Call) -> str | None:
    if isinstance(call.func, ast.Name):
        return call.func.id
    if isinstance(call.func, ast.Attribute):
        return call.func.attr
    return None


def _self_call(call: ast.Call) -> str | None:
    func = call.func
    if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name) and func.value.id == "self":
        return func.attr
    return None


def _is_animate_geometry_change(call: ast.Call) -> bool:
    if not isinstance(call.func, ast.Attribute) or call.func.attr not in _GEOMETRY_CHANGES:
        return False
    return any(isinstance(node, ast.Attribute) and node.attr == "animate" for node in ast.walk(call.func))


def _beat_id(with_node: ast.With) -> str | None:
    for item in with_node.items:
        call = item.context_expr
        if not isinstance(call, ast.Call) or _self_call(call) != "beat" or not call.args:
            continue
        arg = call.args[0]
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
            return arg.value
    return None


def inspect_scene_motion(scene: Path) -> SceneMotionReport:
    """Count causal animation evidence in each beat of ``Episode.construct``.

    Generic entrances, exits, pulses and highlights are excluded.  Calls to episode helper
    methods are followed recursively, so a reusable B3/B6 mechanism is credited to both
    beats without executing the scene.
    """

    tree = ast.parse(scene.read_text(encoding="utf-8"))
    klass = next((n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "Episode"), None)
    if klass is None:
        return SceneMotionReport({}, {})
    methods = {n.name: n for n in klass.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    construct = methods.get("construct")
    if construct is None:
        return SceneMotionReport({}, {})

    def evidence(nodes: Iterable[ast.AST], seen: frozenset[str] = frozenset()) -> list[str]:
        found: set[str] = set()
        helper_names: set[str] = set()
        for root in nodes:
            for node in ast.walk(root):
                if not isinstance(node, ast.Call):
                    continue
                name = _call_name(node)
                if name in _NAMED_CAUSAL:
                    found.add(f"{name}@{node.lineno}")
                elif _is_animate_geometry_change(node):
                    found.add(f"animate.{name}@{node.lineno}")
                helper = _self_call(node)
                if helper and helper in methods and helper not in _SELF_INFRASTRUCTURE and helper not in seen:
                    helper_names.add(helper)
        for helper in helper_names:
            found.update(evidence(methods[helper].body, seen | {helper}))
        return sorted(found)

    beats: dict[str, int] = {}
    all_evidence: dict[str, list[str]] = {}
    for node in ast.walk(construct):
        if not isinstance(node, ast.With) or not (beat := _beat_id(node)):
            continue
        hits = evidence(node.body)
        beats[beat] = len(hits)
        all_evidence[beat] = hits
    return SceneMotionReport(beats, all_evidence)


def judge_scene_motion(
    report: SceneMotionReport,
    *,
    min_causal_beats: int = DEFAULT_MIN_CAUSAL_BEATS,
    required_mechanism_beats: Sequence[str] = ("B3", "B6"),
) -> list[str]:
    """Require causal changes across the story and in both mechanism replays."""

    # B9 is an end-map/loop pose and may intentionally delegate to the shared kit.
    eligible = [beat for beat in report.beats if beat != "B9"]
    causal = [beat for beat in eligible if report.beats[beat] > 0]
    issues = []
    if len(causal) < min(min_causal_beats, len(eligible)):
        generic = [beat for beat in eligible if report.beats[beat] == 0]
        issues.append(
            f"only {len(causal)}/{len(eligible)} story beats show a causal geometry change "
            f"(need {min(min_causal_beats, len(eligible))}); generic-only: {', '.join(generic) or 'none'}"
        )
    missing = [beat for beat in required_mechanism_beats if report.beats.get(beat, 0) == 0]
    if missing:
        issues.append(f"mechanism beat(s) use no causal geometry change: {', '.join(missing)}")
    return issues


def delivery_note_audit(notes: Mapping[str, str]) -> dict:
    """Expose the deliberate limit of NOTE metadata to callers and reports.

    NOTE text is not passed to Kokoro by ``ShortScene.beat``.  This is not an automated pass:
    the caller must keep the sound-on human review open instead of claiming the directions
    were performed merely because the fields exist.
    """

    spoken = [beat for beat, note in notes.items() if note.strip()]
    return {
        "notes_present": spoken,
        "notes_drive_synthesis": False,
        "manual_listen_required": bool(spoken),
    }


__all__ = [
    "FrameProfile", "SceneMotionReport", "delivery_note_audit", "foreground_mask",
    "frame_profile", "gray_motion", "inspect_scene_motion", "judge_rendered",
    "judge_scene_motion", "measure_video", "representative_times", "rgb_frame",
]
