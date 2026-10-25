<#
vid setup: make this folder ready to produce episodes, on a new Windows machine or this one.

1. Portable tools into .tools: uv, FFmpeg, SoX and the GitHub CLI. Each archive must match
   the SHA-256 pinned below: these are the exact builds the series was made with (checked
   2026-10-08 against the binaries in use). A tool that is already there is left alone.
2. Python 3.12. If this PC has none, uv installs CPython 3.12 into .tools\python: no registry
   entry, nothing on PATH, nothing outside this folder.
3. The locked Python packages into .venv (uv sync --locked).
4. The frozen narrator model into .cache\models, checked against voice.toml.
5. vid doctor, then the unit tests.

Run it as "vid setup": vid.cmd sets the folder-local cache variables first. It is safe to
run again; finished steps are skipped. To change a pinned tool, change its URL and SHA-256
together, after checking the new build.
#>

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$tools = Join-Path $root '.tools'
$downloads = Join-Path $root '.cache\downloads'
Set-Location $root
New-Item -ItemType Directory -Force $tools, $downloads | Out-Null

# Folder: where it goes in .tools. Check: the file that proves it is installed.
# Inner: the folder inside the archive that holds the tool ('.' = the archive root).
$pins = @(
    @{ Name = 'uv 0.12.23'; Folder = 'uv'; Check = 'uv\uv.exe'; Inner = '.'
       Url = 'https://github.com/astral-sh/uv/releases/download/0.12.23/uv-x86_64-pc-windows-msvc.zip'
       Sha256 = '75d05de6762778c31ee183398de7dd15093fad0ed90b1f236d8205ea5ec00c90' },
    @{ Name = 'FFmpeg 9.0.2 essentials (gyan.dev)'; Folder = 'ffmpeg'; Check = 'ffmpeg\bin\ffmpeg.exe'
       Inner = 'ffmpeg-9.0.2-essentials_build'
       Url = 'https://github.com/GyanD/codexffmpeg/releases/download/9.0.2/ffmpeg-9.0.2-essentials_build.zip'
       Sha256 = '60f467265b1e312373dbcd92200c2618a74850f98d3d078e94296bb3fa2047ba' },
    @{ Name = 'SoX 14.4.2'; Folder = 'sox'; Check = 'sox\sox.exe'; Inner = 'sox-14.4.2'
       Url = 'https://downloads.sourceforge.net/project/sox/sox/14.4.2/sox-14.4.2-win32.zip'
       Sha256 = '8072cc147cf1a3b3713b8b97d6844bb9389e211ab9e1101e432193fad6ae6662' },
    @{ Name = 'GitHub CLI 2.102.0'; Folder = 'gh'; Check = 'gh\bin\gh.exe'; Inner = '.'
       Url = 'https://github.com/cli/cli/releases/download/v2.102.0/gh_2.102.0_windows_amd64.zip'
       Sha256 = 'ae64e556ecc240b200f7eba60d550e4bb60d78e860e69dd88c449405b86067f4' }
)

function Step([string]$text) { Write-Host "`n== $text" }

function Get-Archive([string]$url, [string]$file) {
    if (Get-Command curl.exe -ErrorAction SilentlyContinue) {
        & curl.exe -sSfL -A curl -o $file $url
        if ($LASTEXITCODE -ne 0) { throw "Download failed: $url" }
    } else {
        Invoke-WebRequest -UseBasicParsing -UserAgent curl -Uri $url -OutFile $file
    }
}

Step 'Portable tools (.tools)'
foreach ($pin in $pins) {
    if (Test-Path (Join-Path $tools $pin.Check)) { Write-Host "  ok    $($pin.Name)"; continue }
    Write-Host "  get   $($pin.Name)"
    $zip = Join-Path $downloads "$($pin.Folder).zip"
    Get-Archive $pin.Url $zip
    $hash = (Get-FileHash -Algorithm SHA256 $zip).Hash.ToLower()
    if ($hash -ne $pin.Sha256) {
        Remove-Item $zip
        throw "$($pin.Name): SHA-256 $hash does not match the pinned $($pin.Sha256). Nothing was installed."
    }
    $stage = Join-Path $downloads "$($pin.Folder)-unpacked"
    if (Test-Path $stage) { Remove-Item -Recurse -Force $stage }
    New-Item -ItemType Directory $stage | Out-Null
    if (Get-Command tar.exe -ErrorAction SilentlyContinue) {
        & tar.exe -xf $zip -C $stage
        if ($LASTEXITCODE -ne 0) { throw "Could not unpack $zip" }
    } else {
        Expand-Archive -Path $zip -DestinationPath $stage
    }
    $target = Join-Path $tools $pin.Folder
    if (Test-Path $target) { Remove-Item -Recurse -Force $target }
    if ($pin.Inner -eq '.') {
        Move-Item $stage $target
    } else {
        Move-Item (Join-Path $stage $pin.Inner) $target
        Remove-Item -Recurse -Force $stage
    }
    Remove-Item $zip
    if (-not (Test-Path (Join-Path $tools $pin.Check))) { throw "$($pin.Name): $($pin.Check) is missing after unpacking." }
    Write-Host "  ok    $($pin.Name)"
}

Step 'Python 3.12'
$uv = Join-Path $tools 'uv\uv.exe'
$ErrorActionPreference = 'Continue'  # PowerShell 5.1 turns redirected stderr into errors
$found = & $uv python find 3.12 --no-project 2>$null
$code = $LASTEXITCODE
$ErrorActionPreference = 'Stop'
if ($code -eq 0 -and $found) {
    Write-Host "  ok    $found"
} else {
    Write-Host '  get   CPython 3.12 into .tools\python (this PC has none)'
    $env:UV_PYTHON_DOWNLOADS = 'manual'
    & $uv python install 3.12 --install-dir (Join-Path $tools 'python') --no-bin --no-registry
    if ($LASTEXITCODE -ne 0) { throw 'Could not install Python 3.12 into .tools\python.' }
    $env:UV_PYTHON_DOWNLOADS = 'never'
}

Step 'Python packages (.venv, from uv.lock)'
& $uv sync --locked
if ($LASTEXITCODE -ne 0) { throw 'uv sync failed; see above.' }
$python = Join-Path $root '.venv\Scripts\python.exe'

Step 'Narrator model (.cache\models, about 340 MB the first time)'
& $python -c "from kit.voices import prepare_kokoro; prepare_kokoro(); print('  ok    Kokoro v1.0, SHA-256 matches voice.toml')"
if ($LASTEXITCODE -ne 0) { throw 'The narrator model could not be fetched or did not match voice.toml.' }

Step 'vid doctor'
& $python (Join-Path $root 'tools\vid.py') doctor

Step 'vid test'
& $python (Join-Path $root 'tools\vid.py') test
if ($LASTEXITCODE -ne 0) { throw 'The unit tests failed; see above.' }

Write-Host "`nReady. Start with: vid status"
exit 0
