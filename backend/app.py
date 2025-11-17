from fastapi import FastAPI, Query, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
import pickle
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer, CrossEncoder
from rapidfuzz import process, fuzz
from functools import lru_cache
from rank_bm25 import BM25Plus
import uuid
import time

# Import Phase 1 enhancements
from query_analyzer import QueryAnalyzer, get_search_strategy
from analytics import get_tracker

# Import Phase 2 enhancements
from user_profile import get_profile_manager
from personalization import get_personalization_engine

# ======================================================
# CONFIGURATION
# ======================================================
MODEL_NAME = "paraphrase-multilingual-mpnet-base-v2"
# Using fine-tuned cross-encoder trained on K-drama data
CROSS_ENCODER_MODEL = r"D:\Projects\SeoulMate\model_traning\models\cross-enc-excellent"
MODEL_DIR = r"D:\Projects\SeoulMate\model_traning\models"
INDEX_DIR = r"D:\Projects\SeoulMate\model_traning\faiss_index"

# ======================================================
# FASTAPI SETUP
# ======================================================
app = FastAPI(
    title="SeoulMate Kdrama Recommendation API",
    version="4.0 (Phase 1)",
    description="Intelligent K-Drama recommendations with AI-powered query understanding and user analytics",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======================================================
# STAGE 1 — LOAD MODELS & INDEXES
# ======================================================
print("Stage 1: Loading models and FAISS index...")

# Try to load fine-tuned SBERT first, fallback to pretrained
finetuned_models = (
    [
        d
        for d in os.listdir(MODEL_DIR)
        if os.path.isdir(os.path.join(MODEL_DIR, d)) and d.startswith("sbert-finetuned")
    ]
    if os.path.exists(MODEL_DIR)
    else []
)

if finetuned_models:
    model_path = os.path.join(MODEL_DIR, finetuned_models[0])
    print(f"Loading fine-tuned SBERT from: {model_path}")
    model = SentenceTransformer(model_path)
else:
    print(f"No fine-tuned model found, using pretrained: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME, cache_folder=MODEL_DIR)

index = faiss.read_index(os.path.join(INDEX_DIR, "index.faiss"))

with open(os.path.join(INDEX_DIR, "meta.pkl"), "rb") as f:
    metadata = pickle.load(f)

titles = [m["Title"] for m in metadata]
corpus = [
    f"{m.get('Title', '')} {m.get('Genre', '')} {m.get('Description', '')} {m.get('Cast', '')}"
    for m in metadata
]
# Using BM25Plus for better performance (improved IDF handling)
bm25 = BM25Plus([doc.split() for doc in corpus])

print(f"Loaded {len(metadata)} dramas successfully.")

# ======================================================
# STAGE 1.5 — INITIALIZE PHASE 1 ENHANCEMENTS
# ======================================================
print("Stage 1.5: Initializing Phase 1 enhancements...")
query_analyzer = QueryAnalyzer()
analytics_tracker = get_tracker()
print("✓ Query analyzer and analytics tracker initialized.")

# ======================================================
# STAGE 2 — LOAD OPTIONAL RERANKER
# ======================================================
try:
    print("Stage 2: Loading cross-encoder reranker...")
    reranker = CrossEncoder(CROSS_ENCODER_MODEL)
    use_reranker = True
    print("Cross-encoder reranker loaded successfully.")
except Exception as e:
    reranker = None
    use_reranker = False
    print(f"Warning: Could not load reranker ({e}). Continuing without it.")


# ======================================================
# STAGE 3 — HELPER FUNCTIONS
# ======================================================
def fuzzy_match_title(user_input: str, threshold=70):
    """Handle typos and near matches using fuzzy logic."""
    match, score, _ = process.extractOne(user_input, titles, scorer=fuzz.WRatio)
    if score >= threshold:
        return match, score
    return None, score


@lru_cache(maxsize=128)
def cached_encode(text: str):
    """Cached embedding generation for speed."""
    emb = model.encode([text], convert_to_numpy=True)
    faiss.normalize_L2(emb)
    return emb


# ======================================================
# STAGE 4 — HYBRID RECOMMENDATION PIPELINE (v4.0 with Phase 1)
# ======================================================
def recommend(
    title: str,
    top_n=5,
    alpha=0.7,  # Will be overridden by dynamic alpha
    genre=None,
    director=None,
    publisher=None,
    top_rated=False,
    description=None,
    rating_value=None,
    rating_count=None,
    keywords=None,
    screenwriters=None,
    sort_by=None,
    sort_order="desc",
    similar_to=None,
    user_id=None,  # NEW: For analytics tracking
    session_id=None,  # NEW: For session tracking
):
    """
    Stage-based pipeline with Phase 1 enhancements:
    0. Query Analysis (NEW) - Intent detection, query expansion
    1. Apply filters to create filtered corpus (PRE-FILTERING)
    2. Resolve user input (fuzzy match or free-text)
    3. Semantic search (FAISS) on filtered corpus with expanded query
    4. Lexical search (BM25) on filtered corpus with expanded query
    5. Hybrid combination with dynamic alpha
    6. Optional reranking (Cross-Encoder)
    7. Analytics logging (NEW)
    """

    # ---- Stage 4.0: QUERY ANALYSIS (Phase 1) ----
    analysis = query_analyzer.analyze(title)
    intent = analysis["intent"]
    expanded_query = analysis["expanded_query"]
    dynamic_alpha = analysis["dynamic_alpha"]
    entities = analysis["entities"]

    print(f"🔍 Query Analysis: Intent={intent.value}, Alpha={dynamic_alpha:.2f}")
    print(f"📝 Expanded Query: {expanded_query}")
    if entities.get("genres"):
        print(f"🎭 Detected Genres: {entities['genres']}")

    # Get search strategy for this intent
    strategy = get_search_strategy(intent)

    # Use dynamic alpha instead of static
    alpha = dynamic_alpha

    # ---- Stage 4.1: PRE-FILTER the dataset ----
    filtered_metadata = metadata.copy()

    # Apply detected genres as filters if no explicit genre filter provided
    detected_genres = entities.get("genres", [])
    detected_actors = entities.get("actors", [])

    if detected_genres and not genre:
        # Filter by detected genres (OR logic - match any detected genre)
        filtered_metadata = [
            r
            for r in filtered_metadata
            if any(
                g.lower() in str(r.get("Genre", "")).lower() for g in detected_genres
            )
        ]
        print(
            f"🎯 Genre filtering applied: {len(filtered_metadata)} dramas match genres {detected_genres}"
        )

    # Apply detected actors as filters (search in Cast field)
    if detected_actors:
        filtered_metadata = [
            r
            for r in filtered_metadata
            if any(
                actor.lower() in str(r.get("Cast", "")).lower()
                for actor in detected_actors
            )
        ]
        print(
            f"🎬 Actor filtering applied: {len(filtered_metadata)} dramas with actors {detected_actors}"
        )

    # Apply all filters to create a subset
    if genre:
        filtered_metadata = [
            r
            for r in filtered_metadata
            if genre.lower() in str(r.get("Genre", "")).lower()
            or genre.lower() in str(r.get("genres", "")).lower()
        ]
    if director:
        filtered_metadata = [
            r
            for r in filtered_metadata
            if director.lower() in str(r.get("Director", "")).lower()
            or director.lower() in str(r.get("directors", "")).lower()
        ]
    if publisher:
        filtered_metadata = [
            r
            for r in filtered_metadata
            if publisher.lower() in str(r.get("publisher", "")).lower()
        ]
    if description:
        filtered_metadata = [
            r
            for r in filtered_metadata
            if description.lower() in str(r.get("Description", "")).lower()
            or description.lower() in str(r.get("description", "")).lower()
        ]
    if rating_value:
        try:
            rating_value_val = float(rating_value)
            filtered_metadata = [
                r
                for r in filtered_metadata
                if float(r.get("rating_value", r.get("score", 0))) >= rating_value_val
            ]
        except Exception:
            pass
    if rating_count:
        try:
            rating_count_val = float(rating_count)
            filtered_metadata = [
                r
                for r in filtered_metadata
                if float(r.get("rating_count", 0)) >= rating_count_val
            ]
        except Exception:
            pass
    if keywords:
        filtered_metadata = [
            r
            for r in filtered_metadata
            if keywords.lower() in str(r.get("keywords", "")).lower()
        ]
    if screenwriters:
        filtered_metadata = [
            r
            for r in filtered_metadata
            if screenwriters.lower() in str(r.get("screenwriters", "")).lower()
        ]

    # If no results after filtering, return empty
    if not filtered_metadata:
        return {
            "query": {"Title": title},
            "filters": {
                "genre": genre,
                "director": director,
                "publisher": publisher,
                "top_rated": top_rated,
                "description": description,
                "rating_value": rating_value,
                "rating_count": rating_count,
                "keywords": keywords,
                "screenwriters": screenwriters,
                "sort_by": sort_by,
                "sort_order": sort_order,
                "similar_to": similar_to,
            },
            "recommendations": [],
            "message": "No dramas match your filters. Try broadening your search criteria.",
        }

    print(
        f"Filtered corpus: {len(filtered_metadata)} dramas (from {len(metadata)} total)"
    )

    # Create indices mapping for the filtered corpus
    title_to_original_idx = {m["Title"]: i for i, m in enumerate(metadata)}
    filtered_indices = [title_to_original_idx[m["Title"]] for m in filtered_metadata]

    # ---- Stage 4.2: Title resolution (use expanded query) ----
    drama = next(
        (m for m in filtered_metadata if m["Title"].lower() == title.lower()), None
    )

    # Only try fuzzy matching for specific title searches, not genre/vague queries
    from query_analyzer import QueryIntent

    skip_fuzzy_intents = [
        QueryIntent.GENRE_BROWSE,
        QueryIntent.VAGUE,
        QueryIntent.EMOTION_BASED,
        QueryIntent.TOP_RATED,
        QueryIntent.TRENDING,
        QueryIntent.ACTOR_BASED,
    ]

    if not drama and intent not in skip_fuzzy_intents:
        # Try fuzzy match only within filtered corpus and only for specific title searches
        filtered_titles = [m["Title"] for m in filtered_metadata]
        if filtered_titles:
            match, score, _ = process.extractOne(
                title, filtered_titles, scorer=fuzz.WRatio
            )
            if match and score >= 70:
                drama = next(
                    (m for m in filtered_metadata if m["Title"] == match), None
                )
                print(
                    f"Fuzzy match: '{title}' -> '{match}' (confidence: {score:.1f}%)".encode(
                        "utf-8", errors="replace"
                    ).decode(
                        "utf-8"
                    )
                )
                # Use expanded query for better semantic search
                query_text = f"{drama['Title']} {drama.get('Genre', '')} {drama.get('Description', '')} {drama.get('Cast', '')} {expanded_query}"
            else:
                print(f"No close match found for '{title}', using expanded query.")
                query_text = expanded_query  # Use expanded query
        else:
            query_text = expanded_query
    elif not drama:
        # For genre/vague queries, use expanded query directly
        print(f"Genre/vague query detected, using expanded query: '{expanded_query}'")
        query_text = expanded_query
    else:
        query_text = f"{drama['Title']} {drama.get('Genre', '')} {drama.get('Description', '')} {drama.get('Cast', '')} {expanded_query}"

    # ---- Stage 4.3: FAISS Semantic Search on filtered corpus ----
    query_emb = cached_encode(query_text)
    # Search more broadly to ensure we get enough results
    search_k = min(len(filtered_metadata) + 50, len(metadata))
    D_all, I_all = index.search(query_emb, search_k)

    # Filter FAISS results to only include filtered_metadata indices
    faiss_results = [
        (metadata[idx], float(score))
        for idx, score in zip(I_all[0], D_all[0])
        if idx < len(metadata) and idx in filtered_indices
    ][
        : top_n + 20
    ]  # Take top results from filtered set

    # ---- Stage 4.3: BM25 Lexical Search on filtered corpus ----
    # Get BM25 scores for all dramas, then filter
    bm25_scores_all = bm25.get_scores(query_text.split())
    bm25_results = [
        (metadata[idx], float(bm25_scores_all[idx])) for idx in filtered_indices
    ]
    bm25_results = sorted(bm25_results, key=lambda x: x[1], reverse=True)[: top_n + 20]

    # ---- Stage 4.4: Combine Results ----
    combined_scores = {}
    max_bm25 = max([score for _, score in bm25_results]) if bm25_results else 1
    if max_bm25 == 0:
        max_bm25 = 1

    for rec, score in faiss_results:
        combined_scores[rec["Title"]] = alpha * score
    for rec, score in bm25_results:
        combined_scores[rec["Title"]] = combined_scores.get(rec["Title"], 0) + (
            1 - alpha
        ) * (score / max_bm25)

    # Apply genre boost if genres were detected
    if detected_genres:
        print(f"🚀 Applying genre boost for: {detected_genres}")
        for title, score in combined_scores.items():
            drama = next((m for m in filtered_metadata if m["Title"] == title), None)
            if drama:
                drama_genres = str(drama.get("Genre", "")).lower()
                # Boost if any detected genre matches
                if any(g.lower() in drama_genres for g in detected_genres):
                    combined_scores[title] = score * 1.3  # 30% boost for genre match
                    print(f"   ✓ Boosted: {title} ({drama.get('Genre', '')})")

    # Sort by combined score (filters already applied in Stage 4.0)
    filtered = [
        next(m for m in filtered_metadata if m["Title"] == t)
        for t, _ in sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
    ]

    # Handle similar_to filter (requires FAISS search)
    if similar_to:
        # Find dramas similar to a given title within filtered metadata
        sim_drama = next(
            (m for m in filtered_metadata if m["Title"].lower() == similar_to.lower()),
            None,
        )
        if sim_drama:
            sim_query = f"{sim_drama['Title']} {sim_drama.get('Genre', '')} {sim_drama.get('Description', '')} {sim_drama.get('Cast', '')}"
            sim_emb = cached_encode(sim_query)
            D_sim, I_sim = index.search(sim_emb, len(filtered_metadata) + 20)
            # Only keep results that are in our filtered set
            sim_titles = [
                metadata[idx]["Title"]
                for idx in I_sim[0]
                if idx < len(metadata) and idx in filtered_indices
            ]
            filtered = [r for r in filtered if r["Title"] in sim_titles]

    # Sorting
    if sort_by:
        reverse = sort_order == "desc"
        filtered = sorted(
            filtered,
            key=lambda r: (
                float(r.get(sort_by, 0))
                if isinstance(r.get(sort_by, 0), (int, float, str))
                and str(r.get(sort_by, 0)).replace(".", "", 1).isdigit()
                else str(r.get(sort_by, ""))
            ),
            reverse=reverse,
        )
    elif top_rated:
        filtered = sorted(
            filtered,
            key=lambda r: float(r.get("rating_value", r.get("score", 0))),
            reverse=True,
        )
    top_results = filtered[:top_n]
    # ---- Stage 4.5: Optional Reranking ----
    # Disabled for performance - cross-encoder adds 2-3 seconds
    # Re-enable for production if accuracy is critical
    if False and use_reranker and reranker:  # Disabled for speed
        try:
            # Limit to top 20 candidates to reduce reranking time
            rerank_candidates = top_results[:20]
            pairs = [[query_text, r["Description"]] for r in rerank_candidates]
            rerank_scores = reranker.predict(pairs)
            top_results = [
                r
                for _, r in sorted(
                    zip(rerank_scores, rerank_candidates),
                    key=lambda x: x[0],
                    reverse=True,
                )
            ] + top_results[
                20:
            ]  # Keep rest in original order
        except Exception as e:
            print(f"Reranking failed: {e}")

    # ---- Stage 4.6: PERSONALIZATION (Phase 2 - NEW!) ----
    personalization_info = None
    if user_id:
        try:
            # Load user profile
            profile_manager = get_profile_manager()
            user_profile = profile_manager.load_profile(user_id)

            # Apply personalized weighting
            personalization_engine = get_personalization_engine()

            # Adjust alpha based on user preferences (explore vs exploit)
            personalized_alpha = personalization_engine.calculate_user_specific_alpha(
                user_profile, alpha
            )

            # Apply personalized boosting to results
            top_results = personalization_engine.personalize_results(
                top_results, user_profile, apply_boosting=True
            )

            print(
                f"🎯 Personalization Applied: Alpha {alpha:.2f} → {personalized_alpha:.2f}"
            )
            print(f"   Boosted based on user preferences")

            # Prepare personalization info for frontend
            # Calculate average boost for reporting
            avg_boost = (
                sum(r.get("boost_multiplier", 1.0) for r in top_results)
                / len(top_results)
                if top_results
                else 1.0
            )
            boost_applied = any(
                r.get("boost_multiplier", 1.0) > 1.01 for r in top_results
            )

            personalization_info = {
                "applied": True,
                "boost_applied": boost_applied,
                "average_boost": avg_boost,
                "alpha_adjusted": abs(personalized_alpha - alpha) > 0.01,
                "original_alpha": alpha,
                "personalized_alpha": personalized_alpha,
                "top_genres": user_profile.get("preferences", {}).get("genres", {}),
                "top_actors": user_profile.get("preferences", {}).get("actors", {}),
                "persona": user_profile.get("persona", []),
                "total_interactions": user_profile.get("statistics", {}).get(
                    "total_interactions", 0
                ),
            }

        except Exception as e:
            print(f"Warning: Personalization failed: {e}")
            # Continue with non-personalized results
            personalization_info = {"applied": False, "error": str(e)}

    # ---- Stage 4.7: Analytics Logging (Phase 1) ----
    result_titles = [r["Title"] for r in top_results]

    # Log search if user_id and session_id provided
    if user_id and session_id:
        try:
            search_id = analytics_tracker.log_search(
                user_id=user_id,
                query=title,
                intent=intent.value,
                results=result_titles,
                filters={
                    "genre": genre,
                    "director": director,
                    "publisher": publisher,
                    "rating_value": rating_value,
                    "rating_count": rating_count,
                },
                session_id=session_id,
            )
            print(f"📊 Search logged: {search_id}")
        except Exception as e:
            print(f"Warning: Analytics logging failed: {e}")

    # Build response with personalization info
    response = {
        "query": {"Title": title, "expanded": expanded_query},
        "analysis": {
            "intent": intent.value,
            "dynamic_alpha": dynamic_alpha,
            "confidence": analysis["confidence"],
        },
        "filters": {
            "genre": genre,
            "director": director,
            "publisher": publisher,
            "top_rated": top_rated,
            "description": description,
            "rating_value": rating_value,
            "rating_count": rating_count,
            "keywords": keywords,
            "screenwriters": screenwriters,
            "sort_by": sort_by,
            "sort_order": sort_order,
            "similar_to": similar_to,
        },
        "recommendations": top_results,
    }

    # Add personalization info if available
    if personalization_info:
        response["personalization"] = personalization_info
        response["personalization_info"] = (
            personalization_info  # For backward compatibility
        )

    return response


# ======================================================
# STAGE 5 — API ROUTES
# ======================================================
@app.get("/")
def root():
    return {
        "message": "SeoulMate Kdrama Recommendation API v4.0 Phase 2 is running",
        "phase_1_features": [
            "Query Intent Detection",
            "Dynamic Weight Adjustment",
            "Query Expansion with Synonyms",
            "Click Tracking & Analytics",
            "Auto-Genre Detection",
        ],
        "phase_2_features": [
            "User Preference Learning",
            "Personalized Weighting (Genre, Actor, Director, Theme)",
            "User Taste Profiles",
            "Dynamic Alpha Adjustment",
            "Interaction-based Learning",
        ],
        "docs": "/docs",
    }


@app.get("/analyze")
def analyze_query(query: str = Query(..., description="Query to analyze")):
    """
    Analyze a query to detect intent, genres, and other entities.
    This is a lightweight endpoint for quick analysis without full recommendation.
    """
    try:
        analysis = query_analyzer.analyze(query)
        return {
            "query": query,
            "intent": (
                analysis["intent"].value
                if hasattr(analysis["intent"], "value")
                else str(analysis["intent"])
            ),
            "entities": analysis["entities"],
            "detected_genres": analysis["entities"].get(
                "genres", []
            ),  # For evaluation script
            "confidence": analysis.get("confidence", 0.8),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.get("/recommend")
def get_recommendations(
    title: str = Query(..., description="Kdrama title or user query"),
    top_n: int = Query(5, description="Number of recommendations"),
    genre: str = Query(None, description="Genre filter"),
    director: str = Query(None, description="Director filter"),
    publisher: str = Query(None, description="Publisher filter"),
    top_rated: bool = Query(False, description="Sort by top rating"),
    description: str = Query(None, description="Description keyword filter"),
    rating_value: float = Query(None, description="Minimum rating value"),
    rating_count: float = Query(None, description="Minimum rating count"),
    keywords: str = Query(None, description="Keywords filter"),
    screenwriters: str = Query(None, description="Screenwriters filter"),
    sort_by: str = Query(
        None,
        description="Sort by field (e.g., rating_value, popularity, date_published, episodes, duration)",
    ),
    sort_order: str = Query("desc", description="Sort order: asc or desc"),
    similar_to: str = Query(None, description="Find dramas similar to this title"),
    user_id: str = Query(None, description="User ID for analytics (optional)"),
    session_id: str = Query(None, description="Session ID for analytics (optional)"),
):
    """Main recommendation endpoint with advanced filters, sorting, and Phase 1 enhancements."""
    # Generate session ID if not provided
    if user_id and not session_id:
        import uuid

        session_id = f"session_{uuid.uuid4().hex[:8]}"

    return recommend(
        title,
        top_n,
        alpha=0.7,  # Will be overridden by dynamic alpha
        genre=genre,
        director=director,
        publisher=publisher,
        top_rated=top_rated,
        description=description,
        rating_value=rating_value,
        rating_count=rating_count,
        keywords=keywords,
        screenwriters=screenwriters,
        sort_by=sort_by,
        sort_order=sort_order,
        similar_to=similar_to,
        user_id=user_id,
        session_id=session_id,
    )


# ======================================================
# ANALYTICS ENDPOINTS (Phase 1)
# ======================================================
class InteractionRequest(BaseModel):
    user_id: str
    drama_title: str
    interaction_type: str
    search_id: Optional[str] = None
    position: Optional[int] = None
    session_id: Optional[str] = None


@app.post("/analytics/interaction", tags=["Analytics"])
def log_interaction(request: InteractionRequest):
    """
    Log user interaction with a drama
    Used for:
    - Click tracking
    - Implicit feedback
    - Recommendation improvement
    """
    try:
        analytics_tracker.log_interaction(
            user_id=request.user_id,
            drama_title=request.drama_title,
            action=request.interaction_type,
            search_id=request.search_id,
            position=request.position,
            session_id=request.session_id,
        )
        return {"status": "success", "message": "Interaction logged"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to log interaction: {str(e)}"
        )


@app.get("/analytics/popular", tags=["Analytics"])
def get_popular_dramas(
    days: int = Query(7, description="Look back period in days"),
    limit: int = Query(20, description="Number of results"),
):
    """
    Get most popular dramas based on user interactions
    Useful for:
    - Trending section
    - Homepage recommendations
    - Popular now widget
    """
    try:
        popular = analytics_tracker.get_popular_dramas(days=days, limit=limit)
        return {"popular_dramas": popular, "period_days": days}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get popular dramas: {str(e)}"
        )


@app.get("/analytics/trending-searches", tags=["Analytics"])
def get_trending_searches(
    days: int = Query(7, description="Look back period in days"),
    limit: int = Query(20, description="Number of results"),
):
    """
    Get trending search queries
    Useful for:
    - Search suggestions
    - Understanding user interests
    - Content discovery
    """
    try:
        trending = analytics_tracker.get_trending_searches(days=days, limit=limit)
        return {"trending_searches": trending, "period_days": days}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get trending searches: {str(e)}"
        )


@app.get("/analytics/summary", tags=["Analytics"])
def get_analytics_summary(
    days: int = Query(7, description="Look back period in days"),
):
    """
    Get overall analytics summary
    Includes:
    - Total searches
    - Total interactions
    - Click-through rate
    - Unique users
    """
    try:
        summary = analytics_tracker.get_analytics_summary(days=days)
        return summary
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get analytics summary: {str(e)}"
        )


# ======================================================
# USER PROFILE ENDPOINTS (Phase 2)
# ======================================================
@app.get("/profile/{user_id}", tags=["Personalization"])
def get_user_profile(user_id: str):
    """
    Get user's taste profile with preferences and statistics

    Returns:
    - Genre preferences with scores
    - Favorite actors and directors
    - Viewing patterns
    - User persona labels
    - Interaction statistics
    """
    try:
        profile_manager = get_profile_manager()
        user_profile = profile_manager.load_profile(user_id)

        # Get top preferences for easier consumption
        top_genres = profile_manager.get_top_preferences(user_id, "genres", n=10)
        top_actors = profile_manager.get_top_preferences(user_id, "actors", n=10)
        top_directors = profile_manager.get_top_preferences(user_id, "directors", n=5)
        top_themes = profile_manager.get_top_preferences(user_id, "themes", n=10)

        # Convert datetime strings to ensure JSON serialization
        import datetime

        def serialize_datetime(obj):
            if isinstance(obj, datetime.datetime):
                return obj.isoformat()
            return obj

        # Ensure all datetime fields are serialized
        if "created_at" in user_profile:
            user_profile["created_at"] = str(user_profile["created_at"])
        if "last_updated" in user_profile:
            user_profile["last_updated"] = str(user_profile["last_updated"])

        return {
            "user_id": user_id,
            "profile": user_profile,
            "top_preferences": {
                "genres": top_genres,
                "actors": top_actors,
                "directors": top_directors,
                "themes": top_themes,
            },
            "persona": user_profile.get("persona", []),
            "statistics": user_profile.get("statistics", {}),
        }
    except Exception as e:
        # Log the full error for debugging
        import traceback

        print(f"ERROR in get_user_profile: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get user profile: {str(e)}"
        )


@app.post("/profile/{user_id}/rate", tags=["Personalization"])
def rate_drama(
    user_id: str,
    drama_title: str = Query(..., description="Title of the drama to rate"),
    rating: float = Query(..., ge=0.0, le=10.0, description="Rating from 0-10"),
):
    """
    Rate a drama and update user preferences

    This will:
    - Update user's genre preferences
    - Update actor/director preferences
    - Adjust user's taste profile
    - Log the rating for analytics
    """
    try:
        # Find the drama in the metadata
        drama_data = None
        for drama in metadata:
            if drama.get("Title", "").lower() == drama_title.lower():
                drama_data = drama
                break

        if not drama_data:
            raise HTTPException(
                status_code=404, detail=f"Drama '{drama_title}' not found"
            )

        # Update user profile
        profile_manager = get_profile_manager()
        profile_manager.update_from_interaction(
            user_id=user_id,
            drama_data=drama_data,
            interaction_type="watched",
            rating=rating,
        )

        # Also log to analytics
        analytics_tracker.log_interaction(
            user_id=user_id,
            session_id=f"rating_{time.time()}",
            search_id=None,
            drama_title=drama_title,
            interaction_type="rating",
            position=None,
            rating=rating,
            metadata={"drama_data": drama_data},
        )

        return {
            "success": True,
            "message": f"Rating recorded: {drama_title} = {rating}/10",
            "user_id": user_id,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to rate drama: {str(e)}")


@app.delete("/profile/{user_id}", tags=["Personalization"])
def reset_user_profile(user_id: str):
    """
    Reset a user's profile (clear all preferences)

    Use this to:
    - Start fresh with recommendations
    - Clear test data
    - Reset after major preference changes
    """
    try:
        profile_manager = get_profile_manager()
        profile_path = profile_manager.profiles_dir / f"{user_id}.json"

        if profile_path.exists():
            profile_path.unlink()
            return {
                "success": True,
                "message": f"Profile reset for user {user_id}",
            }
        else:
            return {
                "success": True,
                "message": f"No profile found for user {user_id} (nothing to reset)",
            }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to reset profile: {str(e)}"
        )


@app.get("/analytics/user-stats/{user_id}", tags=["Analytics"])
def get_user_statistics(user_id: str):
    """
    Get statistics for a specific user
    Includes:
    - Total clicks
    - Watchlist additions
    - Interaction history
    - Preferences
    """
    try:
        stats = analytics_tracker.get_user_stats(user_id)
        if not stats:
            return {"user_id": user_id, "message": "No data found for this user"}
        return {"user_id": user_id, "stats": stats}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get user stats: {str(e)}"
        )


# ======================================================
# STAGE 6 — RUN LOCALLY
# ======================================================
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="127.0.0.1", port=8001, reload=True)
