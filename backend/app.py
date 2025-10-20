from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import os
import pickle
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer, CrossEncoder
from rapidfuzz import process, fuzz
from functools import lru_cache
from rank_bm25 import BM25Okapi

# ======================================================
# Config
# ======================================================
MODEL_NAME = "paraphrase-multilingual-mpnet-base-v2"
CROSS_ENCODER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"  # optional reranker
MODEL_DIR = r"D:\Projects\Kdrama-recommendation\model_training\models"
INDEX_DIR = r"D:\Projects\Kdrama-recommendation\model_training\faiss_index"

# ======================================================
# App Setup
# ======================================================
app = FastAPI(title="Kdrama Hybrid Recommendation API", version="3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======================================================
# Load models and data
# ======================================================
print("Loading models and FAISS index...")
model = SentenceTransformer(MODEL_NAME, cache_folder=MODEL_DIR)
index = faiss.read_index(os.path.join(INDEX_DIR, "index.faiss"))

with open(os.path.join(INDEX_DIR, "meta.pkl"), "rb") as f:
    metadata = pickle.load(f)

titles = [m["Title"] for m in metadata]
corpus = [f"{m.get('Title', '')} {m.get('Genre', '')} {m.get('Description', '')} {m.get('Cast', '')}" for m in metadata]
bm25 = BM25Okapi([doc.split() for doc in corpus])

print(f"Loaded {len(metadata)} dramas successfully!")

# Optional cross-encoder reranker (semantic reranking)
try:
    reranker = CrossEncoder(CROSS_ENCODER_MODEL)
    use_reranker = True
    print("Cross-encoder reranker loaded successfully.")
except Exception as e:
    reranker = None
    use_reranker = False
    print(f"Warning: Could not load cross-encoder reranker ({e}). Continuing without it.")

# ======================================================
# Helpers
# ======================================================
def fuzzy_match_title(user_input: str, threshold=70):
    match, score, _ = process.extractOne(user_input, titles, scorer=fuzz.WRatio)
    if score >= threshold:
        return match, score
    return None, score

@lru_cache(maxsize=128)
def cached_encode(text: str):
    emb = model.encode([text], convert_to_numpy=True)
    faiss.normalize_L2(emb)
    return emb

# ======================================================
# Hybrid Recommendation Logic
# ======================================================
def recommend(title: str, top_n=5, alpha=0.7):
    # Try to find by title
    drama = next((m for m in metadata if m["Title"].lower() == title.lower()), None)

    if not drama:
        match, score = fuzzy_match_title(title)
        if match:
            drama = next((m for m in metadata if m["Title"] == match), None)
            print(f"Fuzzy match: '{title}' → '{match}' ({score:.1f}%)")
        else:
            print(f"No close match for '{title}', treating as query text.")
            query_text = title
    else:
        query_text = f"{drama['Title']} {drama.get('Genre', '')} {drama.get('Description', '')} {drama.get('Cast', '')}"

    # 1️⃣ FAISS semantic search
    query_emb = cached_encode(query_text)
    D, I = index.search(query_emb, top_n + 10)
    faiss_results = [(metadata[idx], float(score)) for idx, score in zip(I[0], D[0])]

    # 2️⃣ BM25 lexical search
    bm25_scores = bm25.get_scores(query_text.split())
    top_bm25_idx = np.argsort(bm25_scores)[::-1][:top_n + 10]
    bm25_results = [(metadata[i], float(bm25_scores[i])) for i in top_bm25_idx]

    # 3️⃣ Combine FAISS + BM25 scores (weighted)
    combined_scores = {}
    for rec, score in faiss_results:
        combined_scores[rec["Title"]] = alpha * score
    for rec, score in bm25_results:
        combined_scores[rec["Title"]] = combined_scores.get(rec["Title"], 0) + (1 - alpha) * (score / max(bm25_scores))

    # 4️⃣ Sort combined results
    sorted_results = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
    top_results = [next(m for m in metadata if m["Title"] == t) for t, _ in sorted_results[:top_n]]

    # 5️⃣ Optional reranking (cross-encoder)
    if use_reranker:
        pairs = [[query_text, r["Description"]] for r in top_results]
        rerank_scores = reranker.predict(pairs)
        top_results = [r for _, r in sorted(zip(rerank_scores, top_results), key=lambda x: x[0], reverse=True)]

    return {"query": {"Title": title}, "recommendations": top_results[:top_n]}

# ======================================================
# API Endpoints
# ======================================================
@app.get("/")
def root():
    return {"message": "Hybrid Kdrama Recommendation API v3.0 is running"}

@app.get("/recommend")
def get_recommendations(
    title: str = Query(..., description="Kdrama title or query"),
    top_n: int = 5
):
    return recommend(title, top_n)

# ======================================================
# Run Server
# ======================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8001, reload=True)
