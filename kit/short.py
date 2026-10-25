"""ShortScene: the base class for every Episode 001-style infographic.

    from kit import *

    class Episode(ShortScene):
        def construct(self):
            with self.beat("B1") as b:          # speaks B1's VO line from script.md
                self.play(FadeIn(thing), run_time=b.duration / 2)
            # leaving the block waits until the line has finished

Narration comes from script.md, so scene.py holds visuals only. Captions are built
from the same VO text, and the script's a / b / link keywords color them.
Approved VO stays locked during animation. Finished scenes must replace every placeholder,
keep production notes off-screen, and register layout constraints for the alignment loop.
See STYLE_GUIDE.md and AGENTS.md.
"""

from __future__ import annotations

import html
import inspect
import json
import math
import os
import re
import textwrap
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

from manim import *  # noqa: F403
from manim_voiceover import VoiceoverScene
from manim_voiceover.tracker import VoiceoverTracker

from tools.scriptfile import Beat, load_script

from . import parts
from .alignment import AlignmentSession, alignment_guides
from .style import *  # noqa: F403
from .voices import speech_service

ROOT = Path(__file__).resolve().parents[1]


@dataclass
class BeatTime:
    beat: Beat
    tracker: VoiceoverTracker

    @property
    def duration(self) -> float:
        """Length of this beat's narration, in seconds."""
        return self.tracker.duration

    @property
    def remaining(self) -> float:
        """Narration time left in this beat, in seconds."""
        return self.tracker.get_remaining_duration()


class ShortScene(VoiceoverScene):
    captions = True
    script_file = "script.md"

    def setup(self):
        super().setup()
        self.camera.background_color = BG
        self.set_speech_service(speech_service(os.environ.get("VID_VOICE")))  # default: voice.toml
        self.episode_dir = Path(inspect.getfile(type(self))).resolve().parent
        self.script = load_script(self.episode_dir / self.script_file)
        self.keyword_colors = {}
        for key, color in (("link", LINK_COLOR), ("b", B_COLOR), ("a", A_COLOR)):
            theme = self.script.theme(key)
            for word in [theme.label, *theme.keywords]:
                if word:
                    self.keyword_colors[word.lower()] = color
        self.cc = Captions(self)
        self.add(self.cc)
        self.guides = safe_zone_guides() if os.environ.get("VID_GUIDES") == "1" else None
        if self.guides:
            self.add(self.guides)
        self.alignment = AlignmentSession.from_environment(default="off")
        self.alignment_guides = alignment_guides() if os.environ.get("VID_ALIGN_GUIDES") == "1" else None
        if self.alignment_guides:
            self.add(self.alignment_guides)
        # `vid qa` uses this render-time manifest rather than guessing how many times a
        # helper containing self.sfx() ran from source text.  The cue time is the exact
        # Manim scene time passed to the mixer; source loudness is measured later by QA.
        self.sfx_cues: list[dict[str, str | float]] = []

    def sfx(self, name: str, gain: float = -12):
        """Play a sound: the episode's own audio/ folder first, then the shared kit/sfx.

        Never copy a sound into an episode from another episode or from kit/sfx
        (`vid lint` fails on copies); call the kit sound by name instead.
        """
        for folder in (self.episode_dir / "audio", ROOT / "kit" / "sfx"):
            source = folder / name
            if source.exists():
                # Manim's gain is dB (`AudioSegment.apply_gain`).  Do not record cues
                # during skipped animation passes because Manim does not mix those.
                renderer = getattr(self, "renderer", None)
                if not getattr(renderer, "skip_animations", False):
                    try:
                        relative = source.resolve().relative_to(ROOT.resolve()).as_posix()
                    except ValueError:  # useful for isolated kit tests; production is always under ROOT
                        relative = str(source.resolve())
                    self.sfx_cues.append({
                        "name": name,
                        "time_s": round(float(self.time), 4),
                        "gain_db": float(gain or 0.0),
                        "source": relative,
                    })
                self.add_sound(str(source), gain=gain)
                return
        raise FileNotFoundError(f"No sound {name!r} in {self.episode_dir.name}/audio or kit/sfx")

    def _write_sfx_manifest(self):
        """Write executed sound cues for export QA.

        A source scan cannot know that a helper ran twice or the exact scene time of a
        cue.  Keeping this small manifest beside the render makes density, audibility and
        masking checks deterministic without changing the audio mix.
        """
        folder = ROOT / "media" / self.episode_dir.name
        folder.mkdir(parents=True, exist_ok=True)
        report = {
            "version": 1,
            "episode": self.episode_dir.name,
            "scene_duration_s": round(float(self.time), 4),
            "cues": self.sfx_cues,
        }
        (folder / "sfx-manifest.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    def alignment_loop(self, label: str, **kwargs):
        """Create a recorded alignment/refinement loop for one layout keyframe."""
        return self.alignment.loop(label, **kwargs)

    def tear_down(self):
        """Flush the report and apply preview/final alignment policy."""
        try:
            self.alignment.finish()
        finally:
            try:
                self._write_sfx_manifest()
            finally:
                super().tear_down()

    @contextmanager
    def beat(self, beat_id: str):
        """Speak one beat of script.md. Animations inside the block run under its line."""
        beat = self.script.beats.get(beat_id)
        if beat is None or not beat.vo:
            raise ValueError(f"{beat_id} has no VO line in {self.script.path}")
        with self.voiceover(text=beat.vo) as tracker:
            if self.captions:
                self.cc.schedule(beat.vo, tracker.start_t, tracker.duration, self.keyword_colors)
            yield BeatTime(beat, tracker)

    def hold(self, b: BeatTime, leave: float = 0.0):
        """Wait until `leave` seconds before this beat's line ends."""
        t = b.remaining - leave
        if t > 1 / config.frame_rate:
            self.wait(t)

    def clear_stage(self, run_time: float = 0.4):
        """Fade out everything except captions and guides."""
        keep = {self.cc, self.guides, self.alignment_guides}
        mobs = [m for m in self.mobjects if m not in keep]
        if mobs:
            self.play(*[FadeOut(m) for m in mobs], run_time=run_time)

    def placeholder(self, b: BeatTime):
        """Animatic card for a beat that has no animation yet: its VIS and TXT lines."""
        beat = b.beat
        parts = [Text(f"{beat.id} · {beat.label}".upper(), font=TITLE_FONT, font_size=LABEL_SIZE, color=MUTED)]
        if beat.txt:
            parts.append(Text(beat.txt, font=TITLE_FONT, weight=BOLD, font_size=TITLE_SIZE, color=INK))
        if beat.vis:
            wrapped = "\n".join(textwrap.wrap(beat.vis, 30))
            parts.append(Text(wrapped, font=BODY_FONT, font_size=BODY_SIZE - 6, color=MUTED))
        card = VGroup(*parts).arrange(DOWN, buff=0.45)
        if card.width > STAGE_WIDTH - 0.8:
            card.scale_to_fit_width(STAGE_WIDTH - 0.8)
        frame = DashedVMobject(
            RoundedRectangle(corner_radius=0.25, width=card.width + 0.8, height=card.height + 0.8,
                             stroke_color=MUTED, stroke_width=2),
            num_dashes=48,
        )
        group = VGroup(frame, card).move_to(STAGE_CENTER)
        fade = max(min(0.3, b.duration / 4), 1 / config.frame_rate)
        self.play(FadeIn(group, shift=0.15 * UP), run_time=fade)
        self.hold(b, leave=fade)
        self.play(FadeOut(group), run_time=fade)

    def end_card(self, run_time: float = 1.6, title: bool = True, both_ways: bool = False,
                 tagline: tuple[str, ...] = (), sound: str | None = None, intro=(), series: bool = False,
                 icons: tuple[Mobject, Mobject] | None = None):
        """The Connection Map: this episode's two worlds, joined by its link.

        both_ways: an arrow runs A -> B, another B -> A, then both merge into the link (the
        STYLE_GUIDE B9 move). tagline: lines under the map, the first one violet. sound: a
        kit/sfx (or episode audio/) sound name played as the link forms. intro: mobjects
        (e.g. the beat header) that fade in with the map, so the beat does not open on an
        empty screen. icons: drawings for world A and B (this episode's own), shown as the
        two nodes; without them the nodes are colored rings. series: also draw every earlier
        episode's pair, faint; only for compilations, never in a single Short, because
        earlier subjects would be carry-over. Registers its own alignment loop.
        """
        here = self.episode_dir.name
        pairs = [p for p in series_pairs() if (p[0] <= here if series else p[0] == here)]
        if not pairs:
            return
        raw = map_layout([(a, b) for _, a, b in pairs])
        pts = np.array(list(raw.values()))
        lo, hi = pts.min(axis=0), pts.max(axis=0)
        span = np.maximum(hi - lo, 1e-6)
        s = min((STAGE_WIDTH - 3.0) / span[0], 4.0 / span[1], 1.6)
        pos = {name: STAGE_CENTER + (p - (lo + hi) / 2) * s for name, p in raw.items()}
        current = next(((a, b) for slug, a, b in pairs if slug == here), None)
        old_edges = VGroup(*[Line(pos[a], pos[b], stroke_width=3, stroke_color=FAINT)
                             for slug, a, b in pairs if slug != here])
        dots, labels = {}, VGroup()
        for name in raw:
            if current and name in current:
                side = current.index(name)
                color = (A_COLOR, B_COLOR)[side]
                if icons:
                    mark = icons[side].copy()
                    mark.scale_to_fit_height(min(1.3, mark.height * 1.3 / max(mark.width, mark.height)))
                else:
                    mark = VGroup(Circle(radius=0.5, color=color, stroke_width=5, fill_color=color, fill_opacity=0.12),
                                  Dot(radius=0.12, color=color))
                dots[name] = mark.move_to(pos[name])
                labels.add(parts.title(name.upper(), 30, color).next_to(mark, DOWN, buff=0.22))
            else:
                dots[name] = Dot(pos[name], radius=0.09, color=MUTED)
                labels.add(Text(name, font=BODY_FONT, font_size=22, color=MUTED, weight=BOLD)
                           .next_to(dots[name], DOWN, buff=0.16))
        graph = VGroup(old_edges, *dots.values(), labels)
        heading = Text("CONNECTION MAP", font=TITLE_FONT, font_size=LABEL_SIZE, color=MUTED)
        heading.next_to(graph, UP, buff=0.5)
        words = VGroup(*[parts.title(line, 40, LINK_COLOR if i == 0 else INK) for i, line in enumerate(tagline)])
        if tagline:
            words.arrange(DOWN, buff=0.10).next_to(graph, DOWN, buff=0.5)
        composition = VGroup(graph, *([heading] if title else []), *([words] if tagline else []))
        composition.set_x(STAGE_CENTER[0])  # labels differ in width; center what the viewer sees
        with self.alignment_loop("Connection map") as align:
            align.centered(composition)
            align.inside_safe(composition)
        show = [*[FadeIn(m) for m in intro], FadeIn(old_edges), *[GrowFromCenter(d) for d in dots.values()],
                FadeIn(labels), *([FadeIn(heading)] if title else [])]
        if not current:
            self.play(*show, run_time=run_time)
            return
        ca, cb = (dots[name].get_center() for name in current)
        way = normalize(cb - ca)
        a = ca + way * dots[current[0]].width / 2   # the link and arrows meet the node edges
        b = cb - way * dots[current[1]].width / 2
        link = Line(a, b, stroke_width=10).set_color([A_COLOR, LINK_COLOR, B_COLOR])
        link.set_sheen_direction(way)  # Manim's default runs gradients from the far end
        lift = 0.24 * UP
        share = (0.16, 0.22, 0.22, 0.16, 0.24) if both_ways else (0.35, 0.0, 0.0, 0.40, 0.25)
        t = [run_time * x for x in share]
        self.play(*show, run_time=t[0])
        arrows = VGroup()
        if both_ways:
            arrows.add(Arrow(a + lift, b + lift, buff=0.12, color=A_COLOR, stroke_width=6))
            self.play(GrowArrow(arrows[0]), run_time=t[1])
            arrows.add(Arrow(b - lift, a - lift, buff=0.12, color=B_COLOR, stroke_width=6))
            self.play(GrowArrow(arrows[1]), run_time=t[2])
        if sound:
            self.sfx(sound, gain=-12)
        merge = [FadeOut(arrows)] if both_ways else []
        self.play(*merge, Create(link), Flash(link.get_center(), color=LINK_COLOR, flash_radius=0.9), run_time=t[3])
        self.bring_to_back(link)
        if tagline:
            self.play(FadeIn(words, shift=0.2 * UP), run_time=t[4])
        else:
            self.wait(t[4])


def map_layout(pairs: list[tuple[str, str]]) -> dict[str, np.ndarray]:
    """Raw Connection Map positions, before scaling to the stage.

    Each episode's pair is a short left/right link in its own slot: the first at the
    center (the way Episode 001 ends), the rest spiral out on the golden angle starting
    below it, so links never cross. A node never moves once placed: the map grows.
    """
    raw: dict[str, np.ndarray] = {}
    for p, (a, b) in enumerate(pairs):
        if p == 0:
            center, half = np.zeros(3), 1.0
        else:
            r, ang = 1.6 * math.sqrt(p), -math.pi / 2 + (p - 1) * 2.39996
            center, half = np.array([r * math.cos(ang), r * math.sin(ang), 0.0]), 0.8
        for name, side in ((a, -1.0), (b, 1.0)):
            if name not in raw:
                raw[name] = center + np.array([side * half, 0.0, 0.0])
    return raw


def series_pairs() -> list[tuple[str, str, str]]:
    """(episode, A label, B label) for every episode script, in episode order."""
    pairs = []
    for path in sorted((ROOT / "episodes").glob("*/script.md")):
        try:
            s = load_script(path)
        except (OSError, ValueError):
            continue
        a, b = s.theme("a").label, s.theme("b").label
        if a and b:
            pairs.append((path.parent.name, a, b))
    return pairs


class Captions(VGroup):
    """Burned-in captions, timed against scene time and split into short chunks.

    All chunks of the current beat stay in the group and only their opacity changes.
    Manim lists the moving mobjects once per animation, so a chunk that was swapped
    out in the middle of an animation would still be drawn.
    """

    def __init__(self, scene: Scene):
        super().__init__()
        self.scene = scene
        self.cues: list[tuple[float, float, Mobject]] = []
        self.shown = None
        self.add_updater(lambda m, dt: m.sync())

    def schedule(self, text: str, start: float, duration: float, colors: dict[str, str]):
        """Replace the previous beat's chunks. Call between animations, never inside one."""
        self.remove(*self.submobjects)
        self.cues, self.shown = [], None
        chunks = caption_chunks(text)
        total = sum(len(c) for c in chunks)
        t = start
        for chunk in chunks:
            d = duration * len(chunk) / total
            cue = show_caption(caption_mobject(chunk, colors), False)
            self.add(cue)
            self.cues.append((t, t + d, cue))
            t += d

    def sync(self):
        now = self.scene.time
        cue = next((m for t0, t1, m in self.cues if t0 <= now < t1), None)
        if cue is not self.shown:
            if self.shown is not None:
                show_caption(self.shown, False)
            if cue is not None:
                show_caption(cue, True)
            self.shown = cue


def show_caption(cue: Mobject, visible: bool) -> Mobject:
    box, label = cue
    box.set_fill(opacity=0.75 if visible else 0)
    label.set_opacity(1 if visible else 0)
    return cue


def caption_chunks(text: str, max_words: int = 3) -> list[str]:
    chunks, cur = [], []
    for word in text.split():
        cur.append(word)
        if len(cur) >= max_words or word[-1] in ".,;:?!":
            chunks.append(" ".join(cur))
            cur = []
    if cur:
        chunks.append(" ".join(cur))
    return chunks


def colorize(text: str, colors: dict[str, str]) -> str:
    """Pango markup with each keyword wrapped in its theme color."""
    out = html.escape(text, quote=False)
    if not colors:
        return out
    pattern = re.compile(
        r"\b(" + "|".join(re.escape(k) for k in sorted(colors, key=len, reverse=True)) + r")\b",
        re.IGNORECASE,
    )
    return pattern.sub(lambda m: f'<span foreground="{colors[m.group(0).lower()]}">{m.group(0)}</span>', out)


_CAPTION_BOX_H = None


def caption_mobject(text: str, colors: dict[str, str]) -> Mobject:
    global _CAPTION_BOX_H
    if _CAPTION_BOX_H is None:
        _CAPTION_BOX_H = MarkupText("Hg", font=BODY_FONT, weight=BOLD, font_size=CAPTION_SIZE).height + 0.36
    label = MarkupText(colorize(text, colors), font=BODY_FONT, weight=BOLD, font_size=CAPTION_SIZE, color=INK)
    if label.width > STAGE_WIDTH - 0.5:
        label.scale_to_fit_width(STAGE_WIDTH - 0.5)
    box = RoundedRectangle(corner_radius=0.16, width=label.width + 0.5, height=_CAPTION_BOX_H,
                           fill_color=BG, fill_opacity=0.75, stroke_width=0)
    return VGroup(box, label.move_to(box)).move_to(CAPTION_CENTER).set_z_index(100)


def safe_zone_guides() -> Mobject:
    """Overlay that marks where the Shorts UI covers the video (approximate)."""
    red = "#FF5C5C"
    safe = Rectangle(width=SAFE_RIGHT - SAFE_LEFT, height=SAFE_TOP - SAFE_BOTTOM, stroke_color=red, stroke_width=2)
    safe.move_to(SAFE_CENTER)
    covered = VGroup(
        Rectangle(width=FRAME_W, height=FRAME_H / 2 + SAFE_BOTTOM).align_to(FRAME_H / 2 * DOWN, DOWN),
        Rectangle(width=FRAME_W / 2 - SAFE_RIGHT, height=FRAME_H).align_to(FRAME_W / 2 * RIGHT, RIGHT),
        Rectangle(width=FRAME_W, height=FRAME_H / 2 - SAFE_TOP).align_to(FRAME_H / 2 * UP, UP),
    ).set_style(fill_color=red, fill_opacity=0.15, stroke_width=0)
    note = Text("Shorts UI (approx.)", font=BODY_FONT, font_size=18, color=red).next_to(safe, DOWN, buff=0.1)
    return VGroup(covered, DashedVMobject(safe, num_dashes=80), note).set_z_index(200)
