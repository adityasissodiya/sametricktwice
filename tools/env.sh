# Pins every tool, cache and temp file for this project to this folder, wherever it is.
# The Linux and macOS twin of env.cmd. Used by ./vid; you can also source it in a shell
# (". tools/env.sh") to get the same setup.
VID_ROOT="$(cd "$(dirname "${BASH_SOURCE:-$0}")/.." 2>/dev/null && pwd)"
[ -f "$VID_ROOT/tools/vid.py" ] || VID_ROOT="$(pwd)"
export VID_ROOT

export PATH="$VID_ROOT/.tools/uv:$VID_ROOT/.tools/ffmpeg/bin:$VID_ROOT/.tools/gh/bin:$PATH"
export GH_CONFIG_DIR="$VID_ROOT/.tools/gh/config"
export UV_CACHE_DIR="$VID_ROOT/.cache/uv"
# Python 3.12: the machine's own if it has one, else the copy vid setup puts in .tools/python.
export UV_PYTHON_DOWNLOADS=never
export UV_PYTHON_PREFERENCE=system
export UV_PYTHON_INSTALL_DIR="$VID_ROOT/.tools/python"
export UV_LINK_MODE=hardlink
export PIP_CACHE_DIR="$VID_ROOT/.cache/pip"
export XDG_CACHE_HOME="$VID_ROOT/.cache"
export HF_HOME="$VID_ROOT/.cache/huggingface"
export TORCH_HOME="$VID_ROOT/.cache/torch"
export MPLCONFIGDIR="$VID_ROOT/.cache/matplotlib"
export TEMP="$VID_ROOT/.cache/tmp"
export TMP="$VID_ROOT/.cache/tmp"
export TMPDIR="$VID_ROOT/.cache/tmp"
export PYTHONUTF8=1
mkdir -p "$TEMP"
