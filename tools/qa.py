"""Export QA: measure the finished Short against the research-backed targets.

`vid final` runs it on every new export, and `vid qa <ep>` runs it again at any time. It
writes exports/<ep>.qa.json, which `vid report` joins with the channel's results. Each
check has the same name in RESEARCH.md; its limits live in design.toml [qa].

    format        1080x1920, 60 fps, H.264 video and AAC 48 kHz audio
    length        45-60 s
    cold-open     the first word comes at once, and frame 0 already shows a moving cover
    hook-time     the hook (B1) is over within the first seconds
    early-answer  the mechanism beat starts within the first third of the video
    speech-rate   a moderate pace: not rushed, and not slowed down
    delivery-pace the house delivery stays in the engaging range of the references
    pauses        clear sentence boundaries (pauses near 0.6 s sound most natural)
    captions      the .srt holds exactly the approved VO, beat by beat, in order
    loudness      about -14 LUFS, true peak at or below -1.5 dBTP
    opening-quality meaningful motion continues through the whole first second
    stage-coverage hero diagrams use enough of the phone-readable safe stage
    layout-variety compositions do not collapse into repeated horizontal strips
    sfx-density   enough action-synced cues to support a Short of this length
    sfx-audibility effects are perceptible relative to the frozen narrator
    sfx-masking   effects do not cover narration or pile up in the same moment
    dead-air      no near-black stretch or frozen picture long enough to lose a viewer

Usage: vid qa <ep> [--video FILE]
"""

from __future__ import annotations

import json
import re
import statistics
import subprocess
import sys
import tomllib
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import NamedTuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import design, qa_contract, sfxqa, visual_quality  # noqa: E402
from tools.design import Result, load_section, result, sentences, show  # noqa: E402
from tools.scriptfile import WORD, Script, load_script  # noqa: E402

EXPORTS = ROOT / "exports"
MEDIA = ROOT / "media"
_STAMP = re.compile(r"(\d+):(\d+):(\d+)[,.](\d+)")


@dataclass
class Limits:
    seconds: list[float] = field(default_factory=lambda: [45, 60])
    narration_start_max: float = 0.3
    first_frame_min_contrast: float = 4.0
    first_frame_min_motion: float = 0.15
    hook_end_max: float = 6.0
    answer_by: float = 0.35
    wpm: list[float] = field(default_factory=lambda: [130, 190])
    delivery_wpm: list[float] = field(default_factory=lambda: [155, 185])
    sentence_pause: list[float] = field(default_factory=lambda: [0.35, 0.9])
    lufs: float = -14.0
    lufs_tolerance: float = 1.0
    true_peak_max: float = -1.5
    black_max: float = 1.0
    freeze_max: float = 3.0
    visual_opening_motion_margin: float = visual_quality.DEFAULT_OPENING_MOTION_MARGIN
    visual_min_density: float = visual_quality.DEFAULT_MIN_DENSITY
    visual_min_median_density: float = visual_quality.DEFAULT_MIN_MEDIAN_DENSITY
    visual_min_height: float = visual_quality.DEFAULT_MIN_HEIGHT
    visual_min_median_height: float = visual_quality.DEFAULT_MIN_MEDIAN_HEIGHT
    visual_strip_min_width: float = visual_quality.DEFAULT_STRIP_MIN_WIDTH
    visual_max_low_density_beats: int = visual_quality.DEFAULT_MAX_LOW_DENSITY_BEATS
    visual_max_horizontal_strip_beats: int = visual_quality.DEFAULT_MAX_HORIZONTAL_STRIP_BEATS
    sfx_min_cues: int = 9
    sfx_min_density: float = 1.5
    sfx_audible_mean_min: float = -18.0
    sfx_audible_peak_min: float = -12.0
    sfx_min_audible_cues: int = 4
    sfx_min_audible_share: float = 0.35
    sfx_masking_mean_max: float = -3.5
    sfx_max_simultaneous: int = 2


class Cue(NamedTuple):
    start: float
    end: float
    text: str


# --- reading the export ----------------------------------------------------------------

def seconds_of(stamp: str) -> float:
    h, m, s, frac = _STAMP.search(stamp).groups()
    return int(h) * 3600 + int(m) * 60 + int(s) + int(frac) / 10 ** len(frac)


def parse_srt(text: str) -> list[Cue]:
    cues = []
    for block in re.split(r"\n\s*\n", text.strip()):
        lines = block.strip().splitlines()
        for i, line in enumerate(lines):
            if "-->" in line:
                start, end = line.split("-->")
                cues.append(Cue(seconds_of(start), seconds_of(end), " ".join(x.strip() for x in lines[i + 1:])))
                break
    return cues


def tokens(text: str) -> list[str]:
    return [w.casefold() for w in WORD.findall(text)]


def beat_times(script: Script, cues: list[Cue]) -> tuple[dict[str, tuple[float, float]], list[str]]:
    """Start and end of every beat's narration, found by matching caption cues to the VO."""
    times: dict[str, tuple[float, float]] = {}
    i = 0
    for beat in (b for b in script.beats.values() if b.vo):
        want, got, start, end = tokens(beat.vo), [], None, 0.0
        while i < len(cues) and len(got) < len(want):
            cue = cues[i]
            i += 1
            start = cue.start if start is None else start
            end = cue.end
            got += tokens(cue.text)
        if got != want:
            said = " ".join(got[:10]) or "nothing"
            return times, [f"{beat.id}: the captions say '{said} ...', the VO says '{' '.join(want[:10])} ...'"]
        times[beat.id] = (start, end)
    if i < len(cues):
        return times, [f"{len(cues) - i} caption cue(s) after the last beat"]
    return times, []


def probe(video: Path) -> dict:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(video)],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def scan(video: Path) -> str:
    """One decoding pass: near-black stretches, frozen pictures and EBU R128 loudness."""
    proc = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-i", str(video),
         "-vf", "blackdetect=d=0.25:pix_th=0.10,freezedetect=n=-60dB:d=1",
         "-af", "ebur128=peak=true", "-f", "null", "-"],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    if proc.returncode:
        raise RuntimeError(proc.stderr[-600:])
    return proc.stderr


def _number(m: re.Match | None) -> float | None:
    if not m:
        return None
    return float("-inf") if m.group(1) == "-inf" else float(m.group(1))


def parse_scan(log: str, duration: float) -> dict:
    blacks = [float(x) for x in re.findall(r"black_duration:\s*([\d.]+)", log)]
    starts = [float(x) for x in re.findall(r"freeze_start:\s*([\d.]+)", log)]
    ends = [float(x) for x in re.findall(r"freeze_end:\s*([\d.]+)", log)]
    freezes = [e - s for s, e in zip(starts, ends)]
    if len(starts) > len(ends):
        freezes.append(duration - starts[-1])
    summary = log[log.rfind("Summary:"):] if "Summary:" in log else ""
    return {
        "black_max_s": round(max(blacks, default=0.0), 3),
        "freeze_max_s": round(max(freezes, default=0.0), 3),
        "lufs": _number(re.search(r"I:\s*(-?[\d.]+|-inf)\s*LUFS", summary)),
        "true_peak_db": _number(re.search(r"True peak:\s*Peak:\s*(-?[\d.]+|-inf)\s*dBFS", summary, re.S)),
    }


STAGE_SHARE = 0.68  # the top 68% of the frame: everything above the caption band


def gray_frame(video: Path, t: float, size: tuple[int, int] = (108, 131)) -> bytes:
    """A small grayscale copy of the stage (captions cropped off) at time t."""
    w, h = size
    return subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", str(video), "-frames:v", "1",
                           "-vf", f"crop=iw:ih*{STAGE_SHARE}:0:0,scale={w}:{h},format=gray",
                           "-f", "rawvideo", "-"],
                          capture_output=True, check=True).stdout


def contrast(frame: bytes) -> float:
    return statistics.pstdev(frame) if frame else 0.0


def motion(a: bytes, b: bytes) -> float:
    n = min(len(a), len(b))
    return sum(abs(x - y) for x, y in zip(a[:n], b[:n])) / n if n else 0.0


def voice_files(ep: Path) -> dict[str, Path]:
    """The narration WAV for each VO line, in the frozen series voice, from the render cache."""
    folder = MEDIA / ep.name / "voiceovers"
    cache = folder / "cache.json"
    if not cache.exists():
        return {}
    voice = tomllib.loads((ROOT / "voice.toml").read_text(encoding="utf-8"))
    want = {"voice": voice["speaker"], "speed": voice["speed"],
            "sentence_pause": voice["sentence_pause"], "clause_pause": voice["clause_pause"]}
    found = {}
    for entry in json.loads(cache.read_text(encoding="utf-8")):
        data = entry.get("input_data", {})
        config = data.get("config", {})
        path = folder / entry.get("final_audio", "")
        if all(config.get(k) == v for k, v in want.items()) and path.is_file():
            found[data.get("input_text", "")] = path
    return found


def media_seconds(path: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True, check=True).stdout
    return float(out.strip())


def silences(wav: Path) -> tuple[list[tuple[float, float]], float]:
    log = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(wav),
                          "-af", "silencedetect=noise=-40dB:d=0.12", "-f", "null", "-"],
                         capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    starts = [float(x) for x in re.findall(r"silence_start:\s*(-?[\d.]+)", log)]
    ends = [float(x) for x in re.findall(r"silence_end:\s*([\d.]+)", log)]
    m = re.search(r"Duration:\s*(\d+:\d+:\d+\.\d+)", log)
    return list(zip(starts, ends)), seconds_of(m.group(1)) if m else 0.0


def sentence_pauses(script: Script, files: dict[str, Path]) -> list[float]:
    """Silences at sentence boundaries: the longest inner silences of each multi-sentence beat."""
    pauses: list[float] = []
    for beat in script.beats.values():
        n = len(sentences(beat.vo)) if beat.vo else 0
        if n < 2 or beat.vo not in files:
            continue
        spans, duration = silences(files[beat.vo])
        inner = sorted((e - s for s, e in spans if s > 0.05 and e < duration - 0.05), reverse=True)
        pauses += inner[:n - 1]
    return pauses


# --- the checks ------------------------------------------------------------------------

def measure(ep: Path, video: Path) -> tuple[dict, list[str]]:
    script = load_script(ep / "script.md")
    info = probe(video)
    v = next((s for s in info["streams"] if s.get("codec_type") == "video"), {})
    a = next((s for s in info["streams"] if s.get("codec_type") == "audio"), {})
    num, _, den = v.get("r_frame_rate", "0/1").partition("/")
    duration = float(info["format"]["duration"])
    srt = video.with_suffix(".srt")
    cues = parse_srt(srt.read_text(encoding="utf-8")) if srt.exists() else []
    times, problems = beat_times(script, cues) if cues else ({}, [f"no captions file {srt.name}"])
    spoken = [b for b in script.beats.values() if b.vo and b.id in times]
    files = voice_files(ep)
    if spoken and all(b.vo in files for b in spoken):  # exact: the narration audio itself
        talk, talk_source = sum(media_seconds(files[b.vo]) for b in spoken), "voice audio"
    else:  # close: caption cues end a little before the audio does
        talk, talk_source = sum(times[b.id][1] - times[b.id][0] for b in spoken), "captions"
    pauses = sentence_pauses(script, files)
    delivery = visual_quality.delivery_note_audit({
        beat.id: beat.note for beat in script.beats.values() if beat.vo
    })
    f0, f1 = gray_frame(video, 0.0), gray_frame(video, 0.5)
    mechanism = load_section(design.Limits, "check").mechanism_beat
    beat_spans = {k: [round(t0, 3), round(t1, 3)] for k, (t0, t1) in times.items()}
    visuals = visual_quality.measure_video(video, beat_spans)
    sfx = sfxqa.measure(
        ep,
        duration,
        list(times.values()),
        [files[b.vo] for b in spoken if b.vo in files],
        expected_voice_files=len(spoken),
    )
    metrics = {
        "width": v.get("width"), "height": v.get("height"),
        "fps": round(float(num) / float(den or 1), 3) if num else None,
        "video_codec": v.get("codec_name"), "audio_codec": a.get("codec_name"),
        "sample_rate": int(a.get("sample_rate", 0)) or None,
        "duration_s": round(duration, 3),
        "narration_start_s": round(cues[0].start, 3) if cues else None,
        "first_frame_contrast": round(contrast(f0), 2),
        "first_frame_motion": round(motion(f0, f1), 3),
        "hook_end_s": round(times["B1"][1], 3) if "B1" in times else None,
        "mechanism_beat": mechanism,
        "answer_start_s": round(times[mechanism][0], 3) if mechanism in times else None,
        "answer_share": round(times[mechanism][0] / duration, 3) if mechanism in times else None,
        "words": sum(len(tokens(b.vo)) for b in spoken),
        "wpm": round(sum(len(tokens(b.vo)) for b in spoken) / talk * 60, 1) if talk else None,
        "talk_s": round(talk, 3),
        "talk_source": talk_source,
        "sentence_pause_s": round(statistics.median(pauses), 3) if pauses else None,
        "sentence_pauses_measured": len(pauses),
        "delivery_note_audit": delivery,
        "beats": beat_spans,
        **parse_scan(scan(video), duration),
        **visuals,
        **sfx,
    }
    return metrics, problems


def narration_pace(ep: Path) -> tuple[int, float, float] | None:
    """Words, narration seconds and words per minute, measured as `measure` does from the
    cached series voice; None until a render has voiced every beat. `vid preview` prints it,
    so a slow or rushed script shows up before the animation work, not at the final."""
    spoken = [b for b in load_script(ep / "script.md").beats.values() if b.vo]
    files = voice_files(ep)
    if not spoken or not all(b.vo in files for b in spoken):
        return None
    words = sum(len(tokens(b.vo)) for b in spoken)
    talk = sum(media_seconds(files[b.vo]) for b in spoken)
    return words, round(talk, 3), round(words / talk * 60, 1) if talk else 0.0


def picture_results(m: dict, lim: Limits) -> list[Result]:
    """The rendered-picture rules: opening-quality, stage-coverage and layout-variety.

    `vid frames` runs these on a preview too, with the same limits, so composition problems
    surface while animating instead of after the final render.
    """
    if "opening_motion_min" not in m:
        return [Result("opening-quality", "skip", "no quarter-second opening samples"),
                Result("stage-coverage", "skip", "no rendered beat profiles"),
                Result("layout-variety", "skip", "no rendered beat profiles")]
    visual_issues = visual_quality.judge_rendered(
        m,
        existing_opening_motion_floor=lim.first_frame_min_motion,
        opening_motion_margin=lim.visual_opening_motion_margin,
        min_density=lim.visual_min_density,
        min_median_density=lim.visual_min_median_density,
        min_height=lim.visual_min_height,
        min_median_height=lim.visual_min_median_height,
        strip_min_width=lim.visual_strip_min_width,
        max_low_density_beats=lim.visual_max_low_density_beats,
        max_horizontal_strip_beats=lim.visual_max_horizontal_strip_beats,
    )
    out = [result(
        "opening-quality", visual_issues["opening-quality"],
        f"weakest/mean opening quarter-second motion {m['opening_motion_min']:.3f}/"
        f"{m['opening_motion_mean']:.3f} gray levels",
    )]
    profiles = m.get("beat_visuals", {})
    if not profiles:
        return out + [Result("stage-coverage", "skip", "needs caption-timed beat profiles"),
                      Result("layout-variety", "skip", "needs caption-timed beat profiles")]
    sparse = sum(
        float(profile.get("foreground_share", 0.0)) < lim.visual_min_density
        for profile in profiles.values()
    )
    strips = sum(
        float(profile.get("width_share", 0.0)) >= lim.visual_strip_min_width
        and float(profile.get("height_share", 0.0)) < lim.visual_min_height
        for profile in profiles.values()
    )
    out.append(result(
        "stage-coverage", visual_issues["stage-coverage"],
        f"median foreground {m['visual_density_median']:.1%}; {sparse}/{len(profiles)} sparse beats",
    ))
    out.append(result(
        "layout-variety", visual_issues["layout-variety"],
        f"median stage height {m['stage_height_median']:.0%}; {strips}/{len(profiles)} wide strips",
    ))
    return out


def judge(m: dict, problems: list[str], lim: Limits) -> list[Result]:
    timed = not problems
    out = []

    issues = []
    if (m["width"], m["height"]) != (1080, 1920):
        issues.append(f"{m['width']}x{m['height']}, not 1080x1920")
    if m["fps"] != 60:
        issues.append(f"{m['fps']} fps, not 60")
    if m["video_codec"] != "h264" or m["audio_codec"] != "aac":
        issues.append(f"{m['video_codec']}/{m['audio_codec']}, not h264/aac")
    if m["sample_rate"] != 48000:
        issues.append(f"audio at {m['sample_rate']} Hz, not 48000")
    out.append(result("format", issues, f"{m['width']}x{m['height']}, {m['fps']} fps, "
                                        f"{m['video_codec']}/{m['audio_codec']} {m['sample_rate']} Hz"))

    lo, hi = lim.seconds
    d = m["duration_s"]
    out.append(result("length", [] if lo <= d <= hi else [f"{d:.1f} s is outside {lo}-{hi} s"],
                      f"{d:.1f} s (target {lo}-{hi} s)"))

    issues = []
    if m["narration_start_s"] is None or m["narration_start_s"] > lim.narration_start_max:
        issues.append(f"the first word comes at {m['narration_start_s']} s (max {lim.narration_start_max} s)")
    if m["first_frame_contrast"] < lim.first_frame_min_contrast:
        issues.append(f"frame 0 is nearly blank (contrast {m['first_frame_contrast']}): open on the cover")
    if m["first_frame_motion"] < lim.first_frame_min_motion:
        issues.append(f"frames 0 s and 0.5 s are the same (change {m['first_frame_motion']}): open in motion")
    out.append(result("cold-open", issues, f"first word at {m['narration_start_s']} s; frame-0 contrast "
                                           f"{m['first_frame_contrast']}, change by 0.5 s {m['first_frame_motion']}"))

    if not timed:
        for rule in ("hook-time", "early-answer", "speech-rate", "delivery-pace"):
            out.append(Result(rule, "skip", "needs captions that match the VO (see captions)"))
    else:
        h = m["hook_end_s"]
        out.append(result("hook-time", [] if h is not None and h <= lim.hook_end_max
                          else [f"B1 ends at {h} s (max {lim.hook_end_max} s)"],
                          f"B1 ends at {h:.1f} s (max {lim.hook_end_max} s)" if h is not None else "no B1"))
        share = m["answer_share"]
        out.append(result("early-answer", [] if share is not None and share <= lim.answer_by
                          else [f"{m['mechanism_beat']} starts at {share:.0%} of the video (max {lim.answer_by:.0%})"
                                if share is not None else f"no {m['mechanism_beat']} beat"],
                          f"{m['mechanism_beat']} starts at {m['answer_start_s']} s = {share:.0%} "
                          f"(max {lim.answer_by:.0%})" if share is not None else "no mechanism beat"))
        lo, hi = lim.wpm
        w = m["wpm"]
        out.append(result("speech-rate", [] if w is not None and lo <= w <= hi
                          else [f"{w} words/min is outside {lo:g}-{hi:g}"],
                          f"{w} words/min over {m['words']} words, timed from the "
                          f"{m.get('talk_source', 'captions')} (range {lo:g}-{hi:g})"))
        lo, hi = lim.delivery_wpm
        out.append(result(
            "delivery-pace",
            [] if w is not None and lo <= w <= hi else [
                f"{w} words/min is outside the {lo:g}-{hi:g} house delivery band; "
                "review the sound-only listen before changing approved VO or the frozen voice"
            ],
            f"{w} words/min (house reference range {lo:g}-{hi:g}; human sound-only review still required)",
        ))

    p = m["sentence_pause_s"]
    if p is None:
        out.append(Result("pauses", "skip", "no cached series-voice audio for multi-sentence beats"))
    else:
        lo, hi = lim.sentence_pause
        out.append(result("pauses", [] if lo <= p <= hi else [f"median sentence pause {p} s is outside {lo}-{hi} s"],
                          f"median sentence pause {p} s over {m['sentence_pauses_measured']} boundaries "
                          f"(range {lo}-{hi} s)"))

    out.append(result("captions", problems, f"{len(m['beats'])} beats, word for word"))

    issues = []
    lufs, peak = m["lufs"], m["true_peak_db"]
    if lufs is None or abs(lufs - lim.lufs) > lim.lufs_tolerance:
        issues.append(f"{lufs} LUFS (target {lim.lufs} ± {lim.lufs_tolerance})")
    if peak is None or peak > lim.true_peak_max:
        issues.append(f"true peak {peak} dBTP (max {lim.true_peak_max})")
    out.append(result("loudness", issues, f"{lufs} LUFS, true peak {peak} dBTP"))

    out.extend(picture_results(m, lim))
    out.extend(sfxqa.judge(m, lim))

    issues = []
    if m["black_max_s"] >= lim.black_max:
        issues.append(f"a near-black stretch of {m['black_max_s']} s (max {lim.black_max} s)")
    if m["freeze_max_s"] >= lim.freeze_max:
        issues.append(f"a frozen picture of {m['freeze_max_s']} s (max {lim.freeze_max} s)")
    out.append(result("dead-air", issues, f"longest near-black {m['black_max_s']} s, longest freeze "
                                          f"{m['freeze_max_s']} s"))
    return out


def run(ep: Path, video: Path | None = None) -> bool:
    video = video or EXPORTS / f"{ep.name}.mp4"
    if not video.exists():
        print(f"Export QA: no {video.name} yet. Make it with: vid final {ep.name[:3]}")
        return False
    lim = load_section(Limits, "qa")
    metrics, problems = measure(ep, video)
    results = judge(metrics, problems, lim)
    passed = show(f"Export QA: {video.name}", results)
    report = {
        "episode": ep.name,
        "video": video.name,
        "checked": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "pipeline_fingerprint": qa_contract.pipeline_fingerprint(),
        "passed": passed,
        "metrics": metrics,
        "results": [asdict(r) for r in results],
    }
    out = video.with_suffix(".qa.json")
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Measurements: {out.name}")
    return passed


if __name__ == "__main__":
    if len(sys.argv) not in (2, 3):
        sys.exit(__doc__)
    sys.exit(0 if run(Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve() if len(sys.argv) == 3 else None) else 1)
