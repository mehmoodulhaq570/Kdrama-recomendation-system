"""
Run controlled ranking-prior experiments against the live API.

Each scenario starts the backend with a different SEOULMATE_PRIOR_WEIGHTS
override, runs the full accuracy evaluator, and prints a compact comparison.
"""

import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

import requests


ROOT = Path(__file__).resolve().parents[2]
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

SCENARIOS = {
    "baseline": {"weights": {}},
    "no_genre_priors": {"weights": {"genre": 0.0, "genre_combo": 0.0}},
    "hybrid_calibrated": {
        "weights": {"hybrid_genre": 0.75, "hybrid_genre_combo": 0.95},
        "env": {"SEOULMATE_GENRE_PRIOR_SOURCE": "hybrid_calibrated"},
    },
    "fallback_genre": {
        "weights": {"fallback_genre": 0.65, "fallback_genre_combo": 0.85},
        "env": {"SEOULMATE_GENRE_PRIOR_SOURCE": "fallback_generated"},
    },
    "generated_actor": {
        "weights": {},
        "env": {"SEOULMATE_ACTOR_PRIOR_SOURCE": "calibrated_generated"},
    },
    "hybrid_actor": {
        "weights": {"hybrid_actor": 1.0},
        "env": {"SEOULMATE_ACTOR_PRIOR_SOURCE": "hybrid_calibrated"},
    },
    "generated_theme": {
        "weights": {},
        "env": {"SEOULMATE_THEME_PRIOR_SOURCE": "calibrated_generated"},
    },
    "hybrid_theme": {
        "weights": {"hybrid_theme": 0.3},
        "env": {"SEOULMATE_THEME_PRIOR_SOURCE": "hybrid_calibrated"},
    },
    "fallback_theme": {
        "weights": {},
        "env": {"SEOULMATE_THEME_PRIOR_SOURCE": "fallback_generated"},
    },
    "fallback_genre_theme": {
        "weights": {
            "fallback_genre": 0.65,
            "fallback_genre_combo": 0.85,
            "fallback_theme": 0.8,
        },
        "env": {
            "SEOULMATE_GENRE_PRIOR_SOURCE": "fallback_generated",
            "SEOULMATE_THEME_PRIOR_SOURCE": "fallback_generated",
        },
    },
    "hybrid_genre_theme": {
        "weights": {
            "hybrid_genre": 0.75,
            "hybrid_genre_combo": 0.95,
            "hybrid_theme": 0.3,
        },
        "env": {
            "SEOULMATE_GENRE_PRIOR_SOURCE": "hybrid_calibrated",
            "SEOULMATE_THEME_PRIOR_SOURCE": "hybrid_calibrated",
        },
    },
    "hybrid_genre_generated_actor": {
        "weights": {"hybrid_genre": 0.75, "hybrid_genre_combo": 0.95},
        "env": {
            "SEOULMATE_GENRE_PRIOR_SOURCE": "hybrid_calibrated",
            "SEOULMATE_ACTOR_PRIOR_SOURCE": "calibrated_generated",
        },
    },
    "hybrid_genre_actor": {
        "weights": {
            "hybrid_genre": 0.75,
            "hybrid_genre_combo": 0.95,
            "hybrid_actor": 1.0,
        },
        "env": {
            "SEOULMATE_GENRE_PRIOR_SOURCE": "hybrid_calibrated",
            "SEOULMATE_ACTOR_PRIOR_SOURCE": "hybrid_calibrated",
        },
    },
    "calibrated_generated_genre": {
        "weights": {},
        "env": {"SEOULMATE_GENRE_PRIOR_SOURCE": "calibrated_generated"},
    },
    "calibrated_generated_genre_soft": {
        "weights": {"genre": 1.65, "genre_combo": 1.9},
        "env": {"SEOULMATE_GENRE_PRIOR_SOURCE": "calibrated_generated"},
    },
    "generated_genre_soft_profiles": {
        "weights": {"genre": 1.65, "genre_combo": 1.9},
        "env": {
            "SEOULMATE_GENRE_PRIOR_SOURCE": "calibrated_generated",
            "SEOULMATE_ENABLE_QUERY_PROFILES": "1",
        },
    },
    "calibrated_generated_genre_strong": {
        "weights": {"genre": 2.55, "genre_combo": 2.9},
        "env": {"SEOULMATE_GENRE_PRIOR_SOURCE": "calibrated_generated"},
    },
    "calibrated_generated_combo_only": {
        "weights": {},
        "env": {"SEOULMATE_GENRE_PRIOR_SOURCE": "calibrated_generated_combo_only"},
    },
    "calibrated_generated_combo_only_soft": {
        "weights": {"genre_combo": 1.9},
        "env": {"SEOULMATE_GENRE_PRIOR_SOURCE": "calibrated_generated_combo_only"},
    },
    "generated_combo_only_soft_profiles": {
        "weights": {"genre_combo": 1.9},
        "env": {
            "SEOULMATE_GENRE_PRIOR_SOURCE": "calibrated_generated_combo_only",
            "SEOULMATE_ENABLE_QUERY_PROFILES": "1",
        },
    },
    "calibrated_generated_combo_only_strong": {
        "weights": {"genre_combo": 2.9},
        "env": {"SEOULMATE_GENRE_PRIOR_SOURCE": "calibrated_generated_combo_only"},
    },
    "no_theme_priors": {"weights": {"theme": 0.0, "theme_combo": 0.0}},
    "no_actor_priors": {"weights": {"actor": 0.0}},
    "old_generated_nudges": {
        "weights": {
            "generated_actor": 0.04,
            "generated_genre": 0.025,
            "generated_theme": 0.025,
            "generated_cap": 1.08,
        },
    },
    "softer_curated_priors": {
        "weights": {
            "genre_combo": 2.35,
            "genre": 2.05,
            "theme_combo": 2.85,
            "theme": 2.2,
            "actor": 2.15,
        },
    },
    "stronger_curated_priors": {
        "weights": {
            "genre_combo": 2.7,
            "genre": 2.35,
            "theme_combo": 3.25,
            "theme": 2.55,
            "actor": 2.5,
        },
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


def parse_metric(output, pattern):
    matches = re.findall(pattern, output)
    return float(matches[-1]) if matches else None


def run_scenario(name, scenario, port):
    overrides = scenario.get("weights", {})
    weights = BASE_WEIGHTS | overrides
    base_url = f"http://127.0.0.1:{port}"
    env = os.environ.copy()
    env["SEOULMATE_PORT"] = str(port)
    env["SEOULMATE_RELOAD"] = "0"
    env["SEOULMATE_PRIOR_WEIGHTS"] = json.dumps(weights)
    env["SEOULMATE_API_URL"] = base_url
    env["PYTHONIOENCODING"] = "utf-8"
    env.update(scenario.get("env", {}))

    log_path = ROOT / "tests" / f".ranking_experiment_{name}.log"
    log_handle = log_path.open("w", encoding="utf-8")
    process = subprocess.Popen(
        [sys.executable, "app.py"],
        cwd=ROOT / "backend",
        env=env,
        stdout=log_handle,
        stderr=subprocess.STDOUT,
        text=True,
    )

    try:
        try:
            wait_for_api(base_url)
        except RuntimeError as exc:
            process.poll()
            log_handle.flush()
            tail = log_path.read_text(encoding="utf-8", errors="replace")[-3000:]
            raise RuntimeError(f"{exc}\nBackend log tail:\n{tail}") from exc
        result = subprocess.run(
            [sys.executable, "tests/evaluation/evaluate_accuracy.py"],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=240,
        )
        output = result.stdout + result.stderr
        if result.returncode != 0:
            raise RuntimeError(output[-3000:])

        return {
            "scenario": name,
            "overall": parse_metric(output, r"OVERALL SYSTEM ACCURACY:\s+([0-9.]+)%"),
            "precision_at_3": parse_metric(output, r"Precision@3:\s+([0-9.]+)%"),
            "recall_at_10": parse_metric(output, r"Recall@10:\s+([0-9.]+)%"),
            "mrr": parse_metric(output, r"MRR:\s+([0-9.]+)"),
            "weights": weights,
        }
    finally:
        process.terminate()
        try:
            process.wait(timeout=15)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=15)
        log_handle.close()


def main():
    port = int(os.environ.get("SEOULMATE_EXPERIMENT_PORT", "8011"))
    results = []

    for index, (name, scenario) in enumerate(SCENARIOS.items()):
        scenario_port = port + index
        print(f"\nRunning scenario: {name} on port {scenario_port}", flush=True)
        result = run_scenario(name, scenario, scenario_port)
        results.append(result)
        print(
            f"  overall={result['overall']:.2f}% "
            f"precision@3={result['precision_at_3']:.2f}% "
            f"recall@10={result['recall_at_10']:.2f}% "
            f"mrr={result['mrr']:.3f}",
            flush=True,
        )

    baseline = next(item for item in results if item["scenario"] == "baseline")
    print("\nRanking prior experiment summary")
    print("-" * 72)
    print("scenario                 overall   delta    p@3      r@10     mrr")
    print("-" * 72)
    for result in sorted(results, key=lambda item: item["overall"], reverse=True):
        delta = result["overall"] - baseline["overall"]
        print(
            f"{result['scenario']:<24}"
            f"{result['overall']:>7.2f}% "
            f"{delta:>+7.2f} "
            f"{result['precision_at_3']:>7.2f}% "
            f"{result['recall_at_10']:>7.2f}% "
            f"{result['mrr']:>7.3f}"
        )


if __name__ == "__main__":
    main()
