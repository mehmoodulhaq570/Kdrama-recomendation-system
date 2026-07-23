# SeoulMate Ranking Mode Comparison

Generated: `2026-07-23T22:26:48`

## Mode Summary

- `curated_baseline`: P@3 `63.58%`, R@10 `98.46%`, MRR `0.963`
- `hybrid_calibrated`: P@3 `63.58%`, R@10 `99.07%`, MRR `0.963`
- `fallback_genre`: P@3 `63.58%`, R@10 `97.84%`, MRR `0.963`
- `generated_actor`: P@3 `60.49%`, R@10 `98.46%`, MRR `0.941`
- `hybrid_actor`: P@3 `63.58%`, R@10 `98.46%`, MRR `0.963`
- `generated_theme`: P@3 `56.17%`, R@10 `91.36%`, MRR `0.865`
- `hybrid_theme`: P@3 `63.58%`, R@10 `98.46%`, MRR `0.963`
- `fallback_theme`: P@3 `63.58%`, R@10 `98.46%`, MRR `0.963`
- `fallback_genre_theme`: P@3 `63.58%`, R@10 `97.84%`, MRR `0.963`
- `hybrid_genre_theme`: P@3 `63.58%`, R@10 `99.07%`, MRR `0.963`
- `hybrid_genre_generated_actor`: P@3 `60.49%`, R@10 `99.07%`, MRR `0.941`
- `hybrid_genre_actor`: P@3 `63.58%`, R@10 `99.07%`, MRR `0.963`
- `generated_genre_soft`: P@3 `56.79%`, R@10 `94.14%`, MRR `0.948`
- `generated_combo_only_soft`: P@3 `55.56%`, R@10 `91.67%`, MRR `0.915`

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
- `generated_genre_soft` deltas: P@3 `-33.33%`, R@10 `+0.00%`, MRR `+0.000`
- `generated_genre_soft` top 5: Stranger, Squid Game, Beyond Evil, Dong Jae, the Good or the Bastard, Voice
- `generated_combo_only_soft` deltas: P@3 `-100.00%`, R@10 `-66.67%`, MRR `-0.750`
- `generated_combo_only_soft` top 5: The Virus, Agents of Mystery, Bad and Crazy, Stranger, Trap

### restaurant food (theme)

- Expected: Itaewon Class, Wok of Love
- Baseline top 5: Wok of Love, Late Night Restaurant, Pasta, Let's Eat, Itaewon Class
- `generated_theme` deltas: P@3 `-33.33%`, R@10 `-100.00%`, MRR `-1.000`
- `generated_theme` top 5: My Sweet Dear, Pasta, Tastefully Yours, Bon Appetit, Your Majesty, Late Night Restaurant

### law firm corruption (theme)

- Expected: Vincenzo, Law School, Extraordinary Attorney Woo
- Baseline top 5: Vincenzo, Law School, Lawless Lawyer, Extraordinary Attorney Woo, My Lawyer, Mr. Jo
- `generated_theme` deltas: P@3 `-66.67%`, R@10 `-66.67%`, MRR `-0.800`
- `generated_theme` top 5: My Lawyer, Mr. Jo, Law and the City, Dong Jae, the Good or the Bastard, The Devil Judge, Vincenzo

### school drama (genre)

- Expected: True Beauty, Dream High, Extraordinary You
- Baseline top 5: True Beauty, Dream High, Extraordinary You, School 2017, IN-SEOUL
- `generated_genre_soft` deltas: P@3 `-66.67%`, R@10 `-66.67%`, MRR `-0.667`
- `generated_genre_soft` top 5: Seasons of Blossom, The World of My 17, True Beauty, Sassy Go Go, Love Alarm
- `generated_combo_only_soft` deltas: P@3 `-66.67%`, R@10 `-66.67%`, MRR `-0.667`
- `generated_combo_only_soft` top 5: Seasons of Blossom, The World of My 17, True Beauty, Sassy Go Go, Love Alarm

### contract marriage (theme)

- Expected: Because This Is My First Life, Marriage Contract
- Baseline top 5: Marriage Contract, Love in Contract, The Story of Park's Marriage Contract, Because This Is My First Life, Perfect Marriage Revenge
- `generated_theme` deltas: P@3 `-33.33%`, R@10 `-50.00%`, MRR `-0.667`
- `generated_theme` top 5: Full House, Love in Contract, The Story of Park's Marriage Contract, Marriage Contract, The Trunk

### healing slice of life (theme)

- Expected: Hospital Playlist, Our Blues, My Mister
- Baseline top 5: Hospital Playlist, My Mister, A Piece of Your Mind, Our Blues, Hyori's Bed and Breakfast
- `generated_theme` deltas: P@3 `-33.33%`, R@10 `-66.67%`, MRR `-0.500`
- `generated_theme` top 5: Doctor Slump, Hospital Playlist, Daily Dose of Sunshine, Yumi's Cells, Lost

### rich CEO romance (theme)

- Expected: Business Proposal, What's Wrong with Secretary Kim
- Baseline top 5: Business Proposal, Strong Woman Do Bong Soon, What's Wrong with Secretary Kim, King the Land, True Beauty
- `generated_theme` deltas: P@3 `-33.33%`, R@10 `-50.00%`, MRR `-0.500`
- `generated_theme` top 5: Protect the Boss, Business Proposal, Lucky Romance, Can Love Become Money, Love Scout

### sageuk royal drama (genre)

- Expected: The Red Sleeve, Empress Ki, Kingdom
- Baseline top 5: Mr. Sunshine, Kingdom, The Red Sleeve, Empress Ki, Bloody Heart
- `generated_genre_soft` deltas: P@3 `-33.33%`, R@10 `-66.67%`, MRR `-0.167`
- `generated_genre_soft` top 5: Under the Queen's Umbrella, My Dearest, The Red Sleeve, Pachinko, My Country: The New Age
- `generated_combo_only_soft` deltas: P@3 `-33.33%`, R@10 `-66.67%`, MRR `-0.167`
- `generated_combo_only_soft` top 5: Under the Queen's Umbrella, My Dearest, The Red Sleeve, Pachinko, My Country: The New Age

### north korea (theme)

- Expected: Crash Landing on You
- Baseline top 5: Crash Landing on You, Iris, Snowdrop, Kingdom: Ashin of the North, Korea-Khitan War
- `generated_theme` deltas: P@3 `-33.33%`, R@10 `+0.00%`, MRR `-0.800`
- `generated_theme` top 5: Curtain Call, My Military Valentine, Snowdrop, Love Andante, Crash Landing on You

### time travel (theme)

- Expected: Signal, Tomorrow with You
- Baseline top 5: Tomorrow with You, Nine: Nine Times Time Travel, Rooftop Prince, Signal, Love in Time
- `generated_theme` deltas: P@3 `+0.00%`, R@10 `-50.00%`, MRR `-0.500`
- `generated_theme` top 5: A Time Called You, Tomorrow with You, Manhole, Marry My Husband, Somehow 18

### Park Seo Joon (actor)

- Expected: Itaewon Class, What's Wrong with Secretary Kim
- Baseline top 5: Itaewon Class, What's Wrong with Secretary Kim, Fight for My Way, Gyeongseong Creature, Dream High Season 2
- `generated_actor` deltas: P@3 `-33.33%`, R@10 `+0.00%`, MRR `-0.667`
- `generated_actor` top 5: Fight for My Way, Gyeongseong Creature, Itaewon Class, Hwarang, What's Wrong with Secretary Kim
- `hybrid_genre_generated_actor` deltas: P@3 `-33.33%`, R@10 `+0.00%`, MRR `-0.667`
- `hybrid_genre_generated_actor` top 5: Fight for My Way, Gyeongseong Creature, Itaewon Class, Hwarang, What's Wrong with Secretary Kim

### zombie drama (genre)

- Expected: All of Us Are Dead, Kingdom, Happiness
- Baseline top 5: All of Us Are Dead, Kingdom, Happiness, Sweet Home, Squid Game
- `generated_genre_soft` deltas: P@3 `-33.33%`, R@10 `+0.00%`, MRR `-0.500`
- `generated_genre_soft` top 5: Sweet Home, All of Us Are Dead, Kingdom: Ashin of the North, Happiness, Kingdom
- `generated_combo_only_soft` deltas: P@3 `-33.33%`, R@10 `+0.00%`, MRR `-0.500`
- `generated_combo_only_soft` top 5: Sweet Home, All of Us Are Dead, Kingdom: Ashin of the North, Happiness, Kingdom

### Lee Min Ho (actor)

- Expected: The Heirs, The King: Eternal Monarch
- Baseline top 5: The Heirs, The King: Eternal Monarch, Boys over Flowers, Boys before Flowers: F4 Talk Show Special, Boys over Flowers: F4 Afterstory
- `generated_actor` deltas: P@3 `-33.33%`, R@10 `+0.00%`, MRR `-0.500`
- `generated_actor` top 5: City Hunter, The King: Eternal Monarch, Personal Taste, The Heirs, Mackerel Run
- `hybrid_genre_generated_actor` deltas: P@3 `-33.33%`, R@10 `+0.00%`, MRR `-0.500`
- `hybrid_genre_generated_actor` top 5: City Hunter, The King: Eternal Monarch, Personal Taste, The Heirs, Mackerel Run

### medical drama (genre)

- Expected: Hospital Playlist, Doctor Cha, Good Doctor
- Baseline top 5: Hospital Playlist, Doctor Cha, Good Doctor, Dr. Romantic, Hospital Ship
- `generated_theme` deltas: P@3 `-66.67%`, R@10 `+0.00%`, MRR `+0.000`
- `generated_theme` top 5: Doctor Cha, Doctor Stranger, Brain, Dr. Romantic, The Trauma Code: Heroes on Call
- `generated_genre_soft` deltas: P@3 `-33.33%`, R@10 `-33.33%`, MRR `+0.000`
- `generated_genre_soft` top 5: Good Doctor, Doctor Cha, Brain, Dr. Romantic Season 3, Emergency Couple
- `generated_combo_only_soft` deltas: P@3 `-33.33%`, R@10 `-33.33%`, MRR `+0.000`
- `generated_combo_only_soft` top 5: Good Doctor, Doctor Cha, Brain, Dr. Romantic Season 3, Emergency Couple

### doctor hospital drama (genre)

- Expected: Hospital Playlist, Doctor Cha, Good Doctor
- Baseline top 5: Hospital Playlist, Doctor Cha, Good Doctor, Dr. Romantic, Hospital Ship
- `generated_theme` deltas: P@3 `-66.67%`, R@10 `+0.00%`, MRR `+0.000`
- `generated_theme` top 5: Doctor Cha, Doctor Stranger, Brain, Dr. Romantic, The Trauma Code: Heroes on Call
- `generated_genre_soft` deltas: P@3 `-33.33%`, R@10 `-33.33%`, MRR `+0.000`
- `generated_genre_soft` top 5: Good Doctor, Doctor Cha, Brain, Dr. Romantic Season 3, Emergency Couple
- `generated_combo_only_soft` deltas: P@3 `-33.33%`, R@10 `-33.33%`, MRR `+0.000`
- `generated_combo_only_soft` top 5: Good Doctor, Doctor Cha, Brain, Dr. Romantic Season 3, Emergency Couple

### office romance (genre)

- Expected: Business Proposal, What's Wrong with Secretary Kim, Romance Is a Bonus Book
- Baseline top 5: Business Proposal, What's Wrong with Secretary Kim, Strong Woman Do Bong Soon, True Beauty, Agency
- `fallback_genre` deltas: P@3 `+0.00%`, R@10 `-33.33%`, MRR `+0.000`
- `fallback_genre` top 5: Business Proposal, What's Wrong with Secretary Kim, Strong Woman Do Bong Soon, True Beauty, Gaus Electronics
- `fallback_genre_theme` deltas: P@3 `+0.00%`, R@10 `-33.33%`, MRR `+0.000`
- `fallback_genre_theme` top 5: Business Proposal, What's Wrong with Secretary Kim, Strong Woman Do Bong Soon, True Beauty, Gaus Electronics
- `generated_genre_soft` deltas: P@3 `-33.33%`, R@10 `-33.33%`, MRR `+0.000`
- `generated_genre_soft` top 5: What's Wrong with Secretary Kim, Gaus Electronics, Fated to Love You, Falling for Innocence, Romance Is a Bonus Book
- `generated_combo_only_soft` deltas: P@3 `-33.33%`, R@10 `-33.33%`, MRR `+0.000`
- `generated_combo_only_soft` top 5: What's Wrong with Secretary Kim, Gaus Electronics, Fated to Love You, Falling for Innocence, Romance Is a Bonus Book

### workplace startup (theme)

- Expected: Start-Up, Misaeng
- Baseline top 5: Start-Up, Agency, Hot Stove League, Gaus Electronics, The New Employee
- `generated_theme` deltas: P@3 `+0.00%`, R@10 `+0.00%`, MRR `-0.500`
- `generated_theme` top 5: Unicorn, Start-Up, Miss Lee, Kkondae Intern, Ms. Temper &amp; Nam Jung Gi

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

### ghost supernatural hotel (theme)

- Expected: Hotel Del Luna, The Master's Sun
- Baseline top 5: Hotel del Luna, The Master's Sun, Oh My Ghost, Ghostderella, Drama Special Season 6: What Is the Ghost Doing?
- `generated_theme` deltas: P@3 `-33.33%`, R@10 `+0.00%`, MRR `+0.000`
- `generated_theme` top 5: The Master's Sun, The Haunted Palace, Sell Your Haunted House, Hotel del Luna, Who Are You

### Ji Chang Wook (actor)

- Expected: Healer, Suspicious Partner
- Baseline top 5: Healer, Suspicious Partner, The K2, Queen Woo, 7 First Kisses
- `generated_actor` deltas: P@3 `-33.33%`, R@10 `+0.00%`, MRR `+0.000`
- `generated_actor` top 5: Healer, The Worst of Evil, Welcome to Samdal-ri, If You Wish Upon Me, The K2
- `hybrid_genre_generated_actor` deltas: P@3 `-33.33%`, R@10 `+0.00%`, MRR `+0.000`
- `hybrid_genre_generated_actor` top 5: Healer, The Worst of Evil, Welcome to Samdal-ri, If You Wish Upon Me, The K2

### IU (actor)

- Expected: Hotel Del Luna, My Mister
- Baseline top 5: Hotel del Luna, My Mister, Moon Lovers: Scarlet Heart Ryeo, Bel Ami, Boss-dol Mart
- `generated_actor` deltas: P@3 `-33.33%`, R@10 `+0.00%`, MRR `+0.000`
- `generated_actor` top 5: Hotel del Luna, You Are the Best!, Persona, My Mister, Moon Lovers: Scarlet Heart Ryeo
- `hybrid_genre_generated_actor` deltas: P@3 `-33.33%`, R@10 `+0.00%`, MRR `+0.000`
- `hybrid_genre_generated_actor` top 5: Hotel del Luna, You Are the Best!, Persona, My Mister, Moon Lovers: Scarlet Heart Ryeo

### Song Hye Kyo (actor)

- Expected: Descendants of the Sun, The Glory
- Baseline top 5: Descendants of the Sun, The Glory, Encounter, All In, Autumn Tale
- `generated_actor` deltas: P@3 `-33.33%`, R@10 `+0.00%`, MRR `+0.000`
- `generated_actor` top 5: The Glory, Encounter, All In, Now, We Are Breaking Up, Descendants of the Sun
- `hybrid_genre_generated_actor` deltas: P@3 `-33.33%`, R@10 `+0.00%`, MRR `+0.000`
- `hybrid_genre_generated_actor` top 5: The Glory, Encounter, All In, Now, We Are Breaking Up, Descendants of the Sun
