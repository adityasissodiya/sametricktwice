"""Tests for the text rules the Kokoro voice applies before synthesis."""

from __future__ import annotations

import tempfile
import unittest

try:
    import manim  # noqa: F401
except ImportError:  # e.g. the CI runner, which has no render stack
    raise unittest.SkipTest("needs the render stack (manim)")

from kit.voices import (
    KOKORO_DIR,
    KOKORO_FILES,
    SERIES,
    KokoroVoice,
    say_year,
    series_voice,
    sha256,
    speech_service,
    spoken_years,
    to_phonemes,
)


class FrozenVoiceTests(unittest.TestCase):
    def test_default_voice_is_the_frozen_series_voice(self):
        self.assertEqual(series_voice(), "kokoro:af_heart")
        with tempfile.TemporaryDirectory() as cache:
            voice = speech_service(None, cache_dir=cache)
        self.assertIsInstance(voice, KokoroVoice)
        self.assertEqual((voice.voice, voice.speed), (SERIES["speaker"], SERIES["speed"]))
        self.assertEqual(voice.pauses, {"sentence_pause": SERIES["sentence_pause"],
                                        "clause_pause": SERIES["clause_pause"]})

    def test_model_files_on_disk_are_the_frozen_ones(self):
        for name, digest in KOKORO_FILES.items():
            path = KOKORO_DIR / name
            if not path.exists():
                self.skipTest(f"{name} not downloaded yet")
            self.assertEqual(sha256(path), digest, name)


class YearTests(unittest.TestCase):
    def test_years_are_read_as_years(self):
        self.assertEqual(say_year(1827), "eighteen twenty-seven")
        self.assertEqual(say_year(1957), "nineteen fifty-seven")
        self.assertEqual(say_year(1905), "nineteen oh five")
        self.assertEqual(say_year(1900), "nineteen hundred")
        self.assertEqual(say_year(2007), "two thousand seven")
        self.assertEqual(say_year(2026), "twenty twenty-six")

    def test_only_year_shaped_numbers_change(self):
        self.assertEqual(spoken_years("Around 1827, Niépce"), "Around eighteen twenty-seven, Niépce")
        self.assertEqual(spoken_years("a 200-year-old trick"), "a 200-year-old trick")
        self.assertEqual(spoken_years("1,827 plates and 3.1957 volts"), "1,827 plates and 3.1957 volts")
        self.assertEqual(spoken_years("a 100 × 100 grid"), "a 100 × 100 grid")


class LexiconTests(unittest.TestCase):
    def setUp(self):
        self.calls = []

        def fake_phonemize(text, lang):
            self.calls.append(text)
            return f"<{text}>"

        self.phonemize = fake_phonemize

    def test_lexicon_words_use_their_ipa_and_the_rest_is_phonemized(self):
        lexicon = {"Niépce": "niːˈɛps", "U.S.": "jˌuːˈɛs"}
        out = to_phonemes("Niépce worked at a U.S. Army lab.", self.phonemize, lexicon)
        self.assertEqual(out, "niːˈɛps <worked at a> jˌuːˈɛs <Army lab.>")

    def test_lexicon_matches_whole_words_only(self):
        out = to_phonemes("Canonical Canon", self.phonemize, {"Canon": "kˈænən"})
        self.assertEqual(out, "<Canonical> kˈænən")

    def test_without_a_lexicon_the_whole_text_is_phonemized_once(self):
        self.assertEqual(to_phonemes("Plain text.", self.phonemize, {}), "<Plain text.>")
        self.assertEqual(self.calls, ["Plain text."])


if __name__ == "__main__":
    unittest.main()
