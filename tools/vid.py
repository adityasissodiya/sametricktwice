"""vid: the episode pipeline. Run it through vid (vid.cmd on Windows), which keeps every tool and cache in this folder.

  vid status [<ep>]      where an episode stands and the one thing to do next (start here)
  vid new <slug>         start an episode from the templates (e.g. 004-film-x-explosives)
  vid check <ep>         STE score (target 80%) + research-backed design rules (design.toml)
  vid lint <ep>          carry-over check: nothing from an earlier episode except series.toml
  vid scene <ep>         write scene.py with one placeholder per beat (= the animatic)
  vid preview <ep>       fast 540x960 render that opens when done; prints the narration pace
        --voice V          default: the frozen series voice in voice.toml (Kokoro af_heart);
                           or kokoro:<speaker> | gtts | recorder | gemini | openai
        --guides           overlay the Shorts UI safe zone
        --no-open          do not open the video when done
  vid align <ep>         guide render + iterative symmetry/alignment report
        --voice V          as above
        --no-open          do not open the guide video
  vid audition <ep>      the same lines in several Kokoro voices -> media/<ep>/voice-auditions/
        --beats B1,B2      which beats to read (default: B1,B2)
        --voices a,b       which Kokoro speakers (default: the best-graded seven)
  vid final <ep>         check + lint + alignment gates, 1080x1920 60 fps, -14 LUFS -> exports/,
                         then vid qa on the new export
        --voice V          as above (leave it out to use the series voice)
        --music FILE       music bed under the voice (default: music.* in the episode folder)
        --force            render even if the check or carry-over gate fails
  vid qa <ep>            measure the export: length, hook, pace, pauses, captions, loudness...
        --video FILE       measure another file (default: exports/<ep>.mp4)
  vid frames <ep>        contact sheets of every beat at phone size, for reading the video,
                         then vid qa's picture rules measured on the same render
        --render           use the newest Manim render (a preview) instead of the export
        --video FILE       use this file (its .srt must sit next to it)
        --at S [S ...]     instead, one frame per given second -> media/<ep>/frames/moments.png
  vid report             channel results (analytics/results.csv) next to each episode's measurements
  vid test               run the unit tests
  vid ci                 check + lint for every scripted episode
  vid doctor             tool versions, where every cache lives, free disk space
  vid setup              a new machine in one go: pinned portable tools, Python 3.12, packages,
                         the narrator model, then doctor and the tests (safe to run again)
  vid uv <args>          run uv with this project's cache settings

<ep> is the episode folder name or its number, e.g. 001.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import textwrap
from importlib.metadata import version
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import design, lint, qa, report, status, ste  # noqa: E402
from tools.scriptfile import load_script  # noqa: E402

EPISODES = ROOT / "episodes"
TEMPLATES = ROOT / "templates"
MEDIA = ROOT / "media"
EXPORTS = ROOT / "exports"
VOICE_POLISH = (
    "highpass=f=85,"
    "equalizer=f=1800:t=q:w=1.2:g=1.5,"
    "acompressor=threshold=0.12:ratio=2.2:attack=8:release=90:makeup=1.25"
)
LOUDNORM = "loudnorm=I=-14:TP=-3.0:LRA=11"  # headroom: AAC encoding can push sharp clicks ~1 dB past the target; the limit is -1.5


def episode(name: str) -> Path:
    if (EPISODES / name).is_dir():
        return EPISODES / name
    hits = sorted(p for p in EPISODES.glob(f"{name}*") if p.is_dir())
    if len(hits) != 1:
        sys.exit(f"No single episode matches {name!r}. Found: {', '.join(p.name for p in hits) or 'none'}")
    return hits[0]


def cmd_new(args) -> int:
    if not re.fullmatch(r"\d{3}-[a-z0-9-]+", args.slug):
        sys.exit("Name it like 004-film-x-explosives: three digits, then lowercase words.")
    dest = EPISODES / args.slug
    if dest.exists():
        sys.exit(f"{dest.relative_to(ROOT)} already exists.")
    dest.mkdir(parents=True)
    for template in sorted(TEMPLATES.glob("*.md")):
        text = template.read_text(encoding="utf-8").replace("{slug}", args.slug)
        (dest / template.name).write_text(text, encoding="utf-8")
    print(f"Created {dest.relative_to(ROOT)}. Next: fill brief.md (WORKFLOW.md step 2); "
          f"`vid status {args.slug[:3]}` tracks every step.")
    return 0


def cmd_status(args) -> int:
    status.run(episode(args.ep) if args.ep else None)
    return 0


def cmd_check(args) -> int:
    ep = episode(args.ep)
    ok = ste.run(ep / "script.md")
    print()
    return 0 if design.run(ep) and ok else 1


def cmd_qa(args) -> int:
    return 0 if qa.run(episode(args.ep), Path(args.video).resolve() if args.video else None) else 1


def cmd_frames(args) -> int:
    from tools import frames

    ep = episode(args.ep)
    video = Path(args.video).resolve() if args.video else None
    if args.render:
        renders = sorted((MEDIA / ep.name / "videos").rglob("Episode.mp4"), key=lambda p: p.stat().st_mtime)
        if not renders:
            sys.exit(f"No render yet. Make one with: vid preview {ep.name[:3]} --no-open")
        video = renders[-1]
    return 0 if frames.run(ep, video, at=args.at) else 1


def cmd_report(args) -> int:
    return 0 if report.run() else 1


def cmd_test(args) -> int:
    return subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-t", "."], cwd=ROOT).returncode


def cmd_ci(args) -> int:
    from tools import ci

    return ci.main()


def cmd_lint(args) -> int:
    return 0 if lint.run(episode(args.ep)) else 1


SCENE_HEAD = '''"""{name}: series house-style infographic visuals.

The approved words live only in script.md; animation work must not rewrite them. Every beat
starts as an animatic placeholder, but no placeholder or VIS note may survive into a final.
Write every label, header and diagram for this episode; never paste from another episode's
scene. Use self.sfx("name.wav") for kit/sfx sounds and run `vid lint {num}`.
Read AGENTS.md and STYLE_GUIDE.md. For each layout keyframe, register centered/mirror/row/
column/safe-area constraints with ``self.alignment_loop(...)`` before ``self.play``. Refine
with ``vid align {num}``, then check the phone-safe preview with ``vid preview {num} --guides``.

What `vid check` asks of this file (WORKFLOW.md, step 5, has the details):
- Time every self.play as a share of its beat, e.g. run_time=0.2 * b.duration. Plan motion
  for at least 65% of each beat, keep the shares under 1.0, then self.hold(b).
- Build the trick once, as a method that takes a skin and one run_time and splits it with a
  tuple of phase shares. In B3 set self.trick_time = min(CAP, share * b.duration) once, with
  CAP (seconds) short enough for the shorter of B3 and B6, and pass that same value in B6.
- Show cause becoming effect (Transform, MoveAlongPath, GrowArrow, .animate.shift ...) in at
  least 7 of B1-B8, always in B3 and B6.
After each preview, `vid frames {num} --render` prints the picture rules that vid qa applies.
"""

from kit import *


class Episode(ShortScene):
    def construct(self):
'''


def cmd_scene(args) -> int:
    ep = episode(args.ep)
    target = ep / "scene.py"
    if target.exists() and not args.force:
        sys.exit(f"{target.relative_to(ROOT)} exists. Use --force to overwrite it.")
    beats = [b for b in load_script(ep / "script.md").beats.values() if b.vo]
    if not beats:
        sys.exit("script.md has no beats with a VO line yet.")
    lines = [SCENE_HEAD.format(name=ep.name, num=ep.name[:3]).rstrip("\n")]
    for beat in beats:
        lines.append(f'        with self.beat("{beat.id}") as b:  # {beat.label}')
        for row in textwrap.wrap(f"VIS: {beat.vis}", 84):
            lines.append(f"            # {row}")
        lines.append("            self.end_card()" if beat is beats[-1] else "            self.placeholder(b)")
        lines.append("")
    lines.append("        self.wait(1)\n")
    target.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {target.relative_to(ROOT)} with {len(beats)} beats. Watch the animatic: vid preview {ep.name[:3]}")
    return 0


def render(ep: Path, width: int, height: int, fps: int, voice: str, guides: bool,
           open_after: bool, align_mode: str = "warn", align_guides: bool = False) -> Path:
    if not (ep / "scene.py").exists():
        sys.exit(f"No scene.py yet. Make one with: vid scene {ep.name[:3]}")
    media = MEDIA / ep.name
    cmd = [sys.executable, "-m", "manim", "render", str(ep / "scene.py"), "Episode",
           "-r", f"{width},{height}", "--fps", str(fps), "--media_dir", str(media)]
    if open_after:
        cmd.append("-p")
    alignment_report = MEDIA / ep.name / "alignment-report.json"
    alignment_report.unlink(missing_ok=True)
    env = dict(
        os.environ,
        VID_GUIDES="1" if guides else "0",
        VID_ALIGN=align_mode,
        VID_ALIGN_GUIDES="1" if align_guides else "0",
        VID_ALIGN_REPORT=str(alignment_report),
    )
    env.pop("VID_VOICE", None)  # no --voice: the scene uses the frozen series voice (voice.toml)
    if voice:
        env["VID_VOICE"] = voice
    if subprocess.run(cmd, env=env, cwd=ROOT).returncode:
        sys.exit("Render failed. See the Manim output above.")
    videos = sorted((media / "videos").rglob("Episode.mp4"), key=lambda p: p.stat().st_mtime)
    return videos[-1]


def cmd_preview(args) -> int:
    ep = episode(args.ep)
    video = render(ep, 540, 960, 30, args.voice, args.guides, open_after=not args.no_open)
    print(f"\nPreview: {video.relative_to(ROOT)}")
    pace = None if args.voice else qa.narration_pace(ep)
    if pace:
        words, talk, wpm = pace
        lo, hi = design.load_section(qa.Limits, "qa").delivery_wpm
        verdict = "inside" if lo <= wpm <= hi else "OUTSIDE"
        print(f"Narration pace: {wpm} words/min ({words} words in {talk:.1f} s); {verdict} vid qa's "
              f"delivery-pace band of {lo:g}-{hi:g}.")
        if verdict == "OUTSIDE":
            print("  Fix the words now, with the creator's approval, before animating (WORKFLOW.md, step 2).")
    return 0


def cmd_align(args) -> int:
    ep = episode(args.ep)
    video = render(ep, 540, 960, 30, args.voice, guides=True,
                   open_after=not args.no_open, align_mode="warn", align_guides=True)
    report_path = MEDIA / ep.name / "alignment-report.json"
    if not report_path.exists():
        print("\nAlignment failed: no report was produced.")
        return 1
    report = json.loads(report_path.read_text(encoding="utf-8"))
    print(f"\nAlignment: {report_path.relative_to(ROOT)}")
    for item in report.get("reports", []):
        status = "PASS" if item.get("passed") else "FAIL"
        print(f"  {status:<4} {item.get('label')} ({item.get('passes', 0)} refinement pass(es))")
        for issue in item.get("issues", [])[:5]:
            print(f"       {issue.get('constraint')}.{issue.get('metric')}: {issue.get('error')}u")
    if report.get("missing_checks"):
        print("  FAIL no alignment loops were registered")
    print(f"Guide render: {video.relative_to(ROOT)}")
    return 0 if report.get("passed") else 1


def cmd_audition(args) -> int:
    from kit.voices import AUDITION_VOICES, KokoroVoice, write_wav
    from tools.scriptfile import WORD

    ep = episode(args.ep)
    beats = load_script(ep / "script.md").beats
    ids = [b.strip().upper() for b in args.beats.split(",")]
    missing = [b for b in ids if b not in beats or not beats[b].vo]
    if missing:
        sys.exit(f"No VO line for {', '.join(missing)} in {ep.name}/script.md")
    text = " ".join(beats[b].vo for b in ids)
    voices = [v.strip() for v in args.voices.split(",")] if args.voices else list(AUDITION_VOICES)
    out = MEDIA / ep.name / "voice-auditions"
    kokoro = KokoroVoice(voice=voices[0], cache_dir=str(out))
    print(f"Text:     {text}\nPhonemes: {kokoro.phonemes(text)}\n")
    words = len(WORD.findall(text))
    for voice in voices:
        if voice not in kokoro.engine().get_voices():
            print(f"  skip {voice}: not a Kokoro voice")
            continue
        kokoro.voice = voice
        samples, rate = kokoro.synthesize(text)
        write_wav(out / f"{voice}.wav", samples, rate)
        seconds = len(samples) / rate
        print(f"  {voice:<11} {seconds:5.1f} s  {words / seconds * 60:4.0f} words/min")
    print(f"\nListen: {out.relative_to(ROOT)}  (the series voice is frozen in voice.toml; "
          f"try another with: vid preview {ep.name[:3]} --voice kokoro:<voice>)")
    return 0


def cmd_final(args) -> int:
    ep = episode(args.ep)
    if not ste.run(ep / "script.md") and not args.force:
        sys.exit("\nThe narration is below the STE target. Fix script.md, or add --force.")
    print()
    if not design.run(ep, final=True) and not args.force:
        sys.exit("\nA design rule fails (see RESEARCH.md for why it matters). Fix it, or add --force.")
    print()
    if not lint.run(ep) and not args.force:
        sys.exit("\nThis episode carries material over from an earlier one. Fix it, or add --force.")
    video = render(ep, 1080, 1920, 60, args.voice, guides=False, open_after=False,
                   align_mode="strict", align_guides=False)
    music = Path(args.music) if args.music else next(iter(sorted(ep.glob("music.*"))), None)
    EXPORTS.mkdir(exist_ok=True)
    out = EXPORTS / f"{ep.name}.mp4"
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(video)]
    if music:
        cmd += ["-stream_loop", "-1", "-i", str(music), "-filter_complex",
                f"[0:a]{VOICE_POLISH}[v];[1:a]volume={args.music_gain}[m];"
                f"[v][m]amix=inputs=2:duration=first:normalize=0,{LOUDNORM}[a]",
                "-map", "0:v", "-map", "[a]"]
    else:
        cmd += ["-af", f"{VOICE_POLISH},{LOUDNORM}"]
    # loudnorm works at 192 kHz internally; resample to the 48 kHz YouTube expects.
    cmd += ["-c:v", "copy", "-c:a", "aac", "-ar", "48000", "-b:a", "192k", "-movflags", "+faststart", str(out)]
    subprocess.run(cmd, check=True)
    srt = video.with_suffix(".srt")
    if srt.exists():
        shutil.copy(srt, out.with_suffix(".srt"))
    print(f"\nExported: {out.relative_to(ROOT)}" + (" (+ .srt to upload as captions)" if srt.exists() else ""))
    print()
    if not qa.run(ep, out):
        print(f"\nThe export fails QA. Fix the cause, then run vid final {ep.name[:3]} again.")
        return 1
    print(f"\nDone. Next: vid frames {ep.name[:3]}, read every sheet, then fill publish.md.")
    return 0


def folder_gb(path: Path) -> float:
    total = 0
    for dirpath, _, files in os.walk(path):
        for f in files:
            try:
                total += os.path.getsize(os.path.join(dirpath, f))
            except OSError:
                pass
    return total / 1e9


def cmd_doctor(args) -> int:
    print(f"Project    {ROOT}")
    print(f"Python     {platform.python_version()}  {sys.executable}")
    for pkg in ("manim", "manim-voiceover", "spacy", "wordfreq"):
        print(f"{pkg:<10} {version(pkg)}")
    for tool in ("uv", "ffmpeg", "ffprobe"):
        print(f"{tool:<10} {shutil.which(tool) or 'NOT FOUND'}")
    print("\nCaches and temp files (all should be under the project):")
    for var in ("UV_CACHE_DIR", "XDG_CACHE_HOME", "HF_HOME", "TORCH_HOME", "PIP_CACHE_DIR", "TEMP"):
        value = os.environ.get(var, "")
        inside = value and Path(value).resolve().is_relative_to(ROOT)
        print(f"  {var:<15} {'ok ' if inside else 'OFF'} {value or '(not set: run through vid)'}")
    print("\nProject folder sizes:")
    for name in (".venv", ".cache", ".tools", "media", "exports"):
        if (ROOT / name).exists():
            print(f"  {name:<8} {folder_gb(ROOT / name):6.2f} GB")
    print("\nFree space:")
    system = "C:\\" if os.name == "nt" else "/"
    for drive in sorted({ROOT.anchor, system}):  # this folder's drive and the system drive
        if Path(drive).exists():
            print(f"  {drive}  {shutil.disk_usage(drive).free / 1e9:6.1f} GB")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="vid", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd")
    p = sub.add_parser("status")
    p.add_argument("ep", nargs="?")
    p.set_defaults(fn=cmd_status)
    p = sub.add_parser("new")
    p.add_argument("slug")
    p.set_defaults(fn=cmd_new)
    p = sub.add_parser("check")
    p.add_argument("ep")
    p.set_defaults(fn=cmd_check)
    p = sub.add_parser("lint")
    p.add_argument("ep")
    p.set_defaults(fn=cmd_lint)
    p = sub.add_parser("scene")
    p.add_argument("ep")
    p.add_argument("--force", action="store_true")
    p.set_defaults(fn=cmd_scene)
    p = sub.add_parser("preview")
    p.add_argument("ep")
    p.add_argument("--voice")
    p.add_argument("--guides", action="store_true")
    p.add_argument("--no-open", action="store_true")
    p.set_defaults(fn=cmd_preview)
    p = sub.add_parser("align")
    p.add_argument("ep")
    p.add_argument("--voice")
    p.add_argument("--no-open", action="store_true")
    p.set_defaults(fn=cmd_align)
    p = sub.add_parser("audition")
    p.add_argument("ep")
    p.add_argument("--beats", default="B1,B2")
    p.add_argument("--voices")
    p.set_defaults(fn=cmd_audition)
    p = sub.add_parser("final")
    p.add_argument("ep")
    p.add_argument("--voice")
    p.add_argument("--music")
    p.add_argument("--music-gain", type=float, default=0.12)
    p.add_argument("--force", action="store_true")
    p.set_defaults(fn=cmd_final)
    p = sub.add_parser("qa")
    p.add_argument("ep")
    p.add_argument("--video")
    p.set_defaults(fn=cmd_qa)
    p = sub.add_parser("frames")
    p.add_argument("ep")
    p.add_argument("--video")
    p.add_argument("--render", action="store_true")
    p.add_argument("--at", nargs="+", type=float, metavar="SECONDS")
    p.set_defaults(fn=cmd_frames)
    sub.add_parser("report").set_defaults(fn=cmd_report)
    sub.add_parser("test").set_defaults(fn=cmd_test)
    sub.add_parser("ci").set_defaults(fn=cmd_ci)
    sub.add_parser("doctor").set_defaults(fn=cmd_doctor)
    args = parser.parse_args()
    if not args.cmd:
        print(__doc__)
        return 0
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
