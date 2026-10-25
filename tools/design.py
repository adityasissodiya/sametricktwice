"""Research-backed design rules for one episode: the second half of `vid check`.

Each rule turns a finding from RESEARCH.md into a test of the episode's files, before
anything is rendered. Look a rule up in RESEARCH.md by its name; its limits live in
design.toml [check]. `vid qa` measures the same ideas again on the exported video.

    one-goal        the brief's bridge is one sentence: one thing to learn per Short
    hook-length     B1 is short, so the hook lands in the first seconds
    hook-relevance  B1 names both worlds, so the viewer knows at once what this is about
    cold-open       no greeting or channel intro, and nothing plays before B1 starts
    early-answer    the mechanism beat comes early: the hook's question is answered fast
    micro-units     every beat is a small unit: few words, few sentences
    delivery-notes  every spoken beat records its intended pace, pause or emphasis
    length          the narration fits the 45-60 s target
    minimal-text    few on-screen words, and none repeats the narration word for word
    title           the title is short and names both worlds
    sourced         every beat with VO is backed by a row of the brief's claim ledger
    color-signals   only the A, B and link color families, plus neutrals
    every-beat      scene.py speaks every beat once, in script order; no placeholder in a final
    motion-timing   animation time follows narration time instead of fixed seconds
    motion-coverage each beat spends most of its narration on meaningful visual change
    recognition-replay B3 and B6 use one mechanism helper with one shared phase clock
    causal-motion   story beats use geometry/state changes, not only generic effects

Usage: vid check <ep>   (vid final runs it with placeholders not allowed)
"""

from __future__ import annotations

import ast
import colorsys
import re
import sys
import tomllib
from dataclasses import dataclass, field, fields
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import ste, visual_quality  # noqa: E402
from tools.lint import screen_strings  # noqa: E402
from tools.scriptfile import WORD, Script, load_script  # noqa: E402

STYLE = ROOT / "kit" / "style.py"
SEMANTIC = ("A_COLOR", "B_COLOR", "LINK_COLOR", "ALERT")
NAMED_COLOR = re.compile(r"^(PURE_)?(RED|GREEN|YELLOW|BLUE|ORANGE|PURPLE|PINK|TEAL|GOLD|MAROON"
                         r"|LIGHT_PINK|LIGHT_BROWN|DARK_BROWN|DARK_BLUE)(_[A-E])?$")
HEX = re.compile(r"#(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b")
_ABBREVIATION = re.compile(r"(?:\b[A-Za-z]\.){2,}$|\b(?:Mr|Mrs|Ms|Dr|St|Jr|Sr|vs|etc|c|ca)\.$")
_LEDGER_ROW = re.compile(r"^\|\s*([A-Z]\d+)\s*\|(.*)$")


@dataclass
class Limits:
    bridge_max_words: int = 30
    hook_max_words: int = 15
    mechanism_beat: str = "B3"
    answer_by: float = 0.35
    beat_max_words: int = 30
    beat_max_sentences: int = 3
    txt_max_words: int = 4
    screen_max_words: int = 5
    echo_words: int = 4
    title_max_chars: int = 60
    intro_phrases: list[str] = field(default_factory=list)
    hue_tolerance: float = 25
    neutral_saturation: float = 0.30
    neutral_value: float = 0.25
    motion_min_share: float = 0.65
    causal_min_beats: int = 7


@dataclass
class Result:
    rule: str
    status: str  # "pass", "fail" or "skip"
    detail: str
    issues: list[str] = field(default_factory=list)


@dataclass
class Plan:
    """What scene.py's Episode class does, read from its source."""
    found: bool
    beats: list[str]
    placeholders: list[int]
    before_first_beat: list[str]


@dataclass
class MethodTiming:
    """Static timing summary for one ``Episode`` helper method."""

    node: ast.FunctionDef
    has_play: bool
    timing_params: set[str]
    split_params: set[str]
    fixed_lines: list[int]
    missing_lines: list[int]


def load_section(cls, section: str, path: Path = ROOT / "design.toml"):
    data = tomllib.loads(path.read_text(encoding="utf-8")).get(section, {}) if path.exists() else {}
    names = {f.name for f in fields(cls)}
    return cls(**{k: v for k, v in data.items() if k in names})


def result(rule: str, issues: list[str], detail: str) -> Result:
    return Result(rule, "fail" if issues else "pass", detail, issues)


def sentences(text: str) -> list[str]:
    """Split narration into sentences. 'U.S.' or 'c.' inside a sentence does not end it."""
    out, start, end = [], 0, len(text.rstrip())
    for m in re.finditer(r"[.!?]+(?=\s|$)", text):
        piece = text[start:m.end()]
        if m.end() < end and _ABBREVIATION.search(piece):
            continue
        out.append(piece.strip())
        start = m.end()
    out.append(text[start:].strip())
    return [s for s in out if WORD.search(s)]


def words(text: str) -> list[str]:
    return [w.casefold() for w in WORD.findall(text)]


def theme_words(script: Script, key: str) -> list[str]:
    theme = script.theme(key)
    return [w for w in [theme.label, *theme.keywords] if w]


def named(text: str, terms: list[str]) -> list[str]:
    """The terms that occur in text as whole words, ignoring case."""
    return [t for t in terms if re.search(rf"(?<!\w){re.escape(t)}(?!\w)", text, re.IGNORECASE)]


def bridge(brief_text: str) -> str:
    m = re.search(r"^\*\*The bridge[^*]*\*\*(.*?)(?=^\s*$|^\*\*|\Z)", brief_text, re.M | re.S)
    return " ".join(m.group(1).split()) if m else ""


def ledger(brief_text: str) -> list[tuple[str, str, str]]:
    """Claim-ledger rows as (id, claim, sources)."""
    rows = []
    for line in brief_text.splitlines():
        m = _LEDGER_ROW.match(line.strip())
        if m:
            cells = [c.strip() for c in m.group(2).split("|")]
            rows.append((m.group(1), cells[0], " | ".join(cells[1:])))
    return rows


def beat_refs(claim: str) -> set[str]:
    refs = set(re.findall(r"\bB\d+\b", claim))
    for m in re.finditer(r"\bB(\d+)\s*[-–]\s*B?(\d+)\b", claim):
        refs.update(f"B{i}" for i in range(int(m.group(1)), int(m.group(2)) + 1))
    return refs


def hsv(color: str) -> tuple[float, float, float]:
    h = color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    hue, sat, val = colorsys.rgb_to_hsv(r, g, b)
    return hue * 360, sat, val


def semantic_hues(style: Path = STYLE) -> dict[str, float]:
    text = style.read_text(encoding="utf-8")
    hues = {}
    for name in SEMANTIC:
        m = re.search(rf'^{name}\s*=\s*"(#[0-9A-Fa-f]{{6}})"', text, re.M)
        if m:
            hues[name] = hsv(m.group(1))[0]
    return hues


def scene_plan(scene: Path, cls: str = "Episode") -> Plan | None:
    if not scene.exists():
        return None
    tree = ast.parse(scene.read_text(encoding="utf-8"))
    klass = next((n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == cls), None)
    if klass is None:
        return Plan(False, [], [], [])

    def self_calls(node: ast.AST, *names: str) -> list[ast.Call]:
        return sorted((n for n in ast.walk(node) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                       and isinstance(n.func.value, ast.Name) and n.func.value.id == "self"
                       and n.func.attr in names), key=lambda n: (n.lineno, n.col_offset))

    beats = [c.args[0].value for c in self_calls(klass, "beat")
             if c.args and isinstance(c.args[0], ast.Constant) and isinstance(c.args[0].value, str)]
    placeholders = [c.lineno for c in self_calls(klass, "placeholder")]
    construct = next((n for n in klass.body if isinstance(n, ast.FunctionDef) and n.name == "construct"), None)
    before: list[str] = []
    for stmt in construct.body if construct else []:
        if self_calls(stmt, "beat"):
            break
        before += [f"self.{c.func.attr}() on line {c.lineno}" for c in self_calls(stmt, "play", "wait")]
    return Plan(True, beats, placeholders, before)


# --- animation timing ---------------------------------------------------------------

def _self_call(node: ast.AST) -> str | None:
    """Return the method name for ``self.name(...)`` calls."""
    if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name) and node.func.value.id == "self"):
        return node.func.attr
    return None


def _target_key(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if (isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name)
            and node.value.id == "self"):
        return f"self.{node.attr}"
    return None


def _references_name(node: ast.AST | None, name: str) -> bool:
    """Whether an expression reads ``name`` directly.

    Recognition replay needs this syntactic distinction: ``self.replay_time`` can carry
    the clock captured in B3 into B6, while the identical-looking expression
    ``b.duration * .8`` reads each beat's *own* clock and is therefore not a replay.
    Dependency analysis alone deliberately treats both expressions as narration-relative.
    """
    return node is not None and any(isinstance(child, ast.Name) and child.id == name
                                    for child in ast.walk(node))


def _clock_is_stable(node: ast.AST, env: dict[str, set[str]], assignments: dict[str, list[int]],
                     first_use_line: int) -> bool:
    """Return true when ``node`` reads a narration clock captured exactly once.

    Merely using the same local name in B3 and B6 is insufficient: code can assign that
    name from ``b.duration`` again in B6, silently giving the replay a different clock.
    The shared clock must be assigned once, before its B3 use, then carried into B6.
    """
    keys: set[str] = set()
    for child in ast.walk(node):
        key = _target_key(child)
        if key in env and "beat" in env[key]:
            keys.add(key)
    return bool(keys) and all(len(assignments.get(key, ())) == 1
                              and assignments[key][0] < first_use_line for key in keys)


def _expr_deps(node: ast.AST | None, env: dict[str, set[str]]) -> set[str]:
    """Parameters/narration clocks that an expression depends on.

    This is deliberately a small data-flow analysis, not a Python evaluator. It follows
    assignments such as ``t = [run_time * share for share in PHASES]`` and
    ``rest = b.remaining`` while treating colors, geometry and numeric constants as
    unrelated to time.
    """
    if node is None:
        return set()
    key = _target_key(node)
    if key and key in env:
        return set(env[key])
    if isinstance(node, ast.Name):
        return set(env.get(node.id, ()))
    if isinstance(node, ast.Attribute):
        return _expr_deps(node.value, env)
    if isinstance(node, ast.Call):
        return set().union(*(_expr_deps(arg, env) for arg in node.args),
                           *(_expr_deps(k.value, env) for k in node.keywords))
    if isinstance(node, ast.Lambda):
        return _expr_deps(node.body, env)
    if isinstance(node, ast.comprehension):
        return _expr_deps(node.iter, env) | set().union(
            *(_expr_deps(x, env) for x in node.ifs), set()
        )
    return set().union(*(_expr_deps(child, env) for child in ast.iter_child_nodes(node)), set())


def _assign_deps(node: ast.AST, env: dict[str, set[str]]) -> bool:
    """Update dependency facts for an assignment; return whether a fact changed."""
    value: ast.AST | None = None
    targets: list[ast.AST] = []
    if isinstance(node, (ast.Assign, ast.AnnAssign)):
        value = node.value
        targets = list(node.targets) if isinstance(node, ast.Assign) else [node.target]
    elif isinstance(node, ast.NamedExpr):
        value, targets = node.value, [node.target]
    if value is None:
        return False
    deps = _expr_deps(value, env)
    changed = False
    for target in targets:
        key = _target_key(target)
        if key is not None and env.get(key) != deps:
            env[key] = deps
            changed = True
    return changed


def _dependency_env(node: ast.AST, seeds: dict[str, set[str]]) -> dict[str, set[str]]:
    env = {name: set(value) for name, value in seeds.items()}
    assignments = [n for n in ast.walk(node) if isinstance(n, (ast.Assign, ast.AnnAssign, ast.NamedExpr))]
    # A few fixed-point passes handle aliases declared before or after their use without
    # attempting control-flow execution. Episode scenes are intentionally straight-line.
    for _ in range(len(assignments) + 1):
        changed = False
        for assignment in assignments:
            changed = _assign_deps(assignment, env) or changed
        if not changed:
            break
    return env


def _number(node: ast.AST | None) -> float | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        value = _number(node.operand)
        if value is not None:
            return value if isinstance(node.op, ast.UAdd) else -value
    return None


def _fraction(node: ast.AST | None, env: dict[str, float | None]) -> float | None:
    """Approximate an expression's intended share of a beat duration.

    Constants alone are not shares. For guards such as ``min(4.4, .8*b.duration)`` the
    narration-relative branch is returned; rendered QA remains responsible for the actual
    seconds after the guard is evaluated.
    """
    if node is None:
        return None
    key = _target_key(node)
    if key and key in env:
        return env[key]
    if isinstance(node, ast.Name):
        return env.get(node.id)
    if isinstance(node, ast.Attribute):
        if node.attr in {"duration", "remaining"}:
            return 1.0
        return _fraction(node.value, env)
    if isinstance(node, ast.BinOp):
        left, right = _fraction(node.left, env), _fraction(node.right, env)
        ln, rn = _number(node.left), _number(node.right)
        if isinstance(node.op, ast.Mult):
            if left is not None and rn is not None:
                return left * rn
            if right is not None and ln is not None:
                return right * ln
        if isinstance(node.op, ast.Div) and left is not None and rn not in (None, 0):
            return left / rn
        if isinstance(node.op, (ast.Add, ast.Sub)):
            if left is not None and right is not None:
                return left + right if isinstance(node.op, ast.Add) else left - right
            return left if left is not None else right
        return None
    if isinstance(node, ast.Call):
        shares = [x for x in (_fraction(a, env) for a in node.args) if x is not None]
        return max(shares) if shares else None
    if isinstance(node, ast.IfExp):
        shares = [x for x in (_fraction(node.body, env), _fraction(node.orelse, env)) if x is not None]
        return min(shares) if shares else None
    return None


def _fraction_env(node: ast.AST) -> dict[str, float | None]:
    env: dict[str, float | None] = {}
    assignments = [n for n in ast.walk(node) if isinstance(n, (ast.Assign, ast.AnnAssign))]
    for _ in range(len(assignments) + 1):
        changed = False
        for item in assignments:
            value = item.value
            targets = list(item.targets) if isinstance(item, ast.Assign) else [item.target]
            share = _fraction(value, env)
            for target in targets:
                key = _target_key(target)
                if key is not None and env.get(key) != share:
                    env[key] = share
                    changed = True
        if not changed:
            break
    return env


def _run_time(call: ast.Call) -> ast.AST | None:
    return next((k.value for k in call.keywords if k.arg == "run_time"), None)


def _episode_class(scene: Path, cls: str = "Episode") -> ast.ClassDef | None:
    if not scene.exists():
        return None
    tree = ast.parse(scene.read_text(encoding="utf-8"))
    return next((n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == cls), None)


def _method_summaries(klass: ast.ClassDef) -> dict[str, MethodTiming]:
    summaries: dict[str, MethodTiming] = {}
    for method in (n for n in klass.body if isinstance(n, ast.FunctionDef)):
        params = [a.arg for a in method.args.args if a.arg != "self"]
        env = _dependency_env(method, {p: {p} for p in params})
        plays = sorted((n for n in ast.walk(method) if _self_call(n) == "play"), key=lambda n: n.lineno)
        deps, fixed, missing = [], [], []
        for play in plays:
            run_time = _run_time(play)
            if run_time is None:
                missing.append(play.lineno)
                deps.append(set())
                continue
            sources = _expr_deps(run_time, env) & set(params)
            deps.append(sources)
            if not sources:
                fixed.append(play.lineno)
        common = set.intersection(*deps) if deps else set()
        used = set.union(*deps) if deps else set()
        # If every play is timed, but different parameters control different phases, the
        # caller cannot provide one narration-relative motion budget for the helper. This
        # used to make motion-timing pass while motion-coverage quietly fell to zero.
        split = used if deps and all(deps) and not common else set()
        summaries[method.name] = MethodTiming(method, bool(plays), common, split, fixed, missing)
    return summaries


def _beat_blocks(klass: ast.ClassDef) -> dict[str, tuple[ast.With, str]]:
    construct = next((n for n in klass.body if isinstance(n, ast.FunctionDef) and n.name == "construct"), None)
    out: dict[str, tuple[ast.With, str]] = {}
    for node in ast.walk(construct) if construct else []:
        if not isinstance(node, ast.With):
            continue
        for item in node.items:
            call = item.context_expr
            if (_self_call(call) == "beat" and call.args and isinstance(call.args[0], ast.Constant)
                    and isinstance(call.args[0].value, str)):
                alias = item.optional_vars.id if isinstance(item.optional_vars, ast.Name) else "b"
                out[call.args[0].value] = (node, alias)
    return out


def _bound_argument(call: ast.Call, method: ast.FunctionDef, parameter: str) -> ast.AST | None:
    keyword = next((k.value for k in call.keywords if k.arg == parameter), None)
    if keyword is not None:
        return keyword
    params = [a.arg for a in method.args.args if a.arg != "self"]
    return call.args[params.index(parameter)] if parameter in params and params.index(parameter) < len(call.args) else None


def _animated_helper_calls(block: ast.With, summaries: dict[str, MethodTiming]) -> list[ast.Call]:
    return sorted((n for n in ast.walk(block)
                   if isinstance(n, ast.Call) and _self_call(n) in summaries
                   and summaries[_self_call(n)].has_play), key=lambda n: n.lineno)


# --- the rules -------------------------------------------------------------------------

def one_goal(ep: Path, lim: Limits) -> Result:
    brief = ep / "brief.md"
    text = bridge(brief.read_text(encoding="utf-8")) if brief.exists() else ""
    if not text.strip("? "):
        return result("one-goal", ["write the bridge in brief.md: the one thing the viewer learns"], "no bridge yet")
    n, count = len(sentences(text)), len(WORD.findall(text))
    issues = []
    if n != 1:
        issues.append(f"the bridge is {n} sentences: one learning goal, one sentence")
    if count > lim.bridge_max_words:
        issues.append(f"the bridge is {count} words (max {lim.bridge_max_words}): narrow the goal")
    return result("one-goal", issues, f"bridge: {n} sentence(s), {count} words (max {lim.bridge_max_words})")


def hook_length(script: Script, lim: Limits) -> Result:
    b1 = script.beats.get("B1")
    if not b1 or not b1.vo:
        return result("hook-length", ["B1 has no VO line"], "no hook yet")
    n = len(WORD.findall(b1.vo))
    issues = [f"B1 is {n} words: cut it to the claim itself"] if n > lim.hook_max_words else []
    return result("hook-length", issues, f"B1: {n} words (max {lim.hook_max_words})")


def hook_relevance(script: Script) -> Result:
    b1 = script.beats.get("B1")
    vo = b1.vo if b1 else ""
    issues, found = [], []
    for key, world in (("a", "world A"), ("b", "world B")):
        terms = theme_words(script, key)
        if not terms:
            issues.append(f"set `{key}:` in the script front matter")
        elif hits := named(vo, terms):
            found.append(hits[0])
        else:
            issues.append(f"B1 does not name {world} (one of: {', '.join(terms[:5])})")
    return result("hook-relevance", issues, "B1 names " + (" and ".join(found) if found else "neither world"))


def cold_open(script: Script, plan: Plan | None, lim: Limits) -> Result:
    b1 = script.beats.get("B1")
    opening = words(b1.vo) if b1 and b1.vo else []
    issues = []
    for phrase in lim.intro_phrases:
        p = words(phrase)
        if p and opening[:len(p)] == p:
            issues.append(f"B1 opens with '{phrase}': open on the claim itself")
    if "subscribe" in opening:
        issues.append("B1 asks for a subscription: keep the hook for the claim")
    if plan is not None and plan.before_first_beat:
        issues.append(f"scene.py runs {', '.join(plan.before_first_beat)} before B1: the narration must start at frame 0")
    return result("cold-open", issues, "B1 opens on the claim" + ("" if plan is None else "; nothing plays before it"))


def early_answer(script: Script, lim: Limits) -> Result:
    beats = [b for b in script.beats.values() if b.vo]
    ids = [b.id for b in beats]
    if lim.mechanism_beat not in ids:
        return result("early-answer", [f"{lim.mechanism_beat} has no VO: that beat answers the hook"], "no mechanism beat")
    total = sum(len(WORD.findall(b.vo)) for b in beats)
    before = sum(len(WORD.findall(b.vo)) for b in beats[:ids.index(lim.mechanism_beat)])
    share = before / total if total else 0.0
    issues = ([f"{lim.mechanism_beat} starts {share:.0%} into the narration: shorten the set-up before it"]
              if share > lim.answer_by else [])
    return result("early-answer", issues, f"{lim.mechanism_beat} starts {share:.0%} in (max {lim.answer_by:.0%})")


def micro_units(script: Script, lim: Limits) -> Result:
    issues, longest = [], 0
    for b in script.beats.values():
        if not b.vo:
            continue
        n, s = len(WORD.findall(b.vo)), len(sentences(b.vo))
        longest = max(longest, n)
        if n > lim.beat_max_words:
            issues.append(f"{b.id} is {n} words (max {lim.beat_max_words}): cut a sentence or split the idea")
        if s > lim.beat_max_sentences:
            issues.append(f"{b.id} has {s} sentences (max {lim.beat_max_sentences})")
    return result("micro-units", issues, f"longest beat: {longest} words (max {lim.beat_max_words})")


def delivery_notes(script: Script) -> Result:
    """Require performance intent without pretending NOTE metadata drives synthesis."""

    spoken = [beat for beat in script.beats.values() if beat.vo]
    missing = [beat.id for beat in spoken if not beat.note.strip()]
    issues = [
        f"{beat_id} has no NOTE: add non-spoken direction for pace, pause, emphasis or turn"
        for beat_id in missing
    ]
    return result(
        "delivery-notes",
        issues,
        f"{len(spoken) - len(missing)}/{len(spoken)} spoken beats have performance direction; "
        "NOTE does not drive synthesis",
    )


def length(script: Script) -> Result:
    cfg = ste.load_config()
    count = script.word_count
    secs = count / cfg.wpm * 60
    lo, hi = cfg.seconds
    issues = [] if lo <= secs <= hi else [f"about {secs:.0f} s: {'cut' if secs > hi else 'add'} words to reach {lo}-{hi} s"]
    return result("length", issues, f"{count} words, about {secs:.0f} s at {cfg.wpm} words/min (target {lo}-{hi} s)")


def minimal_text(script: Script, ep: Path, lim: Limits) -> Result:
    narration = words(script.narration)
    n = lim.echo_words
    grams = {tuple(narration[i:i + n]) for i in range(len(narration) - n + 1)}

    def echo(text: str) -> str | None:
        w = words(text)
        hit = next((w[i:i + n] for i in range(len(w) - n + 1) if tuple(w[i:i + n]) in grams), None)
        return " ".join(hit) if hit else None

    issues = []
    for b in script.beats.values():
        if b.txt:
            count = len(WORD.findall(b.txt))
            if count > lim.txt_max_words:
                issues.append(f"{b.id} TXT is {count} words (max {lim.txt_max_words})")
            if repeat := echo(b.txt):
                issues.append(f"{b.id} TXT repeats the narration ('{repeat}'): the captions already say it")
    shown = sorted(screen_strings(ep / "scene.py"))
    for s in shown:
        count = len(WORD.findall(s))
        if count > lim.screen_max_words:
            issues.append(f"on-screen '{s}' is {count} words (max {lim.screen_max_words})")
        if repeat := echo(s):
            issues.append(f"on-screen '{s}' repeats the narration ('{repeat}'): show a keyword, not the sentence")
    longest = max((len(WORD.findall(s)) for s in shown), default=0)
    return result("minimal-text", issues, f"{len(shown)} on-screen strings, longest {longest} words "
                                          f"(max {lim.screen_max_words}); no narration echoes")


def title(script: Script, lim: Limits) -> Result:
    text = script.meta.get("title", "").strip()
    if not text:
        return result("title", ["set `title:` in the script front matter: the upload title"], "no title yet")
    issues = []
    if len(text) > lim.title_max_chars:
        issues.append(f"the title is {len(text)} characters (max {lim.title_max_chars})")
    for key, world in (("a", "world A"), ("b", "world B")):
        if not named(text, theme_words(script, key)):
            issues.append(f"the title does not name {world}")
    return result("title", issues, f"{len(text)} characters (max {lim.title_max_chars}): {text}")


def sourced(script: Script, ep: Path) -> Result:
    brief = ep / "brief.md"
    rows = ledger(brief.read_text(encoding="utf-8")) if brief.exists() else []
    spoken = [b.id for b in script.beats.values() if b.vo]
    if not rows:
        return result("sourced", ["fill the claim ledger in brief.md before writing VO"], "no ledger rows")
    issues = []
    covered = set().union(*(beat_refs(claim) for _, claim, _ in rows))
    for beat_id in spoken:
        if beat_id not in covered:
            issues.append(f"{beat_id} is not in the claim ledger: add a claim row with sources, "
                          "or a framing row (F#) if it states no new fact")
    for row_id, claim, sources in rows:
        if not beat_refs(claim):
            issues.append(f"{row_id} names no beat: end its claim with the beats, e.g. (B2)")
        if row_id.startswith("C") and not re.search(r"https?://|\b[CF]\d+\b", sources):
            issues.append(f"{row_id} has no source link")
    return result("sourced", issues, f"{len(rows)} ledger rows cover {len(covered & set(spoken))}/{len(spoken)} beats")


def color_signals(ep: Path, lim: Limits) -> Result:
    scene = ep / "scene.py"
    if not scene.exists():
        return Result("color-signals", "skip", "no scene.py yet")
    hues = semantic_hues()
    tree = ast.parse(scene.read_text(encoding="utf-8"))
    issues, colors, names = [], set(), set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            for m in HEX.finditer(node.value):
                color = m.group(0).upper()
                if color in colors:
                    continue
                colors.add(color)
                hue, sat, val = hsv(color)
                if sat < lim.neutral_saturation or val < lim.neutral_value:
                    continue
                gap = min(min(abs(hue - h), 360 - abs(hue - h)) for h in hues.values())
                if gap > lim.hue_tolerance:
                    issues.append(f"line {node.lineno}: {color} is outside the A, B, link and alert color "
                                  "families: use a kit color, a shade of one, or a neutral")
        elif isinstance(node, ast.Name) and NAMED_COLOR.match(node.id) and node.id not in names:
            names.add(node.id)
            issues.append(f"line {node.lineno}: Manim color {node.id}: color means A, B or the link here; "
                          "use A_COLOR, B_COLOR, LINK_COLOR or a neutral")
    return result("color-signals", issues, f"{len(colors)} custom colors, each a neutral or a semantic shade")


def every_beat(script: Script, plan: Plan | None, final: bool) -> Result:
    if plan is None:
        return Result("every-beat", "skip", "no scene.py yet: `vid scene <ep>` writes the animatic")
    if not plan.found:
        return result("every-beat", ["scene.py has no class Episode (the class vid renders)"], "no Episode class")
    want = [b.id for b in script.beats.values() if b.vo]
    issues = []
    if missing := [b for b in want if b not in plan.beats]:
        issues.append(f"never spoken in scene.py: {', '.join(missing)}")
    if extra := [b for b in plan.beats if b not in want]:
        issues.append(f"no VO in script.md: {', '.join(extra)}")
    if twice := sorted({b for b in plan.beats if plan.beats.count(b) > 1}):
        issues.append(f"spoken twice: {', '.join(twice)}")
    if not issues and plan.beats != want:
        issues.append("the beats are out of script order")
    detail = f"{len(plan.beats)}/{len(want)} beats, in order"
    if plan.placeholders:
        lines = ", ".join(map(str, plan.placeholders))
        if final:
            issues.append(f"placeholder card(s) left on line {lines}: animate them before vid final")
        detail += f"; {len(plan.placeholders)} beat(s) still placeholders"
    return result("every-beat", issues, detail)


def motion_rules(script: Script, ep: Path, plan: Plan | None, lim: Limits) -> tuple[Result, Result, Result]:
    """Check narration-relative motion and the B3/B6 recognition replay.

    Rendered freeze detection is the final backstop. These source checks fail much earlier:
    a visual pass cannot silently turn into fixed seconds when the approved narration gets
    longer, and a short list of animations cannot leave most of a beat to ``hold(b)``.
    """
    scene = ep / "scene.py"
    names = ("motion-timing", "motion-coverage", "recognition-replay")
    if plan is None or not scene.exists():
        return tuple(Result(name, "skip", "no scene.py yet") for name in names)  # type: ignore[return-value]
    if not plan.found:
        return tuple(Result(name, "skip", "scene.py has no Episode class") for name in names)  # type: ignore[return-value]
    if plan.placeholders:
        detail = f"animatic only: {len(plan.placeholders)} placeholder beat(s) remain"
        return tuple(Result(name, "skip", detail) for name in names)  # type: ignore[return-value]

    klass = _episode_class(scene)
    if klass is None:  # guarded by plan.found; keep the rule robust when called independently
        return tuple(Result(name, "skip", "scene.py has no Episode class") for name in names)  # type: ignore[return-value]
    summaries = _method_summaries(klass)
    blocks = _beat_blocks(klass)
    construct = summaries.get("construct")
    aliases = {alias for _, alias in blocks.values()}
    deps = _dependency_env(construct.node, {alias: {"beat"} for alias in aliases}) if construct else {}
    fractions = _fraction_env(construct.node) if construct else {}
    clock_assignments: dict[str, list[int]] = {}
    if construct:
        for node in ast.walk(construct.node):
            if isinstance(node, (ast.Assign, ast.AnnAssign, ast.NamedExpr)):
                targets = (list(node.targets) if isinstance(node, ast.Assign) else [node.target])
                for target in targets:
                    if key := _target_key(target):
                        clock_assignments.setdefault(key, []).append(node.lineno)
    timing_issues: list[str] = []
    coverage_issues: list[str] = []
    coverage: dict[str, float] = {}
    reachable: dict[str, list[ast.Call]] = {}

    for beat_id, (block, _) in blocks.items():
        share = 0.0
        calls = sorted((n for n in ast.walk(block) if isinstance(n, ast.Call)), key=lambda n: n.lineno)
        for call in calls:
            name = _self_call(call)
            if name == "play" or name == "end_card":
                run_time = _run_time(call)
                label = "self.play" if name == "play" else "self.end_card"
                if run_time is None:
                    timing_issues.append(f"{beat_id} line {call.lineno}: {label} has no run_time; use b.duration")
                    continue
                if "beat" not in _expr_deps(run_time, deps):
                    timing_issues.append(
                        f"{beat_id} line {call.lineno}: {label} uses fixed run_time={ast.unparse(run_time)}; "
                        "derive it from b.duration or b.remaining"
                    )
                if (part := _fraction(run_time, fractions)) is not None:
                    share += max(0.0, part)
                continue
            if name not in summaries or not summaries[name].has_play:
                continue
            summary = summaries[name]
            reachable.setdefault(name, []).append(call)
            if not summary.timing_params:
                continue
            # A helper's duration parameter is its total motion budget. Its internal phase
            # plays divide that budget, so counting every phase again would double-count it.
            candidates = []
            for parameter in summary.timing_params:
                actual = _bound_argument(call, summary.node, parameter)
                if actual is None:
                    timing_issues.append(
                        f"{beat_id} line {call.lineno}: self.{name} does not receive {parameter}; "
                        "pass a narration-relative duration explicitly"
                    )
                    continue
                if "beat" not in _expr_deps(actual, deps):
                    timing_issues.append(
                        f"{beat_id} line {call.lineno}: self.{name} receives a fixed {parameter}; "
                        "derive the shared duration from narration"
                    )
                if (part := _fraction(actual, fractions)) is not None:
                    candidates.append(part)
            if candidates:
                share += max(candidates)
        coverage[beat_id] = min(share, 1.0)

    for name, calls in sorted(reachable.items()):
        summary = summaries[name]
        if summary.missing_lines:
            lines = ", ".join(map(str, summary.missing_lines))
            timing_issues.append(f"self.{name} has self.play without run_time on line(s) {lines}")
        if summary.fixed_lines:
            lines = ", ".join(map(str, summary.fixed_lines))
            timing_issues.append(
                f"self.{name} hard-codes animation seconds on line(s) {lines}; pass one narration-relative "
                "duration in and divide it into phase shares"
            )
        if summary.split_params:
            parameters = ", ".join(sorted(summary.split_params))
            timing_issues.append(
                f"self.{name} splits its animation clock across unrelated parameters ({parameters}); "
                "pass one narration-relative duration and divide it into phase shares"
            )

    for beat_id in (b.id for b in script.beats.values() if b.vo and b.id in blocks):
        share = coverage.get(beat_id, 0.0)
        if share + 1e-9 < lim.motion_min_share:
            coverage_issues.append(
                f"{beat_id} schedules about {share:.0%} of its narration for animation "
                f"(min {lim.motion_min_share:.0%}); the remaining {1 - share:.0%} can become a static hold"
            )

    timed = sum(1 for value in coverage.values() if value > 0)
    timing_result = result(
        "motion-timing", timing_issues,
        f"{timed}/{len(coverage)} beats use narration-relative animation timing",
    )
    lowest = min(coverage.values(), default=0.0)
    coverage_result = result(
        "motion-coverage", coverage_issues,
        f"lowest scheduled motion share: {lowest:.0%} (min {lim.motion_min_share:.0%})",
    )

    recognition_issues: list[str] = []
    b3, b6 = blocks.get("B3"), blocks.get("B6")
    shared_name = ""
    if not b3 or not b6:
        recognition_issues.append("B3 and B6 must both exist to replay the mechanism")
    else:
        b3_calls: dict[str, list[ast.Call]] = {}
        b6_calls: dict[str, list[ast.Call]] = {}
        for call in _animated_helper_calls(b3[0], summaries):
            if name := _self_call(call):
                b3_calls.setdefault(name, []).append(call)
        for call in _animated_helper_calls(b6[0], summaries):
            if name := _self_call(call):
                b6_calls.setdefault(name, []).append(call)
        shared = sorted((set(b3_calls) & set(b6_calls)) - {None})
        for name in shared:
            summary = summaries[name]
            for first_call in b3_calls[name]:
                for second_call in b6_calls[name]:
                    for parameter in sorted(summary.timing_params):
                        first = _bound_argument(first_call, summary.node, parameter)
                        second = _bound_argument(second_call, summary.node, parameter)
                        if first is None or second is None:
                            continue
                        same_source = (ast.dump(first, include_attributes=False)
                                       == ast.dump(second, include_attributes=False))
                        local_clock = (_references_name(first, b3[1])
                                       or _references_name(second, b6[1]))
                        narration_relative = ("beat" in _expr_deps(first, deps)
                                              and "beat" in _expr_deps(second, deps))
                        stable_clock = _clock_is_stable(first, deps, clock_assignments,
                                                        first_call.lineno)
                        if same_source and not local_clock and narration_relative and stable_clock:
                            shared_name = name
                            break
                    if shared_name:
                        break
                if shared_name:
                    break
            if shared_name:
                break
        if not shared:
            recognition_issues.append(
                "B3 and B6 do not call the same animated helper; build the mechanism once and re-skin it"
            )
        elif not shared_name:
            helpers = ", ".join(f"self.{name}" for name in shared)
            recognition_issues.append(
                f"{helpers} is shared, but B3 and B6 do not reuse one narration-relative phase clock; "
                "compute it once from B3 and pass the same value to both calls"
            )
    recognition_result = result(
        "recognition-replay", recognition_issues,
        f"B3/B6 replay self.{shared_name} with one shared clock" if shared_name else "no verified shared replay",
    )
    return timing_result, coverage_result, recognition_result


def causal_motion(ep: Path, plan: Plan | None, lim: Limits) -> Result:
    """Require story-changing geometry, not only entrances, exits and pulse effects."""
    scene = ep / "scene.py"
    if plan is None or not scene.exists():
        return Result("causal-motion", "skip", "no scene.py yet")
    if not plan.found:
        return Result("causal-motion", "skip", "scene.py has no Episode class")
    if plan.placeholders:
        return Result("causal-motion", "skip", f"animatic only: {len(plan.placeholders)} placeholder beat(s) remain")
    report = visual_quality.inspect_scene_motion(scene)
    issues = visual_quality.judge_scene_motion(report, min_causal_beats=lim.causal_min_beats)
    story = [beat for beat in report.beats if beat != "B9"]
    causal = [beat for beat in story if report.beats[beat] > 0]
    return result("causal-motion", issues, f"{len(causal)}/{len(story)} story beats show causal geometry changes")


def check(ep: Path, final: bool = False) -> list[Result]:
    lim = load_section(Limits, "check")
    script = load_script(ep / "script.md")
    plan = scene_plan(ep / "scene.py")
    motion = motion_rules(script, ep, plan, lim)
    return [
        one_goal(ep, lim),
        hook_length(script, lim),
        hook_relevance(script),
        cold_open(script, plan, lim),
        early_answer(script, lim),
        micro_units(script, lim),
        delivery_notes(script),
        length(script),
        minimal_text(script, ep, lim),
        title(script, lim),
        sourced(script, ep),
        color_signals(ep, lim),
        every_beat(script, plan, final),
        *motion,
        causal_motion(ep, plan, lim),
    ]


def show(heading: str, results: list[Result]) -> bool:
    print(f"{heading}  (the evidence for each rule: RESEARCH.md)\n")
    for r in results:
        print(f"  {r.status.upper():<4}  {r.rule:<15} {r.detail}")
        for issue in r.issues:
            print(f"        x {issue}")
    failed = [r for r in results if r.status == "fail"]
    print(f"\nResult: {len(failed)} rule(s) failed  {'PASS' if not failed else 'FAIL'}")
    return not failed


def run(ep: Path, final: bool = False) -> bool:
    return show(f"Design check: {ep.name}", check(ep, final))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    sys.exit(0 if run(Path(sys.argv[1]).resolve()) else 1)
