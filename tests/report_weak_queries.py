"""
Generate a weak-query report for SeoulMate search accuracy.

The report focuses on expected-result search cases from evaluate_accuracy.py and
captures per-query metrics, top results, analyzer output, and a likely failure
reason. By default it starts an isolated backend instance so the report is
repeatable from a single command.
"""

import argparse
import json
import os
import subprocess
import sys
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import requests

from evaluate_accuracy import (
    SEARCH_TEST_CASES,
    calculate_mrr,
    calculate_ndcg_at_k,
    calculate_precision_at_k,
    calculate_recall_at_k,
)


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "tests" / "reports"
AUDIT_DIR = REPORT_DIR / "audits"
LOG_DIR = REPORT_DIR / "logs"
DEFAULT_PORT = 8021


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


def start_backend(port):
    env = os.environ.copy()
    env["SEOULMATE_PORT"] = str(port)
    env["SEOULMATE_RELOAD"] = "0"
    env["PYTHONIOENCODING"] = "utf-8"

    log_path = LOG_DIR / "weak_query_backend.log"
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_handle = log_path.open("w", encoding="utf-8")
    process = subprocess.Popen(
        [sys.executable, "app.py"],
        cwd=ROOT / "backend",
        env=env,
        stdout=log_handle,
        stderr=subprocess.STDOUT,
        text=True,
    )
    return process, log_handle, log_path


def expected_found_in_top(results, expected, k):
    top_k = results[:k]
    return [
        title
        for title in expected
        if any(title.lower() in result.lower() for result in top_k)
    ]


def classify_failure(category, expected, titles, analysis, precision, recall, mrr):
    detected_genres = analysis.get("detected_genres", [])
    detected_actors = analysis.get("detected_actors", [])
    detected_themes = analysis.get("detected_themes", [])

    if recall == 1.0 and precision < 1.0:
        return "relevant_titles_present_but_not_top3"
    if category == "genre" and not detected_genres:
        return "genre_not_detected"
    if category == "actor" and not detected_actors:
        return "actor_not_detected"
    if category == "theme" and not detected_themes:
        return "theme_not_detected"
    if category == "typo" and mrr == 0.0:
        return "title_alias_or_fuzzy_match_missing"
    if expected and not expected_found_in_top(titles, expected, 10):
        return "expected_titles_missing_from_top10"
    return "ranking_order_weak"


def is_weak_query(row):
    if row["recall_at_10"] < 1.0 or row["mrr"] < 1.0:
        return True
    if len(row["expected"]) > 1 and row["precision_at_3"] < 1.0:
        return True
    return False


def get_json(base_url, path, params):
    response = requests.get(f"{base_url}{path}", params=params, timeout=60)
    response.raise_for_status()
    return response.json()


def collect_report(base_url):
    rows = []
    category_metrics = defaultdict(lambda: {"precision": [], "recall": [], "mrr": []})

    for query, expected, category in SEARCH_TEST_CASES:
        if not expected:
            continue

        recommendation_data = get_json(
            base_url, "/recommend", {"title": query, "top_n": 10}
        )
        analysis = get_json(base_url, "/analyze", {"query": query})
        results = recommendation_data.get("recommendations", [])
        titles = [item["Title"] for item in results]

        precision = calculate_precision_at_k(titles, expected, k=3)
        recall = calculate_recall_at_k(titles, expected, k=10)
        mrr = calculate_mrr(titles, expected)
        ndcg = calculate_ndcg_at_k(titles, expected, k=10)
        found_top3 = expected_found_in_top(titles, expected, 3)
        found_top10 = expected_found_in_top(titles, expected, 10)
        failure_reason = classify_failure(
            category, expected, titles, analysis, precision, recall, mrr
        )

        row = {
            "query": query,
            "category": category,
            "expected": expected,
            "top10": titles,
            "found_top3": found_top3,
            "found_top10": found_top10,
            "precision_at_3": precision,
            "recall_at_10": recall,
            "mrr": mrr,
            "ndcg_at_10": ndcg,
            "failure_reason": failure_reason,
            "detected_genres": analysis.get("detected_genres", []),
            "detected_actors": analysis.get("detected_actors", []),
            "detected_themes": analysis.get("detected_themes", []),
            "intent": analysis.get("intent"),
        }
        rows.append(row)

        category_metrics[category]["precision"].append(precision)
        category_metrics[category]["recall"].append(recall)
        category_metrics[category]["mrr"].append(mrr)

    weak_rows = [row for row in rows if is_weak_query(row)]
    weak_rows.sort(
        key=lambda row: (
            row["recall_at_10"],
            row["precision_at_3"],
            row["mrr"],
        )
    )

    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "base_url": base_url,
        "summary": summarize(rows, weak_rows, category_metrics),
        "weak_queries": weak_rows,
        "all_queries": rows,
    }


def average(values):
    return sum(values) / len(values) if values else 0.0


def summarize(rows, weak_rows, category_metrics):
    reason_counts = defaultdict(int)
    for row in weak_rows:
        reason_counts[row["failure_reason"]] += 1

    categories = {}
    for category, metrics in category_metrics.items():
        categories[category] = {
            "precision_at_3": average(metrics["precision"]),
            "recall_at_10": average(metrics["recall"]),
            "mrr": average(metrics["mrr"]),
        }

    return {
        "total_expected_queries": len(rows),
        "weak_query_count": len(weak_rows),
        "reason_counts": dict(sorted(reason_counts.items())),
        "category_metrics": categories,
    }


def write_markdown(report, path):
    summary = report["summary"]
    lines = [
        "# SeoulMate Weak Query Report",
        "",
        f"Generated: `{report['generated_at']}`",
        f"API: `{report['base_url']}`",
        "",
        "## Summary",
        "",
        f"- Expected-query cases: `{summary['total_expected_queries']}`",
        f"- Weak queries: `{summary['weak_query_count']}`",
        "",
        "## Weak Reasons",
        "",
    ]

    for reason, count in summary["reason_counts"].items():
        lines.append(f"- `{reason}`: `{count}`")

    lines.extend(["", "## Category Metrics", ""])
    for category, metrics in summary["category_metrics"].items():
        lines.append(
            f"- `{category}`: P@3 `{metrics['precision_at_3']:.2%}`, "
            f"R@10 `{metrics['recall_at_10']:.2%}`, "
            f"MRR `{metrics['mrr']:.3f}`"
        )

    lines.extend(["", "## Weak Queries", ""])
    for row in report["weak_queries"]:
        lines.extend(
            [
                f"### {row['query']} ({row['category']})",
                "",
                f"- Reason: `{row['failure_reason']}`",
                f"- Metrics: P@3 `{row['precision_at_3']:.2%}`, "
                f"R@10 `{row['recall_at_10']:.2%}`, MRR `{row['mrr']:.3f}`",
                f"- Expected: {', '.join(row['expected'])}",
                f"- Found top 10: {', '.join(row['found_top10']) or 'none'}",
                f"- Detected genres: {', '.join(row['detected_genres']) or 'none'}",
                f"- Detected themes: {', '.join(row['detected_themes']) or 'none'}",
                f"- Detected actors: {', '.join(row['detected_actors']) or 'none'}",
                f"- Top 10: {', '.join(row['top10'])}",
                "",
            ]
        )

    path.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=None)
    parser.add_argument("--no-start-backend", action="store_true")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = parser.parse_args()

    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    base_url = args.base_url or f"http://127.0.0.1:{args.port}"
    process = None
    log_handle = None

    try:
        if not args.no_start_backend:
            process, log_handle, log_path = start_backend(args.port)
            try:
                wait_for_api(base_url)
            except RuntimeError as exc:
                log_handle.flush()
                tail = log_path.read_text(encoding="utf-8", errors="replace")[-3000:]
                raise RuntimeError(f"{exc}\nBackend log tail:\n{tail}") from exc

        report = collect_report(base_url)
        json_path = AUDIT_DIR / "weak_queries.json"
        markdown_path = AUDIT_DIR / "weak_queries.md"
        json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        write_markdown(report, markdown_path)

        print(f"Wrote {json_path}")
        print(f"Wrote {markdown_path}")
        print(
            "Weak queries: "
            f"{report['summary']['weak_query_count']}/"
            f"{report['summary']['total_expected_queries']}"
        )
        print("Reason counts:")
        for reason, count in report["summary"]["reason_counts"].items():
            print(f"  {reason}: {count}")
    finally:
        if process:
            process.terminate()
            try:
                process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=15)
        if log_handle:
            log_handle.close()


if __name__ == "__main__":
    main()
