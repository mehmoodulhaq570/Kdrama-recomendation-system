# app.py
import os
import json
import numpy as np
import faiss
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List
from sentence_transformers import SentenceTransformer
from sklearn.preprocessing import normalize

INDEX_DIR = "faiss_index"
INDEX_PATH = os.path.join(INDEX_DIR, "kdrama_index_flat_ip.faiss")
META_PATH = os.path.join(INDEX_DIR, "metadata.json")
TITLES_PATH = os.path.join(INDEX_DIR, "titles.npy")

EMBEDDING_MODEL = "paraphrase-multilingual-mpnet-base-v2"  # same as used when building

# weights must match ones used during indexing
W_GENRE = 0.35
W_CAST = 0.25
W_DIRECTOR = 0.10
W_DESC = 0.30

app = FastAPI(title="KDrama Recommender API (Content-based + FAISS)")

# Load index and metadata at startup
print("Loading FAISS index...")
if not os.path.exists(INDEX_PATH):
    raise FileNotFoundError(f"Index not found at {INDEX_PATH}. Run build_index.py first.")
index = faiss.read_index(INDEX_PATH)

print("Loading metadata...")
with open(META_PATH, 'r', encoding='utf-8') as f:
    metadata = json.load(f)

titles = np.load(TITLES_PATH, allow_pickle=True)

print("Loading embedding model...")
model = SentenceTransformer(EMBEDDING_MODEL)

def clean_text(text: str):
    import re
    if not isinstance(text, str):
        return ''
    text = re.sub(r'\[.*?\]', '', text)
    text = text.replace('â€“', '-').replace('\n', ' ')
    text = text.replace('"', '').replace("'", '')
    text = re.sub(r'\s{2,}', ' ', text).strip()
    return text

def encode_item(genre, cast, director, description):
    # encode per-field and fuse with same weights used in build_index
    parts = []
    g = clean_text(genre or "")
    c = clean_text(cast or "")
    d = clean_text(director or "")
    desc = clean_text(description or "")
    # model.encode can accept list, we'll combine
    emb_g = model.encode([g], convert_to_numpy=True)[0]
    emb_c = model.encode([c], convert_to_numpy=True)[0]
    emb_d = model.encode([d], convert_to_numpy=True)[0]
    emb_desc = model.encode([desc], convert_to_numpy=True)[0]
    # normalize each
    from sklearn.preprocessing import normalize
    emb_g = normalize(emb_g.reshape(1, -1))[0]
    emb_c = normalize(emb_c.reshape(1, -1))[0]
    emb_d = normalize(emb_d.reshape(1, -1))[0]
    emb_desc = normalize(emb_desc.reshape(1, -1))[0]
    combined = W_GENRE * emb_g + W_CAST * emb_c + W_DIRECTOR * emb_d + W_DESC * emb_desc
    combined = normalize(combined.reshape(1, -1)).astype('float32')
    return combined

class RecommendResponse(BaseModel):
    title: str
    year: str
    genre: str
    cast: str
    director: str
    description: str
    score: float

@app.get("/recommend", response_model=List[RecommendResponse])
def recommend(title: str = Query(..., description="Drama title present in dataset"), k: int = Query(10, gt=0, le=50)):
    # Find index of given title
    # exact match first, then case-insensitive fallback
    matches = np.where(titles == title)[0]
    if len(matches) == 0:
        matches = np.where(np.char.lower(titles.astype(str)) == title.lower())[0]
    if len(matches) == 0:
        raise HTTPException(status_code=404, detail=f"Title '{title}' not found.")
    idx = int(matches[0])

    # Retrieve corresponding metadata row to re-encode its features (safer) OR use stored embedding
    meta = metadata[idx]
    # Encode query vector using same fusion
    q_emb = encode_item(meta.get('genre', ''), meta.get('cast', ''), meta.get('director', ''), meta.get('description', ''))

    # Search FAISS (inner product on normalized vectors -> cosine similarity)
    D, I = index.search(q_emb, k + 1)  # +1 to skip the item itself
    results = []
    for score, i in zip(D[0], I[0]):
        if i == idx:
            continue
        m = metadata[i]
        results.append({
            "title": m['title'],
            "year": m.get('year', ''),
            "genre": m.get('genre', ''),
            "cast": m.get('cast', ''),
            "director": m.get('director', ''),
            "description": m.get('description', ''),
            "score": float(score)
        })
        if len(results) >= k:
            break

    return results

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
