"""Render-time sound-effect QA used by :mod:`tools.qa`.

The scene writes ``media/<episode>/sfx-manifest.json`` while Manim renders.  Static
source inspection is not enough: a helper can run more than once, and cue timing only
exists at render time.  This module joins that manifest with the actual source-file
levels and the cached narrator audio so the final gate can distinguish a present sound
from a perceptible one.

Levels are deliberately measured before the shared mastering filter.  The narrator and
effects receive that filter together, so their relative level is the useful signal.  A
short transient may qualify through its peak even when its mean is low; sustained sounds
qualify through mean level.  Masking is only flagged while a cue overlaps narration.
"""

from __future__ import annotations

import json
import math
import re
import statistics
import subprocess
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Iterable

from tools.design import Result, result

ROOT = Path(__file__).resolve().parents[1]
MEDIA = ROOT / "media"
MANIFEST = "sfx-manifest.json"


@dataclass(frozen=True)
class AudioStats:
    duration_s: float
    mean_dbfs: float
    peak_dbfs: float


def _db(text: str) -> float:
    return float("-inf") if text == "-inf" else float(text)


@lru_cache(maxsize=None)
def audio_stats(path: Path) -> AudioStats:
    """Return duration, mean and peak dBFS for an audio source using project tools."""
    path = path.resolve()
    duration = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    proc = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af", "volumedetect", "-f", "null", "-"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if proc.returncode:
        raise RuntimeError(proc.stderr[-600:])
    means = re.findall(r"mean_volume:\s*(-?[\d.]+|-inf)\s*dB", proc.stderr)
    peaks = re.findall(r"max_volume:\s*(-?[\d.]+|-inf)\s*dB", proc.stderr)
    if not means or not peaks:
        raise ValueError(f"ffmpeg did not report levels for {path.name}")
    return AudioStats(float(duration), _db(means[-1]), _db(peaks[-1]))


def combined_mean(stats: Iterable[AudioStats]) -> float | None:
    """Duration-weighted mean dBFS for separate narration files."""
    usable = [s for s in stats if s.duration_s > 0 and math.isfinite(s.mean_dbfs)]
    duration = sum(s.duration_s for s in usable)
    if not duration:
        return None
    power = sum((10 ** (s.mean_dbfs / 10)) * s.duration_s for s in usable) / duration
    return 10 * math.log10(power) if power > 0 else None


def _overlaps(start: float, end: float, spans: list[tuple[float, float]]) -> bool:
    return any(start < b and end > a for a, b in spans)


def _max_simultaneous(cues: list[dict]) -> int:
    events: list[tuple[float, int]] = []
    for cue in cues:
        start = float(cue["time_s"])
        end = start + float(cue.get("duration_s", 0.0))
        events.extend(((start, 1), (end, -1)))
    count = peak = 0
    # Ends sort before starts at the same timestamp, so back-to-back cues do not overlap.
    for _, change in sorted(events, key=lambda event: (event[0], event[1])):
        count += change
        peak = max(peak, count)
    return peak


def _empty(status: str, errors: list[str], duration: float) -> dict:
    return {
        "sfx_manifest_status": status,
        "sfx_manifest_errors": errors,
        "sfx_cue_count": 0,
        "sfx_cues_per_10s": 0.0,
        "sfx_voice_mean_dbfs": None,
        "sfx_source_errors": [],
        "sfx_speech_overlap_cues": 0,
        "sfx_max_simultaneous": 0,
        "sfx_cues": [],
        "sfx_duration_s": round(duration, 3),
    }


def measure(ep: Path, duration: float, narration_spans: list[tuple[float, float]],
            voice_paths: Iterable[Path], expected_voice_files: int | None = None) -> dict:
    """Measure executed cues against source files and the frozen narrator."""
    manifest_path = MEDIA / ep.name / MANIFEST
    if not manifest_path.exists():
        return _empty("missing", [f"no {MANIFEST}; render the episode again"], duration)
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return _empty("invalid", [f"cannot read {MANIFEST}: {exc}"], duration)

    manifest_errors: list[str] = []
    if manifest.get("version") != 1:
        manifest_errors.append(f"unsupported manifest version {manifest.get('version')!r}")
    if manifest.get("episode") != ep.name:
        manifest_errors.append(f"manifest is for {manifest.get('episode')!r}, not {ep.name!r}")
    scene_duration = manifest.get("scene_duration_s")
    if not isinstance(scene_duration, (int, float)):
        manifest_errors.append("manifest has no scene duration")
    elif abs(float(scene_duration) - duration) > 0.75:
        manifest_errors.append(
            f"manifest duration {float(scene_duration):.2f} s does not match export {duration:.2f} s; rerender"
        )
    raw_cues = manifest.get("cues")
    if not isinstance(raw_cues, list):
        manifest_errors.append("manifest cues are not a list")
        raw_cues = []

    voice_paths = list(voice_paths)
    voice_errors: list[str] = []
    if expected_voice_files is not None and len(voice_paths) != expected_voice_files:
        voice_errors.append(
            f"found {len(voice_paths)}/{expected_voice_files} cached series-voice files; rerender with the frozen voice"
        )
    voice_levels: list[AudioStats] = []
    for path in voice_paths:
        try:
            voice_levels.append(audio_stats(Path(path)))
        except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
            voice_errors.append(f"{Path(path).name}: {exc}")
    voice_mean = combined_mean(voice_levels)

    root = ROOT.resolve()
    source_errors: list[str] = []
    details: list[dict] = []
    for index, raw in enumerate(raw_cues, start=1):
        if not isinstance(raw, dict):
            source_errors.append(f"cue {index}: entry is not an object")
            continue
        name = str(raw.get("name", f"cue {index}"))
        try:
            start = float(raw["time_s"])
            gain = float(raw["gain_db"])
            source_value = str(raw["source"])
        except (KeyError, TypeError, ValueError) as exc:
            source_errors.append(f"cue {index} ({name}): invalid time, gain or source ({exc})")
            continue
        if not math.isfinite(start) or not math.isfinite(gain) or start < 0 or start > duration + 0.1:
            source_errors.append(f"cue {index} ({name}): invalid time {start} or gain {gain}")
            continue
        source = Path(source_value)
        source = source.resolve() if source.is_absolute() else (root / source).resolve()
        try:
            source.relative_to(root)
        except ValueError:
            source_errors.append(f"cue {index} ({name}): source is outside the project")
            continue
        if not source.is_file():
            source_errors.append(f"cue {index} ({name}): missing source {source_value}")
            continue
        try:
            stats = audio_stats(source)
        except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
            source_errors.append(f"cue {index} ({name}): {exc}")
            continue
        end = start + stats.duration_s
        effective_mean = stats.mean_dbfs + gain
        effective_peak = stats.peak_dbfs + gain
        details.append({
            "name": name,
            "time_s": round(start, 3),
            "duration_s": round(stats.duration_s, 3),
            "gain_db": round(gain, 1),
            "source": source.relative_to(root).as_posix(),
            "source_mean_dbfs": round(stats.mean_dbfs, 1),
            "source_peak_dbfs": round(stats.peak_dbfs, 1),
            "effective_mean_dbfs": round(effective_mean, 1),
            "effective_peak_dbfs": round(effective_peak, 1),
            "relative_mean_db": round(effective_mean - voice_mean, 1) if voice_mean is not None else None,
            "relative_peak_to_voice_mean_db": round(effective_peak - voice_mean, 1)
            if voice_mean is not None else None,
            "overlaps_speech": _overlaps(start, end, narration_spans),
        })

    source_errors = [*voice_errors, *source_errors]
    count = len(raw_cues)
    return {
        "sfx_manifest_status": "invalid" if manifest_errors else "ok",
        "sfx_manifest_errors": manifest_errors,
        "sfx_cue_count": count,
        "sfx_cues_per_10s": round(count / duration * 10, 2) if duration else 0.0,
        "sfx_voice_mean_dbfs": round(voice_mean, 1) if voice_mean is not None else None,
        "sfx_source_errors": source_errors,
        "sfx_speech_overlap_cues": sum(bool(cue["overlaps_speech"]) for cue in details),
        "sfx_max_simultaneous": _max_simultaneous(details),
        "sfx_cues": details,
        "sfx_duration_s": round(duration, 3),
    }


def judge(metrics: dict, lim) -> list[Result]:
    """Return density, audibility and speech-masking results for export QA."""
    status = metrics.get("sfx_manifest_status")
    if status is None:  # synthetic/legacy metric dictionaries used by callers outside measure()
        return [
            Result("sfx-density", "skip", "no render-time SFX metrics"),
            Result("sfx-audibility", "skip", "no render-time SFX metrics"),
            Result("sfx-masking", "skip", "no render-time SFX metrics"),
        ]
    if status == "missing":
        issue = metrics.get("sfx_manifest_errors") or [f"no {MANIFEST}; rerender the episode"]
        return [
            result("sfx-density", issue, "no executed-cue manifest"),
            Result("sfx-audibility", "skip", "needs the executed-cue manifest"),
            Result("sfx-masking", "skip", "needs the executed-cue manifest"),
        ]

    cues = metrics.get("sfx_cues", [])
    count = int(metrics.get("sfx_cue_count", 0))
    density = float(metrics.get("sfx_cues_per_10s", 0.0))
    density_issues = list(metrics.get("sfx_manifest_errors", []))
    if count < lim.sfx_min_cues:
        density_issues.append(f"{count} executed cues (min {lim.sfx_min_cues})")
    if density < lim.sfx_min_density:
        density_issues.append(f"{density:g} cues per 10 s (min {lim.sfx_min_density:g})")
    density_result = result(
        "sfx-density", density_issues,
        f"{count} executed cues = {density:g}/10 s (min {lim.sfx_min_cues} and {lim.sfx_min_density:g}/10 s)",
    )

    source_errors = list(metrics.get("sfx_source_errors", []))
    audible = [
        cue for cue in cues
        if ((cue.get("relative_mean_db") is not None
             and cue["relative_mean_db"] >= lim.sfx_audible_mean_min)
            or (cue.get("relative_peak_to_voice_mean_db") is not None
                and cue["relative_peak_to_voice_mean_db"] >= lim.sfx_audible_peak_min))
    ]
    share = len(audible) / count if count else 0.0
    audibility_issues = source_errors.copy()
    if metrics.get("sfx_voice_mean_dbfs") is None:
        audibility_issues.append("no measurable cached series-voice audio")
    if len(audible) < lim.sfx_min_audible_cues:
        audibility_issues.append(f"only {len(audible)} perceptible cues (min {lim.sfx_min_audible_cues})")
    if share < lim.sfx_min_audible_share:
        audibility_issues.append(
            f"{share:.0%} of cues are perceptible (min {lim.sfx_min_audible_share:.0%}); raise buried cue gains"
        )
    rel = [cue["relative_mean_db"] for cue in cues if cue.get("relative_mean_db") is not None]
    median = f"; median mean {statistics.median(rel):g} dB vs narration" if rel else ""
    audibility_result = result(
        "sfx-audibility", audibility_issues,
        f"{len(audible)}/{count} cues clear the mean/peak floor ({share:.0%}){median}",
    )

    masking = [
        cue for cue in cues
        if cue.get("overlaps_speech") and cue.get("relative_mean_db") is not None
        and cue["relative_mean_db"] > lim.sfx_masking_mean_max
    ]
    masking_issues = []
    if masking:
        examples = ", ".join(f"{c['name']} at {c['time_s']:g} s" for c in masking[:4])
        masking_issues.append(
            f"{len(masking)} cue(s) can mask narration (mean above {lim.sfx_masking_mean_max:g} dB relative): {examples}"
        )
    simultaneous = int(metrics.get("sfx_max_simultaneous", 0))
    if simultaneous > lim.sfx_max_simultaneous:
        masking_issues.append(
            f"{simultaneous} sound effects overlap at once (max {lim.sfx_max_simultaneous})"
        )
    masking_result = result(
        "sfx-masking", masking_issues,
        f"{metrics.get('sfx_speech_overlap_cues', 0)}/{count} cues overlap speech; "
        f"{len(masking)} too loud; max {simultaneous} simultaneous",
    )
    return [density_result, audibility_result, masking_result]
