"""The Learn step: the channel's own results next to each episode's design measurements.

Copy the numbers from YouTube Studio into analytics/results.csv: one row per episode per
reading, taken 1, 7 and 28 days after upload. `vid report` joins the latest reading of each
episode with its measurements from exports/<ep>.qa.json (written by `vid qa`) and with its
script, prints the table and writes analytics/report.md. Use it to test the open questions
in RESEARCH.md ("Open questions to test on this channel") on this channel's viewers.

Usage: vid report
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.scriptfile import WORD, load_script  # noqa: E402

EPISODES = ROOT / "episodes"
EXPORTS = ROOT / "exports"
ANALYTICS = ROOT / "analytics"
RESULTS = ANALYTICS / "results.csv"
FIELDS = ["episode", "date", "days_live", "views", "engaged_views", "stayed_pct", "avg_view_s",
          "avg_pct_viewed", "likes", "comments", "shares", "subs_gained", "notes"]
COLUMNS = [  # (heading, where the value comes from)
    ("Episode", "episode"), ("Length s", "duration_s"), ("Hook ends s", "hook_end_s"),
    ("Answer at", "answer_share"), ("Words/min", "wpm"), ("Pause s", "sentence_pause_s"),
    ("Title chars", "title_chars"), ("Days", "days_live"), ("Views", "views"),
    ("Engaged", "engaged_views"), ("Stayed %", "stayed_pct"), ("Avg view s", "avg_view_s"),
    ("Viewed %", "avg_pct_viewed"), ("Subs", "subs_gained"), ("Shares", "shares"),
]


def number(text: str | None) -> float:
    try:
        return float(str(text).replace(",", "").replace("%", "").strip())
    except ValueError:
        return -1.0


def latest_results(path: Path = RESULTS) -> dict[str, dict]:
    """The reading with the most days live, per episode number."""
    if not path.exists():
        return {}
    best: dict[str, dict] = {}
    with open(path, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            num = (row.get("episode") or "").strip()[:3]
            if num and (num not in best or number(row.get("days_live")) >= number(best[num].get("days_live"))):
                best[num] = row
    return best


def measurements(ep: Path) -> dict:
    qa = EXPORTS / f"{ep.name}.qa.json"
    m = json.loads(qa.read_text(encoding="utf-8")).get("metrics", {}) if qa.exists() else {}
    script = load_script(ep / "script.md")
    m["title_chars"] = len(script.meta.get("title", "")) or None
    b1 = script.beats.get("B1")
    m["hook_words"] = len(WORD.findall(b1.vo)) if b1 and b1.vo else None
    return m


def cell(value, key: str = "") -> str:
    if value is None or value == "":
        return "-"
    if isinstance(value, float):
        return f"{value:.0%}" if key == "answer_share" else f"{value:.2f}".rstrip("0").rstrip(".")
    return str(value)


def table(episodes: list[Path], results: dict[str, dict]) -> str:
    lines = ["| " + " | ".join(h for h, _ in COLUMNS) + " |", "|" + "---|" * len(COLUMNS)]
    for ep in episodes:
        values = {**measurements(ep), **results.get(ep.name[:3], {}), "episode": ep.name}
        lines.append("| " + " | ".join(cell(values.get(key), key) for _, key in COLUMNS) + " |")
    return "\n".join(lines)


def run() -> bool:
    episodes = [p for p in sorted(EPISODES.glob("[0-9][0-9][0-9]-*")) if p.is_dir()]
    results = latest_results()
    text = table(episodes, results)
    ANALYTICS.mkdir(exist_ok=True)
    (ANALYTICS / "report.md").write_text(
        "# Channel report\n\nMade by `vid report` from analytics/results.csv and exports/*.qa.json. "
        "Do not edit; edit the CSV.\n\n" + text + "\n", encoding="utf-8")
    print(text)
    if not results:
        print("\nNo results yet. After an upload, add rows to analytics/results.csv (columns: "
              + ", ".join(FIELDS) + ").")
    print("\nWritten: analytics/report.md. Compare episodes that differ in one design choice only; "
          "log what you learn in analytics/experiments.md.")
    return True


if __name__ == "__main__":
    run()
