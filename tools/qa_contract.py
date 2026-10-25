"""Version the inputs that define whether a saved export-QA report is still valid."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
QA_SCHEMA_VERSION = 2
QA_DEPENDENCIES = (
    ROOT / "tools" / "qa.py",
    ROOT / "tools" / "qa_contract.py",
    ROOT / "tools" / "sfxqa.py",
    ROOT / "tools" / "visual_quality.py",
    ROOT / "tools" / "design.py",
    ROOT / "tools" / "scriptfile.py",
    ROOT / "kit" / "short.py",
    ROOT / "kit" / "style.py",
    ROOT / "design.toml",
    ROOT / "voice.toml",
)


def pipeline_fingerprint(paths: Iterable[Path] | None = None) -> str:
    """Hash every source/config input whose change requires export QA to run again."""

    digest = hashlib.sha256()
    digest.update(f"qa-schema:{QA_SCHEMA_VERSION}\0".encode())
    for path in paths if paths is not None else QA_DEPENDENCIES:
        resolved = Path(path).resolve()
        try:
            name = resolved.relative_to(ROOT).as_posix()
        except ValueError:
            name = resolved.as_posix()
        digest.update(name.encode("utf-8"))
        digest.update(b"\0")
        if resolved.exists():
            # Git checks text out with CRLF on one machine and LF on another; a report must
            # stay current wherever the repository is cloned, so hash the text, not its EOLs.
            digest.update(resolved.read_bytes().replace(b"\r\n", b"\n"))
        else:
            digest.update(b"<missing>")
        digest.update(b"\0")
    return digest.hexdigest()


def report_is_current(
    report: dict,
    *,
    episode: str | None = None,
    video: str | None = None,
) -> bool:
    """Return true only for this export and the current QA implementation."""

    if episode is not None and report.get("episode") != episode:
        return False
    if video is not None and report.get("video") != video:
        return False
    return report.get("pipeline_fingerprint") == pipeline_fingerprint()


__all__ = ["QA_DEPENDENCIES", "QA_SCHEMA_VERSION", "pipeline_fingerprint", "report_is_current"]
