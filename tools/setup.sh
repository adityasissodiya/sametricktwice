#!/usr/bin/env bash
# vid setup on Linux and macOS: the twin of setup.ps1 (Windows).
#
# 1. uv into .tools/uv, checked against the SHA-256 pinned below (the same uv 0.12.23 as on
#    Windows). FFmpeg comes from the system package manager: it is a standard package on
#    every Linux distribution and in Homebrew, and the script tells you the command if it is
#    missing. SoX and the GitHub CLI are optional and not needed to render.
# 2. Python 3.12. If this machine has none, uv installs CPython 3.12 into .tools/python.
# 3. The locked Python packages into .venv (uv sync --locked).
# 4. The frozen narrator model into .cache/models, checked against voice.toml.
# 5. vid doctor, then the unit tests.
#
# Run it as "./vid setup": vid sets the folder-local cache variables first. It is safe to run
# again; finished steps are skipped.
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
tools="$root/.tools"
downloads="$root/.cache/downloads"
cd "$root"
mkdir -p "$tools" "$downloads"

step() { printf '\n== %s\n' "$1"; }

case "$(uname -s)-$(uname -m)" in
    Linux-x86_64)  target=x86_64-unknown-linux-gnu
                   sha=9167d72b3319674b6303c4cbe071854bba13ebdf3d76b1a7cbdc175471fb66d6 ;;
    Linux-aarch64) target=aarch64-unknown-linux-gnu
                   sha=6524bd338177ed50d035d39354e12545e993bbeba2ecbddf0480c5b3a81d313f ;;
    Darwin-x86_64) target=x86_64-apple-darwin
                   sha=960da44cb4b73685206ddd250b19e0a117fa41095710c1038f081f5cb613efb4 ;;
    Darwin-arm64)  target=aarch64-apple-darwin
                   sha=50487ae565ccd96e499056b4674d438f4c53170202617b4c759defe0c6a1b544 ;;
    *) echo "No pinned uv build for $(uname -s) $(uname -m)."; exit 1 ;;
esac

sha256() {
    if command -v sha256sum >/dev/null; then sha256sum "$1" | cut -d' ' -f1
    else shasum -a 256 "$1" | cut -d' ' -f1; fi
}

step 'Portable tools (.tools)'
if [ -x "$tools/uv/uv" ]; then
    echo "  ok    uv 0.12.23"
else
    echo "  get   uv 0.12.23"
    archive="$downloads/uv.tar.gz"
    curl -sSfL -o "$archive" "https://github.com/astral-sh/uv/releases/download/0.12.23/uv-$target.tar.gz"
    got="$(sha256 "$archive")"
    if [ "$got" != "$sha" ]; then
        rm -f "$archive"
        echo "uv: SHA-256 $got does not match the pinned $sha. Nothing was installed."
        exit 1
    fi
    mkdir -p "$tools/uv"
    tar -xzf "$archive" -C "$tools/uv" --strip-components 1
    rm -f "$archive"
    echo "  ok    uv 0.12.23"
fi
if command -v ffmpeg >/dev/null && command -v ffprobe >/dev/null; then
    echo "  ok    FFmpeg $(ffmpeg -version | head -n1 | cut -d' ' -f3)"
else
    echo "  FFmpeg is missing. Install it with your package manager, then run ./vid setup again:"
    echo "    Debian/Ubuntu: sudo apt install ffmpeg      Fedora: sudo dnf install ffmpeg"
    echo "    macOS:         brew install ffmpeg"
    exit 1
fi

step 'Python 3.12'
uv="$tools/uv/uv"
if found="$("$uv" python find 3.12 --no-project 2>/dev/null)"; then
    echo "  ok    $found"
else
    echo '  get   CPython 3.12 into .tools/python (this machine has none)'
    UV_PYTHON_DOWNLOADS=manual "$uv" python install 3.12 --install-dir "$tools/python" --no-bin
fi

step 'Python packages (.venv, from uv.lock)'
"$uv" sync --locked
python="$root/.venv/bin/python"

step 'Narrator model (.cache/models, about 340 MB the first time)'
"$python" -c "from kit.voices import prepare_kokoro; prepare_kokoro(); print('  ok    Kokoro v1.0, SHA-256 matches voice.toml')"

step 'vid doctor'
"$python" "$root/tools/vid.py" doctor

step 'vid test'
"$python" "$root/tools/vid.py" test

printf '\nReady. Start with: ./vid status\n'
