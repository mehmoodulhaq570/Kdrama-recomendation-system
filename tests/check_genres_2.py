import pickle
import os

# Find the metadata file
metadata_path = None
possible_paths = [
    "../training/faiss_index/meta.pkl",
    "./meta.pkl",
    "faiss_index/meta.pkl",
    "d:/Projects/SeoulMate/training/faiss_index/meta.pkl",
]

for path in possible_paths:
    if os.path.exists(path):
        metadata_path = path
        break

if not metadata_path:
    print("❌ metadata.pkl not found!")
    print("Searching for it...")
    import glob

    results = glob.glob("**/*.pkl", recursive=True)
    print(f"Found PKL files: {results}")
    exit(1)

print(f"✓ Using metadata from: {metadata_path}")

# Load metadata
with open(metadata_path, "rb") as f:
    metadata = pickle.load(f)

print("=" * 80)
print("CHECKING ACTUAL GENRE DATA")
print("=" * 80)

# Check first 20 entries
print("\nFirst 20 dramas with their genres:")
for i, drama in enumerate(metadata[:20], 1):
    title = drama.get("Title", drama.get("title", "Unknown"))
    genre = drama.get("Genre", drama.get("genres", "N/A"))
    print(f"{i}. {title}")
    print(f"   Genre: {genre}")
    print()

# Check for medical dramas specifically
print("\n" + "=" * 80)
print("SEARCHING FOR MEDICAL DRAMAS:")
print("=" * 80)
medical_count = 0
for drama in metadata:
    title = drama.get("Title", drama.get("title", "Unknown"))
    genre = str(drama.get("Genre", drama.get("genres", "")))

    if (
        "medical" in genre.lower()
        or "doctor" in genre.lower()
        or "hospital" in genre.lower()
    ):
        medical_count += 1
        print(f"✓ {title}")
        print(f"  Genre: {genre}")
        print()
        if medical_count >= 10:
            break

if medical_count == 0:
    print("❌ NO MEDICAL DRAMAS FOUND!")
    print("\nLet's check what genres exist:")
    all_genres = set()
    for drama in metadata:
        genre = str(drama.get("Genre", drama.get("genres", "")))
        genres_list = [g.strip() for g in genre.split(",")]
        all_genres.update(genres_list)

    print("\nAll unique genres in dataset:")
    for genre in sorted(all_genres)[:50]:
        if genre and genre != "N/A":
            print(f"  - {genre}")
