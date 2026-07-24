import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "backend"))
from query_analyzer import QueryAnalyzer

analyzer = QueryAnalyzer()

# Test various medical queries
test_queries = [
    "medical drama",
    "a medical drama",
    "medical kdrama",
    "medical korean drama",
    "action thriller",
    "historical drama",
    "school romance",
]

print("Testing Query Analysis:")
print("=" * 80)
for query in test_queries:
    analysis = analyzer.analyze(query)
    print(f"\nQuery: '{query}'")
    print(f"  Intent: {analysis['intent']}")
    print(f"  Entities: {analysis['entities']}")
    print(f"  Detected Genres: {analysis['entities'].get('genres', [])}")
    if "expanded_terms" in analysis:
        print(f"  Expanded Terms: {analysis['expanded_terms'][:3]}...")  # First 3 terms
