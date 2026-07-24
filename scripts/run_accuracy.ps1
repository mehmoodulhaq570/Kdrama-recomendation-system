$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")
python tests\evaluation\evaluate_accuracy.py
