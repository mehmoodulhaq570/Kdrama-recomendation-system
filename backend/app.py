from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import os
import pickle
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# ======================================================
# 1️⃣ Config
# ======================================================
MODEL_NAME = "paraphrase-multilingual-mpnet-base-v2"
MODEL_DIR = r"D:\Projects\Kdrama-recomendation\model_traning\models"
INDEX_DIR = r"D:\Projects\Kdrama-recomendation\model_traning\faiss_index"

# ======================================================
# 2️⃣ App Setup
# ======================================================
app = FastAPI(title="Kdrama Recommender API", version="1.0")

# Allow local frontend or React app access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for production, restrict this
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
print(" Model and index loaded!")

# ======================================================
# 4️⃣ Recommendation logic
# ======================================================
def recommend(title: str, top_n=5):
    drama = next((m for m in metadata if m["Title"].lower() == title.lower()), None)
    if not drama:
        return {"error": f"Drama '{title}' not found."}

    query_text = f"{drama['Title']} {drama['Genre']} {drama['Description']} {drama['Cast']}"
    query_emb = model.encode([query_text], convert_to_numpy=True)
    faiss.normalize_L2(query_emb)

    D, I = index.search(query_emb, top_n + 1)
    results = []
    for idx, score in zip(I[0][1:], D[0][1:]):
        rec = metadata[idx]
        rec["similarity"] = float(score)
        results.append(rec)

    return {"query": drama, "recommendations": results}

# ======================================================
# 5️⃣ API Routes
# ======================================================
@app.get("/")
def root():
    return {"message": "Kdrama Recommendation API is running!"}


@app.get("/recommend")
def get_recommendations(title: str = Query(..., description="Kdrama title"), top_n: int = 5):
    return recommend(title, top_n)


# ======================================================
# 6️⃣ Run server
# ======================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8001, reload=True)
