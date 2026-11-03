# Gates

Every rule the pipeline enforces: what passes, how it usually fails, and the fix. Read it before
you write a scene, and again when a check fails. RESEARCH.md has the evidence behind each rule.

`tests/test_frozen_gates.py` fails when a rule appears or disappears without this page changing,
or when a live limit differs from the frozen block at the end.

## Order

`vid check` -> `vid lint` -> `vid preview` -> `vid frames --render` -> `vid align` -> `vid final`
(which runs them again, then `vid qa`). Run `vid check` and `vid lint` right after the script:
they need no render and they catch most failures.

## How the source gates read a scene

They parse `scene.py` without running it, and read no other file. That explains most surprises:

- **A helper counts only as a method of `class Episode` itself.** A mixin or a module function
  that calls `self.play` earns nothing.
- **Clocks are followed through one assignment per line.** `a, b = x, y` loses the trail, which
  fails `motion-timing`, `motion-coverage` and `recognition-replay` together.
- **A play in a `for` loop counts once.** Use one `LaggedStart(..., lag_ratio=1.0)`, or write the
  calls out. `self.wait` and `self.hold` count nothing.
- **Shares come from the code, not the clock.** `min(CAP, 0.8 * b.duration)` counts 0.8.
- **Words and colors are seen in `scene.py` only**, so `resources/` takes them as arguments.

## Source rules (`vid check`)

| Rule | Passes when | Usual failure and fix |
|---|---|---|
| STE score | at least 80% of VO sentences break no ASD-STE100 rule | A first pass scores 75-81%. Reword: may -> can/will, undo -> reverse, a fragment needs a verb; add real technical names to `glossary:` |
| `one-goal` | the brief's bridge is 1 sentence, at most 30 words | Two ideas: keep the one the viewer learns |
| `hook-length` | B1 has at most 15 words | About 12 also keeps `hook-time` safe |
| `hook-relevance` | B1 has an `a:` keyword and a `b:` keyword as whole words | A plural or synonym is missing from the keyword list |
| `cold-open` | B1 has no intro phrase or "subscribe"; no play or wait before the first beat | Move setup into B1 |
| `early-answer` | B3 starts within 35% of the words | Trim B1-B2 |
| `micro-units` | each beat has at most 30 words and 3 sentences | Drafts hit 31-32 words or 4 sentences: cut, do not squeeze |
| `delivery-notes` | every spoken beat has a `NOTE:` | Direction for the human review; it does not change the voice |
| `length` | words / 160 x 60 is inside the target (45-60 s; a special's `limits.toml`) | Cut or add words |
| `minimal-text` | TXT at most 4 words; any on-screen string at most 5; no 4 VO words in a row on screen | Label the thing, do not caption it |
| `title` | at most 60 characters, names both worlds | |
| `sourced` | every spoken beat is in a ledger row; each row names its beats, e.g. `(B2, B5-B8)`; each C row has an http(s) link or points at another row | A local path is not a source; a claim from one is framing (F row) |
| `color-signals` | custom hex colors are neutral or within 25 degrees of a house hue; no Manim named colors | Use `A_COLOR`, `B_COLOR`, `LINK_COLOR`, `ALERT`, `INK`, `MUTED`, `FAINT` |
| `every-beat` | a literal `self.beat("Bn")` for each beat, once, in order; `final` also bans placeholders | |
| `motion-timing` | every direct play and `end_card` has a `run_time` from the beat's `b`; helper plays have one, with no fixed seconds and one timing parameter | Use `run_time=0.2 * b.duration` |
| `motion-coverage` | in each beat the shares add up to at least 0.65 | See "How the source gates read a scene" |
| `recognition-replay` | B3 and B6 call one Episode method with an identical clock argument, assigned once before first use and derived from narration | `self.trick_time = min(CAP, 0.8 * b.duration)` in B3, then `self.trick(SKIN, self.trick_time)` in both |
| `causal-motion` | at least 7 of the story beats (all but B9), always B3 and B6, use `Transform`, `ReplacementTransform`, `TransformFromCopy`, `FadeTransform`, `MoveAlongPath`, `Rotate`, `GrowArrow` or `.animate.` with `shift`, `move_to`, `next_to`, `align_to`, `rotate`, `stretch`, `stretch_to_fit_height`, `stretch_to_fit_width` | The name must be visible in the beat or in an Episode method it calls |

## Carry-over (`vid lint`)

Compares the episode with every earlier episode. A string literal in `scene.py` counts as on-screen,
**dict keys included**, unless it is a docstring, an f-string piece, an argument of `alignment_loop`,
`beat`, `sfx`, `Path` or `get`, a color or font keyword, or a file name. Use `SimpleNamespace` for
skins, and pick specific labels: short generic ones ("CLOSE") collide.

| Kind | Fails on |
|---|---|
| `screen` | an on-screen string that an earlier episode also shows, outside `series.toml` |
| `lines` | a narration sentence that an earlier episode also says |
| `topic` | an earlier episode's `a`, `b`, `link` or glossary word (rarer than Zipf 5) in on-screen text, VO, VIS or TXT |
| `ids` | an episode file that names an earlier episode's number or folder |
| `audio` | a sound file copied from an episode or from `kit/sfx` |

## Export rules (`vid qa`)

The picture rules also run on previews through `vid frames --render`: fix them there. On a preview,
`format` and `loudness` always fail, because only `vid final` sets them.

| Rule | Passes when | Usual failure and fix |
|---|---|---|
| `format` | 1080x1920 (a landscape special: 1920x1080), 60 fps, h264/aac, 48000 Hz | Render with `vid final` |
| `length` | inside the target seconds | Fix the words, not the animation: the narrator sets the time |
| `cold-open` | first word by 0.3 s; frame 0 has contrast at least 4; frames 0 s and 0.5 s differ by 0.15 | Open on the cover, already moving |
| `hook-time` | B1 ends by 6 s | B1 of about 12 words |
| `early-answer` | B3 starts within 35% of the video | |
| `speech-rate` | 130-190 words per minute | |
| `delivery-pace` | 155-185 words per minute | Words too short run fast: `vid preview` prints the pace, so fix it at script time with approval |
| `pauses` | median pause between sentences is 0.35-0.9 s | |
| `captions` | the captions match the VO word for word | Do not edit the words by hand |
| `loudness` | -14 LUFS +-1, true peak at most -1.5 dBTP | `vid final` sets it |
| `opening-quality` | every quarter-second of the first second changes at least 0.30 gray levels | The most common failure. Default easing starts too slowly: put `rate_func=linear` on the first play. A placeholder always fails |
| `stage-coverage` | median foreground at least 18%; at most 2 beats under 13% | Bigger diagrams and a `panel` or `backdrop`. Foreground means 12+ levels from `BG`, and the default opacity 0.10 counts for every house color but `FAINT` |
| `layout-variety` | median height at least 60% of the stage; at most 2 beats are wide strips (62%+ wide, under 45% tall) | Use the stage vertically; stack label, object, verdict |
| `sfx-density` | at least 9 cues and 1.5 per 10 s | About one cue per meaningful action |
| `sfx-audibility` | at least 4 cues and 35% of them clear -18 dB mean or -12 dB peak against the narration | Raise buried gains; gains of -13 to -15 pass |
| `sfx-masking` | no cue over speech is louder than -3.5 dB against the narration; at most 2 at once | A `ping` rings for 1 s: do not stack them (KIT.md, Sounds) |
| `dead-air` | near-black under 1 s, frozen picture under 3 s | Hard cuts, not fades to clear the stage; animate something through long holds |

A QA report counts only if it is newer than its master and its pipeline fingerprint is current.
Editing any file in `tools/qa_contract.py`'s list invalidates every report.

## Frozen numbers

These made the finished videos pass. Change one only with the creator's approval, then update this
block and log the reason in `analytics/experiments.md`. Never move one to get an episode through.

```toml
[check]
bridge_max_words = 30
hook_max_words = 15
mechanism_beat = "B3"
answer_by = 0.35
beat_max_words = 30
beat_max_sentences = 3
txt_max_words = 4
screen_max_words = 5
echo_words = 4
title_max_chars = 60
intro_phrases = ["hi", "hello", "hey", "welcome", "in this video", "in today's video", "today we", "today i", "let's talk", "let us talk", "before we start", "what's up"]
hue_tolerance = 25
neutral_saturation = 0.3
neutral_value = 0.25
motion_min_share = 0.65
causal_min_beats = 7

[qa]
seconds = [45, 60]
narration_start_max = 0.3
first_frame_min_contrast = 4.0
first_frame_min_motion = 0.15
hook_end_max = 6.0
answer_by = 0.35
wpm = [130, 190]
delivery_wpm = [155, 185]
sentence_pause = [0.35, 0.9]
lufs = -14.0
lufs_tolerance = 1.0
true_peak_max = -1.5
black_max = 1.0
freeze_max = 3.0
visual_opening_motion_margin = 2.0
visual_min_density = 0.13
visual_min_median_density = 0.18
visual_min_height = 0.45
visual_min_median_height = 0.6
visual_strip_min_width = 0.62
visual_max_low_density_beats = 2
visual_max_horizontal_strip_beats = 2
sfx_min_cues = 9
sfx_min_density = 1.5
sfx_audible_mean_min = -18.0
sfx_audible_peak_min = -12.0
sfx_min_audible_cues = 4
sfx_min_audible_share = 0.35
sfx_masking_mean_max = -3.5
sfx_max_simultaneous = 2

[ste]
target = 0.8
max_words = 25
pace_words = 20
wpm = 160
seconds = [45, 60]
vocabulary = "frequency"
min_zipf = 4.0
approved_list = "ste/approved-words.txt"
glossary = ["transistor", "transistors", "semiconductor", "semiconductors", "silicon", "microscope", "lens", "lenses", "sensor", "sensors", "pixel", "pixels", "molecule", "molecules", "atom", "atoms", "electron", "electrons", "laser", "lasers", "radar", "polymer", "wafer", "wafers", "coating"]
[ste.rules]
sentence_length = true
complex_verbs = true
ing_forms = true
passive_voice = true
noun_clusters = true
fragments = true
phrasal_verbs = true
contractions = true
vocabulary = true

[voice]
voice = "kokoro"
speaker = "af_heart"
speed = 1.0
sentence_pause = 0.25
clause_pause = 0.1
model = "kokoro-v1.0.onnx"
model_sha256 = "7d5df8ecf7d4b1878015a32686053fd0eebe2bc377234608764cc0ef3636a6c5"
voices = "voices-v1.0.bin"
voices_sha256 = "bca610b8308e8d99f32e6fe4197e7ec01679264efed0cac9140fe9c29f1fbf7d"

[series]
screen = ["Connection map", "SAME TRICK", "TWO WORLDS", "×"]
lines = ["Same trick, two worlds."]
words = ["trick", "tricks", "same", "world", "worlds", "connection", "map"]

[alignment]
tolerance = 0.04
max_passes = 6
```
