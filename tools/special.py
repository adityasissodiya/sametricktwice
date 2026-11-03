"""Specials: videos this pipeline makes that are not Shorts.

A special lives in specials/<name>/ rather than episodes/, so the series never sees it:
`vid status`, `vid ci`, the Connection Map and later episodes' carry-over checks all read
episodes/ only. `vid` finds a special by name, like an episode, and runs the same gates on it,
with three differences:

    format   the script's front matter may set `format: landscape`: a 16:9 frame drawn with
             kit/landscape.py, 960x540 previews and a 1920x1080 master
    limits   specials/<name>/limits.toml overlays keys of ste.toml ([ste]) and of
             design.toml's [qa] for this special only (a three-minute explainer is not
             45-60 s); every key it does not name keeps the series value
    exports  the master, its captions and its QA report stay in the special's own folder

Every key in limits.toml needs the creator's approval and a comment that says why, as a limit
in design.toml does. The picture rules measure a landscape master on its own stage (the
crop below); their floors were calibrated on the 9:16 references.

Usage: vid check | preview | frames | align | final | qa <special>
"""

from __future__ import annotations

import dataclasses
import json
import sys
import tomllib
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import design, qa, qa_contract, ste, visual_quality  # noqa: E402
from tools.design import Result, result, show  # noqa: E402
from tools.scriptfile import Script, load_script  # noqa: E402

SPECIALS = ROOT / "specials"
# Preview and master sizes for each format.
FORMATS = {"short": ((540, 960), (1080, 1920)), "landscape": ((960, 540), (1920, 1080))}
# Contact-sheet frames: a quarter of the master for a phone, a third for a laptop screen.
THUMBS = {"short": (270, 480), "landscape": (640, 360)}
# The landscape stage as fractions of the 16:9 frame, following kit/landscape.py: the
# title-safe width, from under the header band to above the caption band.
WIDE_STAGE_CROP = (0.05, 0.1475, 0.9, 0.65625)
WIDE_SAMPLE_SIZE = (150, 62)
OVERLAYS = {"ste": ste.Config, "qa": qa.Limits}


def is_special(ep: Path) -> bool:
    return ep.resolve().parent == SPECIALS.resolve()


def video_format(ep: Path) -> str:
    """The script's `format:` front matter: "short" (the default) or "landscape"."""
    fmt = load_script(ep / "script.md").meta.get("format", "").strip().lower() or "short"
    if fmt not in FORMATS:
        sys.exit(f"{ep.name}/script.md: format {fmt!r} is not one of: {', '.join(FORMATS)}")
    return fmt


def frame_size(ep: Path, final: bool) -> tuple[int, int]:
    return FORMATS[video_format(ep)][1 if final else 0]


def thumb_size(ep: Path) -> tuple[int, int]:
    return THUMBS[video_format(ep)]


def export_path(ep: Path) -> Path:
    return ep / f"{ep.name}.mp4"


def overlay(ep: Path, section: str) -> dict:
    """One section of the special's limits.toml; unknown sections and keys are errors, so a
    misspelled limit cannot silently fall back to the series value."""
    path = ep / "limits.toml"
    data = tomllib.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    if unknown := sorted(set(data) - set(OVERLAYS)):
        sys.exit(f"{path.relative_to(ROOT)}: no section [{unknown[0]}]; it may overlay {', '.join(OVERLAYS)}")
    values = data.get(section, {})
    names = {f.name for f in dataclasses.fields(OVERLAYS[section])}
    if unknown := sorted(set(values) - names):
        sys.exit(f"{path.relative_to(ROOT)}: [{section}] has no key {unknown[0]!r}")
    return values


def ste_config(ep: Path) -> ste.Config:
    return dataclasses.replace(ste.load_config(), **overlay(ep, "ste"))


def qa_limits(ep: Path) -> qa.Limits:
    return dataclasses.replace(design.load_section(qa.Limits, "qa"), **overlay(ep, "qa"))


# --- vid check ---------------------------------------------------------------------------

def length(script: Script, ep: Path) -> Result:
    """design.py's length rule, against this special's target."""
    cfg = ste_config(ep)
    count = script.word_count
    secs = count / cfg.wpm * 60
    lo, hi = cfg.seconds
    issues = [] if lo <= secs <= hi else [f"about {secs:.0f} s: {'cut' if secs > hi else 'add'} words to reach {lo}-{hi} s"]
    return result("length", issues, f"{count} words, about {secs:.0f} s at {cfg.wpm} words/min (target {lo}-{hi} s)")


def check(ep: Path, final: bool = False) -> bool:
    """The STE score and every design rule, as `vid check` runs them for a Short."""
    script = load_script(ep / "script.md")
    cfg = ste_config(ep)
    ok = ste.report(script, cfg, ste.check(script, cfg))
    print()
    results = [length(script, ep) if r.rule == "length" else r for r in design.check(ep, final)]
    return show(f"Design check: {ep.name} ({video_format(ep)} special)", results) and ok


# --- vid qa ------------------------------------------------------------------------------

def picture_metrics(video: Path, beats: dict) -> dict:
    """visual_quality.measure_video's metrics, sampled from the landscape stage."""

    def sample(t: float) -> bytes:
        return visual_quality.rgb_frame(video, t, size=WIDE_SAMPLE_SIZE, crop=WIDE_STAGE_CROP)

    opening = [sample(t) for t in (0.0, 0.25, 0.50, 0.75, 1.0)]
    steps = [visual_quality.gray_motion(a, b) for a, b in zip(opening, opening[1:])]
    times = visual_quality.representative_times(beats)
    profiles = {beat: visual_quality.frame_profile(sample(t), WIDE_SAMPLE_SIZE) for beat, t in times.items()}
    densities = [p.foreground_share for p in profiles.values()]
    heights = [p.height_share for p in profiles.values()]
    return {
        "opening_motion_steps": [round(value, 3) for value in steps],
        "opening_motion_min": round(min(steps, default=0.0), 3),
        "opening_motion_mean": round(sum(steps) / len(steps), 3) if steps else 0.0,
        "beat_visuals": {beat: {key: round(value, 4) for key, value in asdict(profile).items()}
                         for beat, profile in profiles.items()},
        "visual_density_median": round(visual_quality._median(densities), 4),
        "stage_height_median": round(visual_quality._median(heights), 4),
    }


def format_result(m: dict, fmt: str) -> Result:
    """qa.py's format rule for this special's master size."""
    width, height = FORMATS[fmt][1]
    issues = []
    if (m["width"], m["height"]) != (width, height):
        issues.append(f"{m['width']}x{m['height']}, not {width}x{height}")
    if m["fps"] != 60:
        issues.append(f"{m['fps']} fps, not 60")
    if m["video_codec"] != "h264" or m["audio_codec"] != "aac":
        issues.append(f"{m['video_codec']}/{m['audio_codec']}, not h264/aac")
    if m["sample_rate"] != 48000:
        issues.append(f"audio at {m['sample_rate']} Hz, not 48000")
    return result("format", issues, f"{m['width']}x{m['height']}, {m['fps']} fps, "
                                    f"{m['video_codec']}/{m['audio_codec']} {m['sample_rate']} Hz")


def fingerprint(ep: Path) -> str:
    """The QA fingerprint plus what a special's verdict also depends on."""
    return qa_contract.pipeline_fingerprint([
        *qa_contract.QA_DEPENDENCIES, ROOT / "tools" / "special.py", ROOT / "kit" / "landscape.py", ep / "limits.toml",
    ])


def picture_check(ep: Path, video: Path, times: dict[str, tuple[float, float]]) -> bool:
    """`vid frames`: the picture rules of this special's QA on a render."""
    spans = {beat: [round(t0, 3), round(t1, 3)] for beat, (t0, t1) in times.items()}
    fmt = video_format(ep)
    m = picture_metrics(video, spans) if fmt == "landscape" else visual_quality.measure_video(video, spans)
    return show(f"Picture checks on {video.name} (the limits of this special's QA)", qa.picture_results(m, qa_limits(ep)))


def run_qa(ep: Path, video: Path | None = None) -> bool:
    """qa.run for a special: the same measurements and rules, with this special's limits,
    master size and stage; the report sits next to the master."""
    video = video or export_path(ep)
    if not video.exists():
        print(f"Export QA: no {video.name} yet. Make it with: vid final {ep.name}")
        return False
    fmt = video_format(ep)
    metrics, problems = qa.measure(ep, video)
    if fmt == "landscape":
        metrics.update(picture_metrics(video, metrics["beats"]))
    results = [format_result(metrics, fmt) if r.rule == "format" else r
               for r in qa.judge(metrics, problems, qa_limits(ep))]
    passed = show(f"Export QA: {video.name} ({fmt} special)", results)
    report = {
        "episode": ep.name,
        "video": video.name,
        "format": fmt,
        "checked": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "pipeline_fingerprint": fingerprint(ep),
        "passed": passed,
        "metrics": metrics,
        "results": [asdict(r) for r in results],
    }
    out = video.with_suffix(".qa.json")
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Measurements: {out.name}")
    return passed
