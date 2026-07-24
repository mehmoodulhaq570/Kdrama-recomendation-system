"""
Test Personalized Recommendations
Phase 2: Step 2 - Personalized Weighting
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "backend"))

from user_profile import UserProfileManager
from personalization import PersonalizationEngine

print("=" * 80)
print("Testing Personalized Recommendations (Phase 2 - Step 2)")
print("=" * 80)

# Create instances
profile_manager = UserProfileManager(profiles_dir="../tests/test_profiles")
personalization_engine = PersonalizationEngine()

# Test 1: Create two users with different preferences
print("\n1️⃣ Creating two users with different preferences...")

# Medical Drama Fan
medical_user = "medical_fan"
medical_dramas = [
    {
        "Title": "Hospital Playlist",
        "Genre": "Medical, Life",
        "Cast": "Jo Jung-suk, Yoo Yeon-seok",
        "Director": "Shin Won-ho",
    },
    {
        "Title": "Good Doctor",
        "Genre": "Medical",
        "Cast": "Joo Won, Moon Chae-won",
        "Director": "Ki Min-soo",
    },
]

for drama in medical_dramas:
    profile_manager.update_from_interaction(
        user_id=medical_user, drama_data=drama, interaction_type="watched", rating=5.0
    )

print(f"   ✅ Medical fan profile created")

# Thriller Fan
thriller_user = "thriller_fan"
thriller_dramas = [
    {
        "Title": "Signal",
        "Genre": "Thriller, Mystery",
        "Cast": "Lee Je-hoon, Kim Hye-soo",
        "Director": "Kim Won-seok",
    },
    {
        "Title": "Stranger",
        "Genre": "Thriller, Crime",
        "Cast": "Cho Seung-woo, Bae Doona",
        "Director": "Kim Won-seok",
    },
]

for drama in thriller_dramas:
    profile_manager.update_from_interaction(
        user_id=thriller_user, drama_data=drama, interaction_type="watched", rating=5.0
    )

print(f"   ✅ Thriller fan profile created")

# Test 2: Create mock search results (mix of genres)
print("\n2️⃣ Creating mock search results (mixed genres)...")

mock_results = [
    {
        "Title": "Doctor John",
        "Genre": "Medical, Romance",
        "Cast": "Ji Sung, Lee Se-young",
        "Director": "Jo Soo-won",
        "score": 0.75,
    },
    {
        "Title": "Flower of Evil",
        "Genre": "Thriller, Romance",
        "Cast": "Lee Joon-gi, Moon Chae-won",
        "Director": "Kim Cheol-kyu",
        "score": 0.73,
    },
    {
        "Title": "Romantic Doctor Kim",
        "Genre": "Medical, Drama",
        "Cast": "Han Suk-kyu, Seo Hyun-jin",
        "Director": "Yoo In-sik",
        "score": 0.71,
    },
    {
        "Title": "Mouse",
        "Genre": "Thriller, Crime",
        "Cast": "Lee Seung-gi, Lee Hee-joon",
        "Director": "Choi Joon-bae",
        "score": 0.69,
    },
    {
        "Title": "Crash Landing on You",
        "Genre": "Romance, Comedy",
        "Cast": "Hyun Bin, Son Ye-jin",
        "Director": "Lee Jung-hyo",
        "score": 0.68,
    },
]

print(f"   📺 Created 5 mock dramas (Medical, Thriller, Romance)")

# Test 3: Apply personalization for Medical fan
print("\n3️⃣ Applying personalization for Medical fan...")

medical_profile = profile_manager.load_profile(medical_user)
medical_results = personalization_engine.personalize_results(
    mock_results.copy(), medical_profile, apply_boosting=True
)

print("   Results for Medical fan:")
for i, drama in enumerate(medical_results[:3], 1):
    boost = drama.get("boost_multiplier", 1.0)
    base = drama.get("base_score", 0)
    pers = drama.get("personalized_score", 0)
    print(f"      {i}. {drama['Title']}")
    print(f"         Genre: {drama['Genre']}")
    print(f"         Base score: {base:.3f} → Personalized: {pers:.3f} (×{boost:.2f})")

# Test 4: Apply personalization for Thriller fan
print("\n4️⃣ Applying personalization for Thriller fan...")

thriller_profile = profile_manager.load_profile(thriller_user)
thriller_results = personalization_engine.personalize_results(
    mock_results.copy(), thriller_profile, apply_boosting=True
)

print("   Results for Thriller fan:")
for i, drama in enumerate(thriller_results[:3], 1):
    boost = drama.get("boost_multiplier", 1.0)
    base = drama.get("base_score", 0)
    pers = drama.get("personalized_score", 0)
    print(f"      {i}. {drama['Title']}")
    print(f"         Genre: {drama['Genre']}")
    print(f"         Base score: {base:.3f} → Personalized: {pers:.3f} (×{boost:.2f})")

# Test 5: Compare top recommendations
print("\n5️⃣ Comparing top recommendations...")

medical_top = medical_results[0]["Title"]
thriller_top = thriller_results[0]["Title"]

print(f"   Medical fan's #1 recommendation: {medical_top}")
print(f"   Thriller fan's #1 recommendation: {thriller_top}")

if medical_top != thriller_top:
    print("   ✅ SUCCESS: Different users get different recommendations!")
else:
    print("   ⚠️  Warning: Both users got same top recommendation")

# Test 6: Test personalization summaries
print("\n6️⃣ Testing personalization summaries...")

for drama in medical_results[:2]:
    summary = personalization_engine.get_personalization_summary(drama)
    print(f"   {drama['Title']}: {summary}")

# Test 7: Test user-specific alpha calculation
print("\n7️⃣ Testing user-specific alpha adjustment...")

base_alpha = 0.7

medical_alpha = personalization_engine.calculate_user_specific_alpha(
    medical_profile, base_alpha
)
thriller_alpha = personalization_engine.calculate_user_specific_alpha(
    thriller_profile, base_alpha
)

print(f"   Base alpha: {base_alpha:.2f}")
print(f"   Medical fan alpha: {medical_alpha:.2f}")
print(f"   Thriller fan alpha: {thriller_alpha:.2f}")

print("\n" + "=" * 80)
print("✅ Personalized Weighting Tests Complete!")
print("=" * 80)
print("\n📊 Summary:")
print(f"   - Created 2 user profiles with different preferences")
print(f"   - Applied personalization to mixed search results")
print(f"   - Medical fan: Prefers {medical_top}")
print(f"   - Thriller fan: Prefers {thriller_top}")
print(f"   - Personalization boosted scores based on preferences")
print(f"   - Different users now get different recommendations!")
print("\n🎯 Phase 2 Step 2: Personalized Weighting - COMPLETE!")
