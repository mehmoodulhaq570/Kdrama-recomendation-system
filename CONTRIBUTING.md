# Contributing to SeoulMate

Thank you for improving SeoulMate. This project is organized so backend ranking, frontend UI, training artifacts, tests, and scraping utilities stay separate.

## Development Setup

Install dependencies:

```powershell
pip install -r requirements.txt
```

For smaller installs:

```powershell
pip install -r frontend\requirements.txt
pip install -r training\requirements.txt
```

## Running Locally

Start the backend:

```powershell
.\scripts\run_backend.ps1
```

Start the frontend in a second terminal:

```powershell
.\scripts\run_frontend.ps1
```

## Common Checks

Compile Python files:

```powershell
python -m compileall backend frontend training tests
```

Run offline generated-index validation:

```powershell
python tests\evaluation\validate_generated_indexes.py
```

Run live accuracy evaluation after starting the backend:

```powershell
.\scripts\run_accuracy.ps1
```

## Where Changes Should Go

Use these ownership rules:

| Change Type | Location |
| --- | --- |
| API and recommendation runtime | `backend/` |
| Ranking priors and generated indexes | `backend/ranking/` |
| Streamlit interface | `frontend/` |
| Training and FAISS index generation | `training/` |
| Final dataset | `data/final/` |
| Scraping utilities | `scrapers/` |
| Accuracy and ranking evaluation | `tests/evaluation/`, `tests/ranking/` |
| Debug helpers | `tests/debug/` |
| Historical notes | `docs/archived/` or `tests/docs/` |

## Changelog Rules

Update `CHANGELOG.md` for important changes. Use the current date and keep entries focused on decisions, accuracy changes, structural moves, and user-facing behavior.

## Runtime Data

Do not commit runtime data, cache files, or local user profiles. These are ignored:

```text
backend/runtime_data/
analytics_data/
backend/analytics_data/
backend/user_profiles/
user_profiles/
__pycache__/
*.pyc
```

## Ranking Changes

When changing ranking logic:

1. Run targeted query checks.
2. Run `python tests\evaluation\validate_generated_indexes.py`.
3. Run live accuracy when possible.
4. Keep a note in `CHANGELOG.md` with the accuracy impact.

Do not make generated-only replacement the default unless it beats or matches the stable curated baseline.
