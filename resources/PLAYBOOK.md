# Playbook

What made the finished videos good, and what cost them the most rounds. Rules live in GATES.md and
the API in KIT.md; this page is the judgment around them.

## Before you animate

The costliest mistake is animating words the creator has not approved. So:

1. **Ask first.** Who is this for (the general public, or someone who knows the field)? What must they
   understand at the end? How long should it be? Ask before you draft.
2. **Get the angle and the narration approved before any scene work.** A hook can be fluent and still
   send the wrong idea; the creator judges that, and a definitive claim needs real support.
3. **Render when the creator needs to see it.** Some decisions cannot be made from a script. Offer an
   animatic or a preview, and do not argue a choice in words for long.

## Making a special

A special is a video that is not a Short: a longer explainer, a companion, a landing video.

1. `vid new --special <name>` makes `specials/<name>/` in 16:9. `.gitignore` keeps it out of the public
   repository, because a special can come from unpublished work. **Never name a special or its subject
   in a tracked file.**
2. Write `limits.toml` with the length the creator approved, and quote them. Windows used so far:
   30-45 s (landing), 150-240 s (three-minute explainer), 270-420 s (slow prerequisites).
3. The source rules still apply. Beats run B1..Bn, B3 is still the mechanism, B6 still replays it, and
   every beat still needs motion through 65% of its line.
4. `vid check`, `vid lint`, `vid preview`, `vid frames --render`, `vid align`, `vid final`. There is no
   `vid status` for a special. The master, captions and QA report stay in its own folder.
5. **Write it one micro-unit at a time.** Finished specials ran 36-84k characters, about a quarter
   of it helpers. A wrong first half is expensive to find after writing the second.
6. Finished? Offer to move what two videos could use into `resources/`, under generic names.

## Recipes

**Lay out in this order:** build, register alignment, measure, play. Alignment can move things, so a
path measured earlier points at the old spot.

**The replay.** The mechanism is one Episode method. B3 sets its clock once; B6 passes the same clock.

```python
def trick(self, skin, run_time):          # a method of Episode, or the gates give no credit
    heat, fill, push = 0.22, 0.43, 0.35   # one share per phase
    ...
    self.play(..., run_time=heat * run_time)

self.trick_time = min(CAP, 0.8 * b.duration)   # in B3; CAP in seconds, just under B6's line
self.trick(WORLD_A, self.trick_time)
self.trick(WORLD_B, self.trick_time)           # in B6
```

Skins are `SimpleNamespace(color=..., word=...)`. The same method can replay in a third skin later.

**The opening.** `self.add(cover)` first, so the cover is there at frame 0, then a first play with
`rate_func=linear`. Default easing starts too slowly for `opening-quality`. About 12 words keeps B1 well
under 6 s.

**A new unit.** `self.cut()` and `self.header(...)`, then `self.add(backdrop(color))` or your drawing.
A stage that fades in from nothing is near-black for a moment.

**Partial clear.** `self.play(FadeOut(*self.on_stage(kept_a, kept_b)), Transform(kept_a, x), ...)`.

**Several steps in one play.** `rate_func=between(0.0, 0.4)` on one animation and `between(0.4, 1.0)` on
the next, so they read in order. `swap(old, new)` does it for words.

**Merging N cards into one.** Transform one to the target and the others to a no-fill ghost. N opaque
copies landing on one spot add up to a brighter card.

```python
ghost = target.copy().set_fill(opacity=0).set_stroke(opacity=0)
self.play(Transform(cards[1], target.copy()), Transform(cards[0], ghost), Transform(cards[2], ghost.copy()),
          run_time=0.22 * b.duration)
self.remove(*cards)
self.add(target)
```

**A value, not a position** (a slider, a gauge reading): `tween(card, Card.set_settings, old, new, run_time=...)`.

**Stage too empty.** Scale the diagram up first, then a tinted `panel` behind the composition. Fill shapes
instead of drawing thin outlines. Keep it to one large diagram per beat.

## Manim traps

| You see | Because | Do |
|---|---|---|
| `zip() argument 2 is shorter` | a mobject was faded inside a group while being transformed | `self.on_stage(*keep)` |
| A full-turn `Rotate(x, TAU)` draws nothing | start and end are the same | `0.95 * TAU` |
| `point_from_proportion` crashes with "no points" on a `DashedLine` | it has none of its own | Interpolate its ends, or `DashedVMobject` over a smooth `VMobject` |
| One of two animations is ignored | they target one mobject, or `x` and `x[0]`, in one play | Chain them in one `.animate`, or use two plays |
| `Succession` of `.animate` on one mobject misbehaves | each one captures its start too early | Separate plays |
| `FadeIn(shift=...)` fights a move | both set the position | Fade first, then move |
| Outline icons turn solid, or a card's fill jumps | `set_opacity` sets fill too | `.animate.fade(0.7)` |
| Things drift after a `scale` | an empty `VGroup()` adds a point at the origin | Never return empty groups |
| A faded parent's children come back | its children were transformed away from it | Keep leaves top-level |
| A later animation of a transform's target does nothing | `Transform` leaves the original on stage | `ReplacementTransform` |
| A path misses its target | `inside_safe` scaled or moved after you measured | Measure after alignment, or `allow_scale=False` |
| `even_row` undoes your centering | it re-centers the row | Pass `center_x`; do not add `centered` to the same parts |
| A small label garbles for a moment | a crossfade | `self.header()` swaps at once |
| Text overlaps during a change | crossfading words | `swap(old, new)` |
| Near-black frames between units | a fade to clear the stage | `self.cut()` |
| A fading Flow stays visible | its updater resets opacity | `flow.stop()` first; remove it before a merge |
| A minus sign is missing | the house fonts lack U+2212 | Use an en dash |

On contact sheets, the same faults recur: rails running through chips (`bridge` ends at borders),
returning tokens overlapping where they started, and arcs crossing labels (`route(a, b, angle=...)`).

Tool behavior: `vid frames --render` reads only the newest render, so preview first. `vid align` renders
with guides on, so preview again before you judge the picture. An animatic always fails `opening-quality`.
`vid scene` refuses to overwrite a scene.

## Taste

- **The narrator sets the word speed; slowness lives in the picture.** To make a video feel slower, keep
  the stage still across beats, move one thing at a time, and leave a `breath()` after each beat.
- **Do not make a dense opening denser.** If viewers need terms before the opening makes sense, a
  two-world cover only confuses them. A separate, slow prerequisites video worked better than squeezing
  the terms in.
- **Write for the viewer named in step 1.** A video for people in the field can be precise and still
  simple. Do not explain what they know, and do not skip what makes it hard.
- **Recognition is the payoff.** B6 works because the same geometry and timing return with new color and
  words. Do not improve it the second time.
- **Color tells them where they are.** A world's tint across the stage needs no label. Red stays rare.
- **Close the loop.** The last beat rebuilds the cover, so the last pose flows into the first.
- **Animate only the change.** Hold stable structure still. Cue only what matters now.

## Spending fewer tokens

Estimated from four long specials: 80-85% of output tokens went to thinking, most of all just before
scene writes. Pipeline code and docs took roughly 100-150k tokens of reading per session, contact sheets
30-110k, and each context compaction forced more re-reading. So:

- Read these pages, not `tools/`, `kit/` or old scenes. Look at `gallery.png` once.
- Decide the layout in the script's VIS lines, so the thinking happens once and survives a compaction.
- Run `vid check` and `vid lint` before any render, and `vid frames --beats B3 B6` while you fix a few
  beats. Read all the sheets before and after `vid final`.
- Take the first gate failure seriously: GATES.md says why it fails, so fix the cause once.
- Do not redraw an icon that is in the gallery, or rewrite a helper that is in `resources/`.

## What passing looks like

Measured on five finished special masters, so you can tell a near miss from a healthy margin:

| Measure | Range |
|---|---|
| Stage foreground, median | 31-97% |
| Stage height, median | 87-97% |
| Weakest opening quarter-second | 0.47-2.1 gray levels |
| Sound cues per 10 s | 3.3-7.1, median 4.15 |
| Words per minute | 157-182 |
| Median pause between sentences | 0.38-0.56 s |
| Longest freeze / near-black | up to 2.2 s / up to 0.78 s |
| B1 | 10-14 words, ends at 3.5-5.5 s |
| Loudness, true peak | -14.5..-14.3 LUFS, -2.8..-2.2 dBTP |
