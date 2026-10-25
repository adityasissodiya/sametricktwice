"""Contact sheets: the start, middle and end frame of every beat, at phone size.

An agent cannot watch a video, but it can read images. `vid frames <ep>` cuts frames from
the export at 25% of the master size (the size at which STYLE_GUIDE.md asks every label to
stay legible) and tiles them three beats per sheet:

    media/<ep>/frames/sheet-1.png   B1-B3
    media/<ep>/frames/sheet-2.png   B4-B6 ...
    media/<ep>/frames/cover.png     B1's middle frame at full size: a cover candidate

It then measures the same render with `vid qa`'s picture rules (opening-quality,
stage-coverage, layout-variety), so a preview shows composition problems before the final.
With --at it grabs frames at chosen seconds instead, for the moments the grid misses:

    media/<ep>/frames/moments.png   one frame per requested second, four to a row

Usage: vid frames <ep> [--video FILE | --render] [--at SECONDS ...]
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import visual_quality  # noqa: E402
from tools.design import load_section, show  # noqa: E402
from tools.qa import EXPORTS, MEDIA, Limits, beat_times, parse_srt, picture_results  # noqa: E402
from tools.scriptfile import load_script  # noqa: E402

PHONE = (270, 480)  # 25% of 1080x1920
MOMENTS = ("start", "middle", "end")


def grab(video: Path, t: float, out: Path, size: tuple[int, int] | None = PHONE) -> Path:
    scale = ["-vf", f"scale={size[0]}:{size[1]}"] if size else []
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", str(video), "-frames:v", "1",
                    *scale, str(out)], check=True)
    return out


def moments(t0: float, t1: float) -> list[float]:
    edge = min(0.2, (t1 - t0) / 4)
    return [t0 + edge, (t0 + t1) / 2, t1 - edge]


def timed(ep: Path, video: Path | None = None) -> tuple[Path, dict[str, tuple[float, float]]]:
    """The video to read and each beat's start and end, from the captions beside it."""
    video = video or EXPORTS / f"{ep.name}.mp4"
    srt = video.with_suffix(".srt")
    if not video.exists() or not srt.exists():
        sys.exit(f"Need {video.name} and its .srt. Make them with: vid final {ep.name[:3]}")
    times, problems = beat_times(load_script(ep / "script.md"), parse_srt(srt.read_text(encoding="utf-8")))
    if problems:
        sys.exit("The captions do not match script.md: " + problems[0])
    return video, times


def contact_sheets(ep: Path, video: Path | None = None, per_sheet: int = 3) -> list[Path]:
    from PIL import Image, ImageDraw

    video, times = timed(ep, video)
    out = MEDIA / ep.name / "frames"
    out.mkdir(parents=True, exist_ok=True)
    w, h = PHONE
    pad, head = 10, 26
    ids = list(times)
    sheets = []
    for n, first in enumerate(range(0, len(ids), per_sheet), 1):
        group = ids[first:first + per_sheet]
        sheet = Image.new("RGB", (3 * w + 4 * pad, len(group) * (h + head + pad) + pad), "#202634")
        draw = ImageDraw.Draw(sheet)
        for row, beat_id in enumerate(group):
            for col, (label, t) in enumerate(zip(MOMENTS, moments(*times[beat_id]))):
                x, y = pad + col * (w + pad), pad + row * (h + head + pad)
                draw.text((x + 2, y + 6), f"{beat_id} {label}  {t:5.2f} s", fill="#ECEFF4")
                frame = grab(video, t, out / f"{beat_id}-{label}.png")
                with Image.open(frame) as im:
                    sheet.paste(im.convert("RGB"), (x, y + head))
        path = out / f"sheet-{n}.png"
        sheet.save(path)
        sheets.append(path)
    t0, t1 = times[ids[0]]
    sheets.append(grab(video, (t0 + t1) / 2, out / "cover.png", size=None))
    return sheets


def moment_sheet(ep: Path, video: Path, seconds: list[float], cols: int = 4) -> Path:
    """One phone-size frame per requested second, labeled, in a single sheet."""
    from PIL import Image, ImageDraw

    out = MEDIA / ep.name / "frames"
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("at-*.png"):
        old.unlink()
    w, h = PHONE
    pad, head = 10, 26
    rows = (len(seconds) + cols - 1) // cols
    sheet = Image.new("RGB", (min(cols, len(seconds)) * (w + pad) + pad, rows * (h + head + pad) + pad), "#202634")
    draw = ImageDraw.Draw(sheet)
    for i, t in enumerate(seconds):
        x, y = pad + (i % cols) * (w + pad), pad + (i // cols) * (h + head + pad)
        draw.text((x + 2, y + 6), f"{t:6.2f} s", fill="#ECEFF4")
        with Image.open(grab(video, t, out / f"at-{t:07.2f}.png")) as im:
            sheet.paste(im.convert("RGB"), (x, y + head))
    path = out / "moments.png"
    sheet.save(path)
    return path


def picture_check(video: Path, times: dict[str, tuple[float, float]]) -> bool:
    """`vid qa`'s rendered-picture rules on this render, with the same limits."""
    spans = {beat: [round(t0, 3), round(t1, 3)] for beat, (t0, t1) in times.items()}
    results = picture_results(visual_quality.measure_video(video, spans), load_section(Limits, "qa"))
    return show(f"Picture checks on {video.name} (the limits of vid qa)", results)


def run(ep: Path, video: Path | None = None, at: list[float] | None = None) -> bool:
    video, times = timed(ep, video)
    if at:
        print(f"  {moment_sheet(ep, video, at).relative_to(ROOT)}")
        return True
    for path in contact_sheets(ep, video):
        print(f"  {path.relative_to(ROOT)}")
    print("\nRead every sheet: labels legible at this size, nothing under the Shorts UI, nothing "
          "left over from another episode, and one focal idea per frame.\n")
    picture_check(video, times)
    return True


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    run(Path(sys.argv[1]).resolve())
