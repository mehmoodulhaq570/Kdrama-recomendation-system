import os
import pickle
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer, util

# ======================================================
# 1️⃣ Paths
# ======================================================
MODEL_NAME = "paraphrase-multilingual-mpnet-base-v2"
MODEL_DIR = r"D:\Projects\Kdrama-recomendation\model_traning\models"
INDEX_DIR = r"D:\Projects\Kdrama-recomendation\model_traning\faiss_index"


# ======================================================
# 2️⃣ Load model and FAISS index
# ======================================================
print(" Loading model and FAISS index...")
model = SentenceTransformer(MODEL_NAME, cache_folder=MODEL_DIR)
index = faiss.read_index(os.path.join(INDEX_DIR, "index.faiss"))

with open(os.path.join(INDEX_DIR, "meta.pkl"), "rb") as f:
    metadata = pickle.load(f)

print(" Model and index loaded!")

# ======================================================
# 3️⃣ Helper: Recommend function
# ======================================================
def recommend(title: str, top_n=5):
    """Get top-N recommendations based on drama title."""
    # Find the drama in metadata
    drama = next((m for m in metadata if m["Title"].lower() == title.lower()), None)
    if not drama:
        print(f" Drama '{title}' not found in dataset.")
        return []

    # Create query embedding
    query_text = f"{drama['Title']} {drama['Genre']} {drama['Description']} {drama['Cast']}"
    query_emb = model.encode([query_text], convert_to_numpy=True)
    faiss.normalize_L2(query_emb)

    # Search
    D, I = index.search(query_emb, top_n + 1)  # +1 to exclude the same item
    results = []
    for idx, score in zip(I[0][1:], D[0][1:]):  # skip self-match
        rec = metadata[idx]
        rec["similarity"] = float(score)
        results.append(rec)

    print(f"\n Top {top_n} Recommendations for '{title}':\n")
    for i, r in enumerate(results, 1):
        print(f"{i}. {r['Title']} ({r['Release Years']}) — {r['Genre']}")
        print(f"   Similarity: {r['similarity']:.3f}")
        print(f"   Network: {r.get('Network', '-')}")
        print(f"   Description: {r['Description'][:180]}...\n")

    return results

# ======================================================
# 4️⃣ Example usage
# ======================================================
if __name__ == "__main__":
    recommend("Do Do Sol Sol La La Sol", top_n=5)
