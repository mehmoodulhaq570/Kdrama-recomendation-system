"""
Live search regression suite for SeoulMate.

This suite checks intent routing and result behavior for the current product
semantics. Unlike the older broad accuracy evaluator, exact title queries are
expected to return similar recommendations, not the title itself.

Run after starting the backend:
    python tests/evaluation/search_regression_suite.py
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from typing import Callable

import requests

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = os.environ.get("SEOULMATE_API_URL", "http://127.0.0.1:8001")


@dataclass
class SearchCase:
    name: str
    params: dict
    checks: list[Callable[[dict], tuple[bool, str]]]


def titles(data: dict) -> list[str]:
    return [item.get("Title", "") for item in data.get("recommendations", [])]


def genres(data: dict) -> list[str]:
    return [item.get("Genre", "") for item in data.get("recommendations", [])]


def debug(data: dict) -> dict:
    return data.get("debug", {})


def has_debug_value(key: str, expected):
    def check(data: dict):
        actual = debug(data).get(key)
        return actual == expected, f"debug.{key} expected {expected!r}, got {actual!r}"

    return check


def title_absent(title: str):
    def check(data: dict):
        result_titles = titles(data)
        return title not in result_titles, f"{title!r} should not appear in results"

    return check


def title_in_top(expected: str, k: int = 3):
    def check(data: dict):
        top_titles = titles(data)[:k]
        return (
            expected in top_titles,
            f"{expected!r} expected in top {k}, got {top_titles}",
        )

    return check


def any_title_in_top(expected: list[str], k: int = 8):
    def check(data: dict):
        top_titles = titles(data)[:k]
        return (
            any(title in top_titles for title in expected),
            f"one of {expected!r} expected in top {k}, got {top_titles}",
        )

    return check


def no_title_word(word: str):
    def check(data: dict):
        result_titles = titles(data)
        bad = [title for title in result_titles if word.lower() in title.lower()]
        return not bad, f"literal word {word!r} leaked into titles: {bad}"

    return check


def no_genre(excluded: str):
    def check(data: dict):
        bad = [genre for genre in genres(data) if excluded.lower() in genre.lower()]
        return not bad, f"excluded genre {excluded!r} found in: {bad}"

    return check


def debug_list_contains(key: str, expected: str):
    def check(data: dict):
        values = debug(data).get(key, [])
        return expected in values, f"debug.{key} should contain {expected!r}: {values}"

    return check


def debug_list_contains_prefix(key: str, expected_prefix: str):
    def check(data: dict):
        values = debug(data).get(key, [])
        return any(str(value).startswith(expected_prefix) for value in values), (
            f"debug.{key} should contain prefix {expected_prefix!r}: {values}"
        )

    return check


def result_lists_differ(first: dict, second: dict) -> tuple[bool, str]:
    first_titles = titles(first)
    second_titles = titles(second)
    return first_titles != second_titles, (
        f"refresh should vary results, both were {first_titles}"
    )


CASES = [
    SearchCase(
        name="exact title uses similarity mode",
        params={"title": "Crash Landing on You", "top_n": 8, "debug": True},
        checks=[
            has_debug_value("search_mode", "title_similarity"),
            has_debug_value("bm25_weight", 0.0),
            has_debug_value("resolved_title", "Crash Landing on You"),
            title_absent("Crash Landing on You"),
            no_title_word("crash"),
            any_title_in_top(["King2Hearts", "Descendants of the Sun"], 3),
        ],
    ),
    SearchCase(
        name="alias resolves to title similarity",
        params={"title": "CLOY", "top_n": 8, "debug": True},
        checks=[
            has_debug_value("search_mode", "title_similarity"),
            has_debug_value("resolved_title", "Crash Landing on You"),
            title_absent("Crash Landing on You"),
        ],
    ),
    SearchCase(
        name="similar phrase resolves title",
        params={"title": "shows like Goblin", "top_n": 8, "debug": True},
        checks=[
            has_debug_value("search_mode", "similar_to"),
            has_debug_value("similar_to", "Guardian: The Lonely and Great God"),
            title_absent("Guardian: The Lonely and Great God"),
            any_title_in_top(["Kiss Goblin", "My Demon", "The Atypical Family"], 8),
        ],
    ),
    SearchCase(
        name="explicit similar_to excludes seed",
        params={
            "title": "similar to Business Proposal",
            "similar_to": "Business Proposal",
            "top_n": 8,
            "debug": True,
        },
        checks=[
            has_debug_value("search_mode", "similar_to"),
            has_debug_value("similar_to", "Business Proposal"),
            title_absent("Business Proposal"),
            any_title_in_top(["What's Wrong with Secretary Kim", "King the Land"], 3),
        ],
    ),
    SearchCase(
        name="romance excludes historical",
        params={"title": "romance drama without historical", "top_n": 8, "debug": True},
        checks=[
            debug_list_contains("excluded_genres", "Historical"),
            no_genre("Historical"),
        ],
    ),
    SearchCase(
        name="thriller excludes horror",
        params={"title": "thriller no horror", "top_n": 8, "debug": True},
        checks=[
            debug_list_contains("excluded_genres", "Horror"),
            no_genre("Horror"),
        ],
    ),
    SearchCase(
        name="actor query routes to actor mode",
        params={"title": "Park Seo Joon drama", "top_n": 8, "debug": True},
        checks=[
            has_debug_value("search_mode", "actor_based"),
            title_in_top("Itaewon Class", 3),
        ],
    ),
    SearchCase(
        name="theme query is not mistaken for actor mode",
        params={
            "title": "school bullying revenge drama",
            "top_n": 8,
            "debug": True,
        },
        checks=[
            lambda data: (
                debug(data).get("search_mode") != "actor_based",
                f"search mode should not be actor_based: {debug(data)}",
            ),
            title_in_top("The Glory", 3),
        ],
    ),
    SearchCase(
        name="seen titles are demoted",
        params={
            "title": "comedy drama",
            "top_n": 8,
            "seen_titles": "Business Proposal|What's Wrong with Secretary Kim",
            "debug": True,
        },
        checks=[
            lambda data: (
                "Business Proposal" not in titles(data)[:2],
                f"seen title was not demoted: {titles(data)[:5]}",
            ),
            lambda data: (
                "What's Wrong with Secretary Kim" not in titles(data)[:2],
                f"seen title was not demoted: {titles(data)[:5]}",
            ),
        ],
    ),
    SearchCase(
        name="mood prior supports funny drama",
        params={"title": "funny drama", "top_n": 8, "debug": True},
        checks=[
            debug_list_contains("extra_prior_terms", "mood:funny"),
            any_title_in_top(["Business Proposal", "Mr. Queen", "Gaus Electronics"], 5),
        ],
    ),
    SearchCase(
        name="relationship prior supports office romance",
        params={"title": "office romance", "top_n": 8, "debug": True},
        checks=[
            debug_list_contains("extra_prior_terms", "relationship:office romance"),
            any_title_in_top(["Business Proposal", "What's Wrong with Secretary Kim"], 3),
        ],
    ),
    SearchCase(
        name="setting prior supports school setting",
        params={"title": "school setting", "top_n": 8, "debug": True},
        checks=[
            debug_list_contains("extra_prior_terms", "setting:School"),
            any_title_in_top(["True Beauty", "Extraordinary You", "Weak Hero Class 1"], 5),
        ],
    ),
    SearchCase(
        name="occupation prior supports doctor drama",
        params={"title": "doctor drama", "top_n": 8, "debug": True},
        checks=[
            debug_list_contains("extra_prior_terms", "occupation:Doctor"),
            any_title_in_top(["Hospital Playlist", "Dr. Romantic", "Doctor Cha"], 5),
        ],
    ),
    SearchCase(
        name="ending prior supports happy ending romance",
        params={"title": "romance with happy ending", "top_n": 8, "debug": True},
        checks=[
            debug_list_contains("extra_prior_terms", "ending:happy ending"),
            any_title_in_top(["Business Proposal", "King the Land", "Touch Your Heart"], 5),
        ],
    ),
    SearchCase(
        name="episode-count prior supports short drama",
        params={"title": "short drama", "top_n": 8, "debug": True},
        checks=[
            debug_list_contains("extra_prior_terms", "episode_count:short drama"),
            any_title_in_top(["The Glory", "Bloodhounds", "Move to Heaven"], 5),
        ],
    ),
    SearchCase(
        name="character prior supports strong female lead",
        params={"title": "strong female lead", "top_n": 8, "debug": True},
        checks=[
            debug_list_contains_prefix("extra_prior_terms", "character:strong female lead"),
            any_title_in_top(["Strong Woman Do Bong Soon", "My Name", "The Glory"], 5),
        ],
    ),
]


def fetch(params: dict) -> dict:
    response = requests.get(f"{BASE_URL}/recommend", params=params, timeout=25)
    response.raise_for_status()
    return response.json()


def run_case(case: SearchCase) -> bool:
    data = fetch(case.params)
    print(f"\nCASE: {case.name}")
    print(
        "debug:",
        {
            key: debug(data).get(key)
            for key in [
                "search_mode",
                "resolved_title",
                "resolved_source",
                "similar_to",
                "semantic_weight",
                "bm25_weight",
                "excluded_genres",
                "excluded_themes",
                "seen_titles_penalized",
                "extra_prior_terms",
            ]
        },
    )
    print("top:", titles(data)[:8])

    passed = True
    for check in case.checks:
        ok, message = check(data)
        if ok:
            print(f"  PASS: {message}")
        else:
            print(f"  FAIL: {message}")
            passed = False
    return passed


def run_refresh_check() -> bool:
    first = fetch({"title": "comedy drama", "top_n": 8, "refresh": 1, "debug": True})
    second = fetch({"title": "comedy drama", "top_n": 8, "refresh": 2, "debug": True})
    ok, message = result_lists_differ(first, second)
    print("\nCASE: refresh varies broad browse results")
    print("refresh=1:", titles(first)[:8])
    print("refresh=2:", titles(second)[:8])
    print(f"  {'PASS' if ok else 'FAIL'}: {message}")
    return ok


def main() -> int:
    try:
        health = requests.get(f"{BASE_URL}/", timeout=8)
        health.raise_for_status()
    except Exception as exc:
        print(f"Backend is not reachable at {BASE_URL}: {exc}")
        return 2

    passed = 0
    total = len(CASES) + 1
    for case in CASES:
        if run_case(case):
            passed += 1

    if run_refresh_check():
        passed += 1

    print("\n" + "=" * 60)
    print(f"SEARCH REGRESSION SUMMARY: {passed}/{total} passed ({passed / total:.1%})")
    print("=" * 60)
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
