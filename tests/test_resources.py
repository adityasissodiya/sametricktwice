"""The rules of resources/: it only draws, has no words or colors of its own, and stays pinned."""

from __future__ import annotations

import ast
import json
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

try:
    import manim  # noqa: F401
except ImportError:  # e.g. a runner without the render stack
    raise unittest.SkipTest("needs the render stack (manim)")

from manim import AnimationGroup, ArcBetweenPoints, Line, Mobject, Rectangle, Square, VGroup, linear

import kit.parts
import kit.style
import resources
from kit.alignment import AlignmentLoop, visual_box
from kit.short import ShortScene, caption_mobject
from kit.style import A_COLOR, ALERT, B_COLOR, BG, INK, LINK_COLOR, MUTED
from resources import (PANEL_OPACITY, Flow, StageTools, backdrop, between, bridge, dim, gallery, icons, light, panel,
                       phase_pills, route, stage_box, stamp, swap, tween)
from tests.episode_fixture import write_brief, write_script
from tools import design, lint, visual_quality

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "resources"
BLOCKS = {name: HERE / f"{name}.py" for name in ("stage", "moves", "parts", "icons")}
APPROVAL = ("A frozen part changed its shape. A re-render of a finished video would pick that up, so it needs the "
            "creator's approval (AGENTS.md); then run: vid uv run python -m resources.gallery --pin")


def module_names(path: Path) -> set[str]:
    """Strings in a module's __all__, which are names, not words on screen."""
    names = set()
    for node in ast.parse(path.read_text(encoding="utf-8")).body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "__all__":
            names |= {e.value for e in node.value.elts}
    return names


class BlockRuleTests(unittest.TestCase):
    def test_nothing_plays_because_the_gates_read_motion_in_scene_py_only(self):
        for name, path in BLOCKS.items():
            for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
                if isinstance(node, ast.Call) and getattr(node.func, "attr", "") == "play":
                    self.fail(f"resources/{name}.py:{node.lineno} calls play; return an animation instead")

    def test_no_words_because_lint_reads_them_in_scene_py_only(self):
        for name, path in BLOCKS.items():
            self.assertEqual(lint.screen_strings(path) - module_names(path), set(), f"resources/{name}.py has words")

    def test_no_colors_of_their_own(self):
        for name, path in BLOCKS.items():
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source)
            for node in ast.walk(tree):
                if isinstance(node, ast.Constant) and isinstance(node.value, str):
                    self.assertIsNone(design.HEX.search(node.value), f"resources/{name}.py has a hex color")
                if isinstance(node, ast.Name):
                    self.assertIsNone(design.NAMED_COLOR.match(node.id), f"resources/{name}.py uses {node.id}")

    def test_no_empty_groups_which_add_a_point_at_the_origin(self):
        for name, (build, _) in gallery.catalogue().items():
            for part in build().get_family():
                self.assertFalse(isinstance(part, VGroup) and not part.submobjects, f"{name} has an empty VGroup")

    def test_a_scene_star_import_gets_the_catalogue(self):
        for name in resources.__all__:
            self.assertTrue(hasattr(resources, name), name)


class FrozenShapeTests(unittest.TestCase):
    def test_every_part_keeps_its_pinned_shape(self):
        pins = json.loads((HERE / "frozen.json").read_text(encoding="utf-8"))
        live = gallery.pins()
        self.assertEqual(set(live), set(pins), APPROVAL)
        for name, pin in pins.items():
            for key, value in pin.items():
                self.assertAlmostEqual(live[name][key], value, delta=0.002, msg=f"{name}.{key}. {APPROVAL}")

    def test_every_icon_is_centered_and_scales(self):
        for name in icons.__all__:
            if name == "plate":
                continue
            base, big = getattr(icons, name)(), getattr(icons, name)(size=2.0)
            self.assertAlmostEqual(float(abs(base.get_center()).max()), 0.0, places=6, msg=name)
            self.assertAlmostEqual(big.height, 2 * base.height, places=3, msg=name)

    def test_the_gallery_shows_every_icon(self):
        self.assertLessEqual(set(icons.__all__), set(gallery.catalogue()))
        self.assertTrue(gallery.GALLERY.exists())


class PageTests(unittest.TestCase):
    def test_the_readme_lists_every_name(self):
        page = (HERE / "README.md").read_text(encoding="utf-8")
        for name in [*resources.__all__, *icons.__all__]:
            self.assertTrue(re.search(rf"\b{name}\b", page), f"add {name} to the catalogue in resources/README.md")
        for method in ("header", "onscreen", "on_stage", "cut", "fits", "breath"):
            self.assertTrue(f"StageTools.{method}" in page, f"add StageTools.{method} to resources/README.md")

    def test_the_kit_page_lists_every_public_kit_name(self):
        page = (HERE / "KIT.md").read_text(encoding="utf-8")
        landscape = ast.parse((ROOT / "kit" / "landscape.py").read_text(encoding="utf-8"))
        wide = {n.name for n in landscape.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
        for node in landscape.body:
            if isinstance(node, ast.Assign):  # `SAFE_LEFT, SAFE_RIGHT = ...`, but not `config.x = ...`
                targets = [t for g in node.targets for t in (g.elts if isinstance(g, ast.Tuple) else [g])]
                wide |= {t.id for t in targets if isinstance(t, ast.Name)}
        names = [*kit.style.__all__, *kit.parts.__all__, *sorted(n for n in wide if not n.startswith("_")),
                 *(n for n, v in vars(ShortScene).items()
                   if callable(v) and not n.startswith("_") and n not in ("setup", "tear_down")),
                 *(n for n, v in vars(AlignmentLoop).items()
                   if callable(v) and not n.startswith("_") and n not in ("from_environment",)),
                 "DEFAULT_TOLERANCE", "DEFAULT_MAX_PASSES", "Box", "visual_box", "AlignmentError",
                 *(p.name for p in (ROOT / "kit" / "sfx").glob("*.wav"))]
        for name in names:
            self.assertTrue(re.search(rf"\b{re.escape(name)}\b", page), f"add {name} to resources/KIT.md")


class ExampleSceneTests(unittest.TestCase):
    def test_it_passes_every_source_rule(self):
        with tempfile.TemporaryDirectory() as tmp:
            ep = Path(tmp) / "example"
            ep.mkdir()
            write_script(ep, front={"format": "landscape"})
            write_brief(ep)
            shutil.copy(HERE / "example_scene.py", ep / "scene.py")
            failed = [(r.rule, r.issues) for r in design.check(ep, final=True) if r.status == "fail"]
        self.assertEqual(failed, [])

    def test_it_has_no_dict_literals_for_lint_to_misread(self):
        tree = ast.parse((HERE / "example_scene.py").read_text(encoding="utf-8"))
        self.assertFalse([n.lineno for n in ast.walk(tree) if isinstance(n, ast.Dict)])


class MoveTests(unittest.TestCase):
    def test_between_runs_only_inside_its_part(self):
        rate = between(0.2, 0.6)
        self.assertEqual(rate(0.1), 0.0)
        self.assertEqual(rate(0.8), 1.0)
        self.assertTrue(0.0 < rate(0.4) < 1.0)

    def test_swap_takes_the_old_out_before_the_new_comes_in(self):
        group = swap(Square(), Square(), at=0.4)
        self.assertIsInstance(group, AnimationGroup)
        out, into = group.animations
        self.assertEqual(out.rate_func(0.5), 1.0)
        self.assertEqual(into.rate_func(0.3), 0.0)

    def test_route_joins_points_or_mobjects_straight_or_arced(self):
        a, z = Square().move_to([-1, 0, 0]), [2.0, 1.0, 0.0]
        self.assertIsInstance(route(a, z), Line)
        arc = route(a, z, angle=1.0)
        self.assertIsInstance(arc, ArcBetweenPoints)
        for path in (route(a, z), arc):
            self.assertAlmostEqual(float(abs(path.get_start() - a.get_center()).max()), 0.0, places=6)
            self.assertAlmostEqual(float(abs(path.get_end() - z).max()), 0.0, places=6)

    def test_tween_sets_a_number_or_a_sequence(self):
        seen = []
        mob = Mobject()
        tween(mob, lambda m, v: seen.append(v), 0.0, 10.0, rate_func=linear).interpolate_mobject(0.5)
        tween(mob, lambda m, v: seen.append(v), (0.0, 1.0), (1.0, 3.0), rate_func=linear).interpolate_mobject(0.5)
        self.assertEqual(seen, [5.0, [0.5, 2.0]])


class PartTests(unittest.TestCase):
    def test_a_panel_stays_behind_the_drawing_on_it(self):
        self.assertEqual(panel(2, 2, A_COLOR).z_index, -1)

    def test_the_default_tint_counts_as_picture_for_every_color_you_would_tint_with(self):
        for color in (A_COLOR, B_COLOR, LINK_COLOR, ALERT, INK, MUTED):
            base, tint = [bytes.fromhex(c[1:]) for c in (BG, color)]
            pixel = bytes(round(b + (t - b) * PANEL_OPACITY) for b, t in zip(base, tint))
            self.assertTrue(visual_quality.foreground_mask(pixel, (1, 1))[0], f"{color} at {PANEL_OPACITY}")

    def test_pills_number_their_words_and_light_up(self):
        pills = phase_pills(("ONE", "TWO", "THREE"))
        self.assertEqual(len(pills), 3)
        self.assertLess(pills[0].get_x(), pills[1].get_x())
        self.assertIsInstance(light(pills[0], A_COLOR), AnimationGroup)
        self.assertIsInstance(dim(pills[0]), AnimationGroup)

    def test_a_bridge_starts_and_ends_at_the_borders(self):
        left, right = Square(1.0).move_to([-3, 0, 0]), Square(1.0).move_to([3, 1, 0])
        link = bridge(left, right)
        self.assertGreater(link.get_start()[0], left.get_right()[0])
        self.assertLess(link.get_end()[0], right.get_left()[0])

    def test_a_flow_runs_queues_and_stops(self):
        flow = Flow([-2, 0, 0], [2, 0, 0])
        start = list(flow.alphas)
        flow.advance(0.1)
        self.assertNotEqual(flow.alphas, start)
        flow.hold_at = 0.5
        for _ in range(200):
            flow.advance(0.1)
        waiting = [a for a in flow.alphas if a <= 0.5]
        self.assertAlmostEqual(max(waiting), 0.5)
        self.assertEqual(flow.stop().get_updaters(), [])

    def test_a_stamp_sits_above_the_stage(self):
        self.assertEqual(stamp("WORD", B_COLOR).z_index, 5)

    def test_a_plate_holds_a_wide_or_a_tall_drawing_inside_it(self):
        for drawing in (Rectangle(width=4.0, height=1.0), Rectangle(width=1.0, height=4.0)):
            board, inner = icons.plate(drawing, A_COLOR)
            self.assertLess(inner.width, board.width)
            self.assertLess(inner.height, board.height)

    def test_a_padlock_swings_about_its_hinge_after_scaling(self):
        lock = icons.padlock(INK, 2.0)
        self.assertAlmostEqual(float(abs(lock.hinge() - lock.shackle[0].get_start()).max()), 0.0)
        self.assertIs(lock.recolor(A_COLOR), lock)


class StubScene(StageTools):
    """What StageTools needs from ShortScene, without a voice or a renderer."""

    def __init__(self):
        self.mobjects, self.waited = [], []
        self.cc, self.guides, self.alignment_guides = Mobject(), None, None
        self.add(self.cc)

    def add(self, *mobjects):
        self.mobjects.extend(mobjects)

    def remove(self, *mobjects):
        self.mobjects = [m for m in self.mobjects if not any(m is x for x in mobjects)]

    def wait(self, seconds):
        self.waited.append(seconds)

    def alignment_loop(self, label):
        return AlignmentLoop(label, on_failure="raise")


class StageToolTests(unittest.TestCase):
    def test_a_new_header_replaces_the_old_one_at_once(self):
        scene = StubScene()
        first = scene.header(1, "One", A_COLOR)
        second = scene.header(2, "Two", A_COLOR)
        self.assertFalse(any(m is first for m in scene.mobjects))
        self.assertTrue(any(m is second for m in scene.mobjects))

    def test_on_stage_leaves_out_what_stays_and_makes_it_top_level(self):
        scene = StubScene()
        scene.header(1, "One", A_COLOR)
        gone, kept, part = Square(), Square(), Square()
        scene.add(gone, VGroup(kept, part))
        rest = scene.on_stage(kept)
        self.assertTrue(any(m is kept for m in scene.mobjects))
        self.assertFalse(any(m is kept or m is scene.cc or m is scene.top for m in rest))
        self.assertTrue(any(m is gone for m in rest))

    def test_a_cut_leaves_only_the_captions_and_the_header(self):
        scene = StubScene()
        scene.header(1, "One", A_COLOR)
        scene.add(Square(), Square())
        scene.cut()
        self.assertEqual(len(scene.mobjects), 2)

    def test_fits_moves_a_stray_into_the_stage_but_never_rescales_it(self):
        scene = StubScene()
        stray = Square(1.0).move_to([0, 4.8, 0])
        scene.fits("stray", stray)
        box = visual_box(stray)
        self.assertLessEqual(box.top, stage_box().top + 0.05)
        self.assertAlmostEqual(stray.width, 1.0)

    def test_breath_is_silence(self):
        scene = StubScene()
        scene.breath()
        self.assertEqual(scene.waited, [resources.BREATH])

    def test_the_tall_stage_sits_between_the_header_and_the_captions(self):
        box = stage_box()
        self.assertGreater(kit.parts.beat_header(1, "One", A_COLOR).get_bottom()[1], box.top)
        self.assertLess(caption_mobject("three short words", {}).get_top()[1], box.bottom)

    def test_a_backdrop_stays_on_the_stage(self):
        box, shade = stage_box(), backdrop(A_COLOR)
        self.assertLess(shade.width, box.width)
        self.assertLess(shade.height, box.height)
        self.assertAlmostEqual(shade.get_x(), box.center_x)


# kit.landscape changes Manim's global frame when imported, so this runs in a child process.
WIDE_PROBE = textwrap.dedent("""
    import json, sys
    import resources
    alone = "kit.landscape" in sys.modules
    from kit.landscape import *
    from resources import *
    box = stage_box()
    shade = backdrop(A_COLOR)
    class Stub(StageTools):
        mobjects = []
        def add(self, *m): pass
        def remove(self, *m): pass
    print(json.dumps({
        "imported_alone": alone,
        "same_stage": box == STAGE_BOX,
        "header_left": float(Stub().header(1, "One", A_COLOR).get_left()[0]),
        "safe_left": SAFE_LEFT,
        "shade_inside": bool(shade.width < box.width and shade.height < box.height),
        "frame": config.frame_width,
    }))
""")


class WideFormatTests(unittest.TestCase):
    def test_resources_follow_the_format_the_scene_chose_and_never_choose_one(self):
        out = subprocess.run([sys.executable, "-c", WIDE_PROBE], cwd=ROOT, capture_output=True, text=True, check=True)
        g = json.loads(out.stdout.strip().splitlines()[-1])
        self.assertFalse(g["imported_alone"], "resources must never import kit.landscape")
        self.assertTrue(g["same_stage"])
        self.assertAlmostEqual(g["header_left"], g["safe_left"], places=2)
        self.assertTrue(g["shade_inside"])
        self.assertGreater(g["frame"], 14)


class PrivacyTests(unittest.TestCase):
    """Specials can come from unpublished work. Runs only where they exist: never on a public clone."""

    @classmethod
    def setUpClass(cls):
        cls.specials = sorted(p.name for p in (ROOT / "specials").glob("*") if p.is_dir())
        if not cls.specials:
            raise unittest.SkipTest("no specials on this machine")

    def publishable(self) -> list[Path]:
        out = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard"], cwd=ROOT,
                             capture_output=True, text=True, check=True)
        suffixes = {".py", ".md", ".toml", ".txt", ".json", ".html", ".css", ".js", ".ps1", ".cmd", ".srt", ".csv", ""}
        return [ROOT / line for line in out.stdout.splitlines() if Path(line).suffix in suffixes]

    def test_git_would_not_publish_a_special(self):
        for path in self.publishable():
            self.assertNotEqual(path.relative_to(ROOT).parts[0], "specials", path)

    def test_no_publishable_file_names_a_special(self):
        for path in self.publishable():
            if not path.is_file():
                continue
            source = path.read_text(encoding="utf-8", errors="ignore").lower()
            for name in self.specials:
                self.assertFalse(name.lower() in source, f"{path.relative_to(ROOT)} names a private special")


if __name__ == "__main__":
    unittest.main()
