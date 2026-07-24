"""
Test Genre Detection - Quick Verification
"""

from query_analyzer import QueryAnalyzer

analyzer = QueryAnalyzer()

# Test queries
test_queries = [
    "medical drama",
    "historical drama",
    "action thriller",
    "school drama",
    "office romance",
    "sports anime",
    "medical series",
    "historical period drama",
    "romantic comedy",
]

print("=" * 80)
print("GENRE DETECTION TEST")
print("=" * 80)

for query in test_queries:
    result = analyzer.analyze(query)
    detected_genres = result["entities"].get("genres", [])
    intent = result["intent"]

    print(f"\nQuery: '{query}'")
    print(f"  Intent: {intent}")
    print(f"  Detected Genres: {detected_genres}")
    print(f"  Expanded Query: {result['expanded_query']}")
    print(f"  Dynamic Alpha: {result['dynamic_alpha']}")

print("\n" + "=" * 80)
print("✅ Test complete! Check if genres are detected correctly.")
print("=" * 80)
