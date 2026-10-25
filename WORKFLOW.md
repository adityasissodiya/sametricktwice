# Workflow: from idea to upload

How one episode goes from an idea to an upload, one step at a time. `vid status <ep>` shows
which step an episode is on and prints the next action. Each step below says what to make,
which command checks it (its gate), and when it is done. Do the steps in order; the reasons
behind the rules are in RESEARCH.md.

## The format

**Promise:** two things you use every day, one hidden link. Each Short shows how two
technologies that look unrelated share a trick, a chemistry or a history, and how each helped
the other.

- **Length:** 45-60 s, about 150-170 written words. Shorts can run 3 minutes, but shorter
  videos hold attention better, and one tight idea fits in 60 seconds. The frozen voice
  needs that many words to land in `vid qa`'s delivery band (references: 001 has 160 words at
  163 words/min, 002 has 159 at 177, 003 has 136 at 147, below the band).
- **One goal:** the viewer leaves with one sentence: the bridge from the brief.
- **Frame:** vertical 1080x1920, 60 fps, dark background, clean vector infographic animation
  in Manim. Episode 001 and `STYLE_GUIDE.md` define the house style.
- **Color means something, always:** world A is blue, world B is orange, the shared trick is
  violet, a problem is red. Captions color the same words the same way.
- **Signature moves:** the trick animation plays twice, once in each world (B3, then B6
  re-skinned). Every episode ends on the **Connection Map** of its own pair.
- **Every episode is made fresh:** earlier episodes show the style, never the content. Only
  `series.toml` may repeat; `vid lint` checks it.
- **Composition:** a numbered beat label at the top, one readable diagram in the safe-area
  center, kinetic captions of at most three words near the bottom.
- **Language:** narration reaches 80% ASD-STE100 (Simplified Technical English). The other
  20% is the creative budget: spend it on the hook and the kicker.
- **Series name:** working name *Same Trick Twice*: the GitHub repository and the channel art
  in `brand/` use it. The tagline is already in the pilot: "Same trick, two worlds."

## The nine beats

The beats form three micro-units with a hard cut between them: World A and its trick
(B1-B4), World B and the recognition (B5-B6), the payback and the map (B7-B9).

| Beat | Job | About | Rules that apply |
|---|---|---|---|
| B1 Hook | a specific, surprising claim that names both worlds; the frame is already moving | 0-5 s | `hook-length`, `hook-relevance`, `cold-open`, `hook-time` |
| B2 World A | one moment in history, with concrete details | 5-13 s | |
| B3 The trick | animate the mechanism: this answers the hook | 13-20 s | `early-answer` |
| B4 Name it | three words that become an on-screen badge | 20-23 s | `minimal-text` |
| B5 World B | the problem the other world had | 23-29 s | |
| B6 Same trick | replay B3 in B's colors: the "aha" | 29-37 s | |
| B7 Payback | how B helped A back | 37-45 s | |
| B8 Today | why it matters now | 45-49 s | |
| B9 Kicker + map | a short twist, then the map; the last pose flows back to B1 | 49-58 s | |

Every beat: one idea, at most 30 words and 3 sentences (`micro-units`).

## The steps

| # | Step | You make | Gate | Done when |
|---|---|---|---|---|
| 0 | Pick | a pair from `ideas/backlog.md` | the score | 18/25 or more |
| 1 | Brief | `brief.md`: bridge, claim ledger, myth check, hooks | `vid status <ep>` | the bridge is written and the ledger has sourced rows |
| 2 | Script | `script.md`: nine beats and the front matter | `vid status <ep>` | every beat has VO; `title`, `a`, `b`, `link` are set |
| 3 | Checks | fixes to the script and brief | `vid check <ep>` | STE 80% or more and every design rule passes |
| 4 | Animatic | `scene.py` with placeholder cards | `vid preview <ep> --no-open` | it plays well with cards only |
| 5 | Animation | `scene.py`, one beat at a time | `vid lint <ep>`, `vid frames <ep> --render` | no placeholders, nothing carried over |
| 6 | Alignment | geometry fixes | `vid align <ep> --no-open` | every registered loop passes |
| 7 | Final | `exports/<ep>.mp4`, `.srt`, `.qa.json` | `vid final <ep>` (it runs `vid qa`) | every gate passes |
| 8 | Publish | `publish.md`, the upload | the checklist | every box is ticked |
| 9 | Learn | rows in `analytics/results.csv` | `vid report` | readings at 1, 7 and 28 days |

## Step by step

### 0. Pick

Score each pair in `ideas/backlog.md` from 1 to 5 on five things: **Surprise** (do they
look unrelated?), **Proof** (is the link documented and causal?), **Two-way** (did each one
help the other?), **Picture** (can the trick be animated in about 7 seconds?) and
**Everyday** (does the viewer own or use one of them?). Make it if the total is 18 or more.
Then: `vid new 004-<a>-x-<b>` (three digits, lowercase words).

### 1. Brief (the research)

- Find the bridge: the one trick or material both worlds use. Write it as **one sentence of
  at most 30 words**: it is the episode's single learning goal (`one-goal`).
- Fill the claim ledger. Every fact that will be spoken or shown needs two independent
  sources, or one primary source (a patent, a paper, a museum that holds the object). End each
  claim with the beats that say it, for example `(B2)`; a beat that states no new fact (such
  as B4's three-word name) gets a framing row `F#` (`sourced`).
- Do the myth check. Look for the popular version of the story, compare it with the sources,
  then soften the words ("one of the first", "around") or cut the claim.
- Write five hooks and keep one (see step 2). Keep the spare facts: they are the next
  episodes, and keeping them out of this one avoids seductive details.
- An agent can find sources and draft the ledger, but it must open and verify every link.

Gate: `vid status <ep>` shows step 1 done.

### 2. Script

- Copy the facts from the ledger, one or two sentences per beat. Say each line out loud.
- **The hook (B1)** is a precise information gap, not a teaser: a specific claim with a
  number, a date or an everyday object, naming both worlds, in 15 words or fewer. "Every tap
  on your phone uses an idea from a 1965 radar lab." The video must answer it by B3. Never
  open with a greeting, the channel name or "in this video".
- Put the words for A, B and the trick in the front matter (`a:`, `b:`, `link:`), so the
  captions color them and the checks know the worlds. Put technical names in `glossary:`.
- Set `title:` to the upload title: at most 60 characters, naming both worlds. It must be
  something the video pays off.
- Write `NOTE:` lines for delivery (pace, pauses, emphasis). They are never spoken.
- Budget about 150-170 written words. `vid qa` measures pace as written words per minute of
  narration (`delivery-pace`, 155-185), but the voice reads an acronym letter by letter and a
  year as three words: 003's five "PTFE"s and two dates count as 7 words and take 26 to say,
  which put it at 147 words/min. Give those lines extra words, or use fewer acronyms.

Gate: `vid status <ep>` shows step 2 done. Then ask the creator to approve the VO: after
approval it is locked. The first preview (step 4) prints the measured pace; settle it there,
while the VO can still change cheaply.

### 3. Checks

Run `vid check <ep>`. It prints the STE report (section "Writing to 80% STE" below) and then
the design rules. Fix the script or brief until both pass. Typical fixes:

| Rule fails | Fix |
|---|---|
| `hook-length`, `hook-relevance` | cut B1 to the claim; name both worlds |
| `early-answer` | shorten B1-B2 so B3 starts in the first 35% |
| `micro-units`, `length` | cut a beat's second sentence before you cut a beat |
| `minimal-text` | TXT is keywords, never a sentence from the VO |
| `title` | shorter; both worlds in it |
| `sourced` | add the missing beat to a ledger row, with a source link |
| `delivery-notes` | add non-spoken intent for pace, pause, emphasis or turn to every spoken beat; NOTE does not drive synthesis |
| `motion-timing` | derive every animation duration from `b.duration`, keep it inside the beat, and use `self.hold(b)` only for the unused narration tail |
| `motion-coverage` | make intentional change occupy at least 65% of eligible story-beat time; sequence meaningful transformations instead of padding with idle holds |
| `recognition-replay` | build the mechanism geometry and timing in B3, then replay that same path in B6 with only B's material, labels and semantic color changed |
| `causal-motion` | show cause becoming effect in at least 7 of B1-B8 and always in B3 and B6; replace decorative entrances or static swaps with transformations that explain what changed |

Gate: `vid check <ep>` passes.

### 4. Animatic

`vid scene <ep>` writes `scene.py` with one placeholder card per beat, and
`vid preview <ep> --no-open` renders it with the series voice and captions, then prints the
narration pace against `vid qa`'s delivery band. Then `vid frames <ep> --render` and read the
sheets. If it is boring with cards only, or the pace is outside the band, fix the script now
(with the creator's approval); animation will not save it.

### 5. Animation

The source gates require beat-relative timing from `b.duration`, scheduled intentional motion
through at least 65% of every narrated beat, causal change in at least 7 of B1-B8 including B3 and B6,
and the same mechanism geometry and timing in B3/B6. Plan these constraints before polishing;
decorative entrances and static swaps do not count as causal motion.

Replace one placeholder at a time, in order. For each beat:

1. Read the beat's VIS line and the brief's "Infographic direction".
2. Build it with kit parts (`kit/parts.py`, `ShortScene`) and fresh drawings for this
   episode. Inside a beat, `b.duration` is the narration time; time every animation as a
   fraction of it and end with `self.hold(b)`.
3. **Animate only the change.** Draw the stable diagram, hold it still while the narration
   points at it, and move only the part that changes. One motion path at a time.
4. **Cue only what matters now.** One highlight per moment; color only in its semantic family.
5. Register alignment constraints before `self.play` (step 6 explains the loop).
6. `vid preview <ep> --guides --no-open`, then `vid frames <ep> --render`, and read the
   sheets: legible at phone size, nothing under the red Shorts UI areas, one focal idea per
   frame. The sheets show each beat's start, middle and end only; `vid frames <ep> --render
   --at 14.5 19 33` grabs the moments in between (a transfer, a bounce, a reveal).
7. `vid lint <ep>`: no on-screen text, narration, topic, sound or file from an earlier episode.

Build the trick (B3) as a method with parameters (colors, labels, material), so B6 is one call
with world B's skin. When a piece will be useful again, move it into `kit/` and add a test.
Use `self.clear_stage()` to empty the stage (`self.clear()` also removes the captions). Never
edit `script.md` during the visual pass: time the animation to the approved words.

What made Episode 003's scene pass every source, picture and sound rule on its first final
render (its one failure, `delivery-pace`, came from the word count; see step 2):

- **The shared clock fits the shorter beat.** B6 replays B3 in the same seconds, and B6's line
  is usually shorter. Set `self.trick_time = min(CAP, share * b.duration)` once in B3, with
  CAP in seconds just under B6's narration (003: B6 speaks 4.7 s, CAP is 4.2 s), and spend
  B3's remaining time on world A's setup before the trick.
- **Fill the stage, vertically too.** `vid frames --render` prints `vid qa`'s picture rules for
  the render it sheets; fix any failure on the preview, not after the final. Compositions that
  pass use one large diagram per beat that spans at least 60% of the stage height (tall
  stacks: label, object, verdict) and filled shapes rather than thin outlines only.
- **Sound: one cue per meaningful action.** `vid qa` wants at least 9 cues (1.5 per 10 s),
  enough of them audible, none masking a word. House sounds at about -10 to -16 dB pass; 003
  uses 15. A cue inside the shared trick plays in B3 and B6 alike, so the replay sounds the
  same too.
- **B9 icons of the same shape.** `end_card` scales each icon by its longer side, so a wide
  icon next to a square one comes out small and its label sits higher. Give both worlds the
  same frame (003 sets its pan on a plate the size of its pipe flange); the cover can reuse
  them, so the last pose flows back into the first.

Gate: `vid status <ep>` shows step 5 done (no placeholders, `vid lint` clean).

### 6. Alignment

The visual center is `SAFE_CENTER[0]` (currently `-0.4`), not frame x=0, because the Shorts
controls cover the right edge.

1. Group each composition in a `VGroup` and declare its intent with the helpers described in
   `STYLE_GUIDE.md` (`centered`, `mirror_pair`, `balanced_pair`, `even_row`, `even_column`,
   `inside_safe`).
2. `vid align <ep> --no-open` renders the guides and writes the alignment report.
3. Correct the source geometry, not the pixels; render again; repeat until the report passes.
4. Give intentional asymmetry a named reason. Never widen the tolerance.

Gate: `vid align <ep> --no-open` passes.

### 7. Final

`vid final <ep>` runs every gate in order: STE, the design rules (now placeholders fail),
carry-over, then a strict alignment render at 1080x1920, 60 fps. It polishes the voice,
normalizes loudness to -14 LUFS, writes `exports/<ep>.mp4` with `exports/<ep>.srt`, and then
measures the export with `vid qa`. Then `vid frames <ep>` and read every sheet once more.

If `vid qa` fails:

| Check fails | Fix |
|---|---|
| `length` | trim holds and stage transitions first; then cut words (needs re-approval) |
| `cold-open` | put the cover on screen at frame 0, already moving; nothing before B1 |
| `hook-time`, `early-answer` | shorten B1-B2 (needs re-approval of the VO) |
| `speech-rate`, `pauses` | fewer words per beat; the voice itself needs the creator |
| `captions` | the scene must speak every beat; re-render after any VO change |
| `dead-air` | shorten `clear_stage` gaps; give long holds a small meaningful change |
| `loudness`, `format` | render only through `vid final`; lower loud sound cues |
| `opening-quality` | make the frame-zero cover legible and keep meaningful motion alive through the full first second |
| `stage-coverage` | resize and place the dominant diagram so it deliberately uses the safe stage; remove accidental empty acreage without entering UI zones |
| `layout-variety` | change hierarchy or spatial composition between beats; do not reuse one pose with cosmetic relabeling |
| `sfx-density` | add cues only to meaningful actions, but cover enough of those actions to support the story; do not add filler or a music bed |
| `sfx-audibility` | raise or retime a quiet cue only enough to register at phone playback while keeping it subordinate to narration |
| `sfx-masking` | shorten, lower or move a cue away from consonants and other narration it masks |
| `delivery-pace` | do the sound-only review; if the aggregate pace really needs a script or frozen-voice change, stop for creator approval rather than pretending NOTE changes synthesis |
| QA report fingerprint/freshness | rerun `vid qa <ep>` on the named master after rule changes; rerender first after source/render changes, and never copy or edit a report |

The rendered visual/audio limits above are calibrated house/reference acceptance proxies, not
new research thresholds. After they pass, the creator must still perform three distinct
phone-size reviews: watch with sound, watch muted, and listen to the complete export sound-only
with the picture hidden. In the sound-only pass, verify the delivery follows each `NOTE:`, pauses
and emphasis land, action cues are audible and meaningful, and no cue masks a word. Record the
human review honestly; no automated result substitutes for it.

Gate: `vid final <ep>` ends with "Done".

### 8. Publish

Fill `publish.md` and tick each box as it is done:

- **Title:** at most 60 characters, naming both worlds; the video must pay it off.
- **Description:** the bridge in one simple sentence, then every source from the ledger.
- **Captions:** upload `exports/<ep>.srt`, so YouTube can offer translated subtitles.
- **Cover:** `media/<ep>/frames/cover.png` (from `vid frames`) shows the B1 frame; pick that
  frame in the app.
- **Pinned comment:** ask which two things to connect next.
- The creator watches the export once with sound and once muted at phone size, and does the
  upload. An agent never uploads.

### 9. Learn

At 1, 7 and 28 days after upload, copy these numbers from YouTube Studio into
`analytics/results.csv` (one row per reading): views, engaged views, stayed to watch (viewed
vs swiped away, %), average view duration, average percentage viewed, likes, comments,
shares, subscribers gained. Then `vid report` puts them next to each episode's measurements
(length, hook time, answer time, pace, title length).

Change one thing at a time and log each test in `analytics/experiments.md` (RESEARCH.md
lists the open questions). Add pairs from the comments to the backlog.

## Writing to 80% STE

ASD-STE100 is a controlled English made for aircraft manuals, so people who read English as a
second language understand them. The same rules make narration easy to follow by ear, and
they give YouTube's auto-translated captions clean input.

`vid check` tests the rules a program can check, on each VO sentence. A sentence is clean
when it breaks none of them. The score is clean sentences divided by all sentences, and the
target (in `ste.toml`) is 80%.

| Rule | Instead of | Write |
|---|---|---|
| active voice | The plate was coated by Niépce. | Niépce coated the plate. |
| simple tenses | He has made... / They are making... | He made... / They make... |
| -ing only in names | Using a lens, he... | He used a lens to... |
| one-word verbs | washed away, set up, find out | removed, installed, learned |
| no contractions | don't, it's, can't | do not, it is, cannot |
| can / must / will | should, would, might, may | must, will, can |
| 3 nouns at most | the engine oil pressure indicator light | the light that shows oil pressure |
| common words | ubiquitous, utilize, approximately | everywhere, use, about |
| full sentences | Same trick, two worlds. | (allowed only in your 20%) |
| 25 words at most | one long sentence with "and... and..." | two sentences |

Three things only a human can check:

- **One word, one meaning.** Use one name per thing in the whole script (do not switch between
  "coating", "layer" and "resist").
- **Metaphors and idioms** ("gave cameras new eyes") belong in the hook and kicker only.
- **The glossary is for technical names** (photolithography, transistor), not for hard words
  that have a simple alternative. Explain each technical name the first time it is said.

The vocabulary check uses word frequency as a stand-in for STE's dictionary of about 900
approved words. For the real list, request the free specification at asd-ste100.org, put the
approved words in `ste/approved-words.txt`, and set `vocabulary = "approved-list"` in
`ste.toml`.

## Making it worth watching

Each rule names the check that enforces it, or says "read the sheets" when only a person can.

1. **The first frame is the cover, already moving** (`cold-open`). Never fade in from black.
2. **The hook is a specific claim, not a greeting** (`hook-length`, `hook-relevance`). Name
   both worlds; a number or a date makes the gap precise.
3. **Answer fast** (`early-answer`). The mechanism starts within the first third.
4. **Something meaningful changes every 2-3 seconds** (`dead-air`), but only what matters:
   one motion path at a time, and stable structure holds still (read the sheets).
5. **One idea per Short, one idea per beat** (`one-goal`, `micro-units`). If the trick cannot
   be animated in about 7 seconds, the pair is too big. Split it.
6. **Show, then say.** Transform one thing into another instead of cutting inside a unit.
   Keep on-screen text to keywords (`minimal-text`).
7. **Same animation, twice.** When B6 replays B3 in the other world's colors, the viewer sees
   the link before you say it. That moment is the episode.
8. **Concrete details make it real**: lavender oil, an upside-down microscope, a 1965 radar
   lab. Fun facts that do not serve the bridge go to "Spare facts".
9. **End clean.** Show the map, say a short last line, and let the last frame flow back into
   the first so the loop replays well.
10. **Balance the safe area** (`vid align`). Center primary diagrams on the safe-area axis.

Do not copy another creator's characters, logos, music or branding.

## Ground rules

- **Facts:** nothing reaches the script without the claim ledger. Put the sources in every
  description.
- **Images:** public domain or CC only, with the license noted in `publish.md`. Show brand
  names as text, not logos.
- **Music:** none by default. If the creator wants a bed, use the YouTube Audio Library or a
  licensed track, credited in the description.
- **AI:** an agent may research, draft and code; the creator checks every fact and owns the
  final words. YouTube's "inauthentic content" rule (July 2025) demonetizes mass-produced,
  template-only videos. What keeps the channel safe is original research, new visuals and the
  creator's direction for every episode. If an AI voice sounds like a real person (a clone of
  the creator's own voice included), tick YouTube's "altered or synthetic content" box.

## A sustainable week

Batch by step, not by episode: switching between research, writing and animation is what eats
the time. Start with one episode a week until the kit has the common parts, then:

| Day | Block | Output |
|---|---|---|
| Mon | research, 3-4 h | 3 briefs |
| Tue | writing, 2-3 h | 3 scripts passing `vid check` + 3 animatics |
| Wed-Thu | animation, 2 x 4 h | 3 scenes |
| Fri | final + publish, 2-3 h | 3 Shorts scheduled; 20 min of `vid report` review |

## Prompts that work for an agent

- "Run `vid status` and do the next step for 004. Stop when its gate passes."
- "Find primary sources for these claims and fill the claim ledger in 004's brief."
- "Rewrite B5 of 004 so it passes `vid check` without changing the facts."
- "Animate B3 of 004 from its VIS line in the house style, then run the alignment loop and
  read the contact sheets."
- "Read 004's brief and look for myths or overclaims."
- "Run `vid report` and tell me which design choice differs between our best and worst Short."
