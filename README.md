# videoIdea

Vertical infographic explainers built with Manim. Each episode takes two technologies that
look unrelated and shows the trick, chemistry or history they share, and how each one helped
the other. The narration is written in Simplified Technical English (80% ASD-STE100), so
non-native speakers can follow it too.

This repository is also a **manual for an AI agent**: an agent that reads `AGENTS.md` (Claude
Code loads it through `CLAUDE.md`) can take an episode from an idea to an upload-ready video,
one gated step at a time. The rules come from peer-reviewed research on short science
explainers (`RESEARCH.md`), and the pipeline enforces them with tests: a design check on the
script and scene, and a QA pass on the exported video.

| Read | For |
|---|---|
| [AGENTS.md](AGENTS.md) | the contract: the work loop, what needs approval, the rules every Short follows |
| [WORKFLOW.md](WORKFLOW.md) | the walkthrough: ten steps from a pair of ideas to the upload and the numbers after it |
| [STYLE_GUIDE.md](STYLE_GUIDE.md) | the visual, motion, caption, sound and alignment language |
| [RESEARCH.md](RESEARCH.md) | why: each rule, its evidence, its limit, the check that enforces it, and what earns money |

Episode 001 (Camera × Chip) is the rendered style reference. Episode 003 (Atomic-Bomb Project ×
Non-Stick Pans) is the reference for the current gates: its scene passes every source,
picture and sound rule, so read it to see narration-relative timing, the shared B3/B6 clock
and layouts that fill the safe stage. Copy principles, never subjects.

## Quick start

Open a terminal in this folder. In PowerShell type `.\vid`, in cmd just `vid`.

```
vid setup                       a new machine: tools, Python, packages, voice model, tests
vid status                      every episode: its current step and the next action
vid status 002                  one episode's full checklist (runs the checks)
vid new 004-film-x-explosives   start the next episode from the templates
vid check 004                   STE score + research-backed design rules
vid lint 004                    carry-over check against earlier episodes
vid preview 004 --guides        render a 540x960 preview with the Shorts UI marked; prints the pace
vid frames 004 --render         contact sheets of every beat + the picture rules of vid qa
vid frames 004 --render --at 14.5 19   frames at chosen seconds (moments the grid misses)
vid align 004                   symmetry guides and the alignment report
vid final 004                   every gate, the 1080x1920 master, then the export QA
vid qa 004                      measure an export: length, hook, pace, captions, loudness
vid report                      YouTube results next to each episode's measurements
vid test                        unit tests
vid ci                          check + lint for every scripted episode
vid doctor                      tools, versions, where caches live, free disk space
vid                             all commands
```

Always render through `vid`. It sets the vertical resolution and keeps every tool and cache
inside this folder.

## What is where

```
AGENTS.md, CLAUDE.md  agent contract (CLAUDE.md imports AGENTS.md)
WORKFLOW.md           the step-by-step walkthrough and its gates
STYLE_GUIDE.md        Episode 001 house style, visual grammar and the alignment loop
RESEARCH.md           evidence -> rule -> limit -> check; platform economics; open questions
design.toml           limits for the design rules (vid check) and the export QA (vid qa)
ste.toml              STE target (80%) and series-wide glossary
voice.toml            the frozen series narrator: Kokoro af_heart, speed, model checksums
series.toml           the only things episodes may share (vid lint enforces it)
pronounce.toml        how the voice says names (audio only; captions keep the spelling)
ideas/backlog.md      pairs to make, with a scoring rubric and myth traps
templates/            brief.md, script.md, publish.md: copied by `vid new`
episodes/<ep>/        brief.md (facts + sources), script.md (words), scene.py (visuals),
                      publish.md (title, description, upload checklist)
kit/                  Manim toolkit: style, parts, ShortScene, captions, Connection Map,
                      alignment checks, voices; kit/sfx/ holds the house sounds
tools/                vid command, script parser, STE check, design rules, carry-over lint,
                      export QA, contact sheets, status tracker, analytics report
tests/                unit tests for every check and kit part (`vid test`)
brand/                channel art (profile picture, banner, watermark) in the house style:
                      `vid uv run python brand/make.py` writes them to exports/brand/
analytics/            results.csv (YouTube numbers you enter), experiments.md, report.md
exports/              finished videos (.mp4), captions (.srt), QA measurements (.qa.json), the
                      channel art (brand/) and replaced masters (archive/<date>/); in git
media/                Manim renders, voice caches, contact sheets (safe to delete; rebuilt)
```

`media/`, `.cache/`, `.tools/` and `.venv/` are not in git; `exports/` is, so a clone has every
finished master.

## Everything stays in this folder

`vid.cmd` (through `tools/env.cmd`) points every tool at this folder before it runs, wherever
the folder is:

- `.tools/`: portable uv, FFmpeg, SoX and the GitHub CLI, plus Python 3.12 if the PC has none.
  Nothing is installed system-wide, registered or added to the system PATH.
- `.venv/`: Python packages (Manim, manim-voiceover, spaCy, kokoro-onnx), locked in `uv.lock`.
- `.cache/`: uv's download cache, the Kokoro model, temp files and other caches.

`vid doctor` prints each cache location next to `ok` when it is inside this folder. To add a
package, use `vid uv add <package>` so uv keeps using the folder's cache.

## On a new machine

You need Windows 10 or 11 and Git. Then, in cmd (or PowerShell, with `.\vid`):

1. `git clone https://github.com/adityasissodiya/sametricktwice.git` and `cd sametricktwice`.
   The repository is public, so no sign-in is needed to clone it.
2. `vid setup`. In one go it downloads the pinned portable tools (uv 0.12.23, FFmpeg 9.0.2
   essentials, SoX 14.4.2, GitHub CLI 2.102.0) and refuses any archive whose SHA-256 differs
   from `tools/setup.ps1`; puts CPython 3.12 in `.tools/python` if the PC has no Python 3.12;
   installs the locked packages; fetches the narrator model and checks it against
   `voice.toml`; then prints `vid doctor` and runs `vid test`. About 600 MB of downloads, all
   inside the folder. It is safe to run again.
3. `vid status`, and carry on with the next step it names.

The clone brings `exports/` (finished masters, their captions and QA reports, the channel
art). Git does not carry the licensed research PDF behind `RESEARCH.md` (personal use only,
so it is never committed; copy it across yourself if you want it) or `analytics/report.md`
(`vid report` rebuilds it). Everything in `media/` and `.cache/` is rebuilt when needed; run
`vid align <ep> --no-open` once per episode, because alignment reports live in `media/`.
