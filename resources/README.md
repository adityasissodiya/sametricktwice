# Resources

What finished videos taught, frozen so the next one starts from it. Read these pages instead of
`tools/`, `kit/` or old scenes. If a page is wrong or missing something, fix it in the same change.

| When | Read |
|---|---|
| Planning any video; making a special | [PLAYBOOK.md](PLAYBOOK.md) |
| Writing a scene | [KIT.md](KIT.md) for the API and geometry, `gallery.png` for what the parts look like |
| Your first scene in a format | `example_scene.py`, complete and gate-tested |
| Before a scene, and when a check fails | [GATES.md](GATES.md) |

## What belongs here

`kit/` is what every video stands on. `resources/` is optional building blocks harvested from finished
videos. Everything here follows four rules, and `tests/test_resources.py` enforces them:

- **It only draws.** Nothing here calls `self.play`. The source gates read motion in `scene.py` only.
- **It has no words.** Every on-screen word is an argument from `scene.py`, so lint can see it.
- **It has no colors of its own.** House colors only, passed in or from `kit.style`.
- **It holds grammar, not subjects.** A kind of thing, never a diagram of one topic. Repeated subjects
  are what YouTube's "inauthentic content" rule demonetizes, so a video still draws its own story.

## Catalogue

`from resources import *` works in a Short and in a landscape special. Import your kit first.

### Stage: `class Episode(StageTools, LandscapeScene)`

| Name | Does |
|---|---|
| `StageTools.header(number, words, color)` | swap the beat label at once |
| `StageTools.onscreen(words, color=INK, size=40)` | a beat's TXT on the stage's top line; you play it in |
| `StageTools.on_stage(*keep)` | everything on stage except captions, guides, header and `keep`, for `FadeOut` |
| `StageTools.cut()` | a hard cut: the picture leaves in one frame |
| `StageTools.fits(label, *mobjects)` | an alignment keyframe: must sit on the stage, never rescaled |
| `StageTools.breath(seconds=BREATH)` | silence after a beat |
| `stage_box()` | the current format's stage, as a `Box` |
| `BREATH`, `LONG_BREATH` | 1.4 s and 2.2 s |

### Motion: for `self.play`

| Name | Does |
|---|---|
| `between(start, end)` | a `rate_func` that runs in one part of the play |
| `swap(old, new, at=0.4)` | one thing out, then the next in, with no overlap |
| `pop(mobject, factor=1.12)` | a short swell and return |
| `route(start, end, angle=0.0)` | the path for `MoveAlongPath`, straight or arced, between points or mobjects |
| `tween(mobject, setter, start, end, **kw)` | animate any value: `setter(mobject, value)` on each frame |

### Parts

| Name | Does |
|---|---|
| `panel(width, height, color, opacity=PANEL_OPACITY)` | a tinted panel, behind everything on it |
| `backdrop(color, opacity=PANEL_OPACITY)` | a panel across the whole stage: one world's color |
| `PANEL_OPACITY` | 0.10, the faintest tint that counts as picture for every house color but `FAINT` |
| `phase_pill(number, word, width=2.7, height=0.74, size=24)` | one step of a process: box (0), digit (1), word (2) |
| `phase_pills(words, direction=RIGHT, buff=0.3, **kw)` | one numbered pill per word |
| `light(pill, color)`, `dim(pill)` | animations: a step begins; a step is over |
| `Flow(start, end, color=LINK_COLOR, radius=0.09, spacing=0.9, pace=2.2, phase=0.0)` | dots running along a line; `hold_at`, `stop()` |
| `stamp(words, color, tilt=0.0, size=66)` | a decision in big words on an opaque tag |
| `bridge(start, end, gap=0.08, color=FAINT, width=7)` | a link that starts and ends at two borders |

### Icons: `icons.person(A_COLOR, size=1.2)`

Open `gallery.png`. Each one is centered, has no words, and takes `(color=INK, size=1.0)`; docstrings in
`icons.py` list the parts you can animate. `cross` defaults to `ALERT`, `plate` takes a drawing first.

`battery`, `building`, `clock`, `coin`, `cross`, `doc` (`rows=3`), `eye`, `flag`, `flame`, `gauge`, `gear`
(`teeth=10`), `house`, `key` (`length=1.0`), `laptop`, `lens`, `monitor`, `padlock`, `person`,
`plate(drawing, color=INK, side=2.3)`, `ring`, `seal`, `server`, `star`, `tick`, `truck`.

## What is frozen, and how

| What | Pin | Test |
|---|---|---|
| Limits, narrator, series constants, alignment tolerance | the block at the end of GATES.md | `tests/test_frozen_gates.py` |
| The list of rules | the tables in GATES.md | `tests/test_frozen_gates.py` |
| The shape of every drawn part | `frozen.json` | `tests/test_resources.py` |
| The rules of this folder, and a passing example | this page, `example_scene.py` | `tests/test_resources.py` |

Changing a pin needs the creator's approval (AGENTS.md): a re-render of a finished video would pick up
the change. Adding a new part needs none.

## Adding a part

Add it when a second video could use it, not before. Rewrite it from the video it came from: generic
names, no subject in the docstring, words and colors as arguments, nothing but drawing. Then:

1. Add it to `__all__` and to the catalogue above. New drawn parts go in `gallery.py`'s `catalogue()`
   (an icon joins by itself).
2. Run `vid uv run python -m resources.gallery --pin`, and look at `gallery.png`.
3. Run `vid test`.
