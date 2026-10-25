"""Read an episode's script.md: front matter plus beats (VO / VIS / TXT / NOTE).

The script is the single source of truth for narration. scene.py only refers to
beats by id, so editing a VO line and re-rendering is all it takes to change a line.

    ---
    a: Camera | camera, cameras, lens
    b: Chip | chip, chips, transistor
    link: Light | light, coating
    glossary: asphalt, microscope
    ---
    ## B1 · Hook
    VO: The words that are spoken.
    VIS: What the viewer sees.
    TXT: Big on-screen text (optional).
    NOTE: Non-spoken direction for pace, pauses and emphasis. It never enters narration.
    > Lines that start with ">" are comments.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

_BEAT = re.compile(r"^##\s+(B\d+[a-z]?)\b\s*[·:|\-–—]?\s*(.*)$")
_FIELD = re.compile(r"^(VO|VIS|TXT|NOTE):\s*(.*)$")
WORD = re.compile(r"[\w][\w'’\-]*")


@dataclass
class Beat:
    id: str
    label: str
    line: int
    vo: str = ""
    vis: str = ""
    txt: str = ""
    note: str = ""


@dataclass
class Theme:
    label: str
    keywords: list[str]


@dataclass
class Script:
    path: Path
    meta: dict[str, str]
    beats: dict[str, Beat]

    def theme(self, key: str) -> Theme:
        label, _, words = self.meta.get(key, "").partition("|")
        return Theme(label.strip(), split_list(words))

    @property
    def glossary(self) -> list[str]:
        return split_list(self.meta.get("glossary", ""))

    @property
    def narration(self) -> str:
        return " ".join(b.vo for b in self.beats.values() if b.vo)

    @property
    def word_count(self) -> int:
        return len(WORD.findall(self.narration))


def split_list(text: str) -> list[str]:
    return [w.strip() for w in text.split(",") if w.strip()]


def load_script(path: str | Path) -> Script:
    path = Path(path)
    lines = path.read_text(encoding="utf-8").splitlines()
    meta: dict[str, str] = {}
    start = 0
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                start = i + 1
                break
            key, sep, value = lines[i].partition(":")
            if sep:
                meta[key.strip().lower()] = value.strip()

    beats: dict[str, Beat] = {}
    beat: Beat | None = None
    field: str | None = None
    for n, raw in enumerate(lines[start:], start=start + 1):
        line = raw.strip()
        if line.startswith("#"):
            m = _BEAT.match(line)
            beat = field = None
            if m:
                if m.group(1) in beats:
                    raise ValueError(f"{path.name}:{n}: beat {m.group(1)} appears twice")
                beat = Beat(m.group(1), m.group(2).strip(), n)
                beats[beat.id] = beat
            continue
        if beat is None or line.startswith(">"):
            continue
        if not line:
            field = None
            continue
        m = _FIELD.match(line)
        if m:
            field = m.group(1).lower()
            setattr(beat, field, m.group(2).strip())
        elif field:
            setattr(beat, field, f"{getattr(beat, field)} {line}".strip())
    return Script(path, meta, beats)
