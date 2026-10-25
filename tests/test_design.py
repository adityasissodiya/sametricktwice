"""Tests for the research-backed design rules (tools/design.py): one broken rule at a time."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tests.episode_fixture import BEATS, make_episode, write_brief, write_scene, write_script
from tools import design


class DesignRuleTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ep = make_episode(Path(self.tmp.name))

    def tearDown(self):
        self.tmp.cleanup()

    def failed(self, final: bool = False) -> dict[str, list[str]]:
        return {r.rule: r.issues for r in design.check(self.ep, final) if r.status == "fail"}

    def with_beats(self, **changes: str) -> None:
        write_script(self.ep, {**BEATS, **changes})

    def motion(self) -> dict[str, design.Result]:
        wanted = {"motion-timing", "motion-coverage", "recognition-replay"}
        return {r.rule: r for r in design.check(self.ep) if r.rule in wanted}

    def test_the_fixture_passes_every_rule(self):
        self.assertEqual(self.failed(final=True), {})

    def test_bridge_must_be_one_short_sentence(self):
        write_brief(self.ep, bridge="Kettles push lids. Rockets push loads.")
        self.assertIn("one-goal", self.failed())
        write_brief(self.ep, bridge=" ".join(["word"] * 31) + ".")
        self.assertIn("one-goal", self.failed())
        write_brief(self.ep, bridge="?")
        self.assertIn("one-goal", self.failed())

    def test_hook_is_short_and_names_both_worlds(self):
        self.with_beats(B1="Every rocket that ever flew uses an idea from a small copper kettle in a cold 1900 kitchen.")
        self.assertIn("hook-length", self.failed())
        self.with_beats(B1="Every rocket uses an idea from 1900.")
        self.assertEqual(self.failed(), {"hook-relevance": ["B1 does not name world A (one of: Kettle, kettle, kettles, lid)"]})

    def test_no_greeting_or_intro_before_the_claim(self):
        self.with_beats(B1="Hi, every rocket uses an idea from a kettle.")
        self.assertIn("cold-open", self.failed())
        self.with_beats(B1="In this video, every rocket meets a kettle.")
        self.assertIn("cold-open", self.failed())
        self.with_beats()
        write_scene(self.ep, body='        self.wait(1)\n        with self.beat("B1") as b:\n            pass\n'
                    + "".join(f'        with self.beat("{b}") as b:\n            pass\n' for b in list(BEATS)[1:]))
        issues = self.failed()["cold-open"]
        self.assertEqual(len(issues), 1)
        self.assertRegex(issues[0], r"scene\.py runs self\.wait\(\) on line \d+ before B1")

    def test_the_mechanism_must_come_early(self):
        long_setup = "In 1900, a cook watched the lid of her kettle jump on the stove in a cold room."
        self.with_beats(B2=" ".join([long_setup] * 3), B5="Rocket makers needed a push.")
        self.assertIn("early-answer", self.failed())

    def test_each_beat_is_a_micro_unit(self):
        self.with_beats(B5=" ".join(["Rocket"] * 31) + ".")
        self.assertIn("micro-units", self.failed())
        self.with_beats(B5="Rockets fly. They need a push. Fuel burns. Gas pushes.")
        self.assertIn("B5 has 4 sentences (max 3)", self.failed()["micro-units"])

    def test_every_spoken_beat_needs_delivery_direction(self):
        script = (self.ep / "script.md").read_text(encoding="utf-8")
        script = script.replace(
            "NOTE: Keep the line clear; shape its pace and emphasis.\n",
            "",
            1,
        )
        (self.ep / "script.md").write_text(script, encoding="utf-8")
        issues = self.failed()["delivery-notes"]
        self.assertEqual(len(issues), 1)
        self.assertIn("B1 has no NOTE", issues[0])

    def test_abbreviations_do_not_end_a_sentence(self):
        text = "In 1957, two scientists at a U.S. Army lab needed tiny transistors. Jay Lathrop flipped it."
        self.assertEqual(len(design.sentences(text)), 2)
        self.assertEqual(design.sentences("Around c. 1827 it began. Then it grew!"),
                         ["Around c. 1827 it began.", "Then it grew!"])

    def test_length_must_fit_the_target(self):
        self.with_beats(B2="In 1900, a cook saw it.", B3="Steam needs room.", B5="Rockets need a push.",
                        B6="They used the same trick.", B7="Then rockets helped kettles.", B8="Today it is everywhere.")
        self.assertIn("length", self.failed())

    def test_on_screen_text_is_short_and_never_echoes_the_narration(self):
        write_script(self.ep, txt={"B4": "Heat makes the steam push"})
        self.assertIn("B4 TXT is 5 words (max 4)", self.failed()["minimal-text"])
        write_script(self.ep, txt={})
        write_scene(self.ep, body="".join(f'        with self.beat("{b}") as b:\n            pass\n' for b in BEATS)
                    + '        text("The steam needs much", 24, INK)\n'
                    + '        text("ONE TWO THREE FOUR FIVE SIX", 24, INK)\n')
        issues = self.failed()["minimal-text"]
        self.assertTrue(any("repeats the narration ('the steam needs much')" in i for i in issues), issues)
        self.assertTrue(any("is 6 words (max 5)" in i for i in issues), issues)

    def test_title_is_short_and_names_both_worlds(self):
        write_script(self.ep, front={"title": "Every rocket uses an idea from a kettle, and here is how it all began"})
        self.assertIn("title", self.failed())
        write_script(self.ep, front={"title": "Every rocket uses an idea from 1900"})
        self.assertEqual(self.failed()["title"], ["the title does not name world A"])
        write_script(self.ep, front={"title": ""})
        self.assertIn("title", self.failed())

    def test_every_beat_is_in_the_ledger_and_every_claim_has_a_link(self):
        write_brief(self.ep, rows=[
            "| C1 | A cook saw a kettle lid jump (B1-B3) | [museum](https://example.org/kettle) | | high |",
            "| C2 | Rockets lift loads (B5, B6, B7, B8) | a book I read | | high |",
            "| C3 | Steam needs room | follows from C1 | | high |",
        ])
        issues = self.failed()["sourced"]
        self.assertIn("B4 is not in the claim ledger: add a claim row with sources, or a framing row (F#) "
                      "if it states no new fact", issues)
        self.assertIn("C2 has no source link", issues)
        self.assertIn("C3 names no beat: end its claim with the beats, e.g. (B2)", issues)
        self.assertFalse(any(i.startswith("C3 has no source") for i in issues))

    def test_colors_stay_in_the_semantic_families(self):
        body = "".join(f'        with self.beat("{b}") as b:\n            pass\n' for b in BEATS)
        write_scene(self.ep, body=body + '        x = ("#1B2130", "#D9B45B", "#8A93A5", A_COLOR, "#FF5C5C")\n')
        self.assertNotIn("color-signals", self.failed())
        write_scene(self.ep, body=body + '        x = ("#00FF66", GREEN)\n')
        issues = self.failed()["color-signals"]
        self.assertEqual(len(issues), 2, issues)
        self.assertIn("#00FF66 is outside", issues[0])
        self.assertIn("Manim color GREEN", issues[1])

    def test_scene_speaks_every_beat_once_in_order(self):
        write_scene(self.ep, beats=[b for b in BEATS if b != "B7"])
        self.assertIn("never spoken in scene.py: B7", self.failed()["every-beat"])
        order = list(BEATS)
        order[1], order[2] = order[2], order[1]
        write_scene(self.ep, beats=order)
        self.assertEqual(self.failed()["every-beat"], ["the beats are out of script order"])

    def test_placeholders_block_only_the_final(self):
        body = "".join(f'        with self.beat("{b}") as b:\n            self.placeholder(b)\n' for b in BEATS)
        write_scene(self.ep, body=body)
        self.assertNotIn("every-beat", self.failed(final=False))
        self.assertIn("every-beat", self.failed(final=True))

    def test_fixed_animation_seconds_fail_even_inside_a_helper(self):
        scene = (self.ep / "scene.py").read_text(encoding="utf-8")
        scene = scene.replace("run_time=run_time", "run_time=0.60", 1)
        (self.ep / "scene.py").write_text(scene, encoding="utf-8")
        issues = self.failed()["motion-timing"]
        self.assertTrue(any("self.mechanism hard-codes animation seconds" in i for i in issues), issues)

    def test_missing_run_time_fails_inside_a_reachable_helper(self):
        scene = (self.ep / "scene.py").read_text(encoding="utf-8")
        scene = scene.replace(", run_time=run_time)", ")", 1)
        (self.ep / "scene.py").write_text(scene, encoding="utf-8")
        issues = self.failed()["motion-timing"]
        self.assertTrue(any("self.mechanism has self.play without run_time" in i for i in issues), issues)

    def test_a_helper_call_must_pass_its_motion_budget_explicitly(self):
        scene = (self.ep / "scene.py").read_text(encoding="utf-8")
        scene = scene.replace("self.mechanism(A_COLOR, self.replay_time)",
                              "self.mechanism(A_COLOR)")
        (self.ep / "scene.py").write_text(scene, encoding="utf-8")
        issues = self.failed()["motion-timing"]
        self.assertTrue(any("does not receive run_time" in i for i in issues), issues)

    def test_one_clock_must_drive_every_phase_inside_a_helper(self):
        scene = (self.ep / "scene.py").read_text(encoding="utf-8")
        scene = scene.replace(
            "def mechanism(self, skin, run_time):\n"
            "        mark = Circle(color=skin)\n"
            "        self.play(mark.animate.shift(0.2 * RIGHT), run_time=run_time)",
            "def mechanism(self, skin, enter_time, move_time):\n"
            "        mark = Circle(color=skin)\n"
            "        self.play(FadeIn(mark), run_time=enter_time)\n"
            "        self.play(mark.animate.shift(0.2 * RIGHT), run_time=move_time)",
        )
        scene = scene.replace("self.mechanism(A_COLOR, self.replay_time)",
                              "self.mechanism(A_COLOR, self.replay_time, self.replay_time)")
        scene = scene.replace("self.mechanism(B_COLOR, self.replay_time)",
                              "self.mechanism(B_COLOR, self.replay_time, self.replay_time)")
        (self.ep / "scene.py").write_text(scene, encoding="utf-8")
        issues = self.failed()["motion-timing"]
        self.assertTrue(any("splits its animation clock across unrelated parameters" in i for i in issues), issues)

    def test_an_unused_draft_helper_does_not_fail_the_rendered_scene(self):
        scene = (self.ep / "scene.py").read_text(encoding="utf-8")
        unused = ("    def unused_draft(self):\n"
                  "        self.play(FadeIn(Dot()), run_time=0.25)\n\n")
        scene = scene.replace("    def construct(self):\n", unused + "    def construct(self):\n")
        (self.ep / "scene.py").write_text(scene, encoding="utf-8")
        self.assertEqual(self.motion()["motion-timing"].status, "pass")

    def test_every_play_tracks_the_approved_narration(self):
        scene = (self.ep / "scene.py").read_text(encoding="utf-8")
        scene = scene.replace("run_time=b.duration * 0.80", "run_time=0.80", 1)
        (self.ep / "scene.py").write_text(scene, encoding="utf-8")
        issues = self.failed()["motion-timing"]
        self.assertTrue(any("uses fixed run_time=0.8" in i for i in issues), issues)

    def test_a_beat_cannot_leave_most_of_its_narration_as_a_static_hold(self):
        scene = (self.ep / "scene.py").read_text(encoding="utf-8")
        old = ('mark = text("B8 label", 24, A_COLOR)\n'
               '            self.play(mark.animate.shift(0.2 * RIGHT), run_time=b.duration * 0.80)')
        new = ('mark = text("B8 label", 24, A_COLOR)\n'
               '            self.play(mark.animate.shift(0.2 * RIGHT), run_time=b.duration * 0.20)')
        self.assertIn(old, scene)
        (self.ep / "scene.py").write_text(scene.replace(old, new), encoding="utf-8")
        issues = self.failed()["motion-coverage"]
        self.assertTrue(any(i.startswith("B8 schedules about 20%") for i in issues), issues)
        self.assertNotIn("motion-timing", self.failed())

    def test_motion_coverage_adds_sequential_narration_relative_plays(self):
        scene = (self.ep / "scene.py").read_text(encoding="utf-8")
        old = 'self.play(mark.animate.shift(0.2 * RIGHT), run_time=b.duration * 0.80)'
        new = ('self.play(mark.animate.shift(0.1 * RIGHT), run_time=b.duration * 0.34)\n'
               '            self.play(mark.animate.shift(0.1 * RIGHT), run_time=b.duration * 0.34)')
        # Change B8 only; the earlier beats remain useful controls at 80% coverage.
        marker = 'mark = text("B8 label", 24, A_COLOR)\n            ' + old
        self.assertIn(marker, scene)
        scene = scene.replace(marker, 'mark = text("B8 label", 24, A_COLOR)\n            ' + new)
        (self.ep / "scene.py").write_text(scene, encoding="utf-8")
        motion = self.motion()
        self.assertEqual(motion["motion-coverage"].status, "pass")
        self.assertIn("68%", motion["motion-coverage"].detail)

    def test_motion_coverage_threshold_is_inclusive(self):
        scene = (self.ep / "scene.py").read_text(encoding="utf-8")
        marker = ('mark = text("B8 label", 24, A_COLOR)\n'
                  '            self.play(mark.animate.shift(0.2 * RIGHT), run_time=b.duration * 0.80)')
        at_limit = marker.replace("0.80", "0.65")
        self.assertIn(marker, scene)
        (self.ep / "scene.py").write_text(scene.replace(marker, at_limit), encoding="utf-8")
        self.assertEqual(self.motion()["motion-coverage"].status, "pass")

        just_under = at_limit.replace("0.65", "0.649")
        (self.ep / "scene.py").write_text(scene.replace(marker, just_under), encoding="utf-8")
        issues = self.failed()["motion-coverage"]
        self.assertTrue(any(i.startswith("B8 schedules about 65%") for i in issues), issues)

    def test_b3_and_b6_share_both_the_mechanism_and_its_phase_clock(self):
        scene = (self.ep / "scene.py").read_text(encoding="utf-8")
        scene = scene.replace("self.mechanism(B_COLOR, self.replay_time)",
                              "self.mechanism(B_COLOR, b.duration * 0.80)")
        (self.ep / "scene.py").write_text(scene, encoding="utf-8")
        issues = self.failed()["recognition-replay"]
        self.assertTrue(any("do not reuse one narration-relative phase clock" in i for i in issues), issues)

        # Keeping timing relative is not enough if B6 is rebuilt as unrelated animation.
        scene = scene.replace("self.mechanism(B_COLOR, b.duration * 0.80)",
                              'self.play(FadeIn(text("B6 replay", 24, B_COLOR)), '
                              'run_time=b.duration * 0.80)')
        (self.ep / "scene.py").write_text(scene, encoding="utf-8")
        issues = self.failed()["recognition-replay"]
        self.assertTrue(any("do not call the same animated helper" in i for i in issues), issues)

    def test_identical_local_beat_expressions_are_not_one_replay_clock(self):
        scene = (self.ep / "scene.py").read_text(encoding="utf-8")
        scene = scene.replace("            self.replay_time = b.duration * 0.80\n", "")
        scene = scene.replace("self.replay_time", "b.duration * 0.80")
        (self.ep / "scene.py").write_text(scene, encoding="utf-8")
        motion = self.motion()
        self.assertEqual(motion["motion-timing"].status, "pass")
        self.assertEqual(motion["motion-coverage"].status, "pass")
        issues = motion["recognition-replay"].issues
        self.assertTrue(any("do not reuse one narration-relative phase clock" in i for i in issues), issues)

    def test_a_local_clock_captured_in_b3_can_be_reused_in_b6(self):
        scene = (self.ep / "scene.py").read_text(encoding="utf-8")
        scene = scene.replace("self.replay_time", "replay_time")
        (self.ep / "scene.py").write_text(scene, encoding="utf-8")
        self.assertEqual(self.motion()["recognition-replay"].status, "pass")

    def test_recomputing_the_named_clock_in_b6_is_not_a_replay(self):
        scene = (self.ep / "scene.py").read_text(encoding="utf-8")
        call = "            self.mechanism(B_COLOR, self.replay_time)"
        recomputed = ("            self.replay_time = b.duration * 0.80\n"
                      + call)
        self.assertIn(call, scene)
        (self.ep / "scene.py").write_text(scene.replace(call, recomputed), encoding="utf-8")
        issues = self.motion()["recognition-replay"].issues
        self.assertTrue(any("do not reuse one narration-relative phase clock" in i for i in issues), issues)

    def test_replay_clock_binding_can_mix_positional_and_keyword_arguments(self):
        scene = (self.ep / "scene.py").read_text(encoding="utf-8")
        scene = scene.replace("self.mechanism(B_COLOR, self.replay_time)",
                              "self.mechanism(B_COLOR, run_time=self.replay_time)")
        (self.ep / "scene.py").write_text(scene, encoding="utf-8")
        self.assertEqual(self.motion()["recognition-replay"].status, "pass")

    def test_extra_helper_call_does_not_hide_a_valid_shared_replay(self):
        scene = (self.ep / "scene.py").read_text(encoding="utf-8")
        shared = "            self.mechanism(A_COLOR, self.replay_time)"
        decoy = shared + "\n            self.mechanism(A_COLOR, b.duration * 0.10)"
        self.assertIn(shared, scene)
        (self.ep / "scene.py").write_text(scene.replace(shared, decoy), encoding="utf-8")
        self.assertEqual(self.motion()["recognition-replay"].status, "pass")

    def test_causal_motion_uses_the_design_owned_minimum(self):
        scene = (self.ep / "scene.py").read_text(encoding="utf-8")
        marker = ('mark = text("B1 label", 24, A_COLOR)\n'
                  '            self.play(mark.animate.shift(0.2 * RIGHT), run_time=b.duration * 0.80)')
        generic = ('mark = text("B1 label", 24, A_COLOR)\n'
                   '            self.play(FadeIn(mark), run_time=b.duration * 0.80)')
        self.assertIn(marker, scene)
        (self.ep / "scene.py").write_text(scene.replace(marker, generic), encoding="utf-8")
        plan = design.scene_plan(self.ep / "scene.py")
        self.assertEqual(design.causal_motion(self.ep, plan, design.Limits(causal_min_beats=7)).status,
                         "pass")
        strict = design.causal_motion(self.ep, plan, design.Limits(causal_min_beats=8))
        self.assertEqual(strict.status, "fail")
        self.assertTrue(any("need 8" in issue for issue in strict.issues), strict.issues)

    def test_rules_wait_for_a_scene(self):
        (self.ep / "scene.py").unlink()
        skipped = {r.rule for r in design.check(self.ep) if r.status == "skip"}
        self.assertEqual(skipped, {"color-signals", "every-beat", "motion-timing",
                                   "motion-coverage", "recognition-replay", "causal-motion"})


class MotionReferenceCalibrationTests(unittest.TestCase):
    """Keep the source gates compatible with both finished reference episodes."""

    ROOT = Path(__file__).resolve().parents[1]
    RULES = {"motion-timing", "motion-coverage", "recognition-replay", "causal-motion"}

    def test_reference_episodes_pass_all_motion_source_gates(self):
        for slug in ("001-camera-x-chip", "002-air-traffic-x-touchscreen"):
            with self.subTest(episode=slug):
                results = {r.rule: r for r in design.check(self.ROOT / "episodes" / slug)
                           if r.rule in self.RULES}
                self.assertEqual(set(results), self.RULES)
                self.assertEqual({name: result.issues for name, result in results.items()
                                  if result.status != "pass"}, {})


if __name__ == "__main__":
    unittest.main()
