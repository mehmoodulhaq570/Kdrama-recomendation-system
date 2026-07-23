import pickle
import os

# Load metadata
metadata_path = "../training/faiss_index/meta.pkl"
with open(metadata_path, "rb") as f:
    metadata = pickle.load(f)

print("=" * 80)
print("TESTING GENRE FILTER LOGIC")
print("=" * 80)

# Test the filter logic used in app.py
genre_to_test = "Medical"

print(f"\nTesting filter for genre: '{genre_to_test}'")
print("-" * 80)

filtered = [
    r
    for r in metadata
    if genre_to_test.lower() in str(r.get("Genre", "")).lower()
    or genre_to_test.lower() in str(r.get("genres", "")).lower()
]

print(f"✓ Found {len(filtered)} dramas with '{genre_to_test}' genre")
print("\nFirst 10 results:")
for i, drama in enumerate(filtered[:10], 1):
    title = drama.get("Title", "Unknown")
    genre = drama.get("Genre", "N/A")
    print(f"{i}. {title}")
    print(f"   Genre: {genre}")

# Now test what happens when we search for "medical drama"
# (which the query analyzer would detect as genre="Medical")
print("\n" + "=" * 80)
print("TESTING SEARCH SCENARIO")
print("=" * 80)

# Simulate what happens when user searches "medical drama"
query = "medical drama"
detected_genre = "Medical"  # This is what query_analyzer detects

print(f"\nUser searches: '{query}'")
print(f"Query analyzer detects genre: '{detected_genre}'")
print(f"Backend applies filter: genre.lower() in Genre.lower()")

# Apply the filter
filtered_metadata = [
    r for r in metadata if detected_genre.lower() in str(r.get("Genre", "")).lower()
]

print(f"\n✓ Filter applied successfully")
print(f"✓ Result: {len(filtered_metadata)} medical dramas found")

if len(filtered_metadata) > 0:
    print("\n✅ FILTER IS WORKING!")
    print("Top 5 results would be:")
    for i, drama in enumerate(filtered_metadata[:5], 1):
        print(f"  {i}. {drama.get('Title')}")
else:
    print("\n❌ FILTER FAILED - No results found!")
