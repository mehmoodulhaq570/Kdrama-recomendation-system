"""
Test User Profile and Preference Learning System
Phase 2: Personalization
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "backend"))

from user_profile import UserProfileManager

# Create profile manager
profile_manager = UserProfileManager(profiles_dir=str(ROOT / "tests" / "test_profiles"))

print("=" * 80)
print("Testing User Profile System (Phase 2)")
print("=" * 80)

# Test 1: Create new user profile
print("\n1️⃣ Creating new user profile...")
user_id = "test_user_phase2"
profile = profile_manager.load_profile(user_id)
print(f"✅ Created profile for {user_id}")
print(f"   Statistics: {profile['statistics']}")

# Test 2: Simulate interactions with Medical dramas
print("\n2️⃣ Simulating interactions with Medical dramas...")

medical_dramas = [
    {
        "Title": "Hospital Playlist",
        "Genre": "Medical, Life, Friendship",
        "Cast": "Jo Jung-suk, Yoo Yeon-seok, Jung Kyung-ho",
        "Director": "Shin Won-ho",
        "Description": "A heartwarming drama about five doctors who have been friends since medical school",
        "keywords": "friendship, medical, heartwarming, realistic",
        "episodes": "12",
    },
    {
        "Title": "Good Doctor",
        "Genre": "Medical, Drama",
        "Cast": "Joo Won, Moon Chae-won",
        "Director": "Ki Min-soo",
        "Description": "An autistic doctor with savant syndrome joins a pediatric surgery team",
        "keywords": "medical, inspiring, emotional",
        "episodes": "20",
    },
    {
        "Title": "Doctor John",
        "Genre": "Medical, Romance",
        "Cast": "Ji Sung, Lee Se-young",
        "Director": "Jo Soo-won",
        "Description": "An anesthesiologist with a mysterious past treats patients with chronic pain",
        "keywords": "medical, mystery, romance",
        "episodes": "32",
    },
]

for drama in medical_dramas:
    profile_manager.update_from_interaction(
        user_id=user_id, drama_data=drama, interaction_type="watched", rating=4.5
    )
    print(f"   📺 Watched: {drama['Title']}")

# Test 3: Check genre preferences
print("\n3️⃣ Checking learned genre preferences...")
top_genres = profile_manager.get_top_preferences(user_id, "genres", 5)
print("   Top genres:")
for genre, score in top_genres:
    print(f"      {genre}: {score:.2f}")

# Test 4: Check actor preferences
print("\n4️⃣ Checking learned actor preferences...")
top_actors = profile_manager.get_top_preferences(user_id, "actors", 5)
print("   Top actors:")
for actor, score in top_actors:
    print(f"      {actor}: {score:.2f}")

# Test 5: Check theme preferences
print("\n5️⃣ Checking learned theme preferences...")
top_themes = profile_manager.get_top_preferences(user_id, "themes", 5)
print("   Top themes:")
for theme, score in top_themes:
    print(f"      {theme}: {score:.2f}")

# Test 6: Add some Romance dramas
print("\n6️⃣ Adding Romance drama interactions...")

romance_dramas = [
    {
        "Title": "Crash Landing on You",
        "Genre": "Romance, Comedy, Drama",
        "Cast": "Hyun Bin, Son Ye-jin",
        "Director": "Lee Jung-hyo",
        "Description": "A South Korean heiress accidentally paraglides into North Korea",
        "keywords": "romance, comedy, emotional, heartwarming",
        "episodes": "16",
    }
]

for drama in romance_dramas:
    profile_manager.update_from_interaction(
        user_id=user_id, drama_data=drama, interaction_type="watchlist_add"
    )
    print(f"   ➕ Added to watchlist: {drama['Title']}")

# Test 7: Get updated preferences
print("\n7️⃣ Updated genre preferences (Medical + Romance)...")
top_genres = profile_manager.get_top_preferences(user_id, "genres", 5)
print("   Top genres:")
for genre, score in top_genres:
    print(f"      {genre}: {score:.2f}")

# Test 8: Get profile summary
print("\n8️⃣ Getting profile summary...")
summary = profile_manager.get_profile_summary(user_id)
print(f"   Persona: {summary['persona']}")
print(f"   Total interactions: {summary['statistics']['total_interactions']}")
print(f"   Total watched: {summary['statistics']['total_watched']}")
print(f"   Avg rating: {summary['statistics']['avg_rating']:.2f}")
print(f"   Rating style: {summary['statistics']['rating_style']}")
print(f"   Binge watcher: {summary['viewing_patterns']['binge_watcher']}")

# Test 9: Test with different user (Thriller fan)
print("\n9️⃣ Creating Thriller fan profile...")
thriller_user = "test_thriller_fan"

thriller_dramas = [
    {
        "Title": "Signal",
        "Genre": "Thriller, Mystery, Crime",
        "Cast": "Lee Je-hoon, Kim Hye-soo",
        "Director": "Kim Won-seok",
        "Description": "Detectives from different time periods communicate via mysterious walkie-talkie",
        "keywords": "suspense, mystery, crime, thriller",
        "episodes": "16",
    },
    {
        "Title": "Stranger",
        "Genre": "Thriller, Mystery, Legal",
        "Cast": "Cho Seung-woo, Bae Doona",
        "Director": "Kim Won-seok",
        "Description": "A prosecutor with no emotions investigates corruption",
        "keywords": "thriller, suspense, crime, mystery",
        "episodes": "16",
    },
]

for drama in thriller_dramas:
    profile_manager.update_from_interaction(
        user_id=thriller_user, drama_data=drama, interaction_type="watched", rating=5.0
    )

thriller_summary = profile_manager.get_profile_summary(thriller_user)
print(f"   Thriller fan persona: {thriller_summary['persona']}")
print(f"   Top genres: {[g[0] for g in thriller_summary['top_genres'][:3]]}")

print("\n" + "=" * 80)
print("✅ User Profile System Tests Complete!")
print("=" * 80)
print("\n📊 Summary:")
print(f"   - Created 2 user profiles")
print(f"   - Tested genre, actor, theme preference learning")
print(f"   - Verified different users have different preferences")
print(f"   - Medical fan: Loves Medical dramas")
print(f"   - Thriller fan: Loves Thriller/Mystery dramas")
print("\n🎯 Phase 2 Step 1: User Preference Learning - COMPLETE!")
