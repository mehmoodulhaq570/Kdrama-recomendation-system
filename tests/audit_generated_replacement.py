"""
Audit the gap between curated genre priors and full generated replacement.

This script reads tests/reports/ranking_mode_comparison.json and classifies
why generated replacement loses against the curated baseline. It does not run
the backend; run compare_ranking_modes.py first when fresh data is needed.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "tests" / "reports"
COMPARISON_PATH = REPORT_DIR / "ranking_mode_comparison.json"
JSON_OUT = REPORT_DIR / "generated_replacement_audit.json"
MD_OUT = REPORT_DIR / "generated_replacement_audit.md"
PRIMARY_MODE = "generated_genre_soft"


def title_matches(candidate: str, expected: str) -> bool:
    candidate = candidate.lower()
    expected = expected.lower()
    return expected in candidate or candidate in expected


def expected_in_titles(titles: list[str], expected: str) -> bool:
    return any(title_matches(title, expected) for title in titles)


def expected_found(titles: list[str], expected: list[str], k: int) -> list[str]:
    top_k = titles[:k]
    return [item for item in expected if expected_in_titles(top_k, item)]


def noisy_above_expected(mode_top10: list[str], expected: list[str]) -> list[str]:
    expected_ranks = [
        index
        for index, title in enumerate(mode_top10)
        if any(title_matches(title, item) for item in expected)
    ]
    if not expected_ranks:
        return mode_top10[:5]
    first_expected_rank = min(expected_ranks)
    return mode_top10[:first_expected_rank]


def classify(row: dict, mode: dict) -> list[str]:
    labels = []
    expected = row["expected"]
    top10 = mode["top10"]
    baseline = row["baseline"]

    if not mode["detected_genres"] and row["category"] == "genre":
        labels.append("genre_not_detected")
    if not mode["detected_themes"] and row["category"] == "theme":
        labels.append("theme_not_detected")
    if not mode["detected_actors"] and row["category"] == "actor":
        labels.append("actor_not_detected")

    found_top3 = expected_found(top10, expected, 3)
    found_top10 = expected_found(top10, expected, 10)
    baseline_found_top3 = expected_found(baseline["top10"], expected, 3)

    if len(found_top10) < len(expected):
        labels.append("expected_missing_from_generated_top10")
    if len(found_top3) < len(baseline_found_top3):
        labels.append("expected_ranked_too_low")
    if mode["delta_precision_at_3"] < 0:
        labels.append("top3_precision_regression")
    if mode["delta_mrr"] < 0:
        labels.append("first_relevant_rank_regression")

    noisy = noisy_above_expected(top10, expected)
    if noisy:
        labels.append("noisy_titles_above_expected")

    return labels or ["no_material_gap"]


def impact_score(mode: dict) -> float:
    return (
        abs(min(mode["delta_precision_at_3"], 0)) * 0.45
        + abs(min(mode["delta_recall_at_10"], 0)) * 0.35
        + abs(min(mode["delta_mrr"], 0)) * 0.20
    )


def audit(comparison: dict) -> dict:
    cases = []
    label_counts = Counter()
    category_impact = defaultdict(float)
    query_impact = []

    for row in comparison["comparisons"]:
        mode = row["modes"][PRIMARY_MODE]
        labels = classify(row, mode)
        score = impact_score(mode)
        if score <= 0:
            continue

        for label in labels:
            label_counts[label] += 1
        category_impact[row["category"]] += score

        case = {
            "query": row["query"],
            "category": row["category"],
            "expected": row["expected"],
            "labels": labels,
            "impact": score,
            "baseline_top5": row["baseline"]["top10"][:5],
            "generated_top10": mode["top10"],
            "generated_top5": mode["top10"][:5],
            "missing_top10": [
                item
                for item in row["expected"]
                if not expected_in_titles(mode["top10"], item)
            ],
            "ranked_too_low": [
                item
                for item in row["expected"]
                if expected_in_titles(mode["top10"], item)
                and not expected_in_titles(mode["top10"][:3], item)
            ],
            "noisy_above_expected": noisy_above_expected(
                mode["top10"], row["expected"]
            )[:5],
            "deltas": {
                "precision_at_3": mode["delta_precision_at_3"],
                "recall_at_10": mode["delta_recall_at_10"],
                "mrr": mode["delta_mrr"],
            },
            "detected": {
                "genres": mode["detected_genres"],
                "themes": mode["detected_themes"],
                "actors": mode["detected_actors"],
            },
        }
        cases.append(case)
        query_impact.append((row["query"], score))

    cases.sort(key=lambda item: item["impact"], reverse=True)

    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "source": str(COMPARISON_PATH),
        "primary_mode": PRIMARY_MODE,
        "summary": {
            "baseline": comparison["summary"]["curated_baseline"],
            "generated": comparison["summary"][PRIMARY_MODE],
            "label_counts": dict(label_counts.most_common()),
            "category_impact": dict(
                sorted(category_impact.items(), key=lambda item: item[1], reverse=True)
            ),
            "top_query_impact": query_impact[:10],
        },
        "cases": cases,
    }


def write_markdown(report: dict) -> None:
    summary = report["summary"]
    lines = [
        "# Generated Replacement Audit",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Mode: `{report['primary_mode']}`",
        "",
        "## Baseline Gap",
        "",
        (
            f"- Curated baseline: P@3 `{summary['baseline']['precision_at_3']:.2%}`, "
            f"R@10 `{summary['baseline']['recall_at_10']:.2%}`, "
            f"MRR `{summary['baseline']['mrr']:.3f}`"
        ),
        (
            f"- Generated replacement: P@3 `{summary['generated']['precision_at_3']:.2%}`, "
            f"R@10 `{summary['generated']['recall_at_10']:.2%}`, "
            f"MRR `{summary['generated']['mrr']:.3f}`"
        ),
        "",
        "## Failure Types",
        "",
    ]

    for label, count in summary["label_counts"].items():
        lines.append(f"- `{label}`: `{count}`")

    lines.extend(["", "## Category Impact", ""])
    for category, score in summary["category_impact"].items():
        lines.append(f"- `{category}`: `{score:.3f}`")

    lines.extend(["", "## Highest Impact Cases", ""])
    for case in report["cases"][:15]:
        lines.extend(
            [
                f"### {case['query']} ({case['category']})",
                "",
                f"- Impact: `{case['impact']:.3f}`",
                f"- Labels: {', '.join(f'`{label}`' for label in case['labels'])}",
                f"- Expected: {', '.join(case['expected'])}",
                f"- Missing top10: {', '.join(case['missing_top10']) or 'none'}",
                f"- Ranked too low: {', '.join(case['ranked_too_low']) or 'none'}",
                f"- Noisy above expected: {', '.join(case['noisy_above_expected']) or 'none'}",
                f"- Curated top5: {', '.join(case['baseline_top5'])}",
                f"- Generated top5: {', '.join(case['generated_top5'])}",
                "",
            ]
        )

    lines.extend(
        [
            "## Recommended Fix Order",
            "",
            "1. Fix `expected_missing_from_generated_top10` first because ranking cannot recover missing candidates.",
            "2. Then fix `expected_ranked_too_low` with generated index scoring, not app-level title lists.",
            "3. Treat `noisy_titles_above_expected` as negative-signal work: identify metadata traits of the noisy titles and add general penalties.",
            "4. Re-run `compare_ranking_modes.py` and this audit after every focused change.",
            "",
        ]
    )
    MD_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    comparison = json.loads(COMPARISON_PATH.read_text(encoding="utf-8"))
    report = audit(comparison)
    JSON_OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    write_markdown(report)

    print(f"Wrote {JSON_OUT}")
    print(f"Wrote {MD_OUT}")
    print("Top failure types:")
    for label, count in report["summary"]["label_counts"].items():
        print(f"  {label}: {count}")


if __name__ == "__main__":
    main()
