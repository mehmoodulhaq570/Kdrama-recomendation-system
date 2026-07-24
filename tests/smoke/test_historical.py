import requests

# Test 3: What happens when we search "historical drama" WITH genre context?
print("=" * 80)
print("TEST 3: Searching 'historical drama' AS TEXT but treating it like genre search")
print("=" * 80)

# Better approach: If query mentions a genre, auto-add to filter
response = requests.get(
    "http://127.0.0.1:8001/recommend",
    params={"title": "historical", "genre": "Historical", "top_n": 5},
)
results = response.json()
print(f"\nQuery: {results['query']}")
print(f"Filters: {results['filters']}")
print(f"\nRecommendations ({len(results['recommendations'])}):")
for i, rec in enumerate(results["recommendations"], 1):
    print(f"\n{i}. {rec['Title']}")
    print(f"   Genre: {rec.get('Genre', 'N/A')}")
    print(f"   Rating: {rec.get('rating_value', 'N/A')}")
