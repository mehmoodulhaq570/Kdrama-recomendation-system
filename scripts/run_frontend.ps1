$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")
streamlit run frontend\streamlit_app.py
