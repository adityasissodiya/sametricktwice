@echo off
rem One entry point for the whole pipeline. Run "vid" with no arguments for the commands.
rem Everything it installs, caches or renders stays inside this folder.
setlocal
call "%~dp0tools\env.cmd"
cd /d "%VID_ROOT%"

if /i "%~1"=="setup" goto :setup
if /i "%~1"=="uv" goto :uv
if not exist "%VID_ROOT%\.venv\Scripts\python.exe" (
    echo No environment yet. Run:  vid setup
    exit /b 1
)
"%VID_ROOT%\.venv\Scripts\python.exe" "%VID_ROOT%\tools\vid.py" %*
exit /b %ERRORLEVEL%

:setup
rem Portable tools, Python 3.12, packages and the narrator model; see tools\setup.ps1.
powershell -NoProfile -ExecutionPolicy Bypass -File "%VID_ROOT%\tools\setup.ps1"
exit /b %ERRORLEVEL%

:uv
set "ARGS=%*"
uv %ARGS:~3%
exit /b %ERRORLEVEL%
