"""Speech services by name. Choose one with: vid preview <ep> --voice <name>

The series voice is frozen in voice.toml: Kokoro speaker af_heart at speed 1.0. Every
render uses it unless --voice says otherwise, and the model files are checked against
their SHA-256 on load, so episode 40 sounds like episode 1.

kokoro    Kokoro-82M neural voice, run on this PC: free, offline after a one-time
          340 MB download to .cache/models, Apache-2.0 weights (fine for monetized use).
          `kokoro` is the frozen series speaker; kokoro:<voice> tries another one.
          `vid audition <ep>` renders the same lines in several speakers to compare.
gtts      free Google voice, needs internet. Robotic; kept as a fallback.
          It is sped up to a natural narration pace (DRAFT_SPEED).
recorder  your own microphone, one beat at a time.
gemini    Gemini TTS. Needs `vid uv add "manim-voiceover[gemini]"` and GEMINI_API_KEY.
openai    OpenAI TTS. Needs `vid uv add "manim-voiceover[openai]"` and OPENAI_API_KEY.

Audio is cached per beat text, so only lines you change are generated again.
Whisper transcription stays off (it pulls ~1 GB of PyTorch); beats are short
enough that we sync per beat and do not need word-level bookmarks.

Delivery directions belong in each beat's non-spoken NOTE field. The frozen Kokoro voice is
the publishable narrator; gTTS is only a fallback. EQ/compression improves clarity but cannot
make a flat read expressive. Never change approved VO merely to make a synthetic voice sound
better: fix pronunciation in pronounce.toml.
"""

from __future__ import annotations

import hashlib
import re
import subprocess
import tomllib
import urllib.request
import wave
from pathlib import Path

import numpy as np
from manim import logger
from manim_voiceover.helper import remove_bookmarks
from manim_voiceover.services.base import SpeechService, initialize_speech_service
from manim_voiceover.services.gtts import GTTSService

ROOT = Path(__file__).resolve().parents[1]
VOICES = ("kokoro", "kokoro:<voice>", "gtts", "recorder", "gemini", "openai")
DRAFT_SPEED = 1.3  # plain gTTS talks at about 125 words/min; 1.3x is about 160

SERIES = tomllib.loads((ROOT / "voice.toml").read_text(encoding="utf-8"))
KOKORO_DIR = ROOT / ".cache" / "models" / "kokoro"
KOKORO_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/"
KOKORO_FILES = {SERIES["model"]: SERIES["model_sha256"], SERIES["voices"]: SERIES["voices_sha256"]}
KOKORO_VOICE = SERIES["speaker"]
AUDITION_VOICES = ("af_heart", "af_bella", "af_nicole", "bf_emma", "am_michael", "am_fenrir", "bm_george")
LEXICON_FILE = ROOT / "pronounce.toml"


def series_voice() -> str:
    """The frozen narrator as a --voice name, e.g. 'kokoro:af_heart'."""
    return f"{SERIES['voice']}:{SERIES['speaker']}"


class DraftVoice(GTTSService):
    """gTTS, sped up with ffmpeg's atempo filter (pitch stays the same)."""

    def __init__(self, speed: float = DRAFT_SPEED, **kwargs: object) -> None:
        super().__init__(lang="en", tld="com", **kwargs)
        self.speed = speed

    def generate_from_text(self, text, cache_dir=None, path=None, **kwargs):
        from gtts import gTTS

        cache_dir = Path(cache_dir or self.cache_dir)
        input_text = remove_bookmarks(text)
        input_data = {"input_text": input_text, "service": "gtts", "config": {"speed": self.speed}}
        cached = self.get_cached_result(input_data, cache_dir)
        if cached is not None:
            return cached
        audio = self.get_audio_basename(input_data) + ".mp3"
        raw = cache_dir / f"raw-{audio}"
        gTTS(input_text, lang=self.lang, tld=self.tld).save(str(raw))
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(raw), "-filter:a", f"atempo={self.speed}",
                        str(cache_dir / audio)], check=True)
        raw.unlink()
        return {"input_text": text, "input_data": input_data, "original_audio": audio}


class KokoroVoice(SpeechService):
    """Kokoro-82M, run locally with ONNX Runtime.

    Years are read as years and pronounce.toml fixes names before synthesis. Only the
    audio changes: captions keep the script's spelling. The phonemes are part of the
    cache key, so editing pronounce.toml regenerates exactly the affected lines.
    """

    def __init__(self, voice: str = KOKORO_VOICE, speed: float = SERIES["speed"], **kwargs: object) -> None:
        initialize_speech_service(self, kwargs)
        self.voice, self.speed = voice, speed
        self.pauses = {"sentence_pause": SERIES["sentence_pause"], "clause_pause": SERIES["clause_pause"]}
        self._kokoro = None

    def engine(self):
        if self._kokoro is None:
            from kokoro_onnx import Kokoro

            prepare_kokoro()
            self._kokoro = Kokoro(*(str(KOKORO_DIR / name) for name in KOKORO_FILES))
            if self.voice not in self._kokoro.get_voices():
                raise SystemExit(f"Kokoro has no voice {self.voice!r}. Try one of: {', '.join(AUDITION_VOICES)}")
        return self._kokoro

    def phonemes(self, text: str) -> str:
        return to_phonemes(spoken_years(remove_bookmarks(text)), self.engine().tokenizer.phonemize, load_lexicon())

    def synthesize(self, text: str):
        return self._create(self.phonemes(text))

    def _create(self, phonemes: str):
        return self.engine().create(phonemes, voice=self.voice, speed=self.speed, is_phonemes=True, **self.pauses)

    def generate_from_text(self, text, cache_dir=None, path=None, **kwargs):
        cache_dir = Path(cache_dir or self.cache_dir)
        input_text = remove_bookmarks(text)
        config = {"voice": self.voice, "speed": self.speed, **self.pauses, "phonemes": self.phonemes(input_text)}
        input_data = {"input_text": input_text, "service": "kokoro", "config": config}
        cached = self.get_cached_result(input_data, cache_dir)
        if cached is not None:
            return cached
        audio = self.get_audio_basename(input_data) + ".wav"
        samples, rate = self._create(config["phonemes"])
        write_wav(cache_dir / audio, samples, rate)
        return {"input_text": text, "input_data": input_data, "original_audio": audio}


def prepare_kokoro() -> None:
    """Fetch the frozen model once into .cache/models/kokoro and prove it is the same model."""
    KOKORO_DIR.mkdir(parents=True, exist_ok=True)
    for name, digest in KOKORO_FILES.items():
        target = KOKORO_DIR / name
        if not target.exists():
            logger.info(f"Downloading Kokoro {name} to {KOKORO_DIR} (one time only)")
            partial = target.with_suffix(target.suffix + ".part")
            urllib.request.urlretrieve(KOKORO_URL + name, partial)
            partial.rename(target)
        if sha256(target) != digest:
            raise SystemExit(
                f"{target} is not the frozen series model (SHA-256 mismatch with voice.toml). "
                "Delete it to re-download. Change voice.toml only if the creator approved a new voice."
            )


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def write_wav(path: Path, samples, rate: int) -> None:
    pcm = (np.clip(np.asarray(samples, dtype=np.float32), -1.0, 1.0) * 32767).astype("<i2")
    with wave.open(str(path), "wb") as out:
        out.setnchannels(1)
        out.setsampwidth(2)
        out.setframerate(rate)
        out.writeframes(pcm.tobytes())


def load_lexicon() -> dict[str, str]:
    return tomllib.loads(LEXICON_FILE.read_text(encoding="utf-8")) if LEXICON_FILE.exists() else {}


def to_phonemes(text: str, phonemize, lexicon: dict[str, str]) -> str:
    """Phonemize text, but use the lexicon's IPA for listed words (longest match first)."""
    if not lexicon:
        return phonemize(text, "en-us")
    pattern = re.compile(
        r"(?<!\w)(" + "|".join(re.escape(w) for w in sorted(lexicon, key=len, reverse=True)) + r")(?!\w)"
    )
    pieces, last = [], 0
    for match in pattern.finditer(text):
        before = text[last:match.start()].strip()
        if before:
            pieces.append(phonemize(before, "en-us"))
        pieces.append(lexicon[match.group(1)])
        last = match.end()
    after = text[last:].strip()
    if after:
        pieces.append(phonemize(after, "en-us"))
    return " ".join(pieces)


_ONES = ("zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen "
         "fifteen sixteen seventeen eighteen nineteen").split()
_TENS = "twenty thirty forty fifty sixty seventy eighty ninety".split()
_YEAR = re.compile(r"(?<![\d.,])\b(1[1-9]\d\d|20\d\d)\b(?![.,]?\d)")


def _two_digits(n: int) -> str:
    if n < 20:
        return _ONES[n]
    tens, ones = divmod(n, 10)
    return _TENS[tens - 2] + (f"-{_ONES[ones]}" if ones else "")


def say_year(year: int) -> str:
    century, rest = divmod(year, 100)
    if 2000 <= year <= 2009:
        return "two thousand" + (f" {_ONES[rest]}" if rest else "")
    if rest == 0:
        return f"{_two_digits(century)} hundred"
    if rest < 10:
        return f"{_two_digits(century)} oh {_ONES[rest]}"
    return f"{_two_digits(century)} {_two_digits(rest)}"


def spoken_years(text: str) -> str:
    """'In 1957' -> 'In nineteen fifty-seven'. Covers 1100-2099, the years this series cites."""
    return _YEAR.sub(lambda m: say_year(int(m.group(1))), text)


def speech_service(name: str | None, **kwargs):
    name = (name or series_voice()).lower()
    if name == "gtts":
        return DraftVoice(**kwargs)
    if name == "kokoro" or name.startswith("kokoro:"):
        return KokoroVoice(voice=name.partition(":")[2] or KOKORO_VOICE, **kwargs)
    if name == "recorder":
        from manim_voiceover.services.recorder import RecorderService

        return RecorderService(transcription_model=None)
    if name == "gemini":
        from manim_voiceover.services.gemini import GeminiService

        return GeminiService()
    if name == "openai":
        from manim_voiceover.services.openai import OpenAIService

        return OpenAIService(transcription_model=None)
    raise SystemExit(f"Unknown voice {name!r}. Use one of: {', '.join(VOICES)}")
