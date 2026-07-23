# Generated Replacement Audit

Generated: `2026-07-23T12:18:28`
Mode: `generated_genre_soft`

## Baseline Gap

- Curated baseline: P@3 `63.58%`, R@10 `98.46%`, MRR `0.963`
- Generated replacement: P@3 `56.79%`, R@10 `94.14%`, MRR `0.948`

## Failure Types

- `expected_ranked_too_low`: `10`
- `top3_precision_regression`: `10`
- `expected_missing_from_generated_top10`: `6`
- `first_relevant_rank_regression`: `3`
- `noisy_titles_above_expected`: `3`

## Category Impact

- `genre`: `3.000`

## Highest Impact Cases

### school drama (genre)

- Impact: `0.667`
- Labels: `expected_missing_from_generated_top10`, `expected_ranked_too_low`, `top3_precision_regression`, `first_relevant_rank_regression`, `noisy_titles_above_expected`
- Expected: True Beauty, Dream High, Extraordinary You
- Missing top10: Dream High, Extraordinary You
- Ranked too low: none
- Noisy above expected: Seasons of Blossom, The World of My 17
- Curated top5: True Beauty, Dream High, Extraordinary You, School 2017, IN-SEOUL
- Generated top5: Seasons of Blossom, The World of My 17, True Beauty, Sassy Go Go, Love Alarm

### historical (genre)

- Impact: `0.417`
- Labels: `expected_missing_from_generated_top10`, `expected_ranked_too_low`, `top3_precision_regression`
- Expected: Mr. Sunshine, Kingdom, The Red Sleeve
- Missing top10: Kingdom
- Ranked too low: The Red Sleeve
- Noisy above expected: none
- Curated top5: Mr. Sunshine, Kingdom, The Red Sleeve, Empress Ki, The Three Musketeers
- Generated top5: Mr. Sunshine, Alchemy of Souls, Under the Queen's Umbrella, Tale of the Nine-Tailed 1938, Mr. Queen

### sageuk royal drama (genre)

- Impact: `0.417`
- Labels: `expected_missing_from_generated_top10`, `expected_ranked_too_low`, `top3_precision_regression`, `first_relevant_rank_regression`, `noisy_titles_above_expected`
- Expected: The Red Sleeve, Empress Ki, Kingdom
- Missing top10: Empress Ki, Kingdom
- Ranked too low: none
- Noisy above expected: Under the Queen's Umbrella, My Dearest
- Curated top5: Mr. Sunshine, Kingdom, The Red Sleeve, Empress Ki, Bloody Heart
- Generated top5: Under the Queen's Umbrella, My Dearest, The Red Sleeve, Pachinko, My Country: The New Age

### medical drama (genre)

- Impact: `0.267`
- Labels: `expected_missing_from_generated_top10`, `expected_ranked_too_low`, `top3_precision_regression`
- Expected: Hospital Playlist, Doctor Cha, Good Doctor
- Missing top10: Hospital Playlist
- Ranked too low: none
- Noisy above expected: none
- Curated top5: Hospital Playlist, Doctor Cha, Good Doctor, Dr. Romantic, Hospital Ship
- Generated top5: Good Doctor, Doctor Cha, Brain, Dr. Romantic Season 3, Emergency Couple

### doctor hospital drama (genre)

- Impact: `0.267`
- Labels: `expected_missing_from_generated_top10`, `expected_ranked_too_low`, `top3_precision_regression`
- Expected: Hospital Playlist, Doctor Cha, Good Doctor
- Missing top10: Hospital Playlist
- Ranked too low: none
- Noisy above expected: none
- Curated top5: Hospital Playlist, Doctor Cha, Good Doctor, Dr. Romantic, Hospital Ship
- Generated top5: Good Doctor, Doctor Cha, Brain, Dr. Romantic Season 3, Emergency Couple

### office romance (genre)

- Impact: `0.267`
- Labels: `expected_missing_from_generated_top10`, `expected_ranked_too_low`, `top3_precision_regression`
- Expected: Business Proposal, What's Wrong with Secretary Kim, Romance Is a Bonus Book
- Missing top10: Business Proposal
- Ranked too low: Romance Is a Bonus Book
- Noisy above expected: none
- Curated top5: Business Proposal, What's Wrong with Secretary Kim, Strong Woman Do Bong Soon, True Beauty, Agency
- Generated top5: What's Wrong with Secretary Kim, Gaus Electronics, Fated to Love You, Falling for Innocence, Romance Is a Bonus Book

### zombie drama (genre)

- Impact: `0.250`
- Labels: `expected_ranked_too_low`, `top3_precision_regression`, `first_relevant_rank_regression`, `noisy_titles_above_expected`
- Expected: All of Us Are Dead, Kingdom, Happiness
- Missing top10: none
- Ranked too low: Happiness
- Noisy above expected: Sweet Home
- Curated top5: All of Us Are Dead, Kingdom, Happiness, Sweet Home, Squid Game
- Generated top5: Sweet Home, All of Us Are Dead, Kingdom: Ashin of the North, Happiness, Kingdom

### thriller (genre)

- Impact: `0.150`
- Labels: `expected_ranked_too_low`, `top3_precision_regression`
- Expected: Squid Game, Signal, Stranger
- Missing top10: none
- Ranked too low: Signal
- Noisy above expected: none
- Curated top5: Squid Game, Signal, Stranger, Beyond Evil, The Virus
- Generated top5: Stranger, Squid Game, Beyond Evil, Dong Jae, the Good or the Bastard, Voice

### romantic comedy (genre)

- Impact: `0.150`
- Labels: `expected_ranked_too_low`, `top3_precision_regression`
- Expected: Business Proposal, What's Wrong with Secretary Kim, Strong Woman Do Bong Soon
- Missing top10: none
- Ranked too low: What's Wrong with Secretary Kim
- Noisy above expected: none
- Curated top5: Business Proposal, What's Wrong with Secretary Kim, Strong Woman Do Bong Soon, True Beauty, Romance
- Generated top5: Business Proposal, Strong Woman Do Bong Soon, The Secret Life of My Secretary, What's Wrong with Secretary Kim, Love in Contract

### legal drama (genre)

- Impact: `0.150`
- Labels: `expected_ranked_too_low`, `top3_precision_regression`
- Expected: Extraordinary Attorney Woo, Law School, Vincenzo
- Missing top10: none
- Ranked too low: Law School
- Noisy above expected: none
- Curated top5: Extraordinary Attorney Woo, Law School, Vincenzo, Lawless Lawyer, Delayed Justice
- Generated top5: Extraordinary Attorney Woo, Vincenzo, Defendant, Stranger, The Devil Judge

## Recommended Fix Order

1. Fix `expected_missing_from_generated_top10` first because ranking cannot recover missing candidates.
2. Then fix `expected_ranked_too_low` with generated index scoring, not app-level title lists.
3. Treat `noisy_titles_above_expected` as negative-signal work: identify metadata traits of the noisy titles and add general penalties.
4. Re-run `compare_ranking_modes.py` and this audit after every focused change.
