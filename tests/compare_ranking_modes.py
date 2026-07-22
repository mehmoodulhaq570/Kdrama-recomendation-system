"""
Compare SeoulMate ranking modes query-by-query.

This script runs the expected-result search cases against multiple backend
configurations and writes JSON/Markdown reports that show where generated
genre replacement differs from the curated baseline.
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import requests

from evaluate_accuracy import (
    SEARCH_TEST_CASES,
    calculate_mrr,
    calculate_precision_at_k,
    calculate_recall_at_k,
)


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "tests" / "reports"
BASE_PORT = 8031

BASE_WEIGHTS = {
    "genre_combo": 2.55,
    "genre": 2.2,
    "theme_combo": 3.1,
    "theme": 2.4,
    "actor": 2.35,
    "generated_actor": 0.0,
    "generated_genre": 0.0,
    "generated_theme": 0.0,
    "generated_cap": 1.0,
}

MODES = {
    "curated_baseline": {
        "weights": {},
        "env": {},
    },
    "generated_genre_soft": {
        "weights": {"genre": 1.65, "genre_combo": 1.9},
        "env": {"SEOULMATE_GENRE_PRIOR_SOURCE": "calibrated_generated"},
    },
    "generated_combo_only_soft": {
        "weights": {"genre_combo": 1.9},
        "env": {"SEOULMATE_GENRE_PRIOR_SOURCE": "calibrated_generated_combo_only"},
    },
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


def start_backend(mode_name, mode, port):
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["SEOULMATE_PORT"] = str(port)
    env["SEOULMATE_RELOAD"] = "0"
    env["SEOULMATE_PRIOR_WEIGHTS"] = json.dumps(BASE_WEIGHTS | mode["weights"])
    env["PYTHONIOENCODING"] = "utf-8"
    env.update(mode["env"])

    log_path = REPORT_DIR / f"compare_{mode_name}.log"
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


def get_json(base_url, path, params):
    response = requests.get(f"{base_url}{path}", params=params, timeout=60)
    response.raise_for_status()
    return response.json()


def rank_of_expected(titles, expected):
    for rank, title in enumerate(titles, start=1):
        if any(exp.lower() in title.lower() for exp in expected):
            return rank
    return None


def collect_mode(mode_name, mode, port):
    base_url = f"http://127.0.0.1:{port}"
    process, log_handle, log_path = start_backend(mode_name, mode, port)
    try:
        try:
            wait_for_api(base_url)
        except RuntimeError as exc:
            log_handle.flush()
            tail = log_path.read_text(encoding="utf-8", errors="replace")[-3000:]
            raise RuntimeError(f"{exc}\nBackend log tail:\n{tail}") from exc

        rows = {}
        for query, expected, category in SEARCH_TEST_CASES:
            if not expected:
                continue
            data = get_json(base_url, "/recommend", {"title": query, "top_n": 10})
            analysis = get_json(base_url, "/analyze", {"query": query})
            titles = [item["Title"] for item in data.get("recommendations", [])]
            rows[query] = {
                "query": query,
                "category": category,
                "expected": expected,
                "top10": titles,
                "best_rank": rank_of_expected(titles, expected),
                "precision_at_3": calculate_precision_at_k(titles, expected, k=3),
                "recall_at_10": calculate_recall_at_k(titles, expected, k=10),
                "mrr": calculate_mrr(titles, expected),
                "detected_genres": analysis.get("detected_genres", []),
                "detected_themes": analysis.get("detected_themes", []),
                "detected_actors": analysis.get("detected_actors", []),
            }
        return rows
    finally:
        process.terminate()
        try:
            process.wait(timeout=15)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=15)
        log_handle.close()


def metric_delta(candidate, baseline, metric):
    return candidate[metric] - baseline[metric]


def build_comparison(mode_results):
    baseline = mode_results["curated_baseline"]
    comparisons = []

    for query, baseline_row in baseline.items():
        row = {
            "query": query,
            "category": baseline_row["category"],
            "expected": baseline_row["expected"],
            "baseline": baseline_row,
            "modes": {},
        }
        for mode_name, results in mode_results.items():
            if mode_name == "curated_baseline":
                continue
            mode_row = results[query]
            row["modes"][mode_name] = {
                **mode_row,
                "delta_precision_at_3": metric_delta(
                    mode_row, baseline_row, "precision_at_3"
                ),
                "delta_recall_at_10": metric_delta(
                    mode_row, baseline_row, "recall_at_10"
                ),
                "delta_mrr": metric_delta(mode_row, baseline_row, "mrr"),
            }
        comparisons.append(row)

    comparisons.sort(
        key=lambda row: min(
            mode["delta_precision_at_3"] + mode["delta_recall_at_10"] + mode["delta_mrr"]
            for mode in row["modes"].values()
        )
    )
    return comparisons


def summarize_mode(rows):
    values = list(rows.values())
    return {
        "precision_at_3": sum(row["precision_at_3"] for row in values) / len(values),
        "recall_at_10": sum(row["recall_at_10"] for row in values) / len(values),
        "mrr": sum(row["mrr"] for row in values) / len(values),
    }


def write_markdown(report, path):
    lines = [
        "# SeoulMate Ranking Mode Comparison",
        "",
        f"Generated: `{report['generated_at']}`",
        "",
        "## Mode Summary",
        "",
    ]
    for mode_name, summary in report["summary"].items():
        lines.append(
            f"- `{mode_name}`: P@3 `{summary['precision_at_3']:.2%}`, "
            f"R@10 `{summary['recall_at_10']:.2%}`, MRR `{summary['mrr']:.3f}`"
        )

    lines.extend(["", "## Biggest Generated Regressions", ""])
    regression_count = 0
    for row in report["comparisons"]:
        regressions = [
            (mode_name, mode)
            for mode_name, mode in row["modes"].items()
            if (
                mode["delta_precision_at_3"] < 0
                or mode["delta_recall_at_10"] < 0
                or mode["delta_mrr"] < 0
            )
        ]
        if not regressions:
            continue
        regression_count += 1
        lines.extend(
            [
                f"### {row['query']} ({row['category']})",
                "",
                f"- Expected: {', '.join(row['expected'])}",
                f"- Baseline top 5: {', '.join(row['baseline']['top10'][:5])}",
            ]
        )
        for mode_name, mode in regressions:
            lines.extend(
                [
                    f"- `{mode_name}` deltas: "
                    f"P@3 `{mode['delta_precision_at_3']:+.2%}`, "
                    f"R@10 `{mode['delta_recall_at_10']:+.2%}`, "
                    f"MRR `{mode['delta_mrr']:+.3f}`",
                    f"- `{mode_name}` top 5: {', '.join(mode['top10'][:5])}",
                ]
            )
        lines.append("")
        if regression_count >= 25:
            break

    path.write_text("\n".join(lines), encoding="utf-8")


def main():
    mode_results = {}
    for offset, (mode_name, mode) in enumerate(MODES.items()):
        port = BASE_PORT + offset
        print(f"Collecting {mode_name} on port {port}", flush=True)
        mode_results[mode_name] = collect_mode(mode_name, mode, port)

    report = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "summary": {
            mode_name: summarize_mode(rows)
            for mode_name, rows in mode_results.items()
        },
        "comparisons": build_comparison(mode_results),
    }

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    json_path = REPORT_DIR / "ranking_mode_comparison.json"
    markdown_path = REPORT_DIR / "ranking_mode_comparison.md"
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    write_markdown(report, markdown_path)
    print(f"Wrote {json_path}")
    print(f"Wrote {markdown_path}")

    for mode_name, summary in report["summary"].items():
        print(
            f"{mode_name}: "
            f"P@3={summary['precision_at_3']:.2%} "
            f"R@10={summary['recall_at_10']:.2%} "
            f"MRR={summary['mrr']:.3f}"
        )


if __name__ == "__main__":
    main()
