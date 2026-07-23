$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")
$env:SEOULMATE_RELOAD = "0"
python backend\app.py
