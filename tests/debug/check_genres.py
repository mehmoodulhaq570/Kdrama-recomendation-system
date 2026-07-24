import pickle
from pathlib import Path

# Load metadata
ROOT = Path(__file__).resolve().parents[2]
with open(ROOT / "training" / "faiss_index" / "meta.pkl", "rb") as f:
    meta = pickle.load(f)

print("Sample drama keys:", list(meta[0].keys()))
print("\n" + "=" * 80)
print("FIRST DRAMA:")
print("=" * 80)
for k, v in meta[0].items():
    print(f"  {k}: {str(v)[:200]}")

print("\n" + "=" * 80)
print("GENRE EXAMPLES FROM 20 DRAMAS:")
print("=" * 80)
for i, m in enumerate(meta[:20]):
    print(f"\n{i+1}. {m['Title']}")
    print(f"   Genre field: {m.get('Genre', 'N/A')}")
    print(f"   genres field: {m.get('genres', 'N/A')}")

print("\n" + "=" * 80)
print("SEARCHING FOR 'HISTORICAL' DRAMAS:")
print("=" * 80)
historical_count = 0
for m in meta:
    genre_str = str(m.get("Genre", "")) + str(m.get("genres", ""))
    if "historical" in genre_str.lower():
        historical_count += 1
        if historical_count <= 5:
            print(f"{historical_count}. {m['Title']}")
            print(f"   Genre: {m.get('Genre', 'N/A')}")
            print(f"   genres: {m.get('genres', 'N/A')}")
            print()

print(f"\nTotal dramas with 'historical': {historical_count}")
