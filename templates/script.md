---
title:
a:
b:
link:
glossary:
---

# {slug} · script

> Front matter, for example:  a: Camera | camera, lens, Kodak   b: Chip | chip, transistor
> title = the upload title: 60 characters max, naming world A and world B.
> a / b / link = a short label, then the words that mean world A, world B and the trick.
> Captions color those words blue, orange and violet; the labels go on the Connection Map.
> glossary = technical names the STE check should accept (photolithography, transistor).
>
> One beat = one idea: one or two short sentences, 30 words and 3 sentences max.
> VO is spoken exactly as written. B1 is the hook: a specific claim naming both worlds,
> 15 words max, no greeting. B3 (the answer) must start within the first 35% of the words.
> VIS = what we see. TXT = big on-screen keywords (optional, 4 words max, never a VO phrase).
> NOTE = delivery direction only; it is never spoken and must not rewrite approved VO.
> Target: 45-60 s, about 150-170 written words. `vid qa` counts written words per minute of
> narration (155-185), and the voice spells acronyms (PTFE = 4 words said) and reads a year
> as 3, so give those lines extra words. `vid preview` prints the pace once the voice exists.
> `vid check` must pass: 80% STE + design rules.

## Series infographic house style

- Everything in this episode is made for this episode. Earlier episodes show the house style;
  never copy their words, headers, labels, taglines (beyond series.toml), diagrams, sounds or
  file text. Shared pieces come from `kit/` (parts, `self.sfx`), nothing else. `vid lint`
  must pass.
- Build for vertical 1080x1920 at 60 fps on the dark kit background. Use clean, bold Manim
  shapes, thick phone-legible strokes and minimal text rather than decorative footage.
- Color is semantic: A is blue, B is orange and the shared trick is violet. Keep captions,
  labels, arrows and transformations consistent with those meanings.
- Start already in motion; reveal one idea at a time; change motion, scale, color or state at
  least every 2-3 seconds. Prefer visual transformations that show causality over hard cuts.
- Animate only the change: hold stable diagrams still, move one thing at a time, and cue
  only what matters now.
- Keep the main action around `STAGE_CENTER`, inside the Shorts guide area and clear of the
  caption band. B3 and B6 must use the same animation geometry and timing, with B6 re-skinned.
- End on the Connection Map of this episode's pair only (no earlier episodes on screen) and
  choose a final pose that can flow cleanly into the opening.
- Record or synthesize VO beat by beat with contrast: crisp hook, measured facts, energetic
  mechanism verbs, a lift on the B6 aha and B7 reversal, then a slightly slower kicker. Use
  `NOTE:` for pauses, emphasis and pace; never add those directions to the spoken words.

## Required alignment and symmetry refinement loop

Run this loop after each layout-changing animation pass and again before `vid final`:

1. Group the keyframe and register its intent before `self.play`, for example:
   `with self.alignment_loop("B4 cards") as a: a.even_row(cards, gap=0.30); a.inside_safe(cards)`.
   Use `mirror_pair` for matching objects, `balanced_pair` for unlike objects, `centered` for
   a focal group, and `even_column` for a vertical stack.
2. Use the default 0.04-unit tolerance and safe-area axis / `STAGE_CENTER`, not physical x=0.
   Do not widen tolerance to hide a layout problem.
3. Run `vid align <ep> --no-open`. Inspect the guide render and JSON report at the start,
   middle and end of the beat, both full size and phone size.
4. Correct source positions numerically with the constraint helper, shared spacing constants,
   `VGroup.arrange`, `align_to` or `move_to`; then rerender.
5. Repeat until every registered loop passes, captions are unobstructed, content stays inside
   the safe area and no transition breaks the symmetry it starts or ends on. Give intentional
   asymmetry a named reason; never silently disable the check.

## B1 · Hook
VO:
VIS:
TXT:
NOTE: Enter on the first word; crisp, curious and confident. Stress the surprising contrast.

## B2 · World A
VO:
VIS:
NOTE: Settle into a measured story pace. Give dates and names a small pocket of space.

## B3 · The trick
VO:
VIS:
NOTE: Add momentum. Stress the action verbs and use tiny pauses between mechanism steps.

## B4 · Name the trick
VO:
VIS:
TXT:
NOTE: Slow slightly and separate the key words so the visual badge can land with them.

## B5 · World B
VO:
VIS:
NOTE: Reset the contrast and lift the energy when the new problem appears.

## B6 · Same trick, other world
VO:
VIS: Re-use the B3 animation with world B's colors and labels.
NOTE: Let the recognition sound audible; stress the sameness, then say the technical name cleanly.

## B7 · Payback: B helps A
VO:
VIS:
NOTE: Mark the reversal with a short pause and a warm lift, without changing the words.

## B8 · Today
VO:
VIS:
NOTE: Sound immediate and assured; emphasize why the connection matters now.

## B9 · Kicker + map
VO:
VIS: Connection map: this episode's new link lights up.
NOTE: Ease the pace, balance parallel phrases and land the final tagline cleanly.
