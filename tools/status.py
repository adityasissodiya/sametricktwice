"""Where an episode stands, and the one thing to do next: the agent's walkthrough.

    vid status          every episode on one line: its current step and what to do next
    vid status <ep>     the full checklist for one episode (this runs the checks)

The steps are the steps of WORKFLOW.md. A step counts as done only when its gate passes and
nothing it depends on changed after it: a scene edited after the export means "export again".
"""

from __future__ import annotations

import csv
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import design, lint, qa_contract, ste  # noqa: E402
from tools.scriptfile import load_script  # noqa: E402

EPISODES = ROOT / "episodes"
EXPORTS = ROOT / "exports"
MEDIA = ROOT / "media"
RESULTS = ROOT / "analytics" / "results.csv"


@dataclass
class Step:
    number: int
    name: str
    done: bool | None  # None: not checked in the quick overview
    detail: str
    todo: str


def mtime(path: Path) -> float:
    return path.stat().st_mtime if path.exists() else 0.0


def boxes(text: str) -> tuple[int, int]:
    ticked = len(re.findall(r"^\s*- \[[xX]\]", text, re.M))
    return ticked, ticked + len(re.findall(r"^\s*- \[ \]", text, re.M))


def result_rows(num: str, path: Path = RESULTS) -> int:
    if not path.exists():
        return 0
    with open(path, encoding="utf-8", newline="") as f:
        return sum(1 for row in csv.DictReader(f) if (row.get("episode") or "").strip()[:3] == num)


def ste_score(ep: Path) -> tuple[float, float]:
    cfg = ste.load_config()
    results = ste.check(load_script(ep / "script.md"), cfg)
    clean = sum(1 for r in results if not r.problems)
    return (clean / len(results) if results else 0.0), cfg.target


def steps(ep: Path, full: bool = True) -> list[Step]:
    num = ep.name[:3]
    brief = (ep / "brief.md").read_text(encoding="utf-8") if (ep / "brief.md").exists() else ""
    script = load_script(ep / "script.md")
    scene, report = ep / "scene.py", MEDIA / ep.name / "alignment-report.json"
    video, qa = EXPORTS / f"{ep.name}.mp4", EXPORTS / f"{ep.name}.qa.json"
    plan = design.scene_plan(scene)
    out = []

    rows = [r for r in design.ledger(brief) if re.search(r"https?://", r[2])]
    has_bridge = bool(design.bridge(brief).strip("? "))
    out.append(Step(1, "Brief", has_bridge and bool(rows),
                    f"bridge {'written' if has_bridge else 'missing'}; {len(rows)} ledger rows with sources",
                    f"fill episodes/{ep.name}/brief.md: bridge, claim ledger, myth check, five hooks"))

    beats = list(script.beats.values())
    spoken = [b for b in beats if b.vo]
    missing = [k for k in ("title", "a", "b", "link") if not script.meta.get(k)]
    out.append(Step(2, "Script", bool(beats) and len(spoken) == len(beats) and not missing,
                    f"{len(spoken)}/{len(beats)} beats have VO" + (f"; set {', '.join(missing)}" if missing else ""),
                    f"write every beat of script.md from the ledger, then: vid check {num}"))

    if full and spoken:
        score, target = ste_score(ep)
        failed = [r.rule for r in design.check(ep) if r.status == "fail"]
        out.append(Step(3, "Checks", score >= target and not failed,
                        f"STE {score:.0%} (target {target:.0%}); design rules: "
                        + (f"{', '.join(failed)} failed" if failed else "all pass"),
                        f"fix what `vid check {num}` reports"))
    else:
        out.append(Step(3, "Checks", None if spoken else False, "run vid status <ep> to check",
                        f"fix what `vid check {num}` reports"))

    out.append(Step(4, "Animatic", plan is not None and plan.found,
                    "scene.py exists" if plan else "no scene.py yet",
                    f"vid scene {num}, then vid preview {num} --no-open"))

    if plan is None or not plan.found:
        out.append(Step(5, "Animation", False, "no scene yet", f"vid scene {num}"))
    else:
        left = len(plan.placeholders)
        carried = len(lint.lint(ep)) if full else None
        done = left == 0 and (carried == 0 if full else None)
        detail = f"{left} placeholder beat(s) left" + (f"; vid lint: {carried} problem(s)" if full else "")
        nxt = (f"animate the next placeholder beat in scene.py, then: vid preview {num} --guides --no-open "
               f"and vid lint {num}") if left else f"fix what `vid lint {num}` reports"
        out.append(Step(5, "Animation", done if left == 0 else False, detail, nxt))

    if report.exists():
        data = json.loads(report.read_text(encoding="utf-8"))
        fresh = mtime(report) >= mtime(scene)
        n_loops = len(data.get("reports", []))
        out.append(Step(6, "Alignment", bool(data.get("passed")) and fresh,
                        f"{n_loops} loops, {'all pass' if data.get('passed') else 'failures'}"
                        + ("" if fresh else "; scene.py changed after the last render"),
                        f"vid align {num} --no-open, then fix every FAIL in the report"))
    else:
        out.append(Step(6, "Alignment", False, "no alignment report yet", f"vid align {num} --no-open"))

    if video.exists():
        stale = [p.name for p in (scene, ep / "script.md") if mtime(p) > mtime(video)]
        qa_data = json.loads(qa.read_text(encoding="utf-8")) if qa.exists() else {}
        qa_identity = qa_data.get("episode") == ep.name and qa_data.get("video") == video.name
        qa_fresh = qa_contract.report_is_current(qa_data, episode=ep.name, video=video.name)
        qa_ok = bool(qa_data.get("passed")) and mtime(qa) >= mtime(video) and qa_fresh
        failed = [r["rule"] for r in qa_data.get("results", []) if r.get("status") == "fail"]
        detail = (f"export older than {', '.join(stale)}; " if stale else "") + (
            "vid qa passes" if qa_ok else
            "vid qa: report belongs to another export; rerun it" if qa_data and not qa_identity else
            "vid qa: rules changed; rerun it on this export" if qa_data and not qa_fresh else
            f"vid qa: {', '.join(failed) or 'not run on this export'}")
        todo = f"vid final {num}" if stale or not qa_data else f"fix what `vid qa {num}` reports, then vid final {num}"
        out.append(Step(7, "Final", not stale and qa_ok, detail, todo))
    else:
        out.append(Step(7, "Final", False, "no export yet", f"vid final {num}"))

    pub = (ep / "publish.md").read_text(encoding="utf-8") if (ep / "publish.md").exists() else ""
    ticked, total = boxes(pub)
    out.append(Step(8, "Publish", total > 0 and ticked == total, f"{ticked}/{total} checklist boxes ticked",
                    f"fill publish.md, upload exports/{ep.name}.mp4 with its .srt, and tick each box"))

    n = result_rows(num)
    out.append(Step(9, "Learn", n > 0, f"{n} result row(s) in analytics/results.csv",
                    "after 1, 7 and 28 days, copy YouTube Studio numbers into analytics/results.csv, "
                    "then: vid report"))
    return out


def current(all_steps: list[Step]) -> Step | None:
    return next((s for s in all_steps if s.done is False), None)


def episodes() -> list[Path]:
    return [p for p in sorted(EPISODES.glob("[0-9][0-9][0-9]-*")) if p.is_dir()]


def run(ep: Path | None = None) -> bool:
    if ep is None:
        print(f"{'Episode':<34} {'Step':<13} Next")
        for path in episodes():
            step = current(steps(path, full=False))
            print(f"{path.name:<34} " + (f"{step.number} {step.name:<11} {step.todo}" if step else "done"))
        print("\nFor one episode's full checklist (it runs the checks): vid status <ep>")
        return True
    all_steps = steps(ep)
    print(f"Status: {ep.name}  (steps: WORKFLOW.md)\n")
    for s in all_steps:
        mark = {True: "x", False: " ", None: "?"}[s.done]
        print(f"  [{mark}] {s.number} {s.name:<10} {s.detail}")
    step = current(all_steps)
    print(f"\nNext: {step.todo}" if step else "\nAll steps are done.")
    return True


if __name__ == "__main__":
    run(Path(sys.argv[1]).resolve() if len(sys.argv) == 2 else None)
