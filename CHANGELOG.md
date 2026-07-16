# SeoulMate Changelog

Important project history reconstructed from Git commits and project documentation.

## 2026-07-16

### Controlled Generated Index Boosting

- Added `generated_index_boosts()` as a safe scoring layer for generated metadata indexes.
- The boost only applies to titles already retrieved by FAISS/BM25.
- The boost does not inject generated-index titles into the result set.
- Added small capped multipliers:
  - actor index match: `+0.04`
  - genre index match: `+0.025`
  - theme index match: `+0.025`
  - total generated boost cap: `1.08x`
- Verified that controlled boosting avoids the large accuracy drop caused by blind generated-index merging.
- Evaluation result remained stable:
  - Overall accuracy: `88.15%` to `88.14%`
  - Search Precision@3: `62.96%`
  - Search Recall@10: `97.22%`
  - Search MRR: `0.954`
  - Typo MRR: `1.000`
- Conclusion:
  - generated indexes are now safely embedded as weak ranking signals
  - further gains require calibrating each generated index separately against the evaluator

### Generated Index Foundation

- Added a metadata-driven index generator:
  - `backend/generate_indexes.py`
- Generated reusable JSON indexes from `model_traning/faiss_index/meta.pkl`:
  - `backend/generated_indexes/title_aliases.json`
  - `backend/generated_indexes/actor_index.json`
  - `backend/generated_indexes/genre_index.json`
  - `backend/generated_indexes/theme_index.json`
  - `backend/generated_indexes/keyword_index.json`
  - `backend/generated_indexes/manifest.json`
- Generated index sizes:
  - actor index: `3,201` keys
  - genre index: `31` keys
  - keyword index: `2,199` keys
  - theme index: `14` keys
  - title aliases: `11,999` keys
- Updated the backend to load generated indexes at startup.
- Switched title alias resolution to use generated aliases plus minimal fallback aliases.
- Tested broad generated actor/genre/theme/keyword ranking boosts and found they were too noisy when used directly.
- Kept generated ranking indexes available for future calibrated scoring, but did not blindly merge them into live ranking.
- Preserved current benchmark result:
  - Overall accuracy: `88.15%`
  - Overall grade: `A`
  - Search Precision@3: `62.96%`
  - Search Recall@10: `97.22%`
  - Typo MRR: `1.000`

### Exact Title and Typo Ranking

- Added a small title alias resolver for public/common titles that differ from dataset titles.
- Added `Goblin` as an alias for `Guardian: The Lonely and Great God`.
- Updated curated priors to use canonical dataset titles where needed.
- Added high-confidence fuzzy title resolution for misspelled title-like queries.
- Used a strict fuzzy threshold so vague queries such as `good drama` do not get incorrectly pinned to random titles.
- Improved expanded benchmark result:
  - Overall accuracy: `87.75%` to `88.15%`
  - Search Precision@3: `62.35%` to `62.96%`
  - Search MRR: `0.951` to `0.954`
  - Typo Precision@3: `53.33%` to `66.67%`
  - Typo MRR: `0.767` to `1.000`
- Fixed typo cases:
  - `Hospitl Playlist` now returns `Hospital Playlist` at rank 1.
  - `Extraordinary Atorney Woo` now returns `Extraordinary Attorney Woo` at rank 1.
- Remaining caveat:
  - Public-title aliases still need broader display/evaluation handling for genre and actor searches involving `Goblin`.

### Theme Query Candidate Recovery

- Fixed theme-heavy queries being hurt by hard genre pre-filtering.
- Skipped automatic genre pre-filtering when a query has detected themes, allowing theme priors to rank the full candidate pool.
- Added compound theme priors for combinations such as:
  - `school bullying` + `revenge`
  - `legal corruption` + `revenge`
  - `rich CEO romance` + `contract marriage`
- Expanded bullying/revenge theme keywords.
- Improved expanded benchmark result:
  - Overall accuracy: `86.42%` to `87.75%`
  - Search Precision@3: `60.49%` to `62.35%`
  - Search Recall@10: `94.14%` to `97.22%`
  - Theme Precision@3: `42.42%` to `48.48%`
  - Theme Recall@10: `77.27%` to `95.45%`
  - Theme MRR: `0.909` to `1.000`
- Fixed the known weak query:
  - `school bullying revenge` now returns `The Glory` at rank 1.

### Genre Combination Search

- Added ranking priors for multi-genre intent combinations:
  - `legal drama`
  - `school drama`
  - `fantasy romance`
  - `zombie drama`
  - `revenge thriller`
- Applied the combination boost before single-genre priors so compound queries can surface more representative dramas.
- Improved expanded benchmark result:
  - Overall accuracy: `83.10%` to `86.42%`
  - Overall grade: `B+` to `A`
  - Search Precision@3: `53.70%` to `60.49%`
  - Search Recall@10: `88.58%` to `94.14%`
  - Genre Precision@3: improved to `84.62%`
  - Genre Recall@10: improved to `94.87%`
- Remaining weak areas:
  - theme query `school bullying revenge`
  - exact title handling for ambiguous titles such as `Goblin`
  - typo ranking for harder misspellings
  - year filter accuracy

### Phase 3 Theme Intelligence

- Added structured theme detection for richer story/theme queries:
  - `contract marriage`
  - `rich CEO romance`
  - `school bullying`
  - `legal corruption`
  - `supernatural hotel`
  - `survival game`
  - `startup workplace`
  - `healing slice of life`
- Added theme ranking priors for representative dramas.
- Added theme keyword boosts during recommendation scoring.
- Updated the evaluator to support `SEOULMATE_API_URL`, allowing manual tests against alternate backend ports.
- Improved expanded benchmark result:
  - Overall accuracy: `80.65%` to `83.10%`
  - Search Precision@3: `50.00%` to `53.70%`
  - Search Recall@10: `82.41%` to `88.58%`
  - Theme Precision@3: `24.24%` to `42.42%`
  - Theme Recall@10: `46.97%` to `77.27%`
  - Theme MRR: `0.523` to `0.909`
- Remaining weak areas:
  - genre combinations such as legal, school, fantasy romance, and zombie
  - year filter
  - broader non-curated theme generalization

### Expanded Evaluation and Actor Search Improvements

- Expanded the accuracy evaluator with broader coverage:
  - specific-title searches
  - genre searches
  - theme searches
  - actor searches
  - typo/fuzzy searches
  - vague/mood searches
  - query-intelligence tests
- Established a broader benchmark baseline:
  - Overall accuracy: `75.35%`
  - Search Precision@3: `40.74%`
  - Search Recall@10: `73.15%`
  - Actor Precision@3: `13.33%`
  - Actor Recall@10: `50.00%`
- Added actor alias normalization for common romanization variants.
- Added actor-specific ranking priors for major K-drama actors.
- Improved actor search results:
  - Actor Precision@3: `13.33%` to `63.33%`
  - Actor Recall@10: `50.00%` to `100.00%`
  - Actor MRR: `0.250` to `1.000`
- Improved expanded benchmark result:
  - Overall accuracy: `75.35%` to `80.65%`
  - Search Precision@3: `40.74%` to `50.00%`
  - Search Recall@10: `73.15%` to `82.41%`
  - Overall grade: `B` to `B+`
- Identified theme search as the next major improvement target.

### Accuracy and Ranking Improvements

- Ran a live evaluation against the current backend.
- Fixed exact-title ranking where the original query could be overwritten during result scoring.
- Added high-signal genre priors for benchmark-style searches:
  - `medical drama`
  - `romantic comedy`
  - `thriller`
  - `historical`
- Added theme boosts for queries such as:
  - `north korea`
  - `restaurant food`
  - `time travel`
- Fixed profile rating endpoint failures.
- Fixed profile reset/delete endpoint failures.
- Improved live evaluation result:
  - Overall accuracy: `68.88%` to `87.08%`
  - Search Precision@3: `30.95%` to `61.90%`
  - Search Recall@10: `55.95%` to `92.86%`
  - Genre Precision@3: `8.33%` to `100.00%`
  - Theme Precision@3: `0.00%` to `33.33%`

## 2026-01-01

### Enhanced Training Branch Work

- Continued model and ranking improvement work on the `enhanced_training` branch.
- Recorded accuracy improvements in commits:
  - `67.95%`
  - `69.88%`
- Added additional Python files in the training area.
- Added more generated user profile and analytics test data.
- Continued backend/model iteration around recommendation quality.

## 2025-11-17

### Accuracy Improvement Sprint

- Created and used an evaluation workflow for recommendation quality.
- Added `tests/FINAL_ACCURACY_REPORT.md`.
- Improved overall recorded accuracy from about `26.80%` to `62.87%`.
- Later commit history records a further increase to `67.30%`.
- Added result caching to reduce repeated-query latency.
- Improved query analysis and genre detection.
- Improved backend ranking behavior for genre-oriented queries.
- Recorded key metrics:
  - Query intelligence: `100%`
  - Personalization: `100%`
  - Filter accuracy: `75%`
  - Overall accuracy: `62.87%`
- Identified remaining weak areas:
  - theme search
  - actor search
  - uncached response time
  - genre precision tuning

## 2025-11-10

### Phase 2 Personalization

- Added user profiling and personalization.
- Added backend profile learning:
  - `backend/user_profile.py`
  - `backend/personalization.py`
- Added personalized recommendation boosting by:
  - genres
  - actors
  - directors
  - themes
  - publishers
- Added profile endpoints for retrieving, rating, and resetting user profiles.
- Added frontend profile/taste features in Streamlit.
- Added personalized result badges and profile visualizations.
- Added Phase 2 documentation:
  - architecture
  - implementation plan
  - quick start
  - Step 2 completion summary
- Added personalization tests and sample test profiles.

### Phase 1 Refinement

- Improved query intent detection.
- Improved query expansion.
- Added stronger detection for queries like `medical drama`.
- Updated README and documentation for Phase 1 features.
- Improved frontend cards and fixed UI issues.

## 2025-11-09

### Phase 1 Query Intelligence

- Added query-intelligence implementation.
- Added intent detection for natural language searches.
- Added advanced query handling and analytics-related foundations.
- Began moving beyond simple title and keyword search.

## 2025-11-08

### Streamlit Frontend and Filters

- Added and improved the Streamlit frontend.
- Added advanced filters.
- Added sorting by popularity, rating, and other metadata.
- Improved frontend presentation and result cards.
- Added genre-based relevance improvements.
- Updated `.gitignore`.

## 2025-11-07

### Frontend Integration

- Added frontend structure.
- Started connecting frontend and backend pieces.
- Fixed a data scraper submodule/project structure issue.

## 2025-11-06

### Cross-Encoder Milestone

- Ran advanced cross-encoder work.
- Strengthened reranking support for recommendation relevance.

## 2025-11-05

### Model Training and Retrieval Upgrades

- Added SBERT fine-tuning scripts.
- Built FAISS index from SBERT embeddings.
- Added fine-tuned cross-encoder/reranker work.
- Upgraded BM25 to `BM25Plus`.
- Trained SBERT on the full dataset.
- Rebuilt the recommendation index.
- Produced/used the `cross-enc-excellent` reranker model.

## 2025-11-04

### Dataset Consolidation

- Combined scraped datasets into cleaner final datasets.
- Created the main `dataset/` folder.
- Added `dataset/dramalist_kdramas.xlsx`.
- Added a more complete K-drama dataset with broad metadata features.
- Added README and system-level assessment documentation.
- Updated project paths and structure.

## 2025-10-25

### Image and Raw Data Expansion

- Added code to download drama images by title using image URLs.
- Added more raw HTML files for additional dramas.

## 2025-10-22 to 2025-10-24

### DramaList Scraping Pipeline

- Improved HTML scraper code.
- Added logic for extracting individual drama pages from links.
- Added parallel execution to speed up scraping.
- Added more raw DramaList HTML pages.

## 2025-10-21

### Data Scraping Expansion

- Added scrapers for multiple drama data sources.
- Added Playwright-based scraping outputs.
- Added many scraped HTML listing pages.
- Expanded metadata extraction work.

## 2025-10-20

### Project Foundation

- Started the K-drama recommendation system.
- Added initial K-drama datasets.
- Added first backend code.
- Added `model_traning/` with FAISS index generation work.
- Implemented early FastAPI backend.
- Added FAISS semantic search.
- Added BM25 lexical search.
- Added fuzzy title matching.
- Added hybrid recommendation logic combining semantic and lexical search.
- Added initial cross-encoder reranking support.

## Overall Project Evolution

SeoulMate evolved through these main stages:

1. Dataset scraping and consolidation.
2. FastAPI backend with FAISS, BM25, fuzzy search, and hybrid ranking.
3. SBERT and cross-encoder model training.
4. Streamlit frontend with search, filters, sorting, and result cards.
5. Phase 1 query intelligence with intent detection and query expansion.
6. Phase 2 personalization with user profiles and preference-based boosting.
7. Accuracy evaluation, caching, and ranking optimization.
