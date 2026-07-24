"""
Trace one query through generated-index candidates and final API ranking.

Usage:
    python tests/debug/debug_generated_query.py "school drama"

This is an API-level diagnostic for generated replacement work. It shows what
the calibrated generated indexes can offer for a query, then compares that with
the final recommendations returned by the backend.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from itertools import combinations
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[2]
EVALUATION_DIR = ROOT / "tests" / "evaluation"
sys.path.append(str(EVALUATION_DIR))

from evaluate_accuracy import SEARCH_TEST_CASES


BACKEND_DIR = ROOT / "backend"
GENERATED_INDEX_DIR = BACKEND_DIR / "ranking" / "indexes"
REPORT_DIR = ROOT / "tests" / "reports"
DEBUG_REPORT_DIR = REPORT_DIR / "debug"
LOG_DIR = REPORT_DIR / "logs"
DEFAULT_PORT = 8041

sys.path.append(str(BACKEND_DIR))
from query_analyzer import QueryAnalyzer  # noqa: E402


BASE_WEIGHTS = {
    "genre_combo": 1.9,
    "genre": 1.65,
    "theme_combo": 3.1,
    "theme": 2.4,
    "actor": 2.35,
    "generated_actor": 0.0,
    "generated_genre": 0.0,
    "generated_theme": 0.0,
    "generated_cap": 1.0,
}


def slugify(value):
    slug = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return slug or "query"


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def json_safe(value):
    if hasattr(value, "value"):
        return value.value
    if isinstance(value, dict):
        return {key: json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [json_safe(item) for item in value]
    if isinstance(value, tuple):
        return [json_safe(item) for item in value]
    return value


def normalize_title(title):
    return re.sub(r"[^a-z0-9]+", "", str(title).lower())


def get_expected_titles(query):
    query_lower = query.lower()
    for case_query, expected, category in SEARCH_TEST_CASES:
        if case_query.lower() == query_lower:
            return expected or [], category
    return [], "custom"


def title_matches(title, expected_titles, aliases):
    title_norm = normalize_title(title)
    for expected in expected_titles:
        expected_norm = normalize_title(expected)
        if expected_norm and (expected_norm in title_norm or title_norm in expected_norm):
            return True

        for alias in aliases.get(expected, []):
            alias_norm = normalize_title(alias)
            if alias_norm and (alias_norm in title_norm or title_norm in alias_norm):
                return True
    return False


def title_rank(titles, expected_titles, aliases):
    for rank, title in enumerate(titles, start=1):
        if title_matches(title, expected_titles, aliases):
            return rank
    return None


def genre_key(genre):
    return str(genre).strip().title()


def combo_key(items):
    return "|".join(sorted(str(item).strip().lower() for item in items if item))


def unique_titles(titles):
    seen = set()
    unique = []
    for title in titles:
        key = normalize_title(title)
        if key in seen:
            continue
        seen.add(key)
        unique.append(title)
    return unique


def collect_generated_candidates(analysis, genre_index, combo_index, limit):
    genres = analysis.get("entities", {}).get("genres", [])

    genre_sections = []
    for genre in genres:
        key = genre_key(genre)
        titles = genre_index.get(key, [])[:limit]
        genre_sections.append({"key": key, "titles": titles})

    combo_sections = []
    for combo_size in range(2, min(len(genres), 3) + 1):
        for combo in combinations(genres, combo_size):
            key = combo_key(combo)
            titles = combo_index.get(key, [])[:limit]
            if titles:
                combo_sections.append({"key": key, "titles": titles})

    combined = []
    for section in combo_sections + genre_sections:
        combined.extend(section["titles"])

    return {
        "detected_genres": genres,
        "genre_sections": genre_sections,
        "combo_sections": combo_sections,
        "combined_titles": unique_titles(combined),
    }


def wait_for_api(base_url, timeout=240):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            response = requests.get(f"{base_url}/", timeout=3)
            if response.status_code < 500:
                return
        except requests.RequestException:
            time.sleep(2)
    raise RuntimeError(f"Backend did not become ready at {base_url}")


def start_backend(port, mode):
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["SEOULMATE_PORT"] = str(port)
    env["SEOULMATE_RELOAD"] = "0"
    env["SEOULMATE_GENRE_PRIOR_SOURCE"] = mode
    env["SEOULMATE_PRIOR_WEIGHTS"] = json.dumps(BASE_WEIGHTS)
    env["PYTHONIOENCODING"] = "utf-8"

    log_path = LOG_DIR / "debug_generated_query_backend.log"
    log_handle = log_path.open("w", encoding="utf-8")
    process = subprocess.Popen(
        [sys.executable, "app.py"],
        cwd=BACKEND_DIR,
        env=env,
        stdout=log_handle,
        stderr=subprocess.STDOUT,
        text=True,
    )
    return process, log_handle, log_path


def get_json(base_url, path, params):
    response = requests.get(f"{base_url}{path}", params=params, timeout=60)
    response.raise_for_status()
    return response.json()


def classify_loss(expected, generated_titles, final_titles, aliases):
    generated_rank = title_rank(generated_titles, expected, aliases)
    final_rank = title_rank(final_titles, expected, aliases)

    if not expected:
        return "no_ground_truth", generated_rank, final_rank
    if generated_rank is None:
        return "missing_from_generated_index", generated_rank, final_rank
    if final_rank is None:
        return "lost_between_generated_index_and_final_api", generated_rank, final_rank
    if final_rank > 3:
        return "final_ranking_too_low", generated_rank, final_rank
    return "ok_top3", generated_rank, final_rank


def titles_above_expected(final_titles, expected, aliases):
    rank = title_rank(final_titles, expected, aliases)
    if not rank:
        return final_titles
    return final_titles[: rank - 1]


def write_markdown(report, path):
    lines = [
        "# Generated Query Debug",
        "",
        f"- Query: `{report['query']}`",
        f"- Generated at: `{report['generated_at']}`",
        f"- Mode: `{report['mode']}`",
        f"- Expected: {', '.join(report['expected']) or 'none'}",
        f"- Classification: `{report['classification']}`",
        f"- Generated candidate rank: `{report['generated_expected_rank']}`",
        f"- Final API rank: `{report['final_expected_rank']}`",
        "",
        "## Analyzer",
        "",
        f"- Intent: `{report['analysis'].get('intent')}`",
        f"- Detected genres: {', '.join(report['generated_candidates']['detected_genres']) or 'none'}",
        "",
        "## Final API Top 10",
        "",
    ]
    for rank, title in enumerate(report["final_top10"], start=1):
        lines.append(f"{rank}. {title}")

    lines.extend(["", "## Titles Above Expected", ""])
    above = report["titles_above_expected"]
    if above:
        for title in above:
            lines.append(f"- {title}")
    else:
        lines.append("- none")

    lines.extend(["", "## Generated Combo Candidates", ""])
    if report["generated_candidates"]["combo_sections"]:
        for section in report["generated_candidates"]["combo_sections"]:
            lines.append(f"### {section['key']}")
            for rank, title in enumerate(section["titles"], start=1):
                lines.append(f"{rank}. {title}")
            lines.append("")
    else:
        lines.append("- none")

    lines.extend(["", "## Generated Genre Candidates", ""])
    for section in report["generated_candidates"]["genre_sections"]:
        lines.append(f"### {section['key']}")
        for rank, title in enumerate(section["titles"], start=1):
            lines.append(f"{rank}. {title}")
        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def build_report(args):
    analyzer = QueryAnalyzer()
    local_analysis = analyzer.analyze(args.query)
    genre_index = load_json(GENERATED_INDEX_DIR / "calibrated_genre_index.json")
    combo_index = load_json(GENERATED_INDEX_DIR / "calibrated_genre_combo_index.json")
    aliases = load_json(GENERATED_INDEX_DIR / "title_aliases.json")
    expected, category = get_expected_titles(args.query)
    generated_candidates = collect_generated_candidates(
        local_analysis, genre_index, combo_index, args.index_limit
    )

    base_url = f"http://127.0.0.1:{args.port}"
    process, log_handle, log_path = start_backend(args.port, args.mode)
    try:
        try:
            wait_for_api(base_url)
        except RuntimeError as exc:
            log_handle.flush()
            tail = log_path.read_text(encoding="utf-8", errors="replace")[-3000:]
            raise RuntimeError(f"{exc}\nBackend log tail:\n{tail}") from exc

        api_analysis = get_json(base_url, "/analyze", {"query": args.query})
        recommendation_data = get_json(
            base_url, "/recommend", {"title": args.query, "top_n": 10}
        )
    finally:
        process.terminate()
        try:
            process.wait(timeout=15)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=15)
        log_handle.close()
        try:
            log_path.unlink()
        except OSError:
            pass

    final_top10 = [
        item.get("Title", "") for item in recommendation_data.get("recommendations", [])
    ]
    classification, generated_rank, final_rank = classify_loss(
        expected, generated_candidates["combined_titles"], final_top10, aliases
    )

    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "query": args.query,
        "category": category,
        "mode": args.mode,
        "weights": BASE_WEIGHTS,
        "expected": expected,
        "analysis": {
            "local": json_safe(local_analysis),
            "api": api_analysis,
            "intent": api_analysis.get("intent"),
        },
        "generated_candidates": generated_candidates,
        "final_top10": final_top10,
        "classification": classification,
        "generated_expected_rank": generated_rank,
        "final_expected_rank": final_rank,
        "titles_above_expected": titles_above_expected(final_top10, expected, aliases),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Debug one query in generated replacement mode."
    )
    parser.add_argument("query", help="Query to inspect, for example: school drama")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument(
        "--mode",
        default="calibrated_generated",
        choices=["calibrated_generated", "calibrated_generated_combo_only"],
    )
    parser.add_argument("--index-limit", type=int, default=15)
    args = parser.parse_args()

    DEBUG_REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report(args)
    slug = slugify(args.query)
    json_path = DEBUG_REPORT_DIR / f"debug_generated_query_{slug}.json"
    markdown_path = DEBUG_REPORT_DIR / f"debug_generated_query_{slug}.md"
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    write_markdown(report, markdown_path)

    print(f"Query: {report['query']}")
    print(f"Classification: {report['classification']}")
    print(f"Generated expected rank: {report['generated_expected_rank']}")
    print(f"Final API expected rank: {report['final_expected_rank']}")
    print(f"Wrote {json_path}")
    print(f"Wrote {markdown_path}")


if __name__ == "__main__":
    main()
