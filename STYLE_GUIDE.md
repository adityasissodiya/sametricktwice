# Infographic house style

Episode 001, Camera × Chip, is the rendered reference for this series. Future episodes must
feel like another chapter of that Short: the same visual grammar, pacing, captions, semantic
color and audio restraint, with new diagrams designed for the new facts.

Reference, not source: no header, label, word, diagram, subject or sound from an earlier
episode may appear in a new one. Only the series constants in `series.toml` repeat, and
`vid lint` enforces it (see AGENTS.md, "No carry-over between episodes").

## Canvas and composition

- Master: 1080x1920, 60 fps, H.264 video and AAC audio on `BG` (`#0F1117`).
- Design in Manim units from `kit/style.py`. Essential content stays inside the Shorts safe
  area. The usable center is `SAFE_CENTER`, whose x coordinate is `-0.4`; never assume x=0.
- Top band: a small colored number pill, concise uppercase beat label and faint rule.
- Middle: one dominant infographic around `STAGE_CENTER`. Secondary labels explain the
  drawing but never compete with it.
- Bottom: burned-in kinetic captions around `CAPTION_CENTER`, clear of diagrams and UI.
- Use negative space. A phone viewer must understand the silhouette before reading labels.

## Semantic color and type

| Meaning | Constant | Color |
|---|---|---|
| World A | `A_COLOR` | blue `#58B4FF` |
| World B | `B_COLOR` | orange `#FF9F45` |
| Shared trick / causal link | `LINK_COLOR` | violet `#C792EA` |
| A problem: too big, blocked, wrong | `ALERT` | red `#FF5C5C` |
| Main copy | `INK` | near-white `#ECEFF4` |
| Secondary copy | `MUTED` | gray-blue `#7D869C` |
| Structure / inactive state | `FAINT` | charcoal `#2A2F3A` |

Use `TITLE_FONT`/Bahnschrift for headlines and `BODY_FONT`/Segoe UI for labels and captions.
Use the kit sizes as the baseline. Strokes are normally 3-5 units so they survive phone
scaling. Do not add arbitrary accent colors when opacity or `MUTED` can express hierarchy.
One color family means one concept: a darker or lighter shade of a semantic color, or a
neutral (dark panels, metal gray), is fine; a new hue is not. `vid check` (`color-signals`)
reads every color in `scene.py`. Color coding helps only when it marks meaning, and it can
backfire when it decorates (RESEARCH.md, "Signaling").

## Shape language

- Prefer simple vector silhouettes, cross-sections, arrows, grids, rays and callout labels.
- Use rounded panels and pills sparingly for structure. Avoid a dashboard full of cards.
- Draw brand names as plain text, not logos.
- Use archival images only when the real artifact materially helps; record the source and
  license. Do not use an image where a clear diagram can explain the mechanism better.
- Move any component likely to recur into `kit/`. The top-band `beat_header`, `date_badge`,
  text-sized `pill` labels and the `text`/`title` type helpers already live in `kit/parts.py`.
  Helpers in Episode 001 show the intended construction of chips, cameras, process cards,
  rays and mechanism stacks.

## Motion and beat grammar

The source acceptance gates are minimum structure, not substitutes for visual judgment:

- `motion-timing` requires beat-relative timing from `b.duration`; animations stay inside the
  beat and `self.hold(b)` fills only the unused narration tail.
- `motion-coverage` requires scheduled intentional change through at least 65% of every
  narrated beat.
- `causal-motion` requires a visible cause-to-effect change in at least 7 of B1-B8, including
  B3 and B6. Decorative entrances and static swaps do not establish causality.
- `recognition-replay` requires B6 to reuse B3's mechanism geometry and timing. Change the
  material, labels and semantic color, not the causal path the viewer is meant to recognize.

These checks cannot judge whether a path is clear, whether stable structure should remain
still, or whether a detail is seductive. Keep making those decisions from every contact sheet.

- The opening frame is already moving. Use a pulse, trace, scale change or transformation;
  never begin with a blank frame or generic fade.
- Change one meaningful property every 2-3 seconds: position, scale, color, state, diagram
  layer or camera emphasis. Motion must communicate, not decorate.
- Animate in the order viewers should think. Reveal cause before label; show before saying.
- **Animate only the change.** Animation helps when the idea is motion, sequence or change;
  for stable structure a still, labeled frame is cleaner. Draw a diagram once, hold it still
  while the narration points at it, and move only the part that changes.
- **One motion path at a time.** In any moment only one thing travels across the stage;
  everything else is still or changes in place (color, opacity, a small pulse).
- **Cue only what matters now.** One highlight per moment. Do not stack an arrow, a
  highlight, a label and a sound on the same object unless each has its own job.
- Prefer `Transform`, `TransformFromCopy`, `ReplacementTransform`, `Create`, `GrowArrow` and
  purposeful `LaggedStart` sequences to unrelated cuts.
- Keep each beat to one focal idea. Clear the prior stage with `self.clear_stage()`; do not
  remove the caption system with `self.clear()`.
- Time every animation as a fraction of `b.duration`, then use `self.hold(b)` for the unused
  narration tail. Do not let visuals extend a beat accidentally.

The recurring nine-beat treatment is three micro-units with a hard cut between them (World A
and its trick B1-B4, World B and the recognition B5-B6, payback and map B7-B9); inside a unit,
transform rather than cut:

1. B1: a moving visual claim that can double as the cover. The cover is on screen at frame 0;
   the first word starts at once.
2. B2: World A, one concrete date/object/place.
3. B3: the shared mechanism as a readable step-by-step diagram.
4. B4: compress the mechanism into a three-part mnemonic.
5. B5: World B's problem, with scale or contrast made visible.
6. B6: replay B3's geometry and timing in World B's skin. This recognition is the payoff.
   Build the mechanism once as a method that takes a skin (materials, labels, colors) and
   a run time; Episode 001's `Episode.trick()` with `ASPHALT_SKIN`/`KODAK_SKIN` is the model,
   and Episode 003's `play_ptfe()` shows the clock capped to fit the shorter of B3 and B6.
7. B7: reverse the relationship and make the payback visible.
8. B8: show the modern system as a labeled diagram.
9. B9: resolve both directions on the Connection Map of this episode's pair and leave a
   loopable pose. The kit does this: `self.end_card(both_ways=True, tagline=("SAME TRICK",
   "TWO WORLDS"), title=False, intro=[header], icons=(world_a_icon, world_b_icon))`, with
   icons drawn for this episode (Episode 002 uses its radar scope and phone). It draws this
   episode's pair only; earlier episodes never appear in a Short (`series=True` is for
   compilations). Draw both icons in frames of the same shape: the kit scales each by its
   longer side, so a wide icon beside a square one shrinks and its label rides higher.

## Captions and on-screen words

- Captions are generated from VO and contain at most three words per chunk. Short chunks
  with highlighted keywords help the series' many non-native viewers without turning the
  frame into a transcript (RESEARCH.md, "Captions and on-screen text").
- Theme keywords use the same semantic colors as the art.
- Big TXT is optional and limited to four words; labels and headers to five. On-screen text
  is keywords: it never repeats four or more narration words in a row (`minimal-text`).
- Write every beat header and label for this episode. Generic copy from an earlier episode
  ("The trick", "Remember this") is carry-over; name the thing this episode shows instead.
- VIS, NOTE, prompts, filenames, source notes and TODO text are production metadata. They must
  never appear in a final frame.
- Keep all text horizontal, high contrast and legible at 25% preview size.

## Dialogue and sound

- `delivery-notes` checks that each spoken beat records non-spoken intent for pace, pause,
  emphasis or turn. NOTE text does not enter Kokoro and does not prove that intent was performed.
  `delivery-pace` checks aggregate narration rate against the house references; only the
  mandatory sound-only listen can judge the performance. Never change approved VO or
  `voice.toml` without creator approval.
- Rendered SFX must pass `sfx-density`, `sfx-audibility` and `sfx-masking`: cue only meaningful
  actions, make each cue just audible on phone playback, and shorten, lower or move it whenever
  it masks narration. A passing meter does not replace a sound-only listen.

The script is locked during animation. Interesting delivery comes from performance and timing,
not rewritten words.

- Put non-spoken performance direction in each beat's `NOTE:`: pace, pause, emphasis and turn.
- Shape the arc: crisp hook; measured history; rhythmic mechanism verbs; an audible lift for
  B6 recognition and B7 reversal; a slightly slower, clean kicker.
- The series voice is frozen in `voice.toml`: Kokoro-82M speaker `af_heart` (Apache-2.0,
  runs locally), speed 1.0, SHA-256-checked model. Inside a beat the model sets its own
  pauses (about 0.5 s between sentences, close to the 0.6 s listeners find most natural).
  Every render uses it by default, so drafts time exactly like finals. Fix how a name sounds
  in `pronounce.toml`, never in the VO. Changing the voice needs the creator's approval.
- Pace: 130-190 words per minute (`speech-rate`); the series runs at about 160-180.
- Use tiny action-synced sounds—shutter, whoosh, wash, spark, ticks—at low gain. Silence them
  when they compete with consonants.
- House sounds live once in `kit/sfx` (tap, ping, whoosh, swipe, spark, ticks, wash, shutter,
  pixels, power-up). Play them with `self.sfx("name.wav")`. A sound made for one episode goes
  in its `audio/` folder; never copy sound files between episodes or from the kit.
- Polish speech with high-pass filtering, light presence EQ and compression, then normalize
  the mix to about -14 LUFS with true peak at or below -1.5 dB. Audio polish cannot replace
  an expressive read.

## Alignment and symmetry system

Symmetry is measured around the safe-area axis `SAFE_CENTER[0]`, not the physical frame. Use
the declarative constraints in `kit/alignment.py` for every composition that changes layout.
The system supports:

- a group or object centered on the safe axis;
- a left/right pair mirrored about the safe axis;
- a horizontal row or vertical column with equal gaps and a common baseline/centerline;
- containment inside the safe bounds;
- a named, reasoned exception for intentional asymmetry.

Register constraints before `self.play`:

```python
with self.alignment_loop("B4 process cards") as align:
    align.even_row(cards, y=1.3, gap=0.30)
    align.inside_safe(cards)

with self.alignment_loop("B7 two-way relationship") as align:
    align.mirror_pair(world_a, world_b, y=1.2, min_gap=0.4)
```

Use `balanced_pair` when the two objects have different visual widths, `centered` for one
focal group and `even_column` for a vertical stack. The default tolerance is 0.04 Manim units
(about 5.4 pixels in the master) with at most six correction passes. Conflicting constraints
fail rather than oscillating forever.

Use the default tolerance from the kit. Do not create a looser per-scene tolerance to make a
failure disappear.

The required refinement loop is:

1. Group the layout and register its intended constraints before animation.
2. Let the helper correct small offsets iteratively and record the residual measurements.
3. Run `vid align <episode> --no-open` to create a guide render and JSON report.
4. Inspect the start, middle and end of each layout-changing beat at full and phone size.
5. Correct the source geometry; rerun until all unintended errors pass.
6. Run the audit once more after the final voice because changed timing can expose a bad
   transitional frame.

Do not declare every frame symmetrical. Story-driven asymmetry is valid—for example an object
moving from A to B—but its start/end anchors, paired labels, repeated cards and margins still
need measured alignment. Document the exception; do not disable the audit.

## Final acceptance

- Source motion passes `motion-timing`, `motion-coverage`, `recognition-replay` and
  `causal-motion`.
- The script passes `delivery-notes`; the rendered master passes `opening-quality`,
  `stage-coverage`, `layout-variety`, all three `sfx-*` rules and `delivery-pace`.
- The QA report names this episode and video, is newer than the master, and its pipeline
  fingerprint matches the current QA rules.
- The creator watched at phone size with sound and muted, then listened to the whole export
  sound-only with the picture hidden.
- Automated rendered/audio thresholds are calibrated house/reference acceptance proxies, not
  stronger research claims; contact-sheet judgment and the human listening passes still govern.

A Short is finished only when all are true:

- `vid final` ended with "Done": STE, design rules, carry-over, alignment and `vid qa` pass;
- every contact sheet from `vid frames` was read: one focal idea per frame, one motion path,
  legible at 25% size, nothing under the Shorts UI;
- no placeholder or production-note frames remain;
- `vid lint` passes and no frame shows anything from another episode;
- every spoken fact maps to the brief and the approved VO is unchanged;
- the first frame moves and reads as a cover;
- B3/B6 clearly reuse the same mechanism;
- all essential art is within the safe area and captions never collide with it;
- registered alignment constraints pass and intentional exceptions have reasons;
- the final is watched once with sound and once muted at phone size;
- export metadata, captions, loudness and black/freeze scans pass.

Target 45-60 seconds for new episodes; `vid qa` fails anything longer. Episode 001's current
61-second master is a reference for style, not permission to let future scripts or
transition padding drift beyond the target.
