from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import os
import pickle
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from rapidfuzz import process, fuzz
from functools import lru_cache

# ======================================================
# 1️⃣ Config
# ======================================================
MODEL_NAME = "paraphrase-multilingual-mpnet-base-v2"
MODEL_DIR = r"D:\Projects\Kdrama-recomendation\model_traning\models"
INDEX_DIR = r"D:\Projects\Kdrama-recomendation\model_traning\faiss_index"

# ======================================================
# 2️⃣ App Setup
# ======================================================
app = FastAPI(title="Kdrama Recommender API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 🔒 restrict later in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======================================================
# 3️⃣ Load model and FAISS index
# ======================================================
print(" Loading model and FAISS index...")
model = SentenceTransformer(MODEL_NAME, cache_folder=MODEL_DIR)
index = faiss.read_index(os.path.join(INDEX_DIR, "index.faiss"))

with open(os.path.join(INDEX_DIR, "meta.pkl"), "rb") as f:
    metadata = pickle.load(f)

titles = [m["Title"] for m in metadata]
print(f" Model and index loaded! ({len(titles)} dramas)")

# ======================================================
# 4️⃣ Helper — Find Closest Match (Fuzzy)
# ======================================================
def fuzzy_match_title(user_input: str, threshold=70):
    """Find best fuzzy match for a user-entered title."""
    match, score, _ = process.extractOne(
        user_input, titles, scorer=fuzz.WRatio
    )
    if score >= threshold:
        return match, score
    return None, score

# ======================================================
# 5️⃣ Caching Decorator
# ======================================================
@lru_cache(maxsize=128)
def cached_encode(text: str):
    emb = model.encode([text], convert_to_numpy=True)
    faiss.normalize_L2(emb)
    return emb

# ======================================================
# 6️⃣ Recommendation Logic
# ======================================================
def recommend(title: str, top_n=5):
    """Recommend similar dramas based on title or description."""
    # 1️⃣ Try to find exact title
    drama = next((m for m in metadata if m["Title"].lower() == title.lower()), None)

    # 2️⃣ If not found, fuzzy match
    if not drama:
        match, score = fuzzy_match_title(title)
        if match:
            drama = next((m for m in metadata if m["Title"] == match), None)
            print(f" Fuzzy match: '{title}' -> '{match}' ({score:.1f}%)")
        else:
            # 3️⃣ No fuzzy match — treat as a new query
            print(f" No close title found. Treating '{title}' as free-text query.")
            query_emb = cached_encode(title)
            D, I = index.search(query_emb, top_n)
            results = []
            for idx, score in zip(I[0], D[0]):
                rec = metadata[idx]
                rec["similarity"] = float(score)
                results.append(rec)
            return {"query": {"Title": title, "fuzzy_match": None}, "recommendations": results}

    # 4️⃣ Build query text from metadata
    query_text = f"{drama['Title']} {drama.get('Genre', '')} {drama.get('Description', '')} {drama.get('Cast', '')}"
    query_emb = cached_encode(query_text)

    # 5️⃣ Search in FAISS
    D, I = index.search(query_emb, top_n + 1)
    results = []
    for idx, score in zip(I[0][1:], D[0][1:]):  # skip self
        rec = metadata[idx]
        rec["similarity"] = float(score)
        results.append(rec)

    return {"query": drama, "recommendations": results}

# ======================================================
# 7️⃣ API Routes
# ======================================================
@app.get("/")
def root():
    return {"message": "Kdrama Recommendation API (v2) is running!"}

@app.get("/recommend")
def get_recommendations(
    title: str = Query(..., description="Kdrama title or text query"),
    top_n: int = 5
):
    return recommend(title, top_n)

# ======================================================
# 8️⃣ Run Server
# ======================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8001, reload=True)
