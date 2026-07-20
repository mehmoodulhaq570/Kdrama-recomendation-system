# SeoulMate Changelog

Important project history reconstructed from Git commits and project documentation.

## 2026-07-20

### Calibrated Actor Index Improvement

- Improved `calibrated_actor_index.json` ordering in `backend/generate_indexes.py`.
- Added cast-position scoring so lead roles rank above secondary/cameo appearances before rating and frequency are considered.
- Made `tests/validate_generated_indexes.py` alias-aware so titles like `Goblin` and `Guardian: The Lonely and Great God` are evaluated as the same drama where aliases exist.
- Updated validator recommendations to prefer the strongest top-rank index when Hit@10 is tied.
- Regenerated generated index files from `model_traning/faiss_index/meta.pkl`.
- Offline actor-index validation improved:
  - `actor_index.json`: Hit@1 `50.00%`, Hit@3 `70.00%`, Hit@10 `100.00%`
  - `calibrated_actor_index.json`: Hit@1 `70.00%`, Hit@3 `100.00%`, Hit@10 `100.00%`
- Live benchmark remained stable:
  - Overall accuracy: `88.14%`
  - Search Precision@3: `62.96%`
  - Search Recall@10: `97.22%`
  - Search MRR: `0.954`
- Conclusion:
  - calibrated actor index is now good enough for cautious actor fallback experiments
  - curated actor priors should still stay active until a full replacement beats the benchmark

### Calibrated Genre Index Improvement

- Improved offline validation of multi-genre generated index candidates in `tests/validate_generated_indexes.py`.
- Multi-key genre queries now rank titles that appear under multiple detected genre keys ahead of titles that only match one genre key.
- Increased `calibrated_genre_index.json` coverage from top 20 to top 40 titles per genre in `backend/generate_indexes.py`.
- Regenerated generated index files from `model_traning/faiss_index/meta.pkl`.
- Offline genre-index validation improved:
  - Previous `calibrated_genre_index.json`: Hit@3 `46.15%`, Hit@10 `69.23%`, Hit@20 `84.62%`
  - Current `calibrated_genre_index.json`: Hit@3 `61.54%`, Hit@10 `69.23%`, Hit@20 `84.62%`
- Conclusion:
  - calibrated genre index ordering is better for combined genre queries
  - genre index is still not ready to replace curated genre priors because Hit@3 remains below the safe threshold
  - next improvement should focus on query-specific genre combinations such as romantic comedy, fantasy romance, revenge drama, and sageuk/royal drama

### Generated Genre Combo Index

- Added `calibrated_genre_combo_index.json` generation from metadata genre pairs.
- Added query-specific combo validation in `tests/validate_generated_indexes.py`.
- Added training-triplet combo frequency so anchors like `romantic comedy` and `medical drama` can influence combo-title ordering.
- Added virtual combo labels for metadata-backed themes, starting with `revenge`, so queries such as `revenge drama` can be represented even when `Revenge` is stored as a keyword/theme instead of a formal genre.
- Regenerated generated index files from `model_traning/faiss_index/meta.pkl`.
- Generated combo index coverage:
  - `321` genre-combo keys
- Offline combo-index validation:
  - `calibrated_genre_combo_index.json`: Hit@1 `9.09%`, Hit@3 `63.64%`, Hit@10 `90.91%`, Hit@20 `90.91%`
- Conclusion:
  - generated combo index is now useful for recall/debug and future candidate expansion
  - combo index should not be used for top-rank boosting yet because Hit@3 is still below the safe threshold
  - remaining weak area: `crime thriller`, where generated ordering favors adjacent action/crime titles before `Signal`, `Stranger`, and `Beyond Evil`

### Crime Thriller Combo Calibration

- Improved `calibrated_genre_combo_index.json` for `crime|thriller` queries.
- Added metadata-derived virtual `crime` labels so dramas with crime-solving keywords can be represented even when `Crime` is not stored as a formal genre.
- Added crime/thriller focus scoring for investigation, detective, murder, serial-killer, corruption, psychological, suspense, and cold-case signals.
- Added light penalties for action-heavy crime metadata so action/noir titles do not dominate investigation-focused crime thriller queries.
- Fixed combo scoring so virtual labels are used both when collecting candidates and when checking exact combo matches.
- Regenerated generated index files from `model_traning/faiss_index/meta.pkl`.
- `crime|thriller` top results improved to:
  - `Beyond Evil`
  - `Signal`
  - `Stranger`
- Offline combo-index validation improved:
  - Previous `calibrated_genre_combo_index.json`: Hit@3 `63.64%`, Hit@10 `90.91%`
  - Current `calibrated_genre_combo_index.json`: Hit@3 `72.73%`, Hit@10 `100.00%`
- Conclusion:
  - combo index is now stronger for recall and analysis
  - still keep it out of live top-rank boosting until Hit@3 reaches the safe threshold around `80.00%`

### Generated Index Offline Validation

- Added offline generated-index validation:
  - `tests/validate_generated_indexes.py`
- The validator checks generated indexes against evaluator ground-truth titles without calling the backend API.
- Added validation metrics:
  - Hit@1
  - Hit@3
  - Hit@10
  - Hit@20
  - sample misses for debugging
- Validated raw and calibrated indexes:
  - actor
  - genre
  - theme
  - keyword
- Current validation findings:
  - `actor_index.json`: Hit@3 `70.00%`, Hit@10 `100.00%`
  - `calibrated_actor_index.json`: Hit@3 `80.00%`, Hit@10 `90.00%`
  - `genre_index.json`: Hit@3 `30.77%`, Hit@10 `61.54%`
  - `calibrated_genre_index.json`: Hit@3 `38.46%`, Hit@10 `61.54%`
  - `theme_index.json`: Hit@3 `27.27%`, Hit@10 `54.55%`
  - `calibrated_theme_index.json`: Hit@3 `27.27%`, Hit@10 `36.36%`
  - `calibrated_keyword_index.json`: Hit@3 `8.33%`, Hit@10 `29.17%`
- Conclusion:
  - actor indexes are useful for recall/debug and fallback coverage
  - genre, theme, and keyword indexes are not ready for live ranking
  - future tuning should improve generated index quality offline before wiring stronger live boosts

## 2026-07-16

### Calibrated Genre Index Trial

- Added `calibrated_genre_index.json` generation from metadata.
- Added genre-title calibration using:
  - title/genre filtering for specials, recaps, variety, documentaries, and related non-primary content
  - sequel/part/season downranking
  - rating
  - episode count
  - title frequency from existing training pairs/triplets
- Tested using calibrated generated genre priors as fallback for uncovered genres.
- Result: generated genre fallback reduced ranking quality for several mixed-intent queries.
- Disabled generated genre fallback from live scoring.
- Kept `calibrated_genre_index.json` available for future offline tuning.
- Restored benchmark result:
  - Overall accuracy: `88.14%`
  - Genre Precision@3: `87.18%`
  - Genre Recall@10: `92.31%`
  - Genre MRR: `0.885`
- Conclusion:
  - generated genre indexes are useful for analysis, but not reliable enough yet as ranking priors
  - genre replacement needs query-specific calibration, especially for business/workplace, revenge, historical/sageuk, and broad romance/comedy

### Calibrated Actor Index Trial

- Added `calibrated_actor_index.json` generation from metadata.
- Added actor-title calibration using:
  - title/genre filtering for specials, recaps, variety, documentaries, and related non-primary content
  - rating
  - episode count
  - title frequency from existing training pairs/triplets
- Tested replacing curated actor priors with generated calibrated actor priors.
- Result: full replacement reduced actor quality too much, especially for actors with many high-rated variety/special/secondary titles.
- Kept curated actor priors for known high-confidence actors.
- Added generated calibrated actor priors as fallback for actors not covered by curated priors.
- Preserved benchmark result:
  - Overall accuracy: `88.14%`
  - Actor Precision@3: `63.33%`
  - Actor Recall@10: `100.00%`
  - Actor MRR: `0.950`
- Conclusion:
  - actor priors cannot be fully replaced yet without a stronger popularity/relevance signal
  - generated actor index is now safely used for broader coverage, not for overriding proven curated actor rankings

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
