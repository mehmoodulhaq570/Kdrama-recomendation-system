"""Generate data-driven lookup indexes from the FAISS metadata.

The backend can use these JSON files for ranking and title resolution instead
of keeping every actor, alias, genre, or theme mapping hardcoded in app.py.
"""

from __future__ import annotations

import json
import pickle
import re
from collections import defaultdict
from itertools import combinations
from pathlib import Path
from typing import Iterable

from query_analyzer import QueryAnalyzer


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

VIRTUAL_GENRE_RULES = {
    "crime": [
        "crime",
        "criminal",
        "detective",
        "investigation",
        "murder",
        "serial killer",
        "serial killing",
        "serial killings",
        "corruption",
        "crime solving",
    ],
    "revenge": THEME_RULES["revenge"],
    "youth": [
        "youth",
        "student",
        "students",
        "school",
        "high school",
        "classroom",
        "campus",
    ],
    "horror": [
        "horror",
        "zombie",
        "zombies",
        "zombie apocalypse",
        "epidemic",
        "infectious disease",
        "virus",
        "quarantine",
        "gore",
        "monster",
    ],
}

CRIME_THRILLER_FOCUS_TERMS = [
    "detective",
    "investigation",
    "murder",
    "serial killer",
    "serial killings",
    "corruption",
    "crime solving",
    "cold case",
    "psychological",
    "suspense",
]

CRIME_THRILLER_ACTION_TERMS = [
    "action",
    "gang",
    "gangster",
    "fighter",
    "boxing",
    "skilled fighter",
    "special forces",
    "drug cartel",
    "drug dealer",
]

ZOMBIE_THRILLER_FOCUS_TERMS = [
    "zombie",
    "zombies",
    "zombie apocalypse",
    "epidemic",
    "infectious disease",
    "virus",
    "quarantine",
    "survival",
    "gore",
    "apocalypse",
    "lockdown",
]

ZOMBIE_THRILLER_OFF_TOPIC_TERMS = [
    "revenge",
    "school bullying",
    "suicide",
    "grim reaper",
    "taxi driver",
    "prosecutor",
    "law",
    "melodrama",
]

BUSINESS_ROMANCE_OFF_TOPIC_TERMS = [
    "fantasy",
    "revenge",
    "sports",
    "time travel",
]

ROMANTIC_COMEDY_FOCUS_TERMS = [
    "romantic comedy",
    "comedy",
    "office romance",
    "office",
    "business",
    "secretary",
    "ceo",
    "chaebol",
    "strong female",
    "strong woman",
    "supernatural strength",
    "rich male lead",
    "boss-employee",
    "workplace",
    "contract relationship",
    "fake relationship",
    "love triangle",
    "lighthearted",
]

ROMANTIC_COMEDY_OFF_TOPIC_TERMS = [
    "historical",
    "fantasy",
    "melodrama",
    "thriller",
    "revenge",
    "spin-off",
    "side story",
    "special",
    "short length series",
]

FANTASY_ROMANCE_FOCUS_TERMS = [
    "alchemy",
    "souls",
    "fantasy",
    "supernatural",
    "dokkaebi",
    "goblin",
    "ghost",
    "ghost-seeing",
    "spirit",
    "soul",
    "immortal",
    "immortality",
    "hotel",
    "curse",
    "deity",
    "elemental power",
]

FANTASY_ROMANCE_OFF_TOPIC_TERMS = [
    "mystery",
    "investigation",
    "police",
    "murder",
    "magician",
    "time travel",
    "youth",
    "historical",
    "cooking",
    "revenge",
]

YOUTH_DRAMA_FOCUS_TERMS = [
    "high school",
    "school setting",
    "student",
    "students",
    "school",
    "romance",
    "romantic",
    "comedy",
    "coming of age",
    "friendship",
    "love triangle",
    "adapted from a webtoon",
]

YOUTH_DRAMA_OFF_TOPIC_TERMS = [
    "action",
    "violence",
    "school violence",
    "skilled fighter",
    "gang",
    "thriller",
    "fantasy",
    "time travel",
    "historical",
    "martial law",
    "documentary",
    "web series",
    "short length series",
]

GENRE_FOCUS_TERMS = {
    "business": ["business", "office", "company", "workplace", "secretary", "ceo"],
    "crime": CRIME_THRILLER_FOCUS_TERMS,
    "fantasy": ["fantasy", "supernatural", "ghost", "spirit", "soul", "immortal"],
    "food": ["food", "restaurant", "cooking", "chef", "kitchen", "culinary"],
    "historical": ["historical", "king", "queen", "royal", "joseon", "palace"],
    "law": ["law", "lawyer", "attorney", "court", "legal", "prosecutor"],
    "medical": ["medical", "doctor", "hospital", "surgeon", "clinic"],
    "revenge": VIRTUAL_GENRE_RULES["revenge"],
    "romance": ["romance", "love", "relationship", "couple"],
    "thriller": ["thriller", "suspense", "mystery", "serial killer", "investigation"],
    "youth": ["school", "student", "youth", "class", "high school", "campus"],
}

FOCUS_FIRST_GENRES = {
    "business",
    "crime",
    "food",
    "law",
    "medical",
    "revenge",
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
        rating = parse_rating(drama)
        episodes = parse_episodes(drama)
        return (rating, episodes, title)

    return sorted(set(titles), key=score, reverse=True)[:limit]


def parse_rating(drama: dict) -> float:
    try:
        return float(drama.get("rating_value") or 0)
    except ValueError:
        return 0.0


def parse_episodes(drama: dict) -> int:
    try:
        return int(float(drama.get("episodes") or 0))
    except ValueError:
        return 0


def parse_start_year(drama: dict) -> int:
    match = re.search(r"\b(19|20)\d{2}\b", str(drama.get("Release Years", "")))
    return int(match.group(0)) if match else 0


def title_reliability_score(
    title: str,
    drama: dict,
    title_frequency: dict[str, int],
) -> float:
    """Estimate how safe a generated candidate is for top-rank promotion."""
    title_lower = title.lower()
    genre_lower = str(drama.get("Genre", "")).lower()
    keyword_lower = str(drama.get("keywords", "")).lower()
    description_lower = str(drama.get("Description", "")).lower()
    searchable_text = " ".join([title_lower, genre_lower, keyword_lower, description_lower])

    rating = parse_rating(drama)
    episodes = parse_episodes(drama)
    start_year = parse_start_year(drama)
    frequency = min(title_frequency.get(title, 0), 8)

    score = 0.0
    if rating >= 8.8:
        score += 1.5
    elif rating >= 8.5:
        score += 1.0
    elif rating >= 8.0:
        score += 0.5

    score += frequency * 0.15

    if 8 <= episodes <= 24:
        score += 0.75
    elif episodes and episodes < 6:
        score -= 1.0

    if any(term in title_lower for term in NON_PRIMARY_TITLE_TERMS):
        score -= 4.0
    if any(term in genre_lower for term in NON_PRIMARY_GENRE_TERMS):
        score -= 3.0
    if "web series" in keyword_lower and episodes <= 8:
        score -= 1.25
    if SEQUEL_TITLE_PATTERN.search(title):
        score -= 0.75
    if any(term in searchable_text for term in ["main role", "support role"]):
        score += 0.25
    if start_year >= 2025:
        score -= 1.0
    elif start_year >= 2024:
        score -= 0.5

    return score


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


def build_combo_training_frequency(metadata_by_title: dict[str, dict]) -> dict[str, dict[str, int]]:
    analyzer = QueryAnalyzer()
    frequency = defaultdict(lambda: defaultdict(int))
    for filename in ["st_triplets.json", "training_triplets.json"]:
        path = TRAINING_DATA_DIR / filename
        if not path.exists():
            continue
        with path.open("r", encoding="utf-8", errors="ignore") as handle:
            records = json.load(handle)
        for record in records:
            anchor = record.get("anchor", "")
            positive = record.get("positive", "")
            if positive not in metadata_by_title:
                continue
            genres = sorted(set(analyzer.analyze(anchor)["entities"].get("genres", [])))
            if len(genres) < 2:
                continue
            for genre_a, genre_b in combinations(genres, 2):
                frequency[combo_key([genre_a, genre_b])][positive] += 1
    return frequency


def virtual_genres_for_text(searchable_text: str) -> list[str]:
    return [
        genre
        for genre, terms in VIRTUAL_GENRE_RULES.items()
        if any(term in searchable_text for term in terms)
    ]


def calibrated_actor_titles(
    actor_key: str,
    titles: Iterable[str],
    metadata_by_title: dict[str, dict],
    title_frequency: dict[str, int],
    limit: int = 12,
):
    actor_key = normalized_key(actor_key)

    def score(title: str):
        drama = metadata_by_title.get(title, {})
        title_lower = title.lower()
        genre_lower = str(drama.get("Genre", "")).lower()
        keyword_lower = str(drama.get("keywords", "")).lower()
        cast = [normalized_key(actor) for actor in split_csv(drama.get("Cast"))]

        rating = parse_rating(drama)
        episodes = parse_episodes(drama)

        primary_penalty = 0
        if any(term in title_lower for term in NON_PRIMARY_TITLE_TERMS):
            primary_penalty -= 5
        if any(term in genre_lower for term in NON_PRIMARY_GENRE_TERMS):
            primary_penalty -= 2
        if "web series" in keyword_lower and episodes <= 8:
            primary_penalty -= 1

        if actor_key in cast:
            cast_position = cast.index(actor_key)
        else:
            cast_position = 99

        if cast_position == 0:
            cast_bonus = 4
        elif cast_position == 1:
            cast_bonus = 2.5
        elif cast_position == 2:
            cast_bonus = 1
        else:
            cast_bonus = -2

        drama_bonus = 0
        if any(term in genre_lower for term in ["drama", "romance", "thriller", "comedy"]):
            drama_bonus += 1
        if 8 <= episodes <= 24:
            drama_bonus += 0.5

        frequency = title_frequency.get(title, 0)
        return (primary_penalty, cast_bonus, drama_bonus, rating, frequency, episodes, title)

    return sorted(set(titles), key=score, reverse=True)[:limit]


def calibrated_genre_titles(
    genre_key: str,
    titles: Iterable[str],
    metadata_by_title: dict[str, dict],
    title_frequency: dict[str, int],
    limit: int = 40,
):
    genre_key = normalized_key(genre_key)
    focus_terms = GENRE_FOCUS_TERMS.get(genre_key, [])

    def score(title: str):
        drama = metadata_by_title.get(title, {})
        title_lower = title.lower()
        genre_lower = str(drama.get("Genre", "")).lower()
        keyword_lower = str(drama.get("keywords", "")).lower()
        description_lower = str(drama.get("Description", "")).lower()
        searchable_text = " ".join(
            [title_lower, genre_lower, keyword_lower, description_lower]
        )

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
        reliability = title_reliability_score(title, drama, title_frequency)
        focus_score = sum(term in searchable_text for term in focus_terms)
        if genre_key in FOCUS_FIRST_GENRES:
            return (primary_score, focus_score, reliability, frequency, rating, episodes, title)
        return (primary_score, reliability, frequency, rating, episodes, title)

    return sorted(set(titles), key=score, reverse=True)[:limit]


def combo_key(genres: Iterable[str]) -> str:
    return "|".join(sorted({normalized_key(genre) for genre in genres if genre}))


def calibrated_genre_combo_titles(
    combo_genres: Iterable[str],
    titles: Iterable[str],
    metadata_by_title: dict[str, dict],
    title_frequency: dict[str, int],
    combo_frequency: dict[str, int],
    limit: int = 30,
):
    combo_genres = {normalized_key(genre) for genre in combo_genres}
    combo_key_value = combo_key(combo_genres)

    def score(title: str):
        drama = metadata_by_title.get(title, {})
        title_lower = title.lower()
        genre_lower = str(drama.get("Genre", "")).lower()
        keyword_lower = str(drama.get("keywords", "")).lower()
        searchable_text = " ".join(
            [
                title_lower,
                genre_lower,
                keyword_lower,
                str(drama.get("Description", "")).lower(),
            ]
        )
        drama_genres = {normalized_key(genre) for genre in split_csv(drama.get("Genre"))}
        drama_genres.update(virtual_genres_for_text(searchable_text))

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

        overlap = len(combo_genres & drama_genres)
        exact_combo = int(combo_genres <= drama_genres)
        extra_genres = max(len(drama_genres - combo_genres), 0)
        combo_signal = combo_frequency.get(title, 0)
        combo_focus = 0
        if combo_key_value == "crime|thriller":
            combo_focus += sum(term in searchable_text for term in CRIME_THRILLER_FOCUS_TERMS)
            combo_focus -= 0.75 * sum(term in searchable_text for term in CRIME_THRILLER_ACTION_TERMS)
            if "mystery" in drama_genres or "psychological" in drama_genres or "law" in drama_genres:
                combo_focus += 1
            if "action" in drama_genres:
                combo_focus -= 1
        elif combo_key_value in {
            "drama|horror|thriller",
            "horror|thriller",
            "drama|thriller",
        }:
            combo_focus += sum(term in searchable_text for term in ZOMBIE_THRILLER_FOCUS_TERMS)
            combo_focus -= 0.75 * sum(term in searchable_text for term in ZOMBIE_THRILLER_OFF_TOPIC_TERMS)
        elif combo_key_value == "business|romance":
            combo_focus -= 0.75 * sum(term in searchable_text for term in BUSINESS_ROMANCE_OFF_TOPIC_TERMS)
        elif combo_key_value == "comedy|romance":
            combo_focus += sum(term in searchable_text for term in ROMANTIC_COMEDY_FOCUS_TERMS)
            combo_focus -= 0.75 * sum(term in searchable_text for term in ROMANTIC_COMEDY_OFF_TOPIC_TERMS)
        elif combo_key_value == "fantasy|romance":
            combo_focus += sum(term in searchable_text for term in FANTASY_ROMANCE_FOCUS_TERMS)
            combo_focus -= 0.75 * sum(term in searchable_text for term in FANTASY_ROMANCE_OFF_TOPIC_TERMS)
        elif combo_key_value == "drama|youth":
            combo_focus += sum(term in searchable_text for term in YOUTH_DRAMA_FOCUS_TERMS)
            combo_focus -= 0.75 * sum(term in searchable_text for term in YOUTH_DRAMA_OFF_TOPIC_TERMS)
        frequency = title_frequency.get(title, 0)
        reliability = title_reliability_score(title, drama, title_frequency)
        return (
            exact_combo,
            combo_focus,
            overlap,
            primary_score,
            reliability,
            rating,
            combo_signal,
            frequency,
            -extra_genres,
            episodes,
            title,
        )

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
    combo_training_frequency = build_combo_training_frequency(metadata_by_title)
    actor_index = defaultdict(list)
    genre_index = defaultdict(list)
    genre_combo_candidates = defaultdict(list)
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

        searchable_text = " ".join(
            str(drama.get(field, ""))
            for field in ["Title", "Genre", "Description", "keywords", "Cast", "Also Known As"]
        ).lower()

        for genre in split_csv(drama.get("Genre")):
            append_title(genre_index, genre, title)
        for genre in virtual_genres_for_text(searchable_text):
            append_title(genre_index, genre, title)

        for keyword in split_csv(drama.get("keywords")):
            append_title(keyword_index, keyword, title)

        genres = [genre.title() for genre in split_csv(drama.get("Genre"))]
        genres.extend(
            genre.title()
            for genre in virtual_genres_for_text(searchable_text)
            if genre in {"crime", "revenge"}
        )
        for genre_a, genre_b in combinations(sorted(set(genres)), 2):
            append_title(genre_combo_candidates, combo_key([genre_a, genre_b]), title)

        for theme, terms in THEME_RULES.items():
            if any(term in searchable_text for term in terms):
                theme_candidates[theme].append(title)

    actor_index = {
        key: top_titles(titles, metadata_by_title)
        for key, titles in sorted(actor_index.items())
    }
    calibrated_actor_index = {
        key: calibrated_actor_titles(key, titles, metadata_by_title, title_frequency)
        for key, titles in sorted(actor_index.items())
    }
    genre_index = {
        key.title(): top_titles(titles, metadata_by_title)
        for key, titles in sorted(genre_index.items())
    }
    calibrated_genre_index = {
        key.title(): calibrated_genre_titles(key, titles, metadata_by_title, title_frequency)
        for key, titles in sorted(genre_index.items())
    }
    calibrated_genre_combo_index = {
        key: calibrated_genre_combo_titles(
            key.split("|"),
            titles,
            metadata_by_title,
            title_frequency,
            combo_training_frequency.get(key, {}),
        )
        for key, titles in sorted(genre_combo_candidates.items())
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
        "calibrated_genre_combo_index": calibrated_genre_combo_index,
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
