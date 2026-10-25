@echo off
rem Pins every tool, cache and temp file for this project to this folder, wherever it is.
rem Used by vid.cmd. You can also run it once in a cmd window to get the same setup.
set "VID_ROOT=%~dp0.."
for %%I in ("%VID_ROOT%") do set "VID_ROOT=%%~fI"

set "PATH=%VID_ROOT%\.tools\uv;%VID_ROOT%\.tools\ffmpeg\bin;%VID_ROOT%\.tools\sox;%VID_ROOT%\.tools\gh\bin;%PATH%"
set "GH_CONFIG_DIR=%VID_ROOT%\.tools\gh\config"
set "UV_CACHE_DIR=%VID_ROOT%\.cache\uv"
rem Python 3.12: the PC's own if it has one, else the copy vid setup puts in .tools\python.
set "UV_PYTHON_DOWNLOADS=never"
set "UV_PYTHON_PREFERENCE=system"
set "UV_PYTHON_INSTALL_DIR=%VID_ROOT%\.tools\python"
set "UV_LINK_MODE=hardlink"
set "PIP_CACHE_DIR=%VID_ROOT%\.cache\pip"
set "XDG_CACHE_HOME=%VID_ROOT%\.cache"
set "HF_HOME=%VID_ROOT%\.cache\huggingface"
set "TORCH_HOME=%VID_ROOT%\.cache\torch"
set "MPLCONFIGDIR=%VID_ROOT%\.cache\matplotlib"
set "TEMP=%VID_ROOT%\.cache\tmp"
set "TMP=%VID_ROOT%\.cache\tmp"
set "PYTHONUTF8=1"
if not exist "%TEMP%" mkdir "%TEMP%"
