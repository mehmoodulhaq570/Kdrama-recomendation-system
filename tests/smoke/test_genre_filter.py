import requests
import json

# Test 1: Search with genre filter
print("=" * 80)
print("TEST 1: Searching with genre='Historical' filter")
print("=" * 80)
response = requests.get(
    "http://127.0.0.1:8001/recommend",
    params={"title": "drama", "genre": "Historical", "top_n": 5},
)
results = response.json()
print(f"\nQuery: {results['query']}")
print(f"Filters: {results['filters']}")
print(f"\nRecommendations ({len(results['recommendations'])}):")
for i, rec in enumerate(results["recommendations"], 1):
    print(f"\n{i}. {rec['Title']}")
    print(f"   Genre: {rec.get('Genre', 'N/A')}")

# Test 2: Just search "historical drama" without filter
print("\n" + "=" * 80)
print("TEST 2: Searching 'historical drama' WITHOUT genre filter (like the button)")
print("=" * 80)
response = requests.get(
    "http://127.0.0.1:8001/recommend", params={"title": "historical drama", "top_n": 5}
)
results = response.json()
print(f"\nQuery: {results['query']}")
print(f"Filters: {results['filters']}")
print(f"\nRecommendations ({len(results['recommendations'])}):")
for i, rec in enumerate(results["recommendations"], 1):
    print(f"\n{i}. {rec['Title']}")
    print(f"   Genre: {rec.get('Genre', 'N/A')}")
