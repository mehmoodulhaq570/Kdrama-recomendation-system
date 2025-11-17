# SeoulMate Accuracy Improvement Plan

**Current Overall Accuracy: 26.80% (Grade: C)**

---

## 🎯 Priority 1: Fix Query Intelligence (0% → 85%+)

### Issue:

- Genre detection returns empty array `[]`
- Intent classifier misclassifying queries
- "romantic comedy" → actor_based intent (WRONG!)

### Root Cause:

Check `backend/query_analyzer.py`:

- Genre extraction regex/keywords not matching
- Need to check genre list matches dataset genres exactly
- Intent classification logic needs review

### Fix:

```python
# In query_analyzer.py - add comprehensive genre keywords
GENRE_KEYWORDS = {
    "Romance": ["romantic", "romance", "love story", "love"],
    "Comedy": ["comedy", "funny", "humor"],
    "Medical": ["medical", "hospital", "doctor", "surgery"],
    "Thriller": ["thriller", "suspense", "mystery"],
    "Historical": ["historical", "period drama", "joseon", "king"],
    "Action": ["action", "fight", "spy"],
    # ... more genres
}
```

**Expected Impact:** 0% → 85% genre detection

---

## 🎯 Priority 2: Fix Search Algorithm for Genre Queries (0% → 70%+)

### Issue:

- "medical drama" returns "Mama", "Oh My Baby" (keyword match in title)
- Should return "Hospital Playlist", "Doctor Cha", "Good Doctor"
- Semantic search + BM25 not understanding genre context

### Root Cause:

- Query "medical drama" is matching word "drama" in titles
- Not expanding query to include genre metadata
- Need to boost results where Genre field contains "Medical"

### Fix Options:

**Option A: Query Expansion (Recommended)**

```python
# If genre detected, expand query with genre-specific terms
if detected_genres:
    expanded_query = f"{query} {' '.join(detected_genres)}"
    # Also add to filters
    filters["detected_genres"] = detected_genres
```

**Option B: Metadata Boosting**

```python
# In recommend() function, boost scores for genre matches
for result in results:
    if any(genre in result['Genre'] for genre in detected_genres):
        result['score'] *= 1.5  # Genre boost
```

**Expected Impact:** Genre search accuracy 0% → 70%

---

## 🎯 Priority 3: Fix Personalization (0% → 60%+)

### Issue:

- User rated "Hospital Playlist", "Doctor Cha", "Good Doctor" 9.0/10
- Search for "drama" returned 0 medical dramas
- `boost_applied: False`, `average_boost: 1.00x`

### Root Cause:

Check `backend/app.py` in `/recommend` endpoint:

1. Is `user_id` being passed correctly?
2. Is user profile being fetched?
3. Is boost calculation working?
4. Are boosted scores being applied?

### Debug Steps:

```python
# Add logging in recommend() function
print(f"User ID: {user_id}")
print(f"User Profile: {user_profile}")
print(f"Boost factors: {boost_factors}")
print(f"Boosted results count: {len([r for r in results if r.get('boost_multiplier', 1.0) > 1.0])}")
```

### Expected Fix:

- Profile fetch working but boost not applied to scores
- Need to multiply final scores by boost_multiplier

**Expected Impact:** Personalization 0% → 60%

---

## 🎯 Priority 4: Improve Actor Search (0% → 50%+)

### Issue:

- "Hyun Bin" returns "Dok Go Bin Is Updating" (partial name match in title)
- Should return "Crash Landing on You", "Memories of the Alhambra"

### Root Cause:

- Actor names stored as comma-separated string
- BM25 tokenizes "Hyun Bin" → matches "Bin" in titles
- Need exact actor matching or fuzzy matching on Cast field

### Fix:

```python
# Detect actor names in query
if intent == "actor_based":
    # Search specifically in Cast field
    actor_results = search_by_actor(actor_name, dataset)
    # Merge with semantic results
```

**Expected Impact:** Actor search 0% → 50%

---

## 🎯 Priority 5: Optimize Performance (3714ms → <500ms)

### Issue:

- Average response time: 3.7 seconds (way too slow!)
- Should be <500ms for good UX

### Bottlenecks:

1. **Model loading** - Are models loaded once or per request?
2. **FAISS index** - Is index pre-loaded?
3. **Cross-encoder reranking** - How many candidates being reranked?

### Optimizations:

```python
# 1. Load models globally (not per request)
MODEL = SentenceTransformer('model_path')  # At module level

# 2. Limit cross-encoder reranking
cross_encoder_candidates = top_50_results[:30]  # Only rerank top 30

# 3. Cache frequent queries
from functools import lru_cache
@lru_cache(maxsize=1000)
def cached_search(query, top_n):
    ...
```

**Expected Impact:** 3714ms → 400ms

---

## 📊 Expected Improvements:

| Metric                    | Current   | After Fixes   | Target  |
| ------------------------- | --------- | ------------- | ------- |
| **Specific Title Search** | 100% ✅   | 100%          | 100%    |
| **Genre Search**          | 0% ❌     | 70%           | 80%     |
| **Theme Search**          | 0% ❌     | 50%           | 70%     |
| **Actor Search**          | 0% ❌     | 50%           | 60%     |
| **Query Intelligence**    | 0% ❌     | 85%           | 90%     |
| **Personalization**       | 0% ❌     | 60%           | 75%     |
| **Filter Accuracy**       | 75% ⚠️    | 95%           | 95%     |
| **Response Time**         | 3714ms ❌ | 400ms         | <500ms  |
| **Overall Accuracy**      | 26.8% (C) | **75%+ (B+)** | 85% (A) |

---

## 🔧 Implementation Order:

1. **Week 1: Query Intelligence** (Biggest impact)

   - Fix genre detection (Priority 1)
   - Fix query expansion for genre search (Priority 2)
   - Test: Re-run evaluation, should hit 60%+ overall

2. **Week 2: Personalization & Actor Search**

   - Debug personalization boost (Priority 3)
   - Implement actor-specific search (Priority 4)
   - Test: Should hit 70%+ overall

3. **Week 3: Performance & Polish**
   - Optimize model loading (Priority 5)
   - Cache frequent queries
   - Fine-tune boost factors
   - Test: Should hit 75-80% overall

---

## 🎯 Success Criteria:

- ✅ Overall system accuracy **>75%** (Grade B+)
- ✅ Genre search precision **>70%**
- ✅ Personalization effectiveness **>60%**
- ✅ Response time **<500ms**
- ✅ User satisfaction with recommendations

---

## 📝 Next Steps:

1. **Immediate:** Investigate `query_analyzer.py` for genre detection bug
2. **Today:** Add debug logging to personalization code
3. **This Week:** Implement query expansion for genre searches
4. **Test:** Re-run `python tests/evaluate_accuracy.py` after each fix

---

**Note:** The evaluation code itself is **excellent** ✅ - it successfully identified all the real issues in the system. No improvements needed to the evaluation script.
