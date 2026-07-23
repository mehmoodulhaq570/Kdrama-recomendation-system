# SeoulMate - AI-Powered Korean Drama Recommendation System

> **An intelligent K-Drama discovery platform with advanced query understanding, personalized recommendations, and comprehensive analytics.**

## Current Repository Structure

```text
SeoulMate/
├── backend/
│   ├── app.py
│   ├── analytics.py
│   ├── personalization.py
│   ├── query_analyzer.py
│   ├── user_profile.py
│   ├── ranking/
│   │   ├── generate_indexes.py
│   │   ├── config/
│   │   └── indexes/
│   └── runtime_data/
├── frontend/
│   └── streamlit_app.py
├── training/
│   ├── train_pipeline.py
│   ├── models/
│   ├── faiss_index/
│   └── training_data/
├── data/
│   └── final/
├── scrapers/
├── tests/
│   └── reports/
│       ├── audits/
│       ├── debug/
│       └── logs/
├── docs/
│   └── archived/
└── scripts/
    ├── run_backend.ps1
    ├── run_frontend.ps1
    └── run_accuracy.ps1
```

Core rule:

- `backend/` serves recommendations and user-facing API behavior.
- `backend/ranking/` owns ranking indexes, curated priors, and index generation.
- `training/` owns model training, FAISS index building, and training artifacts.
- `data/final/` owns the final dataset used by training scripts.
- `scrapers/` owns raw data collection scripts and scraped source artifacts.
- `backend/runtime_data/` owns local logs and user profile files created while running the app.

[![FastAPI](https://img.shields.io/badge/FastAPI-v0.104-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-v1.28-FF4B4B?style=flat&logo=streamlit)](https://streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat&logo=python)](https://python.org/)
[![Phase](https://img.shields.io/badge/Phase-1%20Complete-00C853?style=flat)](#)

## 🎯 Project Overview

SeoulMate is a next-generation K-Drama recommendation system that goes beyond simple keyword matching. With **Phase 1 intelligence features** now complete, the system understands user intent, automatically detects genres, expands queries with K-drama terminology, and learns from user behavior to provide increasingly personalized recommendations.

### ✨ What Makes SeoulMate Special

- 🧠 **Query Intelligence**: Automatically detects what you're looking for (genre, mood, actors)
- 🎯 **Auto-Genre Detection**: Type "medical drama" and it knows to filter Medical genre
- 📈 **Smart Recommendations**: Dynamic algorithm weighting based on query intent
- 📊 **User Analytics**: Track your viewing history, watchlist, and preferences
- 🔍 **Hybrid Search**: Combines semantic understanding + keyword matching + AI reranking
- 🌐 **Multilingual**: Understands both Korean and English queries

## 🏗️ Architecture

### 1. Data Collection 🔍

#### Wikipedia Scraper

- **File**: `data_scrapper/wiki_scrapper_playwright.py`
- **Purpose**: Scrapes K-Drama data from Wikipedia
- **Data Collected**:
  - Title
  - Cast
  - Director
  - Genre
  - Episodes
  - Release dates
  - Descriptions

#### MyDramaList Scrapers

- **Scraper**: `data_scrapper/DramaList_Scrapper/scrapper.py`
- **Capabilities**:
  - Collects 250 pages of popular dramas
  - Downloads individual drama pages (10,000+ HTML files)
  - Extracts detailed metadata using fast lxml parsing
  - Multithreaded processing for optimal performance

**Extracted Fields**:

- Basic Info: Title, alternate names, URL, description, image
- Metadata: Country, genres, keywords, publisher
- Ratings: Rating value, rating count, popularity ranking
- Production: Directors, screenwriters
- Details: Episodes, aired dates, duration, content rating
- Engagement: Watchers, ranked position
- Cast: Actors and their roles

#### Dataset

- **File**: `kdrama_dataset_detailed_v8_playwright.csv`
- **Content**: Comprehensive K-Drama information with all extracted fields
- **Size**: 2,000+ dramas

### 2. Recommendation Engine 🎯 (Phase 1 Complete)

#### Phase 1: Query Intelligence System

**New in Phase 1:**

- 🧠 **Intent Detection**: Automatically identifies 10 types of user queries

  - Genre browsing ("show me medical dramas")
  - Actor-based searches ("dramas with Park Seo-joon")
  - Mood-based queries ("something funny and lighthearted")
  - Time-based searches ("recent dramas from 2024")
  - Rating-based ("highest rated romance")
  - Exploratory ("suggest something new")
  - Similar content ("shows like Crash Landing on You")
  - Binge-worthy ("completed series to watch")
  - Award-winning ("critically acclaimed dramas")
  - Emotional ("sad romantic dramas")

- 🎯 **Auto-Genre Detection**: Detects genres from natural language

  - "medical drama" → Auto-applies "Medical" genre filter
  - "historical kdrama" → Auto-applies "Historical" genre filter
  - "school romance" → Auto-applies "Youth" + "Romance" filters
  - Works with 25+ K-drama specific terms

- 📝 **Query Expansion**: Enriches searches with synonyms

  - "doctor drama" → expands to "medical, hospital, healthcare"
  - "sageuk" → expands to "historical, joseon, period drama"
  - "romcom" → expands to "romantic comedy, lighthearted romance"

- ⚖️ **Dynamic Algorithm Weighting**: Adjusts search strategy by intent

  - Genre queries: More keyword-based (alpha=0.35)
  - Actor queries: Balanced approach (alpha=0.6)
  - Mood queries: More semantic-based (alpha=0.8)

- 📊 **Analytics & Learning**: Tracks user behavior
  - Click tracking and position analytics
  - User watchlist and viewing history
  - Popular dramas and trending searches
  - Click-through rate analysis

#### Hybrid Search System

The recommendation engine combines multiple search techniques for optimal results:

1. **Semantic Search**

   - Technology: FAISS + Sentence Transformers
   - Purpose: Understands meaning and context
   - Model: `paraphrase-multilingual-mpnet-base-v2` (fine-tuned)
   - Features: Multilingual support (Korean & English)

2. **Lexical Search**

   - Technology: BM25Plus (improved BM25)
   - Purpose: Keyword matching and exact term retrieval
   - Use Case: Finding specific titles or terms

3. **Cross-Encoder Reranker**

   - Purpose: Improves relevance of final results
   - Function: Re-scores candidates for better ranking
   - Model: Fine-tuned on K-drama data

4. **Fuzzy Matching**
   - Purpose: Handles typos and spelling variations
   - Benefit: More forgiving user input
   - Threshold: 70% similarity

#### Model Details

- **Primary Model**: `paraphrase-multilingual-mpnet-base-v2`
- **Vector Dimension**: 768
- **Language Support**: Multilingual (Korean, English, and more)
- **Index Type**: FAISS for efficient similarity search

### 3. Backend API 🚀 (v4.0 Phase 1)

#### FastAPI Server

- **File**: `backend/app.py`
- **Port**: 8001
- **Framework**: FastAPI v0.104+
- **Version**: 4.0 (Phase 1)

#### Core Endpoints

##### 🔍 `/analyze` - Query Analysis (NEW)

**Method**: GET

Analyzes a query to detect intent, genres, and entities without performing full recommendation.

**Parameters**:

```
query (string, required): The query to analyze
```

**Response**:

```json
{
  "query": "medical drama",
  "intent": "GENRE_BROWSE",
  "entities": {
    "genres": ["Medical"],
    "actors": [],
    "years": [],
    "emotions": []
  },
  "confidence": 0.85
}
```

**Use Cases**:

- Quick genre detection for auto-filtering
- Intent understanding for UI adjustments
- Query validation before search

---

##### 🎯 `/recommend` - Get Drama Recommendations

**Method**: GET

Main recommendation endpoint with advanced filters, sorting, and Phase 1 intelligence.

**Parameters**:

```
title (string, required): Drama title or user query
top_n (int, default=5): Number of recommendations
genre (string, optional): Genre filter (auto-detected if not provided)
director (string, optional): Director filter
publisher (string, optional): Publisher/network filter
rating_value (float, optional): Minimum rating (0-10)
rating_count (float, optional): Minimum number of ratings
keywords (string, optional): Keywords filter
screenwriters (string, optional): Screenwriters filter
sort_by (string, optional): Sort field (rating_value, popularity, episodes, etc.)
sort_order (string, default="desc"): Sort order (asc/desc)
similar_to (string, optional): Find dramas similar to this title
user_id (string, optional): User ID for analytics
session_id (string, optional): Session ID for analytics
```

**Response**:

```json
{
  "query": {
    "Title": "medical drama",
    "expanded": "medical drama doctor hospital healthcare surgery"
  },
  "analysis": {
    "intent": "GENRE_BROWSE",
    "dynamic_alpha": 0.35,
    "confidence": 0.85
  },
  "filters": {
    "genre": "Medical",
    "rating_value": null
  },
  "recommendations": [
    {
      "Title": "Hospital Playlist",
      "Genre": "Medical, Life, Friendship",
      "Description": "...",
      "rating_value": 8.9,
      "episodes": 12,
      "Cast": "Jo Jung-suk, Yoo Yeon-seok",
      "Director": "Shin Won-ho"
    }
  ]
}
```

**Features**:

- Auto-genre detection from query
- Dynamic algorithm weighting
- Query expansion with synonyms
- Comprehensive filtering options
- Analytics tracking

---

##### 📊 Analytics Endpoints (NEW)

**`POST /analytics/interaction`** - Log User Interactions

```json
{
  "user_id": "user123",
  "drama_title": "Hospital Playlist",
  "interaction_type": "click|watchlist_add|watched",
  "search_id": "search_abc123",
  "position": 1,
  "session_id": "session_xyz"
}
```

**`GET /analytics/popular`** - Get Popular Dramas

- Query params: `days` (default=7), `limit` (default=20)
- Returns most clicked/watched dramas

**`GET /analytics/trending-searches`** - Get Trending Searches

- Query params: `days` (default=7), `limit` (default=20)
- Returns most popular search queries

**`GET /analytics/summary`** - Get Analytics Summary

- Query params: `days` (default=7)
- Returns: total searches, interactions, click-through rate, unique users

**`GET /analytics/user-stats/{user_id}`** - Get User Statistics

- Returns user's viewing history, watchlist, preferences

**CORS Features**:

- CORS enabled for frontend integration
- Fast response times with FAISS indexing
- Detailed metadata in responses

### 4. Frontend UI 🎨 (Streamlit)

#### Streamlit Application

- **File**: `frontend/streamlit_app.py`
- **Port**: 8501
- **Framework**: Streamlit v1.28+

#### Features

**5 Interactive Tabs:**

1. **🔍 Smart Search**

   - Natural language search with auto-genre detection
   - Quick search buttons for popular genres
   - Advanced filters sidebar (genre, director, rating, etc.)
   - Real-time recommendations
   - Clickable drama cards with detailed information
   - Active filters display

2. **� My Profile**

   - Personal watchlist management
   - Viewing history tracking
   - Remove items from watchlist
   - Statistics dashboard

3. **📊 Statistics**

   - Popular dramas widget
   - Trending searches
   - Visual analytics

4. **📈 Analytics**

   - User engagement metrics
   - Click-through rates
   - Search patterns
   - Recommendation effectiveness

5. **ℹ️ How It Works**
   - System architecture explanation
   - Feature documentation
   - Usage guide

**UI Features:**

- Responsive design
- Loading animations
- Error handling with user-friendly messages
- Session persistence
- Color-coded genre tags
- Rating displays with stars

## 📁 Project Structure

```
SeoulMate/
├── backend/
│   ├── app.py                                # FastAPI server (v4.0 Phase 1)
│   ├── query_analyzer.py                     # Query intelligence system (NEW)
│   ├── analytics.py                          # Analytics tracking (NEW)
│   ├── interactions.jsonl                    # User interaction logs (NEW)
│   ├── search_log.jsonl                      # Search history logs (NEW)
│   └── user_stats/                           # User statistics (NEW)
│       └── {user_id}.json
├── frontend/
│   └── streamlit_app.py                      # Streamlit UI (5 tabs)
├── data_scrapper/
│   ├── wiki_scrapper_playwright.py           # Wikipedia scraper
│   ├── DramaList_Scrapper/
│   │   ├── scrapper.py                       # Main MyDramaList scraper
│   │   ├── dramas_html/                      # Downloaded HTML files (10K+)
│   │   └── dramalist_all_dramas.csv          # Scraped data output
│   └── kdrama_dataset_detailed_v8_playwright.csv  # Final dataset
├── training/
│   ├── build_index.py                        # FAISS index builder
│   ├── faiss_index/
│   │   ├── index.faiss                       # Vector index
│   │   └── meta.pkl                          # Drama metadata (1922 dramas)
│   └── models/
│       ├── sbert-finetuned-full/             # Fine-tuned embedding model
│       └── cross-enc-excellent/              # Fine-tuned reranker
├── tests/                                     # Test files (NEW)
│   ├── test_genre_detection.py
│   ├── test_filter.py
│   └── test_complete_flow.py
├── docs/                                      # Documentation
│   ├── PHASE1_COMPLETE.md
│   ├── PHASE1_QUICKSTART.md
│   └── GENRE_FILTER_FIX.md
└── README.md                                  # This file
```

## 🚀 Getting Started

### Prerequisites

```bash
# Backend dependencies
pip install fastapi uvicorn pydantic
pip install sentence-transformers faiss-cpu
pip install rank-bm25 rapidfuzz thefuzz
pip install python-multipart

# Frontend dependencies
pip install streamlit requests

# Data scraping dependencies
pip install beautifulsoup4 lxml
pip install playwright pandas tqdm
```

### Quick Start (Phase 1)

**1. Start the Backend:**

```bash
cd backend
python app.py
# Server runs at http://127.0.0.1:8001
```

**2. Start the Frontend:**

```bash
cd frontend
streamlit run streamlit_app.py
# UI opens at http://localhost:8501
```

**3. Start Using SeoulMate:**

- Open browser to `http://localhost:8501`
- Try natural language searches:
  - "medical drama"
  - "show me historical dramas with romance"
  - "funny romantic comedy"
  - "dramas like Crash Landing on You"
- Watch as genres are auto-detected!
- Use filters for advanced search
- Build your watchlist in My Profile

### Running the Scraper (Optional)

```bash
# Scrape MyDramaList data
cd scrapers/DramaList_Scrapper
python scrapper.py
```

## 🔧 Configuration

### Backend Configuration (`backend/app.py`)

```python
# Model paths
MODEL_DIR = r"D:\Projects\SeoulMate\training\models"
INDEX_DIR = r"D:\Projects\SeoulMate\training\faiss_index"
CROSS_ENCODER_MODEL = r"D:\Projects\SeoulMate\training\models\cross-enc-excellent"

# Server settings
HOST = "127.0.0.1"
PORT = 8001
RELOAD = True  # Auto-reload on code changes
```

### Frontend Configuration (`frontend/streamlit_app.py`)

```python
# API endpoint
API_URL = "http://127.0.0.1:8001"

# UI settings
DEFAULT_TOP_N = 10  # Number of recommendations per search
```

### Query Analyzer Settings (`backend/query_analyzer.py`)

- **10 Intent Types**: Genre, Actor, Mood, Time, Rating, Similar, Binge, Award, Emotional, Exploratory
- **25+ K-drama Synonyms**: romcom, sageuk, chaebol, makjang, etc.
- **Dynamic Alpha Range**: 0.35-0.95 based on intent
- **Confidence Scoring**: Pattern-based with fallback to 0.7

## 📊 Data Pipeline (Phase 1)

```
Wikipedia + MyDramaList
        ↓
   HTML Scraping (Playwright/lxml)
        ↓
   Data Extraction & Cleaning
        ↓
   CSV Dataset (1922 dramas)
        ↓
   Fine-tuning (Optional)
        ├── Sentence Transformers (SBERT)
        └── Cross-Encoder Reranker
        ↓
   Embedding Generation
        ↓
   FAISS Index Creation
        ↓
   Query Intelligence Layer (Phase 1)
        ├── Intent Detection
        ├── Genre Auto-Detection
        ├── Query Expansion
        └── Dynamic Weighting
        ↓
   Hybrid Search Engine
        ├── Semantic Search (FAISS)
        ├── Lexical Search (BM25Plus)
        └── Cross-Encoder Reranking
        ↓
   Analytics & Learning (Phase 1)
        ├── Click Tracking
        ├── User Preferences
        └── Popular/Trending Analysis
        ↓
   FastAPI REST API + Streamlit UI
```

## 🎨 Features

### ✅ Phase 1 Complete (Query Intelligence & Analytics)

**Query Understanding:**

- ✅ **10 Intent Types**: Auto-detects genre, actor, mood, time-based, rating, exploratory, similar, binge, award, emotional queries
- ✅ **Auto-Genre Detection**: "medical drama" → automatically applies Medical genre filter
- ✅ **Query Expansion**: Enriches searches with 25+ K-drama specific synonyms
- ✅ **Dynamic Algorithm Weighting**: Adjusts semantic vs. lexical balance (alpha 0.35-0.95) based on query intent
- ✅ **Confidence Scoring**: Pattern-based confidence with intelligent fallbacks

**User Analytics:**

- ✅ **Click Tracking**: Records drama clicks with position and search context
- ✅ **User Profiles**: Personal watchlist and viewing history
- ✅ **Popular Dramas**: Real-time popularity based on user interactions
- ✅ **Trending Searches**: Tracks most common search queries
- ✅ **Analytics Dashboard**: CTR, engagement metrics, user statistics
- ✅ **Session Management**: Persistent user sessions across visits

**Frontend:**

- ✅ **5-Tab Interface**: Smart Search, My Profile, Statistics, Analytics, How It Works
- ✅ **Natural Language Search**: Type queries like "funny romantic comedy"
- ✅ **Quick Search Buttons**: One-click genre browsing
- ✅ **Advanced Filters**: 10+ filter options (genre, director, rating, etc.)
- ✅ **Interactive Drama Cards**: Click for details, add to watchlist
- ✅ **Real-time Feedback**: Loading states, success/error messages

### 🔄 Original Features (Enhanced in Phase 1)

**Data Collection:**

- ✅ Multi-source scraping (Wikipedia + MyDramaList)
- ✅ Multithreaded processing for speed
- ✅ Comprehensive metadata extraction (10,000+ dramas → 1922 curated)
- ✅ Error handling and retry logic
- ✅ Progress tracking with tqdm

**Recommendation System:**

- ✅ Semantic understanding of queries (FAISS + fine-tuned SBERT)
- ✅ Keyword-based search (BM25Plus)
- ✅ Intelligent reranking (fine-tuned Cross-Encoder)
- ✅ Typo tolerance (Fuzzy matching)
- ✅ Multilingual support (Korean & English)
- ✅ Fast retrieval (< 1 second response time)

**API:**

- ✅ RESTful API design with FastAPI
- ✅ CORS support for frontend integration
- ✅ JSON responses with rich metadata
- ✅ Comprehensive filtering and sorting
- ✅ Analytics endpoints
- ✅ Auto-generated API documentation (/docs)

## 🔮 Roadmap

### ✅ Phase 1: Query Intelligence & Analytics (COMPLETE)

- ✅ Intent detection system
- ✅ Auto-genre detection
- ✅ Query expansion with synonyms
- ✅ Dynamic algorithm weighting
- ✅ Click tracking & analytics
- ✅ User profiles & watchlists
- ✅ Streamlit frontend with 5 tabs

### 🚀 Phase 2: Personalization (NEXT)

- [ ] User preference learning from interactions
- [ ] Personalized recommendation weights
- [ ] "Because you watched X" recommendations
- [ ] User taste profile generation
- [ ] Collaborative filtering integration
- [ ] Social features (share watchlists)

### 🔄 Phase 3: Advanced Features

- [ ] Real-time data updates from sources
- [ ] User ratings and reviews
- [ ] Watch history timeline
- [ ] Recommendation explanations ("Why this?")
- [ ] Multi-user accounts
- [ ] Email notifications for new dramas
- [ ] Mobile-responsive design

### 🌐 Phase 4: Production & Scale

- [ ] Docker containerization
- [ ] Database migration (PostgreSQL)
- [ ] Redis caching layer
- [ ] API rate limiting
- [ ] User authentication (JWT)
- [ ] Deployment to cloud (AWS/GCP)
- [ ] CDN for images
- [ ] Monitoring & logging (Prometheus/Grafana)

### 📱 Future Considerations

- [ ] Mobile app (React Native / Flutter)
- [ ] Browser extension
- [ ] Integration with streaming platforms
- [ ] Community features (forums, discussions)
- [ ] Advanced analytics dashboard
- [ ] A/B testing framework
- [ ] Multi-language UI support

## � Documentation

- **[PHASE1_COMPLETE.md](docs/PHASE1_COMPLETE.md)**: Complete Phase 1 feature documentation
- **[PHASE1_QUICKSTART.md](docs/PHASE1_QUICKSTART.md)**: Quick start guide for Phase 1 features
- **[GENRE_FILTER_FIX.md](docs/GENRE_FILTER_FIX.md)**: Technical details on genre auto-detection
- **[/docs API](http://127.0.0.1:8001/docs)**: Interactive API documentation (when backend is running)

## 🧪 Testing

```bash
# Run all tests
cd tests
python test_genre_detection.py    # Test query analyzer
python test_filter.py              # Test backend filtering
python test_complete_flow.py       # Test end-to-end flow
```

## 🎯 Example Usage

### Natural Language Queries

```python
# Medical dramas
"medical drama"  → Auto-detects Medical genre
"show me doctor kdramas" → Auto-detects Medical genre

# Historical dramas
"historical drama" → Auto-detects Historical genre
"sageuk" → Auto-detects Historical genre

# Mood-based
"funny romantic comedy" → Detects Romance + Comedy, high semantic weight
"sad emotional drama" → Detects emotional intent

# Actor-based
"dramas with Park Seo-joon" → Balanced semantic/keyword search

# Similar content
"shows like Crash Landing on You" → Similar drama search
```

### API Examples

```bash
# Analyze a query
curl "http://127.0.0.1:8001/analyze?query=medical+drama"

# Get recommendations with auto-genre detection
curl "http://127.0.0.1:8001/recommend?title=medical+drama&top_n=10&user_id=user123"

# Get popular dramas
curl "http://127.0.0.1:8001/analytics/popular?days=7&limit=20"

# Get user statistics
curl "http://127.0.0.1:8001/analytics/user-stats/user123"
```

## 🏆 Performance Metrics

- **Search Speed**: < 1 second average response time
- **Dataset Size**: 1,922 curated K-dramas
- **Genre Detection Accuracy**: ~85% confidence
- **Intent Classification**: 10 types with pattern matching
- **Query Expansion**: 25+ K-drama specific synonyms
- **User Sessions**: Persistent across browser sessions

## �📝 License

This project is for educational and personal use.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

### Development Guidelines

1. Follow PEP 8 style guide for Python code
2. Add tests for new features in the `tests/` folder
3. Update documentation when adding features
4. Use meaningful commit messages
5. Test locally before submitting PR

## 📧 Contact

For questions or suggestions, please open an issue in the repository.

---

## 🙏 Acknowledgments

- **MyDramaList**: For comprehensive K-drama data
- **Wikipedia**: For additional drama information
- **Sentence Transformers**: For semantic search capabilities
- **FAISS**: For efficient vector similarity search
- **FastAPI**: For modern, fast web framework
- **Streamlit**: For rapid UI development

---

**Built with ❤️ for K-Drama enthusiasts**

_Last Updated: November 2025 - Phase 1 Complete_
