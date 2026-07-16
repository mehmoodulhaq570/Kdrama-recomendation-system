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


def build_indexes(metadata: list[dict]) -> dict[str, dict]:
    metadata_by_title = {item.get("Title", ""): item for item in metadata}
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
    genre_index = {
        key.title(): top_titles(titles, metadata_by_title)
        for key, titles in sorted(genre_index.items())
    }
    keyword_index = {
        key: top_titles(titles, metadata_by_title, limit=30)
        for key, titles in sorted(keyword_index.items())
    }
    theme_index = {
        key: top_titles(titles, metadata_by_title)
        for key, titles in sorted(theme_candidates.items())
    }

    # Common English public title not always present in scraped aliases.
    title_aliases.setdefault("goblin", "Guardian: The Lonely and Great God")
    title_aliases.setdefault("guardian", "Guardian: The Lonely and Great God")

    return {
        "actor_index": actor_index,
        "genre_index": genre_index,
        "keyword_index": keyword_index,
        "theme_index": theme_index,
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
