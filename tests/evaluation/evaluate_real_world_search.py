"""
Evaluate SeoulMate against real-world user query examples.

Run after starting the backend:
    python tests/evaluation/evaluate_real_world_search.py

Optional:
    SEOULMATE_API_URL=http://127.0.0.1:8001 python tests/evaluation/evaluate_real_world_search.py
"""

from __future__ import annotations

import json
import os
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import requests

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = os.environ.get("SEOULMATE_API_URL", "http://127.0.0.1:8001")
DATASET_PATH = Path(__file__).with_name("real_world_queries.json")
TOP_N = int(os.environ.get("SEOULMATE_EVAL_TOP_N", "10"))


def normalize_title(title: str) -> str:
    return " ".join(str(title).casefold().split())


def load_cases() -> list[dict[str, Any]]:
    with DATASET_PATH.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        raise ValueError(f"{DATASET_PATH} must contain a JSON list")
    return data


def fetch(query: str) -> dict[str, Any]:
    response = requests.get(
        f"{BASE_URL}/recommend",
        params={"title": query, "top_n": TOP_N, "debug": True},
        timeout=45,
    )
    response.raise_for_status()
    return response.json()


def first_hit_rank(result_titles: list[str], expected_titles: list[str]) -> int | None:
    expected = {normalize_title(title) for title in expected_titles}
    for index, title in enumerate(result_titles, start=1):
        if normalize_title(title) in expected:
            return index
    return None


def recall_at(result_titles: list[str], expected_titles: list[str], k: int) -> float:
    expected = {normalize_title(title) for title in expected_titles}
    if not expected:
        return 0.0
    found = {
        normalize_title(title)
        for title in result_titles[:k]
        if normalize_title(title) in expected
    }
    return len(found) / len(expected)


def has_forbidden_leak(
    recommendations: list[dict[str, Any]], case: dict[str, Any]
) -> tuple[bool, list[str]]:
    leaks: list[str] = []
    title_terms = [term.casefold() for term in case.get("forbidden_title_terms", [])]
    genre_terms = [term.casefold() for term in case.get("forbidden_genre_terms", [])]

    for item in recommendations:
        title = str(item.get("Title", ""))
        genre = str(item.get("Genre", item.get("genres", "")))
        if any(term in title.casefold() for term in title_terms):
            leaks.append(f"title:{title}")
        if any(term in genre.casefold() for term in genre_terms):
            leaks.append(f"genre:{title} [{genre}]")

    return bool(leaks), leaks


def main() -> int:
    cases = load_cases()
    totals = {
        "cases": 0,
        "hit_at_1": 0,
        "hit_at_3": 0,
        "hit_at_5": 0,
        "hit_at_10": 0,
        "mrr": 0.0,
        "recall_at_5": 0.0,
        "recall_at_10": 0.0,
        "forbidden_pass": 0,
    }
    tag_totals: dict[str, dict[str, float]] = defaultdict(
        lambda: {
            "cases": 0,
            "hit_at_5": 0,
            "mrr": 0.0,
            "recall_at_10": 0.0,
        }
    )
    failures: list[str] = []

    print(f"Evaluating {len(cases)} real-world search cases against {BASE_URL}")

    for case in cases:
        totals["cases"] += 1
        query = case["query"]
        expected = case.get("expected", [])
        data = fetch(query)
        recommendations = data.get("recommendations", [])
        result_titles = [item.get("Title", "") for item in recommendations]
        rank = first_hit_rank(result_titles, expected)
        forbidden_leak, leaks = has_forbidden_leak(recommendations, case)

        hit_at_1 = rank is not None and rank <= 1
        hit_at_3 = rank is not None and rank <= 3
        hit_at_5 = rank is not None and rank <= 5
        hit_at_10 = rank is not None and rank <= 10
        reciprocal_rank = 0.0 if rank is None else 1.0 / rank
        case_recall_5 = recall_at(result_titles, expected, 5)
        case_recall_10 = recall_at(result_titles, expected, 10)

        totals["hit_at_1"] += int(hit_at_1)
        totals["hit_at_3"] += int(hit_at_3)
        totals["hit_at_5"] += int(hit_at_5)
        totals["hit_at_10"] += int(hit_at_10)
        totals["mrr"] += reciprocal_rank
        totals["recall_at_5"] += case_recall_5
        totals["recall_at_10"] += case_recall_10
        totals["forbidden_pass"] += int(not forbidden_leak)

        for tag in case.get("tags", []):
            tag_totals[tag]["cases"] += 1
            tag_totals[tag]["hit_at_5"] += int(hit_at_5)
            tag_totals[tag]["mrr"] += reciprocal_rank
            tag_totals[tag]["recall_at_10"] += case_recall_10

        status = "PASS" if hit_at_5 and not forbidden_leak else "FAIL"
        print(f"\n{status}: {case['id']} :: {query}")
        print(f"  expected: {expected}")
        print(f"  top: {result_titles[:10]}")
        print(
            f"  first_hit_rank={rank} recall@5={case_recall_5:.2f} "
            f"recall@10={case_recall_10:.2f}"
        )
        if forbidden_leak:
            print(f"  forbidden leaks: {leaks}")

        if status == "FAIL":
            failures.append(case["id"])

    case_count = totals["cases"] or 1
    print("\n" + "=" * 64)
    print("REAL-WORLD SEARCH EVALUATION SUMMARY")
    print("=" * 64)
    print(f"Cases: {int(totals['cases'])}")
    print(f"Hit@1:  {totals['hit_at_1'] / case_count:.1%}")
    print(f"Hit@3:  {totals['hit_at_3'] / case_count:.1%}")
    print(f"Hit@5:  {totals['hit_at_5'] / case_count:.1%}")
    print(f"Hit@10: {totals['hit_at_10'] / case_count:.1%}")
    print(f"MRR:    {totals['mrr'] / case_count:.3f}")
    print(f"Avg Recall@5:  {totals['recall_at_5'] / case_count:.3f}")
    print(f"Avg Recall@10: {totals['recall_at_10'] / case_count:.3f}")
    print(f"Forbidden checks passed: {totals['forbidden_pass'] / case_count:.1%}")

    print("\nTag breakdown:")
    for tag, stats in sorted(tag_totals.items()):
        tag_count = stats["cases"] or 1
        print(
            f"  {tag}: cases={int(stats['cases'])} "
            f"Hit@5={stats['hit_at_5'] / tag_count:.1%} "
            f"MRR={stats['mrr'] / tag_count:.3f} "
            f"Recall@10={stats['recall_at_10'] / tag_count:.3f}"
        )

    if failures:
        print("\nFailed cases:")
        for case_id in failures:
            print(f"  - {case_id}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
