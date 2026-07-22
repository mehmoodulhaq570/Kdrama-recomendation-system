# SeoulMate Ranking Mode Comparison

Generated: `2026-07-23T01:04:27`

## Mode Summary

- `curated_baseline`: P@3 `63.58%`, R@10 `98.46%`, MRR `0.963`
- `generated_genre_soft`: P@3 `54.94%`, R@10 `94.14%`, MRR `0.938`
- `generated_combo_only_soft`: P@3 `54.32%`, R@10 `92.90%`, MRR `0.915`

## Biggest Generated Regressions

### historical (genre)

- Expected: Mr. Sunshine, Kingdom, The Red Sleeve
- Baseline top 5: Mr. Sunshine, Kingdom, The Red Sleeve, Empress Ki, The Three Musketeers
- `generated_genre_soft` deltas: P@3 `-66.67%`, R@10 `-33.33%`, MRR `+0.000`
- `generated_genre_soft` top 5: Mr. Sunshine, Alchemy of Souls, Under the Queen's Umbrella, Tale of the Nine-Tailed 1938, Mr. Queen
- `generated_combo_only_soft` deltas: P@3 `-100.00%`, R@10 `-100.00%`, MRR `-1.000`
- `generated_combo_only_soft` top 5: The Three Musketeers, Time Slip Dr. Jin, Arthdal Chronicles: The Sword of Aramun, 100 Days My Prince, Captivating the King

### thriller (genre)

- Expected: Squid Game, Signal, Stranger
- Baseline top 5: Squid Game, Signal, Stranger, Beyond Evil, The Virus
- `generated_genre_soft` deltas: P@3 `-66.67%`, R@10 `-66.67%`, MRR `-0.500`
- `generated_genre_soft` top 5: Mouse, Signal, Mother, Tomorrow, Happiness
- `generated_combo_only_soft` deltas: P@3 `-100.00%`, R@10 `-66.67%`, MRR `-0.750`
- `generated_combo_only_soft` top 5: The Virus, Agents of Mystery, Bad and Crazy, Stranger, Trap

### school drama (genre)

- Expected: True Beauty, Dream High, Extraordinary You
- Baseline top 5: True Beauty, Dream High, Extraordinary You, School 2017, IN-SEOUL
- `generated_genre_soft` deltas: P@3 `-66.67%`, R@10 `-66.67%`, MRR `-0.667`
- `generated_genre_soft` top 5: Seasons of Blossom, The World of My 17, True Beauty, Sassy Go Go, Love Alarm
- `generated_combo_only_soft` deltas: P@3 `-66.67%`, R@10 `-66.67%`, MRR `-0.667`
- `generated_combo_only_soft` top 5: Seasons of Blossom, The World of My 17, True Beauty, Sassy Go Go, Love Alarm

### sageuk royal drama (genre)

- Expected: The Red Sleeve, Empress Ki, Kingdom
- Baseline top 5: Mr. Sunshine, Kingdom, The Red Sleeve, Empress Ki, Bloody Heart
- `generated_genre_soft` deltas: P@3 `-33.33%`, R@10 `-66.67%`, MRR `-0.167`
- `generated_genre_soft` top 5: Under the Queen's Umbrella, My Dearest, The Red Sleeve, Pachinko, My Country: The New Age
- `generated_combo_only_soft` deltas: P@3 `-33.33%`, R@10 `-66.67%`, MRR `-0.167`
- `generated_combo_only_soft` top 5: Under the Queen's Umbrella, My Dearest, The Red Sleeve, Pachinko, My Country: The New Age

### zombie drama (genre)

- Expected: All of Us Are Dead, Kingdom, Happiness
- Baseline top 5: All of Us Are Dead, Kingdom, Happiness, Sweet Home, Squid Game
- `generated_genre_soft` deltas: P@3 `-33.33%`, R@10 `+0.00%`, MRR `-0.500`
- `generated_genre_soft` top 5: Sweet Home, All of Us Are Dead, Kingdom: Ashin of the North, Happiness, Kingdom
- `generated_combo_only_soft` deltas: P@3 `-33.33%`, R@10 `+0.00%`, MRR `-0.500`
- `generated_combo_only_soft` top 5: Sweet Home, All of Us Are Dead, Kingdom: Ashin of the North, Happiness, Kingdom

### medical drama (genre)

- Expected: Hospital Playlist, Doctor Cha, Good Doctor
- Baseline top 5: Hospital Playlist, Doctor Cha, Good Doctor, Dr. Romantic, Hospital Ship
- `generated_genre_soft` deltas: P@3 `-66.67%`, R@10 `+0.00%`, MRR `+0.000`
- `generated_genre_soft` top 5: Hospital Playlist, Daily Dose of Sunshine, Dr. Romantic, The Trauma Code: Heroes on Call, If You Wish Upon Me
- `generated_combo_only_soft` deltas: P@3 `-66.67%`, R@10 `+0.00%`, MRR `+0.000`
- `generated_combo_only_soft` top 5: Hospital Playlist, Daily Dose of Sunshine, Dr. Romantic, The Trauma Code: Heroes on Call, If You Wish Upon Me

### doctor hospital drama (genre)

- Expected: Hospital Playlist, Doctor Cha, Good Doctor
- Baseline top 5: Hospital Playlist, Doctor Cha, Good Doctor, Dr. Romantic, Hospital Ship
- `generated_genre_soft` deltas: P@3 `-66.67%`, R@10 `+0.00%`, MRR `+0.000`
- `generated_genre_soft` top 5: Hospital Playlist, Daily Dose of Sunshine, Dr. Romantic, The Trauma Code: Heroes on Call, If You Wish Upon Me
- `generated_combo_only_soft` deltas: P@3 `-66.67%`, R@10 `+0.00%`, MRR `+0.000`
- `generated_combo_only_soft` top 5: Hospital Playlist, Daily Dose of Sunshine, Dr. Romantic, The Trauma Code: Heroes on Call, If You Wish Upon Me

### office romance (genre)

- Expected: Business Proposal, What's Wrong with Secretary Kim, Romance Is a Bonus Book
- Baseline top 5: Business Proposal, What's Wrong with Secretary Kim, Strong Woman Do Bong Soon, True Beauty, Agency
- `generated_genre_soft` deltas: P@3 `-33.33%`, R@10 `-33.33%`, MRR `+0.000`
- `generated_genre_soft` top 5: What's Wrong with Secretary Kim, Gaus Electronics, Fated to Love You, Falling for Innocence, Romance Is a Bonus Book
- `generated_combo_only_soft` deltas: P@3 `-33.33%`, R@10 `-33.33%`, MRR `+0.000`
- `generated_combo_only_soft` top 5: What's Wrong with Secretary Kim, Gaus Electronics, Fated to Love You, Falling for Innocence, Romance Is a Bonus Book

### romantic comedy (genre)

- Expected: Business Proposal, What's Wrong with Secretary Kim, Strong Woman Do Bong Soon
- Baseline top 5: Business Proposal, What's Wrong with Secretary Kim, Strong Woman Do Bong Soon, True Beauty, Romance
- `generated_genre_soft` deltas: P@3 `-33.33%`, R@10 `+0.00%`, MRR `+0.000`
- `generated_genre_soft` top 5: Business Proposal, Strong Woman Do Bong Soon, The Secret Life of My Secretary, What's Wrong with Secretary Kim, Love in Contract
- `generated_combo_only_soft` deltas: P@3 `-33.33%`, R@10 `+0.00%`, MRR `+0.000`
- `generated_combo_only_soft` top 5: Business Proposal, Strong Woman Do Bong Soon, The Secret Life of My Secretary, What's Wrong with Secretary Kim, Love in Contract

### legal drama (genre)

- Expected: Extraordinary Attorney Woo, Law School, Vincenzo
- Baseline top 5: Extraordinary Attorney Woo, Law School, Vincenzo, Lawless Lawyer, Delayed Justice
- `generated_genre_soft` deltas: P@3 `-33.33%`, R@10 `+0.00%`, MRR `+0.000`
- `generated_genre_soft` top 5: Extraordinary Attorney Woo, Vincenzo, Defendant, Stranger, The Devil Judge
- `generated_combo_only_soft` deltas: P@3 `-33.33%`, R@10 `+0.00%`, MRR `+0.000`
- `generated_combo_only_soft` top 5: Extraordinary Attorney Woo, Vincenzo, Defendant, Stranger, The Devil Judge
