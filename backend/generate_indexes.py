"""Generate data-driven lookup indexes from the FAISS metadata.

The backend can use these JSON files for ranking and title resolution instead
of keeping every actor, alias, genre, or theme mapping hardcoded in app.py.
"""

from __future__ import annotations

import json
import pickle
import re
from collections import defaultdict
from pathlib import Path
from typing import Iterable


BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
META_PATH = PROJECT_DIR / "model_traning" / "faiss_index" / "meta.pkl"
TRAINING_DATA_DIR = PROJECT_DIR / "model_traning" / "training_data"
OUTPUT_DIR = BASE_DIR / "generated_indexes"

THEME_RULES = {
    "north korea": ["north korea", "north korean", "defector", "dmz"],
    "food": ["restaurant", "food", "cooking", "chef", "culinary", "kitchen", "cafe"],
    "time travel": ["time travel", "time slip", "time loop", "past life", "future"],
    "contract marriage": ["contract marriage", "fake marriage", "marriage contract"],
    "rich ceo romance": ["ceo", "chaebol", "rich boss", "heir", "billionaire"],
    "school bullying": ["school bullying", "bullying", "bullied", "school violence"],
    "legal corruption": ["corruption", "corrupt", "prosecutor", "law firm"],
    "supernatural hotel": ["ghost", "supernatural", "hotel", "spirit", "haunted"],
    "survival game": ["survival game", "death game", "deadly game"],
    "startup workplace": ["startup", "start-up", "workplace", "office", "company"],
    "healing slice of life": ["healing", "slice of life", "comfort", "friendship"],
    "revenge": ["revenge", "vengeance", "payback", "retribution"],
    "medical": ["doctor", "hospital", "medical", "surgeon"],
    "law": ["lawyer", "attorney", "law", "court", "legal"],
}

NON_PRIMARY_TITLE_TERMS = [
    "special",
    "behind",
    "behind the scenes",
    "bts",
    "recap",
    "talk",
    "interview",
    "documentary",
    "docu",
    "fanmeeting",
    "fan meeting",
    "concert",
    "variety",
    "reunion",
    "camping",
    "every moment",
    "summoning",
    "young actors",
    "youn's",
    "busted",
    "in the soop",
]

NON_PRIMARY_GENRE_TERMS = [
    "documentary",
    "music",
    "variety show",
    "reality show",
]

SEQUEL_TITLE_PATTERN = re.compile(r"\b(season|part)\s+\d+\b", re.IGNORECASE)


def split_csv(value: object) -> list[str]:
    if value is None:
        return []
    return [part.strip() for part in str(value).split(",") if part.strip()]


def normalized_key(value: str) -> str:
    return re.sub(r"\s+", " ", value.lower().strip())


def append_title(index: dict[str, list[str]], key: str, title: str) -> None:
    key = normalized_key(key)
    if not key or not title:
        return
    if title not in index[key]:
        index[key].append(title)


def top_titles(titles: Iterable[str], metadata_by_title: dict[str, dict], limit: int = 40):
    def score(title: str):
        drama = metadata_by_title.get(title, {})
        try:
            rating = float(drama.get("rating_value") or 0)
        except ValueError:
            rating = 0.0
        try:
            episodes = int(float(drama.get("episodes") or 0))
        except ValueError:
            episodes = 0
        return (rating, episodes, title)

    return sorted(set(titles), key=score, reverse=True)[:limit]


def build_title_frequency(metadata_by_title: dict[str, dict]) -> dict[str, int]:
    frequency = defaultdict(int)
    titles = list(metadata_by_title.keys())
    title_pattern = re.compile(
        "|".join(re.escape(title) for title in sorted(titles, key=len, reverse=True))
    )
    for filename in ["st_pairs.json", "st_triplets.json", "training_pairs.json", "training_triplets.json"]:
        path = TRAINING_DATA_DIR / filename
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for match in title_pattern.finditer(text):
            frequency[match.group(0)] += 1
    return frequency


def calibrated_actor_titles(
    titles: Iterable[str],
    metadata_by_title: dict[str, dict],
    title_frequency: dict[str, int],
    limit: int = 12,
):
    def score(title: str):
        drama = metadata_by_title.get(title, {})
        title_lower = title.lower()
        genre_lower = str(drama.get("Genre", "")).lower()
        keyword_lower = str(drama.get("keywords", "")).lower()

        try:
            rating = float(drama.get("rating_value") or 0)
        except ValueError:
            rating = 0.0
        try:
            episodes = int(float(drama.get("episodes") or 0))
        except ValueError:
            episodes = 0

        primary_penalty = 0
        if any(term in title_lower for term in NON_PRIMARY_TITLE_TERMS):
            primary_penalty -= 5
        if any(term in genre_lower for term in NON_PRIMARY_GENRE_TERMS):
            primary_penalty -= 2
        if "web series" in keyword_lower and episodes <= 8:
            primary_penalty -= 1

        drama_bonus = 0
        if any(term in genre_lower for term in ["drama", "romance", "thriller", "comedy"]):
            drama_bonus += 1
        if 8 <= episodes <= 24:
            drama_bonus += 0.5

        frequency = title_frequency.get(title, 0)
        return (primary_penalty, drama_bonus, frequency, rating, episodes, title)

    return sorted(set(titles), key=score, reverse=True)[:limit]


def calibrated_genre_titles(
    titles: Iterable[str],
    metadata_by_title: dict[str, dict],
    title_frequency: dict[str, int],
    limit: int = 20,
):
    def score(title: str):
        drama = metadata_by_title.get(title, {})
        title_lower = title.lower()
        genre_lower = str(drama.get("Genre", "")).lower()
        keyword_lower = str(drama.get("keywords", "")).lower()

        try:
            rating = float(drama.get("rating_value") or 0)
        except ValueError:
            rating = 0.0
        try:
            episodes = int(float(drama.get("episodes") or 0))
        except ValueError:
            episodes = 0

        primary_score = 0
        if any(term in title_lower for term in NON_PRIMARY_TITLE_TERMS):
            primary_score -= 5
        if any(term in genre_lower for term in NON_PRIMARY_GENRE_TERMS):
            primary_score -= 4
        if "web series" in keyword_lower and episodes <= 8:
            primary_score -= 1
        if SEQUEL_TITLE_PATTERN.search(title):
            primary_score -= 1.25
        if 8 <= episodes <= 24:
            primary_score += 0.5

        frequency = title_frequency.get(title, 0)
        return (primary_score, frequency, rating, episodes, title)

    return sorted(set(titles), key=score, reverse=True)[:limit]


def calibrated_topic_titles(
    titles: Iterable[str],
    metadata_by_title: dict[str, dict],
    title_frequency: dict[str, int],
    limit: int = 20,
):
    def score(title: str):
        drama = metadata_by_title.get(title, {})
        title_lower = title.lower()
        genre_lower = str(drama.get("Genre", "")).lower()
        keyword_lower = str(drama.get("keywords", "")).lower()
        description_lower = str(drama.get("Description", "")).lower()

        try:
            rating = float(drama.get("rating_value") or 0)
        except ValueError:
            rating = 0.0
        try:
            episodes = int(float(drama.get("episodes") or 0))
        except ValueError:
            episodes = 0

        primary_score = 0
        if any(term in title_lower for term in NON_PRIMARY_TITLE_TERMS):
            primary_score -= 5
        if any(term in genre_lower for term in NON_PRIMARY_GENRE_TERMS):
            primary_score -= 4
        if "web series" in keyword_lower and episodes <= 8:
            primary_score -= 1
        if SEQUEL_TITLE_PATTERN.search(title):
            primary_score -= 1
        if 8 <= episodes <= 24:
            primary_score += 0.5
        if any(term in genre_lower for term in ["drama", "romance", "thriller", "comedy", "life"]):
            primary_score += 0.25

        metadata_depth = 0
        if keyword_lower:
            metadata_depth += 0.25
        if description_lower:
            metadata_depth += 0.25

        frequency = title_frequency.get(title, 0)
        return (primary_score, metadata_depth, frequency, rating, episodes, title)

    return sorted(set(titles), key=score, reverse=True)[:limit]


def build_indexes(metadata: list[dict]) -> dict[str, dict]:
    metadata_by_title = {item.get("Title", ""): item for item in metadata}
    title_frequency = build_title_frequency(metadata_by_title)
    actor_index = defaultdict(list)
    genre_index = defaultdict(list)
    keyword_index = defaultdict(list)
    title_aliases = {}
    theme_candidates = defaultdict(list)

    for drama in metadata:
        title = drama.get("Title", "").strip()
        if not title:
            continue

        for alias in split_csv(drama.get("Also Known As")):
            alias_key = normalized_key(alias)
            if alias_key and alias_key != normalized_key(title):
                title_aliases.setdefault(alias_key, title)

        for actor in split_csv(drama.get("Cast")):
            append_title(actor_index, actor, title)

        for genre in split_csv(drama.get("Genre")):
            append_title(genre_index, genre, title)

        for keyword in split_csv(drama.get("keywords")):
            append_title(keyword_index, keyword, title)

        searchable_text = " ".join(
            str(drama.get(field, ""))
            for field in ["Title", "Genre", "Description", "keywords", "Cast", "Also Known As"]
        ).lower()
        for theme, terms in THEME_RULES.items():
            if any(term in searchable_text for term in terms):
                theme_candidates[theme].append(title)

    actor_index = {
        key: top_titles(titles, metadata_by_title)
        for key, titles in sorted(actor_index.items())
    }
    calibrated_actor_index = {
        key: calibrated_actor_titles(titles, metadata_by_title, title_frequency)
        for key, titles in sorted(actor_index.items())
    }
    genre_index = {
        key.title(): top_titles(titles, metadata_by_title)
        for key, titles in sorted(genre_index.items())
    }
    calibrated_genre_index = {
        key.title(): calibrated_genre_titles(titles, metadata_by_title, title_frequency)
        for key, titles in sorted(genre_index.items())
    }
    keyword_index = {
        key: top_titles(titles, metadata_by_title, limit=30)
        for key, titles in sorted(keyword_index.items())
    }
    calibrated_keyword_index = {
        key: calibrated_topic_titles(titles, metadata_by_title, title_frequency, limit=20)
        for key, titles in sorted(keyword_index.items())
    }
    theme_index = {
        key: top_titles(titles, metadata_by_title)
        for key, titles in sorted(theme_candidates.items())
    }
    calibrated_theme_index = {
        key: calibrated_topic_titles(titles, metadata_by_title, title_frequency, limit=20)
        for key, titles in sorted(theme_candidates.items())
    }

    # Common English public title not always present in scraped aliases.
    title_aliases.setdefault("goblin", "Guardian: The Lonely and Great God")
    title_aliases.setdefault("guardian", "Guardian: The Lonely and Great God")

    return {
        "actor_index": actor_index,
        "calibrated_actor_index": calibrated_actor_index,
        "genre_index": genre_index,
        "calibrated_genre_index": calibrated_genre_index,
        "keyword_index": keyword_index,
        "calibrated_keyword_index": calibrated_keyword_index,
        "theme_index": theme_index,
        "calibrated_theme_index": calibrated_theme_index,
        "title_aliases": dict(sorted(title_aliases.items())),
    }


def save_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def main() -> None:
    with META_PATH.open("rb") as handle:
        metadata = pickle.load(handle)

    indexes = build_indexes(metadata)
    for name, data in indexes.items():
        save_json(OUTPUT_DIR / f"{name}.json", data)
        print(f"{name}: {len(data)} keys")

    manifest = {
        "source": str(META_PATH.relative_to(PROJECT_DIR)),
        "drama_count": len(metadata),
        "files": [f"{name}.json" for name in indexes],
    }
    save_json(OUTPUT_DIR / "manifest.json", manifest)
    print(f"Generated indexes in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
