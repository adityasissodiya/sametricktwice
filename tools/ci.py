"""The text and logic gates for every scripted episode (`vid ci`).

Every episode whose script is written (step 2 of `vid status`) must pass `vid check` (STE and
the design rules) and `vid lint` (carry-over). Episodes still in research are skipped. Nothing
is rendered here; `vid final` and `vid qa` render and measure the export.

Usage: python tools/ci.py   (exit 1 if any episode fails)
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import design, lint, status, ste  # noqa: E402


def main() -> int:
    failed = []
    for ep in status.episodes():
        script_step = status.steps(ep, full=False)[1]
        if not script_step.done:
            print(f"skip {ep.name}: the script is not written yet ({script_step.detail})\n")
            continue
        ok = ste.run(ep / "script.md")
        print()
        ok = design.run(ep) and ok
        print()
        ok = lint.run(ep) and ok
        print("\n" + "-" * 72 + "\n")
        if not ok:
            failed.append(ep.name)
    print("CI: " + ("PASS" if not failed else "FAIL in " + ", ".join(failed)))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
