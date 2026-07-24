"""
Test the complete flow: analyze query -> detect genre -> filter results
"""

import requests

API_URL = "http://127.0.0.1:8001"

test_queries = [
    "medical drama",
    "a medical drama",
    "medical kdrama",
    "historical drama",
    "action thriller",
    "school romance",
]

print("Testing Complete Flow: Analyze -> Detect Genre -> Filter")
print("=" * 80)

for query in test_queries:
    print(f"\n{'='*80}")
    print(f"Query: '{query}'")
    print(f"{'='*80}")

    # Step 1: Analyze query
    print("\n1️⃣ ANALYZING QUERY...")
    try:
        analyze_response = requests.get(
            f"{API_URL}/analyze", params={"query": query}, timeout=3
        )
        if analyze_response.status_code == 200:
            analysis = analyze_response.json()
            detected_genres = analysis.get("entities", {}).get("genres", [])
            print(f"   ✅ Detected genres: {detected_genres}")

            if detected_genres:
                genre = detected_genres[0]

                # Step 2: Get recommendations with detected genre
                print(f"\n2️⃣ SEARCHING WITH GENRE FILTER: {genre}")
                rec_response = requests.get(
                    f"{API_URL}/recommend",
                    params={
                        "title": query,
                        "top_n": 5,
                        "genre": genre,
                        "user_id": "test_user",
                        "session_id": "test_session",
                    },
                    timeout=10,
                )

                if rec_response.status_code == 200:
                    results = rec_response.json()
                    recommendations = results.get("recommendations", [])
                    print(f"   ✅ Found {len(recommendations)} recommendations")

                    if recommendations:
                        print(f"\n   📺 Top 3 results:")
                        for i, drama in enumerate(recommendations[:3], 1):
                            genres = drama.get("Genre", "N/A")
                            print(f"      {i}. {drama.get('Title', 'Unknown')}")
                            print(f"         Genres: {genres}")
                else:
                    print(f"   ❌ Recommendation failed: {rec_response.status_code}")
            else:
                print("   ⚠️  No genres detected")
        else:
            print(f"   ❌ Analysis failed: {analyze_response.status_code}")
            print(f"   Response: {analyze_response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

print("\n" + "=" * 80)
print("✅ Test Complete!")
