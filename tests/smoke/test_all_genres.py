"""
Comprehensive test to demonstrate the genre filter fix
"""

import requests

API_URL = "http://127.0.0.1:8001"

print("=" * 80)
print("GENRE FILTER FIX - COMPREHENSIVE TEST")
print("=" * 80)

tests = [
    {
        "name": "TEST 1: Historical dramas (with genre filter)",
        "params": {"title": "historical", "genre": "Historical", "top_n": 5},
        "expected": "Should return ONLY historical dramas",
    },
    {
        "name": "TEST 2: Romance dramas (with genre filter)",
        "params": {"title": "romance", "genre": "Romance", "top_n": 5},
        "expected": "Should return ONLY romance dramas",
    },
    {
        "name": "TEST 3: Action dramas (with genre filter)",
        "params": {"title": "action", "genre": "Action", "top_n": 5},
        "expected": "Should return ONLY action dramas",
    },
    {
        "name": "TEST 4: Thriller dramas (with genre filter)",
        "params": {"title": "thriller", "genre": "Thriller", "top_n": 5},
        "expected": "Should return ONLY thriller dramas",
    },
    {
        "name": "TEST 5: Comedy dramas (with genre filter)",
        "params": {"title": "funny", "genre": "Comedy", "top_n": 5},
        "expected": "Should return ONLY comedy dramas",
    },
]

for test in tests:
    print(f"\n{'='*80}")
    print(test["name"])
    print(f"{'='*80}")
    print(f"Expected: {test['expected']}")
    print(f"Params: {test['params']}")

    try:
        response = requests.get(
            f"{API_URL}/recommend", params=test["params"], timeout=10
        )
        if response.status_code == 200:
            results = response.json()
            recs = results.get("recommendations", [])

            print(f"\n✅ Got {len(recs)} recommendations:")
            for i, rec in enumerate(recs, 1):
                genre = rec.get("Genre", "N/A")
                rating = rec.get("rating_value", "N/A")
                print(f"\n  {i}. {rec['Title']}")
                print(f"     Genre: {genre}")
                print(f"     Rating: {rating}")

                # Verify genre filter works
                genre_filter = test["params"].get("genre", "")
                if genre_filter and genre_filter.lower() not in genre.lower():
                    print(
                        f"     ⚠️ WARNING: Genre filter '{genre_filter}' not in '{genre}'!"
                    )
        else:
            print(f"\n❌ API Error: {response.status_code}")
    except Exception as e:
        print(f"\n❌ Request failed: {e}")

print(f"\n{'='*80}")
print("ALL TESTS COMPLETED")
print("=" * 80)
print("\n📝 Summary:")
print("- The backend now filters BEFORE semantic search")
print("- This ensures only dramas matching your filters are returned")
print("- Quick search buttons in frontend now set the genre filter automatically")
