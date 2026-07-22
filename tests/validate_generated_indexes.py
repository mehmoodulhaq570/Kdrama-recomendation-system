"""Offline validation for generated SeoulMate lookup indexes.

This script checks whether generated/calibrated JSON indexes contain the
expected evaluator titles before those indexes are trusted in live ranking.
It does not call the backend API.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from itertools import combinations
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"
INDEX_DIR = BACKEND_DIR / "generated_indexes"

sys.path.append(str(BACKEND_DIR))
sys.path.append(str(Path(__file__).resolve().parent))

from evaluate_accuracy import SEARCH_TEST_CASES  # noqa: E402
from query_analyzer import QueryAnalyzer  # noqa: E402


INDEX_FILES = {
    "actor": ["actor_index.json", "calibrated_actor_index.json"],
    "genre": ["genre_index.json", "calibrated_genre_index.json"],
    "genre_combo": ["calibrated_genre_combo_index.json"],
    "theme": ["theme_index.json", "calibrated_theme_index.json"],
    "keyword": ["keyword_index.json", "calibrated_keyword_index.json"],
}

RANK_CUTOFFS = [1, 3, 10, 20]


def load_json(filename: str) -> dict:
    path = INDEX_DIR / filename
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


TITLE_ALIASES = load_json("title_aliases.json")
CANONICAL_ALIASES = defaultdict(set)
for alias, title in TITLE_ALIASES.items():
    CANONICAL_ALIASES[title.lower()].add(alias.lower())


def title_matches(candidate: str, expected_title: str) -> bool:
    candidate_lower = candidate.lower()
    expected_lower = expected_title.lower()
    if expected_lower in candidate_lower or candidate_lower in expected_lower:
        return True

    candidate_alias_target = TITLE_ALIASES.get(candidate_lower, "").lower()
    expected_alias_target = TITLE_ALIASES.get(expected_lower, "").lower()
    if candidate_alias_target and candidate_alias_target == expected_lower:
        return True
    if expected_alias_target and expected_alias_target == candidate_lower:
        return True

    return (
        expected_lower in CANONICAL_ALIASES.get(candidate_lower, set())
        or candidate_lower in CANONICAL_ALIASES.get(expected_lower, set())
    )


def best_rank(candidates: list[str], expected_titles: list[str]) -> int | None:
    for index, candidate in enumerate(candidates, start=1):
        if any(title_matches(candidate, expected) for expected in expected_titles):
            return index
    return None


def category_keys(category: str, query: str, analysis: dict) -> list[str]:
    entities = analysis["entities"]
    if category == "actor":
        return [actor.lower() for actor in entities.get("actors", [])]
    if category == "genre":
        return entities.get("genres", [])
    if category == "genre_combo":
        genres = sorted(set(entities.get("genres", [])))
        if len(genres) < 2:
            return []
        return ["|".join(genre.lower() for genre in combo) for combo in combinations(genres, 2)]
    if category == "theme":
        return entities.get("themes", [])
    if category == "keyword":
        query_lower = query.lower()
        keys = set(query_lower.split())
        keys.add(query_lower)
        keys.update(theme.lower() for theme in entities.get("themes", []))
        keys.update(genre.lower() for genre in entities.get("genres", []))
        return sorted(keys)
    return []


def candidates_for_keys(index_data: dict, keys: list[str]) -> list[str]:
    title_scores = {}
    for key_order, key in enumerate(keys):
        titles = index_data.get(key, [])
        for rank, title in enumerate(titles, start=1):
            title_key = title.lower()
            if title_key not in title_scores:
                title_scores[title_key] = {
                    "title": title,
                    "overlap": 0,
                    "best_rank": rank,
                    "rank_sum": 0,
                    "first_key_order": key_order,
                }
            score = title_scores[title_key]
            score["overlap"] += 1
            score["best_rank"] = min(score["best_rank"], rank)
            score["rank_sum"] += rank
            score["first_key_order"] = min(score["first_key_order"], key_order)

    return [
        score["title"]
        for score in sorted(
            title_scores.values(),
            key=lambda item: (
                -item["overlap"],
                item["best_rank"],
                item["rank_sum"],
                item["first_key_order"],
                item["title"],
            ),
        )
    ]


def empty_metrics():
    return {
        "cases": 0,
        "keyed_cases": 0,
        "hits": {cutoff: 0 for cutoff in RANK_CUTOFFS},
        "misses": [],
        "near_misses": [],
    }


def validate_index(category: str, filename: str, analyzer: QueryAnalyzer):
    index_data = load_json(filename)
    metrics = empty_metrics()

    for query, expected_titles, test_category in SEARCH_TEST_CASES:
        if not expected_titles:
            continue
        if category == "keyword":
            if test_category not in {"genre", "theme"}:
                continue
        elif category == "genre_combo":
            if test_category != "genre":
                continue
        elif test_category != category:
            continue

        analysis = analyzer.analyze(query)
        keys = category_keys(category, query, analysis)
        if not keys:
            if category == "genre_combo":
                continue
            metrics["cases"] += 1
            metrics["misses"].append((query, expected_titles, "no detected keys", []))
            continue

        metrics["cases"] += 1
        metrics["keyed_cases"] += 1
        candidates = candidates_for_keys(index_data, keys)
        rank = best_rank(candidates, expected_titles)
        if rank is None:
            metrics["misses"].append((query, expected_titles, keys, candidates[:5]))
            continue
        if 3 < rank <= 10:
            metrics["near_misses"].append((query, expected_titles, keys, rank, candidates[:10]))

        for cutoff in RANK_CUTOFFS:
            if rank <= cutoff:
                metrics["hits"][cutoff] += 1

    return metrics


def print_report(results: dict):
    print("=" * 72)
    print("GENERATED INDEX OFFLINE VALIDATION")
    print("=" * 72)

    for category, file_results in results.items():
        print(f"\n{category.upper()}")
        print("-" * 72)
        for filename, metrics in file_results.items():
            cases = metrics["cases"]
            keyed = metrics["keyed_cases"]
            print(f"\n{filename}")
            print(f"  Cases: {cases}")
            print(f"  Cases with detected index keys: {keyed}")
            for cutoff in RANK_CUTOFFS:
                rate = (metrics["hits"][cutoff] / cases * 100) if cases else 0
                print(f"  Hit@{cutoff}: {metrics['hits'][cutoff]}/{cases} ({rate:.2f}%)")

            if metrics["misses"]:
                print("  Sample misses:")
                for query, expected, keys, sample in metrics["misses"][:5]:
                    print(f"    - {query!r} expected={expected} keys={keys} sample={sample}")
            if metrics["near_misses"]:
                print("  Near misses:")
                for query, expected, keys, rank, sample in metrics["near_misses"][:5]:
                    print(
                        f"    - {query!r} best_rank={rank} "
                        f"expected={expected} keys={keys} sample={sample}"
                    )


def summarize_recommendations(results: dict):
    print("\n" + "=" * 72)
    print("RECOMMENDATIONS")
    print("=" * 72)

    for category, file_results in results.items():
        best_file = None
        best_score = (-1, -1, -1)
        for filename, metrics in file_results.items():
            score = (metrics["hits"][10], metrics["hits"][3], metrics["hits"][1])
            if score > best_score:
                best_file = filename
                best_score = score

        if not best_file:
            continue

        metrics = file_results[best_file]
        cases = metrics["cases"] or 1
        hit_at_10 = metrics["hits"][10] / cases * 100
        hit_at_3 = metrics["hits"][3] / cases * 100

        if hit_at_3 >= 80:
            guidance = "candidate for cautious ranking fallback"
        elif hit_at_10 >= 80:
            guidance = "use for recall/debug only, not top-rank boosting"
        else:
            guidance = "not ready for live ranking"

        print(
            f"{category}: best={best_file}, Hit@3={hit_at_3:.2f}%, "
            f"Hit@10={hit_at_10:.2f}% -> {guidance}"
        )


def main():
    analyzer = QueryAnalyzer()
    results = defaultdict(dict)

    for category, filenames in INDEX_FILES.items():
        for filename in filenames:
            results[category][filename] = validate_index(category, filename, analyzer)

    print_report(results)
    summarize_recommendations(results)


if __name__ == "__main__":
    main()
