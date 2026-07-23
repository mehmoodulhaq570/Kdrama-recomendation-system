# SeoulMate Weak Query Report

Generated: `2026-07-21T17:18:20`
API: `http://127.0.0.1:8021`

## Summary

- Expected-query cases: `54`
- Weak queries: `22`

## Weak Reasons

- `ranking_order_weak`: `1`
- `relevant_titles_present_but_not_top3`: `20`
- `theme_not_detected`: `1`

## Category Metrics

- `specific_title`: P@3 `51.11%`, R@10 `100.00%`, MRR `1.000`
- `genre`: P@3 `89.74%`, R@10 `97.44%`, MRR `0.885`
- `theme`: P@3 `48.48%`, R@10 `95.45%`, MRR `1.000`
- `actor`: P@3 `63.33%`, R@10 `100.00%`, MRR `0.950`
- `typo`: P@3 `66.67%`, R@10 `100.00%`, MRR `1.000`

## Weak Queries

### workplace startup (theme)

- Reason: `theme_not_detected`
- Metrics: P@3 `33.33%`, R@10 `50.00%`, MRR `1.000`
- Expected: Start-Up, Misaeng
- Found top 10: Start-Up
- Detected genres: Business
- Detected themes: none
- Detected actors: none
- Top 10: Start-Up, Agency, Hot Stove League, Gaus Electronics, The New Employee, Today's Webtoon, Wish Woosh Season 2, Beethoven Virus, The Woman Who Still Wants to Marry, I Need Romance Season 3

### fantasy romance (genre)

- Reason: `ranking_order_weak`
- Metrics: P@3 `66.67%`, R@10 `66.67%`, MRR `0.500`
- Expected: Goblin, Hotel Del Luna, Alchemy of Souls
- Found top 10: Hotel Del Luna, Alchemy of Souls
- Detected genres: Romance, Fantasy
- Detected themes: none
- Detected actors: none
- Top 10: Guardian: The Lonely and Great God, Hotel del Luna, Alchemy of Souls, My Love from the Star, Business Proposal, What's Wrong with Secretary Kim, Strong Woman Do Bong Soon, True Beauty, Genie, Make a Wish, Eccentric Romance

### Gong Yoo (actor)

- Reason: `relevant_titles_present_but_not_top3`
- Metrics: P@3 `33.33%`, R@10 `100.00%`, MRR `0.500`
- Expected: Goblin, Coffee Prince
- Found top 10: Goblin, Coffee Prince
- Detected genres: none
- Detected themes: none
- Detected actors: none
- Top 10: Guardian: The Lonely and Great God, Coffee Prince, Big, Because I Want to Talk, Biscuit Teacher and Star Candy, Coffee Prince Special, Goblin Special: Every Moment of It Shined, Goblin Special: The Summoning, Maybe, Maybe Not, Soundtrack #2

### restaurant food (theme)

- Reason: `relevant_titles_present_but_not_top3`
- Metrics: P@3 `33.33%`, R@10 `100.00%`, MRR `1.000`
- Expected: Itaewon Class, Wok of Love
- Found top 10: Itaewon Class, Wok of Love
- Detected genres: Food
- Detected themes: none
- Detected actors: none
- Top 10: Wok of Love, Late Night Restaurant, Pasta, Let's Eat, Itaewon Class, Ga Doo Ri’s Sushi Restaurant, Jinny's Kitchen, Kang's Kitchen, My Romantic Some Recipe, Soul Plate

### time travel (theme)

- Reason: `relevant_titles_present_but_not_top3`
- Metrics: P@3 `33.33%`, R@10 `100.00%`, MRR `1.000`
- Expected: Signal, Tomorrow with You
- Found top 10: Signal, Tomorrow with You
- Detected genres: none
- Detected themes: none
- Detected actors: none
- Top 10: Tomorrow with You, Nine: Nine Times Time Travel, Rooftop Prince, Signal, Love in Time, One More Time, Time Slip Dr. Jin, Time, A Time Called You, When Time Stopped

### crime thriller (genre)

- Reason: `relevant_titles_present_but_not_top3`
- Metrics: P@3 `66.67%`, R@10 `100.00%`, MRR `0.500`
- Expected: Signal, Stranger, Beyond Evil
- Found top 10: Signal, Stranger, Beyond Evil
- Detected genres: Thriller, Crime
- Detected themes: none
- Detected actors: none
- Top 10: Squid Game, Signal, Stranger, Beyond Evil, Crime Puzzle, Evilive, The Killer's Shopping List, The Ghost Detective, Less Than Evil, Spy

### sageuk royal drama (genre)

- Reason: `relevant_titles_present_but_not_top3`
- Metrics: P@3 `66.67%`, R@10 `100.00%`, MRR `0.500`
- Expected: The Red Sleeve, Empress Ki, Kingdom
- Found top 10: The Red Sleeve, Empress Ki, Kingdom
- Detected genres: Drama, Historical
- Detected themes: none
- Detected actors: none
- Top 10: Mr. Sunshine, Kingdom, The Red Sleeve, Empress Ki, Bloody Heart, Under the Queen's Umbrella, Jang Ok Jung, Queen for Seven Days, Grand Prince, Dong Yi

### office romance (genre)

- Reason: `relevant_titles_present_but_not_top3`
- Metrics: P@3 `66.67%`, R@10 `100.00%`, MRR `1.000`
- Expected: Business Proposal, What's Wrong with Secretary Kim, Romance Is a Bonus Book
- Found top 10: Business Proposal, What's Wrong with Secretary Kim, Romance Is a Bonus Book
- Detected genres: Romance, Business
- Detected themes: none
- Detected actors: none
- Top 10: Business Proposal, What's Wrong with Secretary Kim, Strong Woman Do Bong Soon, True Beauty, Agency, The Secret Life of My Secretary, The Queen of Office, Romance Is a Bonus Book, The Interest of Love, Love in Contract

### contract marriage (theme)

- Reason: `relevant_titles_present_but_not_top3`
- Metrics: P@3 `66.67%`, R@10 `100.00%`, MRR `1.000`
- Expected: Because This Is My First Life, Marriage Contract
- Found top 10: Because This Is My First Life, Marriage Contract
- Detected genres: none
- Detected themes: none
- Detected actors: none
- Top 10: Marriage Contract, Love in Contract, The Story of Park's Marriage Contract, Because This Is My First Life, Perfect Marriage Revenge, The Wedding Scheme, Marriage, Not Dating, Marry My Husband, Wedding Impossible, Can We Get Married?

### rich CEO romance (theme)

- Reason: `relevant_titles_present_but_not_top3`
- Metrics: P@3 `66.67%`, R@10 `100.00%`, MRR `1.000`
- Expected: Business Proposal, What's Wrong with Secretary Kim
- Found top 10: Business Proposal, What's Wrong with Secretary Kim
- Detected genres: Romance
- Detected themes: none
- Detected actors: none
- Top 10: Business Proposal, Strong Woman Do Bong Soon, What's Wrong with Secretary Kim, King the Land, True Beauty, Rich Man, Que Sera Sera, Rich Family's Son, Lucky Romance, Passionate Love

### law firm corruption (theme)

- Reason: `relevant_titles_present_but_not_top3`
- Metrics: P@3 `66.67%`, R@10 `100.00%`, MRR `1.000`
- Expected: Vincenzo, Law School, Extraordinary Attorney Woo
- Found top 10: Vincenzo, Law School, Extraordinary Attorney Woo
- Detected genres: Law
- Detected themes: none
- Detected actors: none
- Top 10: Vincenzo, Law School, Lawless Lawyer, Extraordinary Attorney Woo, My Lawyer, Mr. Jo, One Dollar Lawyer, Law and the City, Divorce Lawyer in Love, Good Partner, Suits

### ghost supernatural hotel (theme)

- Reason: `relevant_titles_present_but_not_top3`
- Metrics: P@3 `66.67%`, R@10 `100.00%`, MRR `1.000`
- Expected: Hotel Del Luna, The Master's Sun
- Found top 10: Hotel Del Luna, The Master's Sun
- Detected genres: Supernatural
- Detected themes: none
- Detected actors: none
- Top 10: Hotel del Luna, The Master's Sun, Oh My Ghost, Ghostderella, Drama Special Season 6: What Is the Ghost Doing?, My Secret Hotel, Hotel King, Cheo Yong, Item, Drama Special Season 3: Don't Worry, It's a Ghost

### healing slice of life (theme)

- Reason: `relevant_titles_present_but_not_top3`
- Metrics: P@3 `66.67%`, R@10 `100.00%`, MRR `1.000`
- Expected: Hospital Playlist, Our Blues, My Mister
- Found top 10: Hospital Playlist, Our Blues, My Mister
- Detected genres: Life
- Detected themes: none
- Detected actors: none
- Top 10: Hospital Playlist, My Mister, A Piece of Your Mind, Our Blues, Hyori's Bed and Breakfast, Kian's Bizarre B&amp;B, Sea of Hope, BTS in the Soop Season 2, Love Tractor, Finland Papa

### Hyun Bin (actor)

- Reason: `relevant_titles_present_but_not_top3`
- Metrics: P@3 `66.67%`, R@10 `100.00%`, MRR `1.000`
- Expected: Crash Landing on You, Memories of the Alhambra
- Found top 10: Crash Landing on You, Memories of the Alhambra
- Detected genres: none
- Detected themes: none
- Detected actors: none
- Top 10: Crash Landing on You, Memories of the Alhambra, Secret Garden, Crash Landing on You Special: Lunar New Year, Friend, Our Legend, Hyde, Jekyll, Me, Love Andante, My Lovely Sam Soon, Part-Time Idol, Summer Guys

### Park Seo Joon (actor)

- Reason: `relevant_titles_present_but_not_top3`
- Metrics: P@3 `66.67%`, R@10 `100.00%`, MRR `1.000`
- Expected: Itaewon Class, What's Wrong with Secretary Kim
- Found top 10: Itaewon Class, What's Wrong with Secretary Kim
- Detected genres: none
- Detected themes: none
- Detected actors: none
- Top 10: Itaewon Class, What's Wrong with Secretary Kim, Fight for My Way, Gyeongseong Creature, Dream High Season 2, Gyeongseong Creature Season 2, Hwarang, Hwarang Special, I Summon You, Gold!, In The Soop: Friendcation

### Song Joong Ki (actor)

- Reason: `relevant_titles_present_but_not_top3`
- Metrics: P@3 `66.67%`, R@10 `100.00%`, MRR `1.000`
- Expected: Vincenzo, Descendants of the Sun
- Found top 10: Vincenzo, Descendants of the Sun
- Detected genres: none
- Detected themes: none
- Detected actors: none
- Top 10: Vincenzo, Descendants of the Sun, Arthdal Chronicles Part 1: The Children of Prophecy, Sungkyunkwan Scandal, Sungkyunkwan Scandal: Special, Arthdal Chronicles Part 2: The Sky Turning Inside Out, Rising Land, Arthdal Chronicles Part 3: The Prelude to All Legends, Descendants of the Sun: BTS, Descendants of the Sun: Recap Special, My Youth

### Kim Soo Hyun (actor)

- Reason: `relevant_titles_present_but_not_top3`
- Metrics: P@3 `66.67%`, R@10 `100.00%`, MRR `1.000`
- Expected: My Love from the Star, It's Okay to Not Be Okay
- Found top 10: My Love from the Star, It's Okay to Not Be Okay
- Detected genres: none
- Detected themes: none
- Detected actors: none
- Top 10: My Love from the Star, It's Okay to Not Be Okay, Moon Embracing the Sun, A-Teen, A-Teen Season 2, Dream High, Dream High Special Concert, Go, Back Diary, Good Day, One Ordinary Day

### Lee Min Ho (actor)

- Reason: `relevant_titles_present_but_not_top3`
- Metrics: P@3 `66.67%`, R@10 `100.00%`, MRR `1.000`
- Expected: The Heirs, The King: Eternal Monarch
- Found top 10: The Heirs, The King: Eternal Monarch
- Detected genres: none
- Detected themes: none
- Detected actors: none
- Top 10: The Heirs, The King: Eternal Monarch, Boys over Flowers, Boys before Flowers: F4 Talk Show Special, Boys over Flowers: F4 Afterstory, City Hunter, Faith, Mackerel Run, Pachinko, Pachinko Season 2

### Ji Chang Wook (actor)

- Reason: `relevant_titles_present_but_not_top3`
- Metrics: P@3 `66.67%`, R@10 `100.00%`, MRR `1.000`
- Expected: Healer, Suspicious Partner
- Found top 10: Healer, Suspicious Partner
- Detected genres: none
- Detected themes: none
- Detected actors: none
- Top 10: Healer, Suspicious Partner, The K2, Queen Woo, 7 First Kisses, Bachelor's Vegetable Store, Backstreet Rookie, Empress Ki, Five Fingers, Gangnam B-Side

### IU (actor)

- Reason: `relevant_titles_present_but_not_top3`
- Metrics: P@3 `66.67%`, R@10 `100.00%`, MRR `1.000`
- Expected: Hotel Del Luna, My Mister
- Found top 10: Hotel Del Luna, My Mister
- Detected genres: none
- Detected themes: none
- Detected actors: none
- Top 10: Hotel del Luna, My Mister, Moon Lovers: Scarlet Heart Ryeo, Bel Ami, Boss-dol Mart, Dream High, Dream High Special Concert, EXO Arcade, EXO Arcade Season 2, EXO's Ladder Season 2

### Park Min Young (actor)

- Reason: `relevant_titles_present_but_not_top3`
- Metrics: P@3 `66.67%`, R@10 `100.00%`, MRR `1.000`
- Expected: What's Wrong with Secretary Kim, Her Private Life
- Found top 10: What's Wrong with Secretary Kim, Her Private Life
- Detected genres: none
- Detected themes: none
- Detected actors: none
- Top 10: What's Wrong with Secretary Kim, Her Private Life, Healer, Glory Jane, I Am Your Teacher, Sungkyunkwan Scandal, A New Leaf, Busted, Busted Season 2, Busted Season 3

### Song Hye Kyo (actor)

- Reason: `relevant_titles_present_but_not_top3`
- Metrics: P@3 `66.67%`, R@10 `100.00%`, MRR `1.000`
- Expected: Descendants of the Sun, The Glory
- Found top 10: Descendants of the Sun, The Glory
- Detected genres: none
- Detected themes: none
- Detected actors: none
- Top 10: Descendants of the Sun, The Glory, Encounter, All In, Autumn Tale, Descendants of the Sun: BTS, Descendants of the Sun: Recap Special, Full House, Hotelier, Now, We Are Breaking Up
