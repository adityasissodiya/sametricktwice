"""Check narration against the ASD-STE100 writing rules that a program can test.

    sentence_length  max 25 words in a descriptive sentence
    complex_verbs    simple tenses only: not "has made", "is making", "would make"
    ing_forms        -ing words only inside technical names
    passive_voice    active voice: "Kodak made it", not "it was made by Kodak"
    noun_clusters    no more than 3 nouns in a row
    fragments        full sentences, each with a main verb
    phrasal_verbs    one-word verbs: "remove", not "wash away"
    contractions     full forms: "do not", not "don't"
    vocabulary       common words; rare words must be in a glossary

A sentence is clean when it breaks none of these. The score is clean sentences
divided by all sentences, and ste.toml sets the target (80%). STE's "one word,
one meaning" dictionary rule still needs a human read (see WORKFLOW.md).

Usage: python tools/ste.py episodes/<ep>/script.md   (or: vid check <ep>)
"""

from __future__ import annotations

import sys
import tomllib
from dataclasses import dataclass, field, fields
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.scriptfile import WORD, Script, load_script  # noqa: E402

ALLOWED_MODALS = {"can", "could", "must", "will", "do", "does", "did", "ca", "wo"}
CONTRACTIONS = {"n't", "'re", "'ve", "'ll", "'d", "'m"}
NOT_CONTENT = {"PROPN", "NUM", "SYM", "PUNCT", "X", "SPACE", "INTJ"}


@dataclass
class Config:
    target: float = 0.80
    max_words: int = 25
    pace_words: int = 20
    wpm: int = 160
    seconds: list[int] = field(default_factory=lambda: [45, 60])
    vocabulary: str = "frequency"
    min_zipf: float = 4.0
    approved_list: str = "ste/approved-words.txt"
    glossary: list[str] = field(default_factory=list)
    rules: dict[str, bool] = field(default_factory=dict)

    def on(self, rule: str) -> bool:
        return self.rules.get(rule, True)


@dataclass
class Sentence:
    beat: str
    text: str
    problems: list[str]
    notes: list[str]


def load_config(path: Path = ROOT / "ste.toml") -> Config:
    data = tomllib.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    names = {f.name for f in fields(Config)}
    return Config(**{k: v for k, v in data.items() if k in names})


def allowed_words(script: Script, cfg: Config) -> set[str]:
    terms = [*cfg.glossary, *script.glossary]
    for key in ("a", "b", "link"):
        theme = script.theme(key)
        terms += [theme.label, *theme.keywords]
    return {w.lower() for term in terms for w in WORD.findall(term.replace("-", " "))}


def check(script: Script, cfg: Config) -> list[Sentence]:
    import spacy

    nlp = spacy.load("en_core_web_sm", disable=["ner"])
    allow = allowed_words(script, cfg)
    approved = None
    if cfg.vocabulary == "approved-list":
        lines = (ROOT / cfg.approved_list).read_text(encoding="utf-8").splitlines()
        approved = {w.strip().lower() for w in lines if w.strip()}
    results = []
    for beat in script.beats.values():
        for sent in nlp(beat.vo).sents if beat.vo else []:
            if WORD.search(sent.text):
                problems, notes = check_sentence(sent, cfg, allow, approved)
                results.append(Sentence(beat.id, sent.text.strip(), problems, notes))
    return results


def check_sentence(sent, cfg: Config, allow: set[str], approved: set[str] | None):
    problems, notes = [], []
    n = len(WORD.findall(sent.text))
    if cfg.on("sentence_length") and n > cfg.max_words:
        problems.append(f"{n} words (STE max {cfg.max_words}): split it")
    elif n > cfg.pace_words:
        notes.append(f"{n} words: long to say in one breath")
    toks = [t for t in sent if not t.is_space]
    if cfg.on("fragments") and not any(is_finite(t) for t in toks):
        problems.append("no main verb: write a full sentence")
    run: list[str] = []
    for t in [*toks, None]:
        if t is not None and t.pos_ == "NOUN":
            run.append(t.text)
            continue
        if cfg.on("noun_clusters") and len(run) > 3:
            problems.append(f"noun cluster '{' '.join(run)}': max 3 nouns in a row")
        run = []
    for t in toks:
        low = t.text.lower().replace("’", "'")
        if cfg.on("contractions") and (low in CONTRACTIONS or (low == "'s" and t.tag_ != "POS")):
            problems.append(f"contraction '{t.text}': write the full form")
        if cfg.on("complex_verbs") and t.dep_ == "aux":
            if t.lemma_ == "have" and t.head.tag_ == "VBN":
                problems.append(f"'{t.text} {t.head.text}': use the simple past or present")
            elif t.lemma_ == "be" and t.head.tag_ == "VBG":
                problems.append(f"'{t.text} {t.head.text}': use the simple present or past")
            elif t.tag_ == "MD" and low not in ALLOWED_MODALS:
                problems.append(f"'{t.text}': use can, must or will")
        if cfg.on("passive_voice") and t.dep_ == "auxpass":
            problems.append(f"passive '{t.text} {t.head.text}': say who does the action")
        if cfg.on("ing_forms") and t.tag_ == "VBG" and low not in allow and not is_progressive(t):
            problems.append(f"-ing form '{t.text}': use it only in a technical name")
        if cfg.on("phrasal_verbs") and t.dep_ == "prt":
            problems.append(f"phrasal verb '{t.head.text} {t.text}': use one verb")
        if cfg.on("vocabulary") and is_content(t) and low not in allow and t.lemma_.lower() not in allow:
            problem = vocabulary_problem(t, cfg, approved)
            if problem:
                problems.append(problem)
    return list(dict.fromkeys(problems)), notes


def is_finite(t) -> bool:
    return t.tag_ in {"VBD", "VBZ", "VBP", "MD"} or (t.tag_ == "VB" and t.dep_ == "ROOT")


def is_progressive(t) -> bool:
    return any(c.dep_ == "aux" and c.lemma_ == "be" for c in t.children)


def is_content(t) -> bool:
    return t.is_alpha and not t.is_stop and t.pos_ not in NOT_CONTENT


def vocabulary_problem(t, cfg: Config, approved: set[str] | None) -> str | None:
    low, lemma = t.text.lower(), t.lemma_.lower()
    if approved is not None:
        return None if {low, lemma} & approved else f"'{t.text}' is not an approved STE word"
    from wordfreq import zipf_frequency

    z = max(zipf_frequency(low, "en"), zipf_frequency(lemma, "en"))
    if z >= cfg.min_zipf:
        return None
    return f"uncommon word '{t.text}' (Zipf {z:.1f}): use a common word, or add it to the glossary"


def report(script: Script, cfg: Config, results: list[Sentence]) -> bool:
    clean = sum(1 for r in results if not r.problems)
    score = clean / len(results) if results else 0.0
    passed = bool(results) and score >= cfg.target
    print(f"STE check: {script.path.parent.name}\n")
    for r in results:
        print(f"  {r.beat:<4} {'ok' if not r.problems else '--'}  {r.text}")
        for p in r.problems:
            print(f"            x {p}")
        for note in r.notes:
            print(f"            . {note}")
    print(f"\nScore:  {clean}/{len(results)} sentences clean = {score:.0%} "
          f"(target {cfg.target:.0%})  {'PASS' if passed else 'FAIL'}")
    return passed


def run(script_path: Path) -> bool:
    script = load_script(script_path)
    cfg = load_config()
    return report(script, cfg, check(script, cfg))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    sys.exit(0 if run(Path(sys.argv[1])) else 1)
