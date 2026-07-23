# 🚀 Phase 2: Personalization - Implementation Plan

> **Goal**: Transform SeoulMate from a smart search engine into a personalized recommendation system that learns from each user's preferences and viewing habits.

## 📋 Overview

**Timeline**: 2-3 weeks  
**Status**: Planning → Implementation  
**Prerequisites**: ✅ Phase 1 Complete (Query Intelligence & Analytics)

---

## 🎯 Phase 2 Objectives

### Primary Goals:

1. **Learn from user behavior** - Track and analyze what users watch, click, and add to watchlist
2. **Build user profiles** - Create comprehensive preference profiles for each user
3. **Personalize recommendations** - Adjust results based on individual preferences
4. **Explain recommendations** - Show WHY each drama was recommended
5. **Create personalized sections** - "For You", "Because You Watched X", "Continue Watching"

### Success Metrics:

- Users see different recommendations based on their history
- Recommendation explanations are accurate and helpful
- Click-through rate increases by 20%+
- Users return more frequently (session count)

---

## 🏗️ Architecture Design

### Current Flow (Phase 1):

```
User Query → Query Analysis → Search → Results (Same for Everyone)
```

### Phase 2 Flow:

```
User Query → Query Analysis → User Profile → Personalized Search →
Personalized Reranking → Results (Unique per User) + Explanations
```

### New Components:

```
┌─────────────────────────────────────────────────────────────┐
│                   USER PROFILE SYSTEM                        │
│  • Preference Learning (genres, actors, themes)             │
│  • Viewing History Tracking                                 │
│  • Taste Profile Generation                                 │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│              PERSONALIZATION ENGINE                          │
│  • User-Specific Weighting                                  │
│  • History-Based Boosting                                   │
│  • Similar-to-Watched Recommendations                       │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│              EXPLANATION GENERATOR                           │
│  • "Because you watched X"                                  │
│  • "Matches your interest in Medical dramas"               │
│  • "Features your favorite actor Park Seo-joon"            │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 Implementation Steps

### Step 1: User Preference Learning System (Week 1)

**File**: `backend/user_profile.py` (NEW)

**Features**:

1. **Genre Preferences**

   - Track genre frequency in clicks, watchlist, views
   - Calculate preference scores (0-1) for each genre
   - Update scores with each interaction

2. **Actor Preferences**

   - Track actor frequency in watched dramas
   - Build favorite actors list
   - Weight by rating (if available) and completion

3. **Theme Preferences**

   - Track keywords/themes (romantic, sad, funny, action)
   - Extract from drama descriptions
   - Build theme preference vector

4. **Rating Patterns**
   - Track average rating given
   - Track rating variance (picky vs. lenient)
   - Identify rating biases (e.g., always rates romance higher)

**Data Structure**:

```python
{
  "user_id": "user123",
  "preferences": {
    "genres": {
      "Medical": 0.85,      # High preference
      "Romance": 0.72,
      "Historical": 0.45,
      "Thriller": 0.15      # Low preference
    },
    "actors": {
      "Park Seo-joon": 0.92,
      "IU": 0.88,
      "Kim Soo-hyun": 0.76
    },
    "themes": {
      "emotional": 0.78,
      "funny": 0.65,
      "action": 0.32
    },
    "avg_rating": 4.2,
    "total_watched": 45,
    "total_clicks": 120,
    "watchlist_size": 15
  },
  "last_updated": "2025-11-10T10:30:00"
}
```

---

### Step 2: Personalized Weighting (Week 1)

**File**: Update `backend/app.py` `recommend()` function

**Features**:

1. **Genre Boosting**

   - Boost scores for dramas matching user's favorite genres
   - Formula: `score *= (1 + genre_preference * 0.5)`

2. **Actor Boosting**

   - Boost scores for dramas with favorite actors
   - Formula: `score *= (1 + actor_preference * 0.3)`

3. **Theme Matching**

   - Boost based on theme alignment
   - Use cosine similarity between user theme vector and drama themes

4. **User-Specific Alpha**
   - Adjust semantic vs. lexical weight per user
   - Users who click diverse genres → higher semantic (explore)
   - Users who stick to favorites → higher lexical (exploit)

**Example**:

```python
def personalize_scores(results, user_profile):
    for drama in results:
        score = drama['score']

        # Genre boost
        for genre in drama['genres']:
            if genre in user_profile['preferences']['genres']:
                boost = user_profile['preferences']['genres'][genre]
                score *= (1 + boost * 0.5)

        # Actor boost
        for actor in drama['cast']:
            if actor in user_profile['preferences']['actors']:
                boost = user_profile['preferences']['actors'][actor]
                score *= (1 + boost * 0.3)

        drama['personalized_score'] = score

    return sorted(results, key=lambda x: x['personalized_score'], reverse=True)
```

---

### Step 3: "Because You Watched" Feature (Week 2)

**File**: `backend/similarity_recommender.py` (NEW)

**Features**:

1. **Watch History Analysis**

   - Get user's last 10 watched dramas
   - Extract common patterns (genres, actors, themes)

2. **Similar Drama Discovery**

   - For each watched drama, find 5 most similar
   - Use FAISS semantic similarity
   - Filter out already watched

3. **Recommendation Generation**
   - Create "Because you watched X" sections
   - Group by similarity reason (genre, actor, theme)

**API Endpoint**: `GET /recommend/based-on-history`

**Response**:

```json
{
  "sections": [
    {
      "title": "Because you watched Hospital Playlist",
      "reason": "Similar medical dramas",
      "dramas": [
        { "title": "Doctor John", "similarity": 0.92 },
        { "title": "Good Doctor", "similarity": 0.88 }
      ]
    },
    {
      "title": "More with IU",
      "reason": "Features your favorite actress",
      "dramas": [
        { "title": "Hotel Del Luna", "similarity": 0.95 },
        { "title": "My Mister", "similarity": 0.91 }
      ]
    }
  ]
}
```

---

### Step 4: User Taste Profile (Week 2)

**File**: `backend/taste_profile.py` (NEW)

**Features**:

1. **Profile Generation**

   - Aggregate all user interactions
   - Calculate comprehensive preference vectors
   - Identify user "persona" (e.g., "Romance Enthusiast", "Thriller Seeker")

2. **Dynamic Updating**

   - Update profile after each interaction
   - Use exponential decay for old preferences
   - Recent interactions weighted higher

3. **Profile Visualization**
   - Generate charts/graphs of preferences
   - Show top genres, actors, themes
   - Display in frontend profile tab

**Data Structure**:

```python
{
  "user_id": "user123",
  "persona": "Medical Drama Enthusiast",
  "top_genres": ["Medical", "Romance", "Life"],
  "top_actors": ["Jo Jung-suk", "IU", "Park Seo-joon"],
  "top_themes": ["emotional", "heartwarming", "realistic"],
  "viewing_patterns": {
    "preferred_episode_count": "16 episodes",
    "preferred_year": "2020-2024",
    "binge_watcher": true,
    "rating_style": "generous"
  }
}
```

---

### Step 5: Recommendation Explanations (Week 2)

**File**: `backend/explainer.py` (NEW)

**Features**:

1. **Explanation Types**

   - Genre Match: "Matches your interest in Medical dramas (85% match)"
   - Actor Match: "Features Park Seo-joon (your top actor)"
   - Similar: "Similar to Hospital Playlist which you rated 5/5"
   - Popular: "Trending in Medical genre (1000+ watchers)"
   - Highly Rated: "Top-rated (8.9/10 from 5000 users)"

2. **Multi-Reason Explanations**

   - Combine multiple reasons
   - Prioritize by strength
   - Example: "Medical drama (your #1 genre) with IU (your #2 actress)"

3. **Confidence Scores**
   - Show how confident the system is
   - Use for UI display (strong/medium/weak match)

**API Response**:

```json
{
  "title": "Hospital Playlist",
  "score": 0.95,
  "explanations": [
    {
      "type": "genre_match",
      "text": "Matches your interest in Medical dramas",
      "confidence": 0.85
    },
    {
      "type": "similar_to",
      "text": "Similar to Good Doctor which you rated 5/5",
      "confidence": 0.78
    },
    {
      "type": "actor_match",
      "text": "Features Jo Jung-suk",
      "confidence": 0.65
    }
  ]
}
```

---

### Step 6: Personalized Homepage (Week 3)

**File**: Update `frontend/streamlit_app.py`

**New Sections**:

1. **For You** (Top of page)

   - Top 5 personalized recommendations
   - Based on complete user profile
   - Auto-refreshes based on new interactions

2. **Continue Watching**

   - Shows incomplete dramas from watchlist
   - Sorted by recency
   - Progress indicator

3. **Because You Watched X** (Carousels)

   - Multiple sections based on watch history
   - Each section shows 5 similar dramas
   - Swipeable/scrollable

4. **Trending in Your Genres**

   - Popular dramas in user's favorite genres
   - Real-time based on all user data

5. **Explore New Genres**
   - Recommendations from genres user hasn't tried
   - Encourages exploration
   - Lower weight, occasional refresh

**UI Layout**:

```
┌─────────────────────────────────────────┐
│         🎯 For You (Top Picks)          │
│  [Drama1] [Drama2] [Drama3] [Drama4]   │
└─────────────────────────────────────────┘
┌─────────────────────────────────────────┐
│      ▶️ Continue Watching (Progress)    │
│  [Drama5] [Drama6] [Drama7]             │
└─────────────────────────────────────────┘
┌─────────────────────────────────────────┐
│   💫 Because You Watched Hospital Playlist │
│  [Drama8] [Drama9] [Drama10]            │
└─────────────────────────────────────────┘
┌─────────────────────────────────────────┐
│   🔥 Trending in Medical Dramas         │
│  [Drama11] [Drama12] [Drama13]          │
└─────────────────────────────────────────┘
```

---

## 🔧 Technical Implementation Details

### Files to Create:

1. `backend/user_profile.py` - User preference learning
2. `backend/similarity_recommender.py` - Watch-history based recommendations
3. `backend/taste_profile.py` - Comprehensive profile generation
4. `backend/explainer.py` - Recommendation explanations
5. `tests/test_personalization.py` - Phase 2 tests

### Files to Modify:

1. `backend/app.py` - Add personalization to recommend()
2. `backend/analytics.py` - Enhanced tracking for preferences
3. `frontend/streamlit_app.py` - New personalized homepage

### New API Endpoints:

1. `GET /profile/{user_id}` - Get user profile
2. `GET /recommend/for-you` - Personalized top picks
3. `GET /recommend/based-on-history` - "Because you watched" sections
4. `GET /recommend/continue-watching` - Incomplete dramas
5. `POST /profile/{user_id}/update` - Manual preference updates

---

## 📊 Data Requirements

### User Interaction Data (Already Collecting):

- ✅ Clicks (position, drama, search context)
- ✅ Watchlist additions
- ✅ Viewing marks
- ✅ Search queries

### New Data to Collect:

- [ ] Watch duration (how long user views drama details)
- [ ] Ratings (explicit feedback) - Optional
- [ ] Skip/dismiss actions (negative feedback)
- [ ] Drama completion status

---

## 🧪 Testing Strategy

### Unit Tests:

```python
# Test preference calculation
def test_genre_preference_calculation():
    interactions = [
        {"drama": "Hospital Playlist", "genres": ["Medical", "Life"]},
        {"drama": "Good Doctor", "genres": ["Medical"]},
        {"drama": "Crash Landing on You", "genres": ["Romance"]}
    ]
    prefs = calculate_genre_preferences(interactions)
    assert prefs["Medical"] > prefs["Romance"]

# Test personalized scoring
def test_personalized_scoring():
    user_profile = {"preferences": {"genres": {"Medical": 0.9}}}
    drama = {"title": "Hospital Playlist", "genres": ["Medical"]}
    score = calculate_personalized_score(drama, user_profile)
    assert score > calculate_base_score(drama)
```

### Integration Tests:

- User with Medical preference gets medical dramas boosted
- "Because you watched" returns similar dramas
- Explanations are accurate and relevant
- Profile updates after interactions

---

## 🎯 Success Criteria

### Phase 2 is COMPLETE when:

- ✅ User profiles are automatically generated from interactions
- ✅ Recommendations are personalized based on profiles
- ✅ "Because you watched X" section works
- ✅ Explanations show WHY dramas were recommended
- ✅ Personalized homepage with 5 sections
- ✅ Different users see different recommendations
- ✅ Tests pass for all personalization features

### Metrics to Track:

- Click-through rate improvement
- Average session duration increase
- Return user rate
- Recommendations diversity
- Explanation accuracy (user surveys)

---

## 🚀 Getting Started

**Step 1**: Read this plan thoroughly  
**Step 2**: Start with `user_profile.py` - Build preference learning  
**Step 3**: Integrate into `app.py` - Add personalization  
**Step 4**: Build "Because you watched" feature  
**Step 5**: Add explanations  
**Step 6**: Update frontend with personalized sections  
**Step 7**: Test thoroughly  
**Step 8**: Deploy and monitor

---

## 📚 Resources

- **Surprise Library**: Collaborative filtering basics
- **LightFM**: Hybrid recommendations
- **TensorFlow Recommenders**: Advanced models (Phase 3)
- **RecBole**: Recommendation system framework

---

**Let's build amazing personalization! 🚀**

_Phase 2 Implementation - November 2025_
