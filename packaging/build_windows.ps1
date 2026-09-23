$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
py -3.12 -m venv .venv-win
& .\.venv-win\Scripts\python.exe -m pip install --upgrade pip
& .\.venv-win\Scripts\python.exe -m pip install ".[ui,windows,test]"
& .\.venv-win\Scripts\python.exe -m pytest
& .\.venv-win\Scripts\pyinstaller.exe --noconfirm --clean --name PowerPointApp --windowed --collect-all matplotlib --add-data "templates;templates" src\powerpoint_app\main.py
& .\.venv-win\Scripts\pyinstaller.exe --noconfirm --clean --onefile --name PowerPointPreview --distpath dist\PowerPointApp src\powerpoint_app\office\preview_worker.py
Write-Host "Mappebygning klar i dist\PowerPointApp"
