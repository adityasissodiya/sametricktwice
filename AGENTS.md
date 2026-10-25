# Agent manual

You are working in a production line for vertical science Shorts. Each episode takes two
technologies that look unrelated and shows the one trick they share, in 45-60 seconds of
Manim infographic animation with a frozen synthetic narrator. The goal is a Short that people
**watch to the end, understand and share**: on YouTube, money follows engaged views, and only
original work can earn (see RESEARCH.md, "What earns money here").

This file is the contract. `WORKFLOW.md` is the step-by-step walkthrough, `STYLE_GUIDE.md` is
the visual and audio language, and `RESEARCH.md` explains why each rule exists. Episode 001
is the rendered reference for style; Episode 003 is the reference for the current source,
picture and sound gates (its scene passed them all). Copy their principles, never their
subjects.

## How to work: the loop

0. On a fresh clone, run `vid setup` once (README.md, "On a new machine"). Every command
   below needs it.
1. Run `vid status` to see every episode's step, or `vid status <ep>` for one episode's full
   checklist. It prints the next action.
2. Read that step in `WORKFLOW.md` before you start it.
3. Do the step. Then run its gate (each step names the command).
4. Fix what the gate reports and run it again until it passes. Then go back to 1.

Rules for the loop:

- Never skip a step or start one before the gate before it passes.
- Never use `--force`, never loosen a limit in `design.toml`, `ste.toml` or the alignment
  tolerance, and never disable a check to get past a failure. Fix the cause.
- When a check fails, look up the rule in RESEARCH.md first: the reason tells you the fix.
- You cannot watch a video, so read it: `vid frames <ep>` (or `--render` for a preview)
  writes contact sheets at phone size. Open every sheet after every render you judge.
- Report honestly. If a gate fails and you cannot fix it, say which gate and why; never call
  an episode finished while `vid status <ep>` shows an open step.

## Ask the creator first

These need the creator's explicit approval. Propose; do not do.

- Changing the narrator: anything in `voice.toml` (speaker, speed, pauses, model).
- Changing a limit in `design.toml`, `ste.toml` or `series.toml`, or the alignment tolerance.
- Changing VO in a script after the creator approved it.
- Changing the house style (palette, fonts, caption form, the nine-beat format).
- Uploading, publishing, or posting anything outside this folder.
- Deleting or replacing exports, media or caches (keep a copy of an export before you replace
  it when it is the only one).
- Spending money or creating accounts.

Choosing the next pair from `ideas/backlog.md`, researching, drafting, animating and running
the pipeline need no approval.

## Sources of truth

1. `episodes/<ep>/brief.md` owns the facts and their sources (the claim ledger).
2. `episodes/<ep>/script.md` owns every spoken word. Once the creator approves the script, do
   not change VO while animating, aligning, polishing audio or exporting.
3. `STYLE_GUIDE.md` owns the visual, motion, caption, audio and alignment language.
4. `WORKFLOW.md` owns the production steps and their gates.
5. `design.toml`, `ste.toml`, `voice.toml` and `series.toml` own the limits, the narrator and
   the series constants. `RESEARCH.md` explains them.

VIS, TXT and NOTE fields are directions, never spoken words. Never render prompts, VIS notes,
TODOs, production comments or placeholder cards in a final video.

## What every Short must be (the research-backed rules)

`vid check` and `vid qa` enforce these; RESEARCH.md has the evidence for each by name.

- **One goal.** The brief's bridge is one sentence: the one thing the viewer learns.
- **Win the first seconds.** B1 is a specific claim in 15 words or fewer that names both
  worlds; no greeting, no intro, no channel name. The cover is on screen at frame 0, already
  moving, and the first word starts at once. B1 is over by 6 s.
- **Answer fast.** The mechanism (B3) starts within the first 35% of the Short.
- **Small units.** Each beat is one idea: at most 30 words and 3 sentences.
- **Short.** 45-60 seconds.
- **Few words on screen.** TXT at most 4 words, labels at most 5; no on-screen text repeats
  the narration (the captions already say it).
- **Color means one thing.** A blue, B orange, the trick violet, a problem red (`ALERT`),
  everything else neutral.
- **Plain English.** At least 80% of VO sentences pass ASD-STE100 rules; explain every
  technical term at first use without removing the science.
- **Moderate pace.** 130-190 words per minute; clear pauses between sentences.
- **Sourced.** Every beat with VO maps to a claim-ledger row with sources (or a framing row).
- **Titles.** 60 characters or fewer, naming both worlds.

Checks a program cannot make yet (read the contact sheets): one motion path at a time;
animate only what changes and hold stable structure still; cue only what matters now; no
seductive details.

## Automated production acceptance

- Source motion must pass `motion-timing`, `motion-coverage`, `recognition-replay` and
  `causal-motion`: time animations from `b.duration`, keep intentional motion in at least 65%
  of eligible story-beat time, replay B3's mechanism geometry and timing in B6, and show a
  causal change in at least 7 of B1-B8, including both B3 and B6.
- Script direction must pass `delivery-notes`. Rendered pictures must pass `opening-quality`,
  `stage-coverage` and `layout-variety`; rendered sound must pass `sfx-density`,
  `sfx-audibility`, `sfx-masking` and `delivery-pace`.
- A QA report counts only when its episode/video identity matches the master, it is newer than
  that master, and its pipeline fingerprint matches the current QA rules. Regenerate QA after
  any export or QA-rule change; never reuse or edit a stale report.
- Rendered and audio thresholds are calibrated house/reference acceptance proxies. They are
  regression tripwires, not stronger research claims, and passing them never replaces reading
  every contact sheet or the creator's human reviews.

## Required episode shape

- Use the nine beats B1-B9. Keep one idea and one dominant visual per beat. The beats form
  three micro-units: World A and the trick (B1-B4), World B and the recognition (B5-B6),
  payback and map (B7-B9).
- Use the semantic palette from `kit/style.py`.
- Put a compact numbered beat label at the top, the main diagram around `STAGE_CENTER`, and
  captions in the caption band. Essential content stays inside the Shorts safe area.
- Use clean Manim vectors, thick phone-readable strokes and minimal on-screen text. Something
  meaningful changes every 2-3 seconds.
- Build B3 as a reusable mechanism and replay the same geometry and timing in B6 with B's
  material, labels and color. That repeat is the episode's recognition moment.
- Use transformations to show causality. Use hard cuts between micro-units or when the story
  changes time or place. End on the Connection Map of this episode's pair and make the last
  pose flow back into B1.
- Keep captions to three words per chunk; color semantic words consistently.
- The narrator is frozen in `voice.toml`: Kokoro speaker `af_heart`, speed 1.0,
  SHA-256-checked model files. Render without `--voice`. If a name or term sounds wrong, add
  its IPA to `pronounce.toml`; never respell approved VO.
- Sound cues support actions at low gain and never cover narration. No music bed unless the
  creator asks: unnecessary additions cost attention (RESEARCH.md, "Openings").

## No carry-over between episodes

Every episode is made fresh. Viewers meet each Short on its own, so anything left over from
an earlier episode reads as a mistake, and repeated material is what YouTube's "inauthentic
content" rule demonetizes.

- Start every episode with `vid new`. Never copy a `scene.py`, brief, script, publish sheet,
  sound or any other file from another episode's folder, and never paste code from one.
- Write every header, label, pill, date, mnemonic, diagram and on-screen word for this
  episode's facts. Only the text in `series.toml` may repeat (today: "Connection map", the
  "SAME TRICK / TWO WORLDS" sign-off, "×", and the spoken line "Same trick, two worlds.").
- Never show or say an earlier episode's subject: its A/B labels, keywords and glossary are
  off-limits in on-screen text, VO, VIS and TXT, unless this episode's front matter lists them
  because they are truly part of this topic.
- The Connection Map shows this episode's pair only. `end_card(series=True)` draws earlier
  pairs and is for compilations, never for a single Short.
- Shared code and sound live in `kit/`. Play house sounds with `self.sfx("name.wav")` from
  `kit/sfx`; add a new house sound there once, named for what it sounds like. Never copy a
  sound file into an episode, and never save one sound under two names.
- Episode files (scene, brief, script, publish) must not mention another episode's number or
  folder name.
- `vid lint <episode>` checks all of this against every earlier episode, and `vid final`
  refuses to render while it fails.

## Required alignment refinement loop

The composition axis is the center of the usable Shorts area, `SAFE_CENTER[0]` (currently
`-0.4` Manim units), not physical frame x=0. For every layout-changing beat:

1. Build a logical `VGroup` for the composition and identify centered objects, intended
   mirrored pairs, and any row or column that needs equal gaps.
2. Register those constraints with the helpers in `kit/alignment.py` before the group is
   animated, so refinement changes source geometry rather than rendered pixels.
3. Run `vid align <episode> --no-open`. Inspect the JSON report and the contact sheets.
4. Fix positions numerically with shared constants, `arrange`, `align_to`, `move_to` or the
   refinement helper. Re-render and repeat until every unintended error is within tolerance.
5. If asymmetry is intentional, register a named exception with a short visual reason.

The loop is **group → check → refine → render → inspect → repeat**. An episode is not ready
for `vid final` with no registered checks, unresolved alignment failures, clipped safe-area
content or an unexplained exception.

## Commands

Always run through `vid` (in PowerShell `.\vid`, in cmd `vid`). It pins tools, caches,
resolution and export settings to this folder.

| Command | Use it to |
|---|---|
| `vid setup` | a new machine in one go: pinned tools, Python 3.12, packages, voice model, tests |
| `vid status [<ep>]` | see the current step and the next action |
| `vid new <slug>` | start an episode (`004-film-x-explosives`) from the templates |
| `vid check <ep>` | STE score and the design rules (script, brief, scene) |
| `vid lint <ep>` | carry-over check against every earlier episode |
| `vid scene <ep>` | write the animatic `scene.py` (one placeholder per beat) |
| `vid preview <ep> --guides --no-open` | fast 540x960 render with the Shorts UI marked; prints the narration pace |
| `vid frames <ep> [--render]` | contact sheets of every beat, then `vid qa`'s picture rules on that render |
| `vid frames <ep> --render --at S ...` | one frame per given second, for moments the sheets miss |
| `vid align <ep> --no-open` | guide render plus the alignment report |
| `vid audition <ep>` | phonemes and other Kokoro voices for a few beats |
| `vid final <ep>` | all gates, then the 1080x1920 60 fps master and `vid qa` |
| `vid qa <ep>` | measure the export against the research targets |
| `vid report` | channel results next to each episode's measurements |
| `vid test` | the unit tests; run them after any change to `tools/` or `kit/` |
| `vid ci` | `check` and `lint` for every scripted episode |
| `vid doctor` | tool versions, cache locations, free disk space |

A Short is finished only when `vid status <ep>` shows steps 1-7 done, the contact sheets
show nothing from another episode and nothing under the Shorts UI, and the export was watched
by the creator once with sound and once muted at phone size. The creator must also listen to
the whole export sound-only, with the picture hidden, to judge delivery, pauses, cue audibility
and narration masking.

## Repository discipline

- Reuse or extend `kit/` for components that will appear in another episode, and add a test
  in `tests/` for every new check or kit part. Run `vid test` before you hand over.
- Keep research claims out of visuals until they exist in the brief's ledger.
- Use public-domain or properly licensed archival media and record the license in
  `publish.md`. Keep logos out of the art; brand names can appear as plain text.
- Do not install system-wide tools. Use `vid uv ...`; all tools, caches and binaries stay
  inside this folder (`vid setup` puts them there, pinned by SHA-256 in `tools/setup.ps1`).
- Do not overwrite unrelated user changes or delete media/cache files unless asked.
- Commit only when the creator asks. `media/`, `.cache/`, `.tools/` and `.venv/` are never
  committed (`.gitignore`). `exports/` is committed by the creator's choice: finished masters,
  captions, QA reports and channel art travel with the repository. A replaced master keeps
  its copy in `exports/archive/<date>/`.
- There is no CI on GitHub: the creator removed GitHub Actions on purpose. Run `vid test` and
  `vid ci` locally before you push, and do not add workflows without asking.
