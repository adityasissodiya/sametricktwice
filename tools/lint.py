"""Carry-over check: nothing in an episode may come from an earlier episode.

Each episode is compared with every episode before it (lower number). The only shared
things allowed are the series constants in series.toml and what lives in kit/.

    screen  on-screen text in scene.py that repeats an earlier episode's on-screen text
    lines   narration sentences that repeat an earlier episode's narration
    topic   an earlier episode's topic words (a/b/link labels, keywords, glossary) in this
            episode's on-screen text, VO, VIS or TXT, unless this episode declares them too
    ids     this episode's files mention an earlier episode's number or folder name
    audio   sound files copied from an earlier episode or from kit/sfx, or one sound
            saved under two names

Usage: vid lint <ep>   (vid final runs it as a gate)
"""

from __future__ import annotations

import ast
import hashlib
import re
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.scriptfile import Script, load_script  # noqa: E402

EPISODES = ROOT / "episodes"
KIT_SFX = ROOT / "kit" / "sfx"
EPISODE_FILES = ("scene.py", "script.md", "brief.md", "publish.md")
AUDIO = (".wav", ".mp3", ".ogg", ".flac")
SKIP_CALLS = {"alignment_loop", "beat", "sfx", "add_sound", "with_name", "Path", "get", "getenv"}
SKIP_KEYWORDS = {"name", "font", "color", "fill_color", "stroke_color", "weight", "sound"}
NOT_TEXT = re.compile(r"^(#[0-9a-fA-F]{3,8}|B\d+[a-z]?|.+\.(wav|mp3|png|jpg|svg|md|py|toml))$")
COMMON_ZIPF = 5.0  # words this common are not anyone's topic


@dataclass
class Finding:
    kind: str
    message: str


def load_series(path: Path = ROOT / "series.toml") -> dict[str, set[str]]:
    data = tomllib.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    return {key: {fold(x) for x in data.get(key, [])} for key in ("screen", "lines", "words")}


def fold(text: str) -> str:
    return " ".join(text.split()).casefold()


def screen_strings(scene: Path) -> set[str]:
    """String literals in scene.py that can reach the screen.

    Skipped: docstrings, f-string pieces, alignment labels, beat ids, sound and file
    names, colors and font names, and anything without a letter or digit.
    """
    if not scene.exists():
        return set()
    tree = ast.parse(scene.read_text(encoding="utf-8"))
    parent = {child: node for node in ast.walk(tree) for child in ast.iter_child_nodes(node)}
    docstrings = {id(node.body[0].value) for node in ast.walk(tree)
                  if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef)) and node.body
                  and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant)}
    found = set()
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Constant) and isinstance(node.value, str)) or id(node) in docstrings:
            continue
        up, skip = parent.get(node), False
        while up is not None and not skip:
            if isinstance(up, ast.JoinedStr):
                skip = True
            elif isinstance(up, ast.keyword) and up.arg in SKIP_KEYWORDS:
                skip = True
            elif isinstance(up, ast.Call):
                func = up.func.attr if isinstance(up.func, ast.Attribute) else getattr(up.func, "id", "")
                skip = func in SKIP_CALLS
                break
            up = parent.get(up)
        text = " ".join(node.value.split())
        if not skip and text and re.search(r"[^\W_]", text) and not NOT_TEXT.match(text):
            found.add(text)
    return found


def topic_terms(script: Script) -> set[str]:
    terms = set(script.glossary)
    for key in ("a", "b", "link"):
        theme = script.theme(key)
        terms.update([theme.label, *theme.keywords])
    return {fold(t) for t in terms if t.strip()}


def sentences(text: str) -> list[str]:
    return [s for s in (fold(x) for x in re.split(r"(?<=[.!?])\s+", text)) if s]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audio_files(folder: Path) -> list[Path]:
    return sorted(p for p in folder.glob("*") if p.suffix.lower() in AUDIO) if folder.exists() else []


def earlier_episodes(ep: Path) -> list[Path]:
    number = ep.name[:3]
    return [p for p in sorted(EPISODES.glob("[0-9][0-9][0-9]-*")) if p.is_dir() and p.name[:3] < number]


def lint(ep: Path) -> list[Finding]:
    from wordfreq import zipf_frequency

    series = load_series()
    script = load_script(ep / "script.md")
    mine_screen = screen_strings(ep / "scene.py")
    own_terms = topic_terms(script)
    findings: list[Finding] = []

    texts = {f"on-screen '{s}'": s for s in mine_screen}
    for beat in script.beats.values():
        for field in ("vo", "vis", "txt"):
            if getattr(beat, field):
                texts[f"{beat.id} {field.upper()}"] = getattr(beat, field)

    for old in earlier_episodes(ep):
        old_screen = {fold(s) for s in screen_strings(old / "scene.py")}
        for s in sorted(mine_screen):
            if fold(s) in old_screen and fold(s) not in series["screen"]:
                findings.append(Finding("screen", f"'{s}' is on screen in {old.name[:3]} too: write it for this episode"))

        old_script = load_script(old / "script.md")
        old_lines = set(sentences(old_script.narration))
        for s in sentences(script.narration):
            if s in old_lines and s not in series["lines"]:
                findings.append(Finding("lines", f"narration repeats {old.name[:3]}: \"{s}\""))

        for term in sorted(topic_terms(old_script) - own_terms - series["words"]):
            if len(term) < 3 or zipf_frequency(term, "en") >= COMMON_ZIPF:
                continue
            pattern = re.compile(rf"(?<!\w){re.escape(term)}(?!\w)", re.IGNORECASE)
            for where, text in texts.items():
                if pattern.search(text):
                    findings.append(Finding("topic", f"{old.name[:3]}'s topic word '{term}' in {where}"))

        ids = re.compile(rf"(?<![\w-])({re.escape(old.name)}|{old.name[:3]})(?![\w])")
        for name in EPISODE_FILES:
            path = ep / name
            if path.exists():
                for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                    if ids.search(line):
                        findings.append(Finding("ids", f"{name}:{n} mentions episode {old.name[:3]}: {line.strip()[:70]}"))

        old_audio = {sha(p): p for p in audio_files(old / "audio")}
        for p in audio_files(ep / "audio"):
            if sha(p) in old_audio:
                source = old_audio[sha(p)]
                findings.append(Finding("audio", f"audio/{p.name} is a copy of {old.name[:3]}/audio/{source.name}: "
                                                 "use a kit/sfx sound or make a new one"))

    kit = {sha(p): p for p in audio_files(KIT_SFX)}
    seen: dict[str, Path] = {}
    for p in audio_files(ep / "audio"):
        digest = sha(p)
        if digest in kit:
            findings.append(Finding("audio", f"audio/{p.name} is a copy of kit/sfx/{kit[digest].name}: "
                                             f"call self.sfx(\"{kit[digest].name}\") instead"))
        if digest in seen:
            findings.append(Finding("audio", f"audio/{p.name} and audio/{seen[digest].name} are the same sound"))
        seen.setdefault(digest, p)
    return findings


def run(ep: Path) -> bool:
    findings = lint(ep)
    older = ", ".join(p.name[:3] for p in earlier_episodes(ep)) or "none"
    print(f"Carry-over check: {ep.name} (against earlier episodes: {older})\n")
    for f in findings:
        print(f"  x {f.kind:<6} {f.message}")
    print(f"\nResult: {len(findings)} problem(s)  {'PASS' if not findings else 'FAIL'}")
    return not findings


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    sys.exit(0 if run(Path(sys.argv[1]).resolve()) else 1)
