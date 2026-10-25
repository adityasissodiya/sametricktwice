"""Tests for render-time SFX manifests and export audio-quality gates."""

from __future__ import annotations

import json
import math
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from kit import short as short_module
from kit.short import ShortScene
from tests.test_qa import GOOD
from tools import qa, sfxqa


class RuntimeManifestTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.ep = self.root / "episodes" / "009-kettle-x-rocket"
        self.ep.mkdir(parents=True)
        (self.ep / "audio").mkdir()
        (self.root / "kit" / "sfx").mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def scene(self, *, skip: bool = False):
        sounds: list[tuple[str, float]] = []
        scene = SimpleNamespace(
            episode_dir=self.ep,
            renderer=SimpleNamespace(skip_animations=skip),
            time=2.34567,
            sfx_cues=[],
            add_sound=lambda path, gain: sounds.append((path, gain)),
        )
        return scene, sounds

    def test_sfx_records_the_executed_time_gain_and_resolved_source(self):
        own = self.ep / "audio" / "tap.wav"
        kit = self.root / "kit" / "sfx" / "tap.wav"
        own.write_bytes(b"episode")
        kit.write_bytes(b"kit")
        scene, sounds = self.scene()

        with mock.patch.object(short_module, "ROOT", self.root):
            ShortScene.sfx(scene, "tap.wav", gain=-7.5)

        self.assertEqual(sounds, [(str(own), -7.5)])
        self.assertEqual(scene.sfx_cues, [{
            "name": "tap.wav",
            "time_s": 2.3457,
            "gain_db": -7.5,
            "source": "episodes/009-kettle-x-rocket/audio/tap.wav",
        }])

    def test_skipped_animation_pass_does_not_create_a_phantom_cue(self):
        (self.root / "kit" / "sfx" / "tap.wav").write_bytes(b"kit")
        scene, sounds = self.scene(skip=True)

        with mock.patch.object(short_module, "ROOT", self.root):
            ShortScene.sfx(scene, "tap.wav")

        self.assertEqual(scene.sfx_cues, [])
        self.assertEqual(len(sounds), 1)

    def test_manifest_contains_runtime_cues_and_scene_duration(self):
        scene, _ = self.scene()
        scene.time = 54.32109
        scene.sfx_cues = [{"name": "tap.wav", "time_s": 1.0, "gain_db": -8.0,
                           "source": "kit/sfx/tap.wav"}]

        with mock.patch.object(short_module, "ROOT", self.root):
            ShortScene._write_sfx_manifest(scene)

        path = self.root / "media" / self.ep.name / sfxqa.MANIFEST
        self.assertEqual(json.loads(path.read_text(encoding="utf-8")), {
            "version": 1,
            "episode": self.ep.name,
            "scene_duration_s": 54.3211,
            "cues": scene.sfx_cues,
        })

    def test_teardown_flushes_alignment_manifest_and_base_scene(self):
        scene = object.__new__(ShortScene)
        scene.alignment = SimpleNamespace(finish=mock.Mock())
        scene._write_sfx_manifest = mock.Mock()
        with mock.patch.object(short_module.VoiceoverScene, "tear_down") as base_teardown:
            ShortScene.tear_down(scene)

        scene.alignment.finish.assert_called_once_with()
        scene._write_sfx_manifest.assert_called_once_with()
        base_teardown.assert_called_once_with()


class SfxMeasurementTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.media = self.root / "media"
        self.ep = self.root / "episodes" / "009-kettle-x-rocket"
        self.ep.mkdir(parents=True)
        (self.root / "kit" / "sfx").mkdir(parents=True)
        self.voice = self.root / "voice.wav"
        self.click = self.root / "kit" / "sfx" / "click.wav"
        self.buried = self.root / "kit" / "sfx" / "buried.wav"
        for path in (self.voice, self.click, self.buried):
            path.write_bytes(b"audio")

    def tearDown(self):
        sfxqa.audio_stats.cache_clear()
        self.tmp.cleanup()

    def write_manifest(self, cues, **changes):
        folder = self.media / self.ep.name
        folder.mkdir(parents=True)
        data = {
            "version": 1,
            "episode": self.ep.name,
            "scene_duration_s": 50.0,
            "cues": cues,
            **changes,
        }
        (folder / sfxqa.MANIFEST).write_text(json.dumps(data), encoding="utf-8")

    @staticmethod
    def stats(path: Path) -> sfxqa.AudioStats:
        values = {
            "voice.wav": sfxqa.AudioStats(10.0, -20.0, -2.0),
            "click.wav": sfxqa.AudioStats(0.25, -30.0, -8.0),
            "buried.wav": sfxqa.AudioStats(0.5, -45.0, -24.0),
        }
        return values[path.name]

    def test_audio_stats_reads_duration_mean_and_peak_from_project_tools(self):
        probe = SimpleNamespace(stdout="0.250000\n")
        detect = SimpleNamespace(
            returncode=0,
            stderr="[Parsed_volumedetect_0] mean_volume: -23.5 dB\n"
                   "[Parsed_volumedetect_0] max_volume: -2.0 dB\n",
        )
        sfxqa.audio_stats.cache_clear()
        with mock.patch.object(sfxqa.subprocess, "run", side_effect=[probe, detect]) as run:
            measured = sfxqa.audio_stats(self.click)

        self.assertEqual(measured, sfxqa.AudioStats(0.25, -23.5, -2.0))
        self.assertEqual(run.call_args_list[0].args[0][0], "ffprobe")
        self.assertEqual(run.call_args_list[1].args[0][0], "ffmpeg")

    def measure(self, spans=((0.0, 20.0),), voice_paths=None, expected=1):
        with (mock.patch.object(sfxqa, "ROOT", self.root),
              mock.patch.object(sfxqa, "MEDIA", self.media),
              mock.patch.object(sfxqa, "audio_stats", side_effect=self.stats)):
            return sfxqa.measure(
                self.ep, 50.0, list(spans),
                [self.voice] if voice_paths is None else voice_paths,
                expected_voice_files=expected,
            )

    def test_missing_and_malformed_manifests_are_explicit(self):
        missing = self.measure()
        self.assertEqual(missing["sfx_manifest_status"], "missing")
        self.assertIn("render the episode again", missing["sfx_manifest_errors"][0])

        folder = self.media / self.ep.name
        folder.mkdir(parents=True)
        (folder / sfxqa.MANIFEST).write_text("{not json", encoding="utf-8")
        malformed = self.measure()
        self.assertEqual(malformed["sfx_manifest_status"], "invalid")
        self.assertIn("cannot read", malformed["sfx_manifest_errors"][0])

    def test_manifest_identity_and_duration_must_match_the_export(self):
        self.write_manifest([], episode="003-other", scene_duration_s=47.0)
        measured = self.measure()
        self.assertEqual(measured["sfx_manifest_status"], "invalid")
        self.assertTrue(any("manifest is for" in issue for issue in measured["sfx_manifest_errors"]))
        self.assertTrue(any("does not match export" in issue for issue in measured["sfx_manifest_errors"]))

    def test_effective_levels_include_scene_gain_and_compare_to_narration(self):
        self.write_manifest([
            {"name": "click.wav", "time_s": 2.0, "gain_db": -8.0,
             "source": "kit/sfx/click.wav"},
            {"name": "buried.wav", "time_s": 30.0, "gain_db": -12.0,
             "source": "kit/sfx/buried.wav"},
        ])
        measured = self.measure()

        click, buried = measured["sfx_cues"]
        self.assertEqual(measured["sfx_voice_mean_dbfs"], -20.0)
        self.assertEqual(click["effective_mean_dbfs"], -38.0)
        self.assertEqual(click["relative_mean_db"], -18.0)
        self.assertEqual(click["relative_peak_to_voice_mean_db"], 4.0)
        self.assertTrue(click["overlaps_speech"])
        self.assertFalse(buried["overlaps_speech"])
        self.assertEqual(measured["sfx_cue_count"], 2)
        self.assertEqual(measured["sfx_cues_per_10s"], 0.4)

    def test_missing_voice_cache_and_unsafe_sources_are_reported(self):
        outside = self.root.parent / "outside.wav"
        outside.write_bytes(b"audio")
        self.addCleanup(outside.unlink, missing_ok=True)
        self.write_manifest([
            {"name": "outside.wav", "time_s": 2.0, "gain_db": -8.0, "source": str(outside)},
            {"name": "missing.wav", "time_s": 3.0, "gain_db": -8.0,
             "source": "kit/sfx/missing.wav"},
        ])
        measured = self.measure(voice_paths=[], expected=1)

        errors = "\n".join(measured["sfx_source_errors"])
        self.assertIn("found 0/1 cached", errors)
        self.assertIn("outside the project", errors)
        self.assertIn("missing source", errors)
        self.assertIsNone(measured["sfx_voice_mean_dbfs"])

    def test_simultaneous_count_uses_sound_duration_and_not_touching_edges(self):
        cues = [
            {"time_s": 0.0, "duration_s": 1.0},
            {"time_s": 0.5, "duration_s": 1.0},
            {"time_s": 1.0, "duration_s": 0.5},
        ]
        self.assertEqual(sfxqa._max_simultaneous(cues), 2)

    def test_combined_voice_mean_is_duration_weighted_in_linear_power(self):
        combined = sfxqa.combined_mean([
            sfxqa.AudioStats(1.0, -10.0, -1.0),
            sfxqa.AudioStats(3.0, -20.0, -1.0),
        ])
        expected = 10 * math.log10((0.1 + 3 * 0.01) / 4)
        self.assertAlmostEqual(combined, expected)


class SfxJudgementTests(unittest.TestCase):
    lim = qa.Limits()

    @staticmethod
    def metrics(cues, *, count=None, duration=50.0, **changes):
        count = len(cues) if count is None else count
        return {
            "sfx_manifest_status": "ok",
            "sfx_manifest_errors": [],
            "sfx_cue_count": count,
            "sfx_cues_per_10s": count / duration * 10,
            "sfx_voice_mean_dbfs": -20.0,
            "sfx_source_errors": [],
            "sfx_speech_overlap_cues": sum(bool(c.get("overlaps_speech")) for c in cues),
            "sfx_max_simultaneous": 1 if cues else 0,
            "sfx_cues": cues,
            **changes,
        }

    def judged(self, metrics):
        return {item.rule: item for item in sfxqa.judge(metrics, self.lim)}

    def test_density_uses_executed_cues_not_source_call_sites(self):
        cues = [{"relative_mean_db": -10.0, "relative_peak_to_voice_mean_db": -5.0,
                 "overlaps_speech": False} for _ in range(8)]
        result = self.judged(self.metrics(cues))["sfx-density"]
        self.assertEqual(result.status, "fail")
        self.assertTrue(any("8 executed cues" in issue for issue in result.issues))

        cues.append(cues[0].copy())
        self.assertEqual(self.judged(self.metrics(cues))["sfx-density"].status, "pass")

    def test_buried_files_fail_even_though_they_exist_and_execute(self):
        cues = [{"relative_mean_db": -30.0, "relative_peak_to_voice_mean_db": -20.0,
                 "overlaps_speech": True} for _ in range(9)]
        result = self.judged(self.metrics(cues))["sfx-audibility"]
        self.assertEqual(result.status, "fail")
        self.assertTrue(any("0 perceptible cues" in issue for issue in result.issues))
        self.assertTrue(any("0% of cues" in issue for issue in result.issues))

    def test_transient_peak_or_sustained_mean_can_make_a_cue_perceptible(self):
        transient = {"relative_mean_db": -25.0, "relative_peak_to_voice_mean_db": -8.0,
                     "overlaps_speech": False}
        sustained = {"relative_mean_db": -12.0, "relative_peak_to_voice_mean_db": -20.0,
                     "overlaps_speech": False}
        cues = [transient, sustained, transient, sustained, transient,
                sustained, transient, sustained, transient]
        self.assertEqual(self.judged(self.metrics(cues))["sfx-audibility"].status, "pass")

    def test_loud_speech_overlap_and_stacked_effects_fail_masking(self):
        cues = [
            {"name": "hit.wav", "time_s": 2.0, "relative_mean_db": -2.0,
             "relative_peak_to_voice_mean_db": 3.0, "overlaps_speech": True},
            {"name": "quiet.wav", "time_s": 2.1, "relative_mean_db": -12.0,
             "relative_peak_to_voice_mean_db": -8.0, "overlaps_speech": True},
        ]
        judged = self.judged(self.metrics(cues, count=9, sfx_max_simultaneous=3))
        result = judged["sfx-masking"]
        self.assertEqual(result.status, "fail")
        self.assertTrue(any("can mask narration" in issue for issue in result.issues))
        self.assertTrue(any("3 sound effects overlap" in issue for issue in result.issues))

    def test_audio_thresholds_preserve_references_and_reject_episode_003(self):
        """Lock the defaults to measured house-file gains and the frozen narrator level."""

        def cue(mean, peak, *, speech=True):
            return {
                "name": "measured.wav", "time_s": 1.0,
                "relative_mean_db": mean,
                "relative_peak_to_voice_mean_db": peak,
                "overlaps_speech": speech,
            }

        # Duration-weighted narrator mean is -22.2 dBFS in all three cached masters.
        # These relative levels are source volumedetect + scene gain - narrator mean.
        quiet = cue(-29.0, -16.0)
        episode_001 = [cue(-13.3, 2.0), cue(-13.7, -5.0), cue(-8.6, 5.2),
                       cue(-20.4, -11.9), cue(-16.7, -8.0), cue(-11.3, 4.0),
                       *[quiet] * 7]
        episode_002 = [cue(-4.9, 7.9), cue(-14.3, 1.0), cue(-15.7, -7.0),
                       cue(-3.9, 8.9), cue(-4.9, 7.9), cue(-14.3, 1.0),
                       *[quiet] * 9]
        episode_003 = [cue(-12.9, -0.1), cue(-12.9, -0.1), *[quiet] * 5]

        for reference in (episode_001, episode_002):
            judged = self.judged(self.metrics(reference))
            with self.subTest(cues=len(reference)):
                self.assertTrue(all(item.status == "pass" for item in judged.values()), judged)

        judged = self.judged(self.metrics(episode_003))
        self.assertEqual(judged["sfx-density"].status, "fail")
        self.assertEqual(judged["sfx-audibility"].status, "fail")
        self.assertEqual(judged["sfx-masking"].status, "pass")

    def test_loud_cue_outside_speech_does_not_count_as_narration_masking(self):
        cue = {"name": "hit.wav", "time_s": 22.0, "relative_mean_db": 0.0,
               "relative_peak_to_voice_mean_db": 6.0, "overlaps_speech": False}
        result = self.judged(self.metrics([cue] * 9))["sfx-masking"]
        self.assertEqual(result.status, "pass")

    def test_missing_manifest_fails_density_and_skips_level_claims(self):
        judged = self.judged({
            "sfx_manifest_status": "missing",
            "sfx_manifest_errors": ["no sfx-manifest.json"],
        })
        self.assertEqual(judged["sfx-density"].status, "fail")
        self.assertEqual(judged["sfx-audibility"].status, "skip")
        self.assertEqual(judged["sfx-masking"].status, "skip")

    def test_export_qa_includes_all_three_audio_rules(self):
        metrics = {
            **GOOD,
            **self.metrics([], count=0),
        }
        results = {item.rule: item for item in qa.judge(metrics, [], self.lim)}
        self.assertEqual(results["sfx-density"].status, "fail")
        self.assertEqual(results["sfx-audibility"].status, "fail")
        self.assertEqual(results["sfx-masking"].status, "pass")


if __name__ == "__main__":
    unittest.main()
