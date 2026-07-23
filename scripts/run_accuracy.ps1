$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")
python tests\evaluate_accuracy.py
