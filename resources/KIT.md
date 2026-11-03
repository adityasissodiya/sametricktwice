# Kit reference

What a scene can call, without reading `kit/`. If this page is wrong or missing something, fix it in
the same change. `tests/test_resources.py` fails if a public kit name is missing here.

## Scene skeleton

```python
from kit.landscape import *   # a landscape special; a Short uses `from kit import *`
from resources import *

class Episode(StageTools, LandscapeScene):   # a Short: ShortScene
    def construct(self):
        with self.beat("B1") as b:           # speaks B1; everything inside runs under its line
            ...
            self.play(..., run_time=0.3 * b.duration)
            self.hold(b)                     # wait out the rest of the line
```

`resources/example_scene.py` is a complete one.

## ShortScene (and LandscapeScene)

| Call | Does |
|---|---|
| `beat(id)` | context manager giving a `BeatTime`: `b.duration`, `b.remaining`, `b.beat` (`.id`, `.vo`, `.vis`, `.txt`, `.note`, `.label`) |
| `hold(b, leave=0.0)` | wait until `leave` seconds before the line ends |
| `clear_stage(run_time=0.4)` | fade the stage out. Inside a video, prefer `self.cut()` |
| `placeholder(b)` | animatic card; banned in a final |
| `sfx(name, gain=-12)` | play a sound from the episode's `audio/`, then `kit/sfx` |
| `alignment_loop(label, **kw)` | context manager: register constraints, refined on exit (see below) |
| `end_card(run_time=1.6, title=True, both_ways=False, tagline=(), sound=None, intro=(), series=False, icons=None)` | a Short's Connection Map. `icons`: this episode's two drawings, same frame. `series=True` is for compilations only. A special ends on its own last beat instead |

Attributes: `cc` (captions), `guides`, `alignment_guides`, `alignment`, `script`, `episode_dir`,
`keyword_colors`.

## Parts and style

`kit.parts`: `text(words, size=34, color=INK, weight=NORMAL)`, `title(words, size=64, color=INK)`,
`beat_header(number, words, color)`, `date_badge(year, color)` (year is a string),
`pill(words, color, size=20, pad=0.42)`, `phone(height=5.0, color=FAINT)` (body, screen, speaker).

`kit.style` colors: `BG` #0F1117, `INK` #ECEFF4, `MUTED` #7D869C, `FAINT` #2A2F3A, `A_COLOR` #58B4FF
(world A), `B_COLOR` #FF9F45 (world B), `LINK_COLOR` #C792EA (the trick), `ALERT` #FF5C5C (a problem).

Sizes: `TITLE_SIZE` 64, `BODY_SIZE` 34, `LABEL_SIZE` 28, `CAPTION_SIZE` 40, `STROKE` 5. Fonts:
`TITLE_FONT`, `BODY_FONT`.

## Geometry (1 unit = 135 px at the master's size)

| | Short (`kit`) | Landscape (`kit.landscape`) |
|---|---|---|
| Frame `FRAME_W` x `FRAME_H` | 8 x 14.22 | 14.22 x 8 |
| Safe `SAFE_LEFT`..`SAFE_RIGHT` | -3.55..2.75 | -6.4..6.4 |
| Safe `SAFE_BOTTOM`..`SAFE_TOP` | -4..5.45 | -3.6..3.6 |
| `SAFE_CENTER` | (-0.4, 0.725): **the axis is -0.4** | (0, 0) |
| Header | `beat_header`, y 5 | `wide_header`, `HEADER_Y` 3.32 |
| `STAGE_CENTER` | (-0.4, 1.325) | (0, 0.195) |
| `stage_box()` (resources) | x -3.55..2.75, y -2.68..4.5 | x -6.4..6.4, y -2.43..2.82 |
| `STAGE_WIDTH` | 6.3 | 12.8; also `STAGE_HEIGHT` 5.25, `STAGE_TOP`, `STAGE_BOTTOM` |
| `CAPTION_CENTER` | (-0.4, -3.3) | (0, -3.05) |

Outside a render, `kit.style` prints `FRAME_H` 4.5, from Manim's default pixel size. Importing
`kit.landscape` turns the frame to 16:9 for the whole process, so never import it from shared code.
It also provides `wide_header`, `wide_caption`, `WideCaptions`, `wide_guides`, `LandscapeScene`,
`SAFE_BOX`, `STAGE_BOX`.

## Alignment (`kit.alignment`)

```python
with self.alignment_loop("B4 row") as align:
    align.even_row(cards, name="cards", y=0.5, gap=0.4)
    align.inside_safe(VGroup(*cards), name="row", allow_scale=False)
```

| Constraint | Signature (all also take `tolerance=`) |
|---|---|
| `centered` | `(m, *, name=None, horizontal=True, vertical=False, axis_x=None, axis_y=None)` |
| `mirror_pair` | `(left, right, *, name=None, axis_x=None, y=None, align_y=True, min_gap=0.0)` |
| `balanced_pair` | `(left, right, **kw)`, an `even_row` of two unlike objects |
| `even_row` | `(mobs, *, name="row", center_x=None, y=None, gap=None, min_gap=0.0)`; it re-centers the row |
| `even_column` | `(mobs, *, name="column", x=None, center_y=None, gap=None, min_gap=0.0)` |
| `inside_safe` | `(m, *, name=None, padding=0.12, allow_scale=True, bounds=None)`; it can scale, so pass `allow_scale=False` once the layout is set |

Tolerance `DEFAULT_TOLERANCE` 0.04, `DEFAULT_MAX_PASSES` 6. `Box(left, right, bottom, top)` has `.width`,
`.height`, `.center_x`, `.center_y`; `visual_box(m)` measures a mobject with its strokes. A loop's
`check()` and `refine()` run by themselves when the `with` block ends. Modes: `vid preview` and
`vid align` warn, `vid final` raises.

`AlignmentLoop`, `AlignmentSession` and `AlignmentError` are what `alignment_loop` is built on;
`alignment_guides` is the overlay `vid align` draws. A scene never needs them directly.

## Sounds (`kit/sfx`)

Gains are the medians from finished videos. At most 2 cues may overlap, so length matters.

| Sound | Seconds | Gain | Goes with |
|---|---|---|---|
| `tap.wav` | 0.07 | -15 | something appears or lands |
| `shutter.wav` | 0.18 | -13 | a stamp, a decision |
| `swipe.wav` | 0.32 | -14 | a sweep, `GrowArrow` |
| `spark.wav` | 0.35 | -14 | a break, a change to `ALERT` |
| `ticks.wav` | 0.48 | -15 | a timer, a scan, `Rotate` |
| `whoosh.wav` | 0.55 | -14 | `MoveAlongPath`, a big move |
| `wash.wav` | 0.65 | -14.5 | the stage clears |
| `power-up.wav` | 0.7 | -15 | the closing assembly |
| `pixels.wav` | 0.85 | -14 | many small things change |
| `ping.wav` | 1.01 | -14 | success, arrival; once a second at most |

## Files

`script.md`:

```
---
title: At most 60 characters, naming both worlds
a: Label | keyword, keyword
b: Label | keyword, keyword
link: Label | keyword, keyword
glossary: technical, names
format: landscape        (specials only)
---
## B1 · Hook
VO: The spoken words.
VIS: Direction, never spoken.
TXT: Big words on screen, at most 4.
NOTE: How to say it, for the human review.
```

Lines that start with `>` are comments. Keywords color the captions.

`brief.md`: `**The bridge...:** one sentence`, then ledger rows:
`| C1 | The claim (B2, B5-B8) | [source](https://...) | | high |`. A framing row is `F1` and says why.

`limits.toml` (a special only): `[ste] seconds = [a, b]` and `[qa] seconds = [a, b]`, or any other key
of those two sections, each with a comment that quotes the creator's approval.
