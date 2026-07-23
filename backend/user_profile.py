"""
User Profile and Preference Learning System
Phase 2: Personalization

This module tracks and analyzes user interactions to build comprehensive
preference profiles for personalized recommendations.
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import json
import os
import math
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parent
DEFAULT_PROFILES_DIR = BACKEND_DIR / "runtime_data" / "user_profiles"


class UserProfileManager:
    """
    Manages user profiles and learns preferences from interactions.

    Features:
    - Genre preference tracking
    - Actor preference tracking
    - Theme preference extraction
    - Rating pattern analysis
    - Dynamic profile updating
    """

    def __init__(self, profiles_dir: str = None):
        self.profiles_dir = str(Path(profiles_dir) if profiles_dir else DEFAULT_PROFILES_DIR)
        os.makedirs(self.profiles_dir, exist_ok=True)

    def get_profile_path(self, user_id: str) -> str:
        """Get file path for user profile"""
        return os.path.join(self.profiles_dir, f"{user_id}.json")

    def load_profile(self, user_id: str) -> Dict:
        """
        Load user profile from disk.
        Creates new profile if doesn't exist.
        """
        profile_path = self.get_profile_path(user_id)

        if os.path.exists(profile_path):
            with open(profile_path, "r", encoding="utf-8") as f:
                return json.load(f)

        # Create new profile
        return self._create_new_profile(user_id)

    def save_profile(self, user_id: str, profile: Dict):
        """Save user profile to disk"""
        profile_path = self.get_profile_path(user_id)
        profile["last_updated"] = datetime.now().isoformat()

        with open(profile_path, "w", encoding="utf-8") as f:
            json.dump(profile, f, indent=2, ensure_ascii=False)

    def _create_new_profile(self, user_id: str) -> Dict:
        """Create a new user profile with default values"""
        return {
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "preferences": {
                "genres": {},
                "actors": {},
                "directors": {},
                "themes": {},
                "publishers": {},
            },
            "statistics": {
                "total_interactions": 0,
                "total_clicks": 0,
                "total_watchlist_adds": 0,
                "total_watched": 0,
                "avg_rating": 0.0,
                "total_ratings": 0,
            },
            "viewing_patterns": {
                "preferred_episode_count": None,
                "preferred_years": [],
                "binge_watcher": False,
                "rating_style": "neutral",  # generous, neutral, critical
            },
            "recent_interactions": [],  # Last 50 interactions
        }

    def update_from_interaction(
        self,
        user_id: str,
        drama_data: Dict,
        interaction_type: str,
        rating: Optional[float] = None,
    ):
        """
        Update user profile based on an interaction.

        Args:
            user_id: User identifier
            drama_data: Drama metadata (Title, Genre, Cast, etc.)
            interaction_type: click, watchlist_add, watched, etc.
            rating: Optional rating given by user (0-10)
        """
        profile = self.load_profile(user_id)

        # Update statistics
        profile["statistics"]["total_interactions"] += 1

        if interaction_type == "click":
            profile["statistics"]["total_clicks"] += 1
            weight = 0.3  # Clicks have lower weight
        elif interaction_type == "watchlist_add":
            profile["statistics"]["total_watchlist_adds"] += 1
            weight = 0.6  # Watchlist adds show higher interest
        elif interaction_type == "watched":
            profile["statistics"]["total_watched"] += 1
            weight = 1.0  # Watched dramas have highest weight
        else:
            weight = 0.5  # Default weight

        # Update rating statistics
        if rating is not None:
            self._update_rating_stats(profile, rating)
            weight *= rating / 5.0  # Scale weight by rating

        # Update genre preferences
        self._update_genre_preferences(profile, drama_data, weight)

        # Update actor preferences
        self._update_actor_preferences(profile, drama_data, weight)

        # Update director preferences
        self._update_director_preferences(profile, drama_data, weight)

        # Update theme preferences (from keywords/description)
        self._update_theme_preferences(profile, drama_data, weight)

        # Update publisher preferences
        self._update_publisher_preferences(profile, drama_data, weight)

        # Add to recent interactions
        self._add_recent_interaction(profile, drama_data, interaction_type)

        # Analyze viewing patterns
        self._analyze_viewing_patterns(profile, drama_data)

        # Normalize all preferences (keep scores between 0-1)
        self._normalize_preferences(profile)

        # Save updated profile
        self.save_profile(user_id, profile)

        return profile

    def _update_genre_preferences(self, profile: Dict, drama_data: Dict, weight: float):
        """Update genre preferences from drama genres"""
        genres_str = drama_data.get("Genre", drama_data.get("genres", ""))

        if not genres_str:
            return

        # Parse genres (comma-separated or list)
        if isinstance(genres_str, str):
            genres = [g.strip() for g in genres_str.split(",")]
        else:
            genres = genres_str

        for genre in genres:
            if not genre:
                continue

            current_score = profile["preferences"]["genres"].get(genre, 0.5)
            # Update with exponential moving average
            new_score = current_score * 0.8 + weight * 0.2
            profile["preferences"]["genres"][genre] = min(new_score, 1.0)

    def _update_actor_preferences(self, profile: Dict, drama_data: Dict, weight: float):
        """Update actor preferences from cast"""
        cast_str = drama_data.get("Cast", drama_data.get("cast", ""))

        if not cast_str:
            return

        # Parse cast (comma-separated or list)
        if isinstance(cast_str, str):
            actors = [a.strip() for a in cast_str.split(",")[:5]]  # Top 5 actors
        else:
            actors = cast_str[:5]

        for actor in actors:
            if not actor:
                continue

            current_score = profile["preferences"]["actors"].get(actor, 0.5)
            new_score = current_score * 0.8 + weight * 0.2
            profile["preferences"]["actors"][actor] = min(new_score, 1.0)

    def _update_director_preferences(
        self, profile: Dict, drama_data: Dict, weight: float
    ):
        """Update director preferences"""
        director = drama_data.get("Director", drama_data.get("director", ""))

        if not director:
            return

        current_score = profile["preferences"]["directors"].get(director, 0.5)
        new_score = current_score * 0.8 + weight * 0.2
        profile["preferences"]["directors"][director] = min(new_score, 1.0)

    def _update_theme_preferences(self, profile: Dict, drama_data: Dict, weight: float):
        """Extract and update theme preferences from keywords/description"""
        # Get keywords
        keywords_str = drama_data.get("keywords", "")
        description = drama_data.get("Description", drama_data.get("description", ""))

        themes = []

        # Parse keywords
        if keywords_str:
            if isinstance(keywords_str, str):
                themes.extend([k.strip().lower() for k in keywords_str.split(",")])
            else:
                themes.extend([k.lower() for k in keywords_str])

        # Extract themes from description (simple keyword matching)
        theme_keywords = {
            "emotional": ["emotional", "tearjerker", "touching", "heartwarming"],
            "funny": ["funny", "comedy", "humorous", "hilarious"],
            "action": ["action", "fighting", "martial arts", "chase"],
            "romantic": ["romantic", "love", "romance", "relationship"],
            "suspense": ["suspense", "mystery", "thriller", "twist"],
            "realistic": ["realistic", "slice of life", "everyday", "real"],
            "fantasy": ["fantasy", "supernatural", "magical", "mystical"],
        }

        if description:
            desc_lower = description.lower()
            for theme, keywords in theme_keywords.items():
                if any(keyword in desc_lower for keyword in keywords):
                    themes.append(theme)

        # Update theme preferences
        for theme in themes:
            if not theme:
                continue

            current_score = profile["preferences"]["themes"].get(theme, 0.5)
            new_score = current_score * 0.8 + weight * 0.2
            profile["preferences"]["themes"][theme] = min(new_score, 1.0)

    def _update_publisher_preferences(
        self, profile: Dict, drama_data: Dict, weight: float
    ):
        """Update publisher/network preferences"""
        publisher = drama_data.get("publisher", drama_data.get("Publisher", ""))

        if not publisher:
            return

        current_score = profile["preferences"]["publishers"].get(publisher, 0.5)
        new_score = current_score * 0.8 + weight * 0.2
        profile["preferences"]["publishers"][publisher] = min(new_score, 1.0)

    def _update_rating_stats(self, profile: Dict, rating: float):
        """Update rating statistics"""
        stats = profile["statistics"]
        total_ratings = stats["total_ratings"]
        current_avg = stats["avg_rating"]

        # Calculate new average
        new_avg = (current_avg * total_ratings + rating) / (total_ratings + 1)

        stats["avg_rating"] = new_avg
        stats["total_ratings"] = total_ratings + 1

        # Determine rating style
        if new_avg >= 4.5:
            stats["rating_style"] = "generous"
        elif new_avg <= 3.5:
            stats["rating_style"] = "critical"
        else:
            stats["rating_style"] = "neutral"

    def _add_recent_interaction(
        self, profile: Dict, drama_data: Dict, interaction_type: str
    ):
        """Add interaction to recent history (keep last 50)"""
        interaction = {
            "drama_title": drama_data.get("Title", drama_data.get("title", "Unknown")),
            "interaction_type": interaction_type,
            "timestamp": datetime.now().isoformat(),
        }

        profile["recent_interactions"].insert(0, interaction)

        # Keep only last 50
        profile["recent_interactions"] = profile["recent_interactions"][:50]

    def _analyze_viewing_patterns(self, profile: Dict, drama_data: Dict):
        """Analyze viewing patterns from interactions"""
        patterns = profile["viewing_patterns"]

        # Analyze episode count preference
        episodes = drama_data.get("episodes", drama_data.get("Episodes"))
        if episodes:
            try:
                ep_count = int(episodes)
                if not patterns["preferred_episode_count"]:
                    patterns["preferred_episode_count"] = ep_count
                else:
                    # Moving average
                    current = patterns["preferred_episode_count"]
                    patterns["preferred_episode_count"] = int(
                        current * 0.7 + ep_count * 0.3
                    )
            except (ValueError, TypeError):
                pass

        # Analyze year preferences
        year_aired = drama_data.get("year_aired", drama_data.get("Year"))
        if year_aired:
            try:
                year = int(year_aired)
                if year not in patterns["preferred_years"]:
                    patterns["preferred_years"].append(year)
                # Keep last 5 years
                patterns["preferred_years"] = patterns["preferred_years"][-5:]
            except (ValueError, TypeError):
                pass

        # Determine if binge watcher (watches many dramas)
        total_watched = profile["statistics"]["total_watched"]
        if total_watched >= 20:
            patterns["binge_watcher"] = True

    def _normalize_preferences(self, profile: Dict):
        """
        Normalize all preference scores to 0-1 range.
        Apply decay to old preferences.
        """
        for pref_type in ["genres", "actors", "directors", "themes", "publishers"]:
            prefs = profile["preferences"][pref_type]

            if not prefs:
                continue

            # Apply time decay (older preferences fade)
            # TODO: Implement time-based decay using last_updated timestamps

            # Ensure all values are between 0 and 1
            for key in prefs:
                prefs[key] = max(0.0, min(1.0, prefs[key]))

            # Keep only top N preferences (reduce noise)
            max_items = 50
            if len(prefs) > max_items:
                # Keep top-scoring items
                sorted_items = sorted(prefs.items(), key=lambda x: x[1], reverse=True)
                profile["preferences"][pref_type] = dict(sorted_items[:max_items])

    def get_top_preferences(
        self, user_id: str, pref_type: str, top_n: int = 10
    ) -> List[tuple]:
        """
        Get top N preferences of a specific type.

        Args:
            user_id: User identifier
            pref_type: 'genres', 'actors', 'directors', 'themes', or 'publishers'
            top_n: Number of top items to return

        Returns:
            List of (item, score) tuples sorted by score descending
        """
        profile = self.load_profile(user_id)
        prefs = profile["preferences"].get(pref_type, {})

        sorted_prefs = sorted(prefs.items(), key=lambda x: x[1], reverse=True)
        return sorted_prefs[:top_n]

    def get_profile_summary(self, user_id: str) -> Dict:
        """Get a summary of user profile for display"""
        profile = self.load_profile(user_id)

        return {
            "user_id": user_id,
            "persona": self._determine_persona(profile),
            "top_genres": self.get_top_preferences(user_id, "genres", 5),
            "top_actors": self.get_top_preferences(user_id, "actors", 5),
            "top_directors": self.get_top_preferences(user_id, "directors", 3),
            "top_themes": self.get_top_preferences(user_id, "themes", 5),
            "statistics": profile["statistics"],
            "viewing_patterns": profile["viewing_patterns"],
            "last_updated": profile["last_updated"],
        }

    def _determine_persona(self, profile: Dict) -> str:
        """
        Determine user persona based on preferences.
        e.g., "Medical Drama Enthusiast", "Romance Lover", "Thriller Seeker"
        """
        genres = profile["preferences"].get("genres", {})

        if not genres:
            return "New Viewer"

        # Get top genre
        top_genre = max(genres.items(), key=lambda x: x[1])
        genre_name, score = top_genre

        if score >= 0.8:
            return f"{genre_name} Drama Enthusiast"
        elif score >= 0.6:
            return f"{genre_name} Fan"
        else:
            return "Diverse Viewer"


# Global instance
_profile_manager = None


def get_profile_manager() -> UserProfileManager:
    """Get global UserProfileManager instance"""
    global _profile_manager
    if _profile_manager is None:
        _profile_manager = UserProfileManager()
    return _profile_manager
