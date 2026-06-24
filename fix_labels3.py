"""
Third correction pass: fix remaining systematic mislabels.
"""
import pandas as pd

df = pd.read_csv('nba_posts.csv')

corrections = {
    # === SOURCE=ANALYSIS ROWS LABELED COMMENTARY THAT SHOULD BE ANALYSIS ===

    # row 84: "They've fallen off lately but still currently tied for highest scoring offense"
    # stat claim (highest scoring offense) → analysis
    84: ('analysis', ''),

    # row 87: "There are currently 26 players with True Shooting Points Added of -55 or worse... Jalen Green / He's done it in 14 games"
    # historical stat comparison making a point → analysis
    87: ('analysis', ''),

    # row 111: "Jonathan Kuminga in his first 3 games in ATL: 21.3 points, 7.7 rebounds and 3.3 assists per game on 79% TS, +59"
    # specific stats to support a point about his performance → analysis
    111: ('analysis', ''),

    # row 121: "Kon was the best shooting of any 20-year old in the NBA, ever. And it was dynamic shooting..."
    # "best shooting of any 20-year old" is a historical claim based on stats → analysis
    121: ('analysis', ''),

    # row 138: "a) Are we considering him a former NBA player just because it's technically true (3 games, 7 minutes, 0/1 shooting)"
    # humorous rhetorical question using trivial stats → hot_take
    138: ('hot_take', 'borderline hot_take/analysis: uses trivial stats (3 games, 7 min, 0/1 shooting) rhetorically/humorously to make a judgment; stat is decoration not argument'),

    # row 151: "Many things about the NBA have changed since last season. The main thing that hasn't, though, is that the Thunder look like one of the best teams we've ever seen"
    # opinion claim "best teams we've ever seen" → hot_take
    151: ('hot_take', ''),

    # row 174: "Per NBA Stats and Info: Pacers played their starters only 38.2% of available minutes of game 2, while OKC played theirs 77.2% of available minutes. You'd think this would be more lopsided. Seems calculated by Pacers."
    # specific stat to draw a tactical conclusion → analysis
    174: ('analysis', 'borderline analysis/commentary: specific stat (minutes % for starters) used to argue Pacers minutes strategy was calculated; stat is doing argumentative work'),

    # row 181: "Scoring was extremely hard in the mid 2000s apparently for the good players while being easier for good players in the 90s. Also, notice how KG and Dirk are on here while one PF isn't."
    # stat-based comparison of eras and players → analysis
    181: ('analysis', ''),

    # row 208: "Also All-NBA had position restrictions so Andre Drummond had a 49.9% true shooting as a C and made it over Harden"
    # specific stat making an argumentative point about All-NBA selection → analysis
    208: ('analysis', ''),

    # row 209: "The Knicks have a 2-0 lead despite Jalen Brunson having a very inefficient 42% true shooting, with the same number of assists as turnovers."
    # specific stats used to make a point about Brunson's inefficiency → analysis
    209: ('analysis', ''),

    # row 218: "The Pelicans finished summer league 1st in rebounds per game. It's difficult to gauge how much of a positive that is without the NBA providing rate based stats, but it is positive regardless."
    # stat (1st in rebounds) with analytical caveat → analysis
    218: ('analysis', ''),

    # row 237: "Some cool stats that show Daniels' leap this season"
    # teaser/reference to stats without showing them → commentary (just a caption/reference)
    237: ('commentary', 'borderline analysis/commentary: very brief caption referencing stats without presenting them; no stat or argument visible in post text'),

    # row 248: "OKC is in the bottom half for free throw attempts per game this season per espn.com"
    # specific stat claim making a point about OKC → analysis
    248: ('analysis', ''),

    # row 249: "San Antonio Spurs forward Keldon Johnson won the NBA Sixth Man of the Year award for the 2025-26 season. He's the second Spur to win the award, joining Manu Ginobili. He led reserves in win shares (6.4) and was second in bench points (1,081)..."
    # stats used to support award narrative → analysis
    249: ('analysis', ''),

    # row 265: "Spurs finally starting to get loose with the ball here late in the third, and the Thunder are immediately making them pay for it"
    # live game commentary (no stats, no argument) → commentary
    265: ('commentary', ''),

    # row 271: "Broadcast details for the 2026 NBA Finals schedule confirm absolute structural continuity on ABC. Analytics favor the East's net rating, but the West's true shooting percentage remains elite."
    # mentions analytics/TS% but primarily a broadcast preview → commentary
    271: ('commentary', 'borderline analysis/commentary: mentions analytics and true shooting percentage but primarily a broadcast schedule/preview post'),

    # row 287: "Look, 2.3 points, 1.1 assists, and 0.7 rebounds per game just isn't NBA-level output. The talent is there, but he still needs more development before he can hang at this level. Bronny James stats..."
    # specific stats making argument about Bronny → analysis
    287: ('analysis', 'borderline analysis/hot_take: specific stats (2.3/1.1/0.7) doing work to argue Bronny isn\'t NBA-level yet; stat is the point'),

    # row 297: "My rage, in graphs: #wnba #nba / 'The W.N.B.A. makes more money than the N.B.A. did at the same point in its history'"
    # references a stat comparison (WNBA vs NBA historical revenues) → analysis
    297: ('analysis', 'borderline analysis/commentary: references a revenue comparison stat; treated as analysis since the stat makes an argumentative point about WNBA growth'),

    # row 309: "This guy made a fantastic dashboard of Knicks 1999-2026, worth a look: valueaddvc.com/knicks"
    # just linking to a dashboard, no stats shown → commentary
    309: ('commentary', ''),

    # row 315: "Two things can be true at the same time, the Knicks are shooting terribly AND the refs are doing everything they can to make sure the series evens out..."
    # conspiracy/opinion claim about refs → hot_take
    315: ('hot_take', 'borderline hot_take/analysis: "shooting terribly" is a stat reference but post is primarily a conspiracy opinion about refs manipulating the series'),

    # row 350: "Derrick White also led the NBA in defensive win shares in February (min. 2 games played). He ranks fifth in that category for the season (min. 40 games played)."
    # specific stat (led NBA in defensive win shares) → analysis
    350: ('analysis', ''),

    # row 353: "It's not only Scottie's scoring production that's taken a dip. His attempts to score the ball have also plunged since February. Interestingly, the only months Scottie managed to sustain 20 ppg (October and January - although with varying efficiency), he also averaged over 15 field goal attempts."
    # stat-based analysis of Scottie Barnes production → analysis
    353: ('analysis', ''),

    # row 363: "Why do many NBA people ignore games missed? If a player misses a game, that's a huge negative to his team. Seems that people thing that per game stats are more important than total and that's incredibly foolish."
    # opinion about stat methodology ("incredibly foolish") with specific examples → hot_take
    363: ('hot_take', 'borderline hot_take/analysis: argues specific stat methodology point (totals vs per-game) but uses strong opinion framing ("incredibly foolish"); treated as hot_take'),

    # row 379: "Yes, the Sixers got blown out Sunday because they missed a lot of makeable shots. But it's also pretty crazy that they could've shot 83% on open threes and *still* lost that game"
    # specific stat (83% open 3s) used to argue a point about the game → analysis
    379: ('analysis', 'borderline analysis/commentary: specific counterfactual stat (83% on open 3s) used to make a point about Sixers game; treating as analysis'),

    # row 391: "I've been watching Rocco Zikarsky closely in Iowa. Here were my latest thoughts on him after January:"
    # scouting note → commentary (no stats shown in text)
    391: ('commentary', ''),

    # row 401: "The NBA player with the most career Win Shares is LeBron James, with 276.82. The NBA player with the fewest career Win Shares is Woody Sauldsberry, with -10.7. LeBron James has averaged 8.92 rebounds per playoff game. Woody Sauldsberry averaged 8.93 rebounds per playoff game."
    # fascinating stat comparison making a fun observation → analysis
    401: ('analysis', ''),

    # row 415: "The Spurs leading scorer in game five of the NBA Finals is a 20-year-old rookie who has 21-points on 76% true shooting"
    # stat highlighting in context of game → analysis (stat making a point about rookie performance)
    415: ('analysis', 'borderline analysis/commentary: specific stat (21 pts, 76% TS) highlighting remarkable rookie performance in NBA Finals; stat is doing the argumentative work'),

    # row 420: "Also, I know it's not exactly a radical notion, but: As someone with an awards ballot, potentially being unable to put a guy who's done all this, and who played 90 percent of his team's games before someone landed on his back, on *any* of the All-NBA teams seems extremely dumb."
    # opinion about awards process ("extremely dumb") with implicit stat reference (90% of games) → hot_take
    420: ('hot_take', 'borderline hot_take/analysis: argues about awards ballot criteria; "extremely dumb" is strong opinion framing; implicit stat (90% of games) is decoration not the point'),

    # row 425: "NBA-dot-com's defensive tracking (which, grain of salt) has IND shooting 5-for-14 against Jalen Brunson in Game 5: / IND scored 85.5 points-per-100 with Brunson the floor tonight / He contributed to the defensive effort. That's what they need."
    # specific stats to argue Brunson's defensive contribution → analysis
    425: ('analysis', ''),

    # row 439: "This man def got First Team All-NBA stats."
    # very brief opinion claim without stats shown → hot_take
    439: ('hot_take', 'borderline hot_take/commentary: brief subjective claim about All-NBA worthiness; no stats shown; treated as hot_take'),

    # row 447: "According to NBA stats there were 61 guards who took at least 2.5 shots in the paint per game last season. The median player shot 46%. 51. Harden - 34% / 55. Garland - 30%..."
    # stat breakdown with specific rankings → analysis
    447: ('analysis', ''),

    # row 449: "Just looking it up quickly, Kareem led NBA in win shares during Magic's first two seasons and then basically stayed in double digit win shares through 85-86. It's difficult to imagine a better 'win early' scenario..."
    # historical win shares analysis → analysis
    449: ('analysis', ''),

    # row 468: 'ME: "You have to be able to pass to be a good NBA player." YOU, A TRUE GENIUS: "Oh and that's all it takes?..."'
    # meta-commentary/rhetorical about NBA discourse → hot_take
    468: ('hot_take', 'borderline: rhetorical exchange about NBA analytics discourse; treated as hot_take due to subjective framing'),

    # row 477: "I derive my sports opinions from history and data across sports. This is an #NBA example of why the backhanded compliment #Orioles fans commonly give Elias... drafting high doesn't guarantee shit"
    # opinion about draft analytics using an NBA comparison → hot_take
    477: ('hot_take', ''),

    # row 479: "It IS funny, bc SGA plays in that building"
    # very short reaction, off-context → commentary
    479: ('commentary', ''),

    # row 482: 'When I say "elite defense" it's not an exaggeration. #DetroitBasketball #Pistons'
    # brief claim about team defense → hot_take
    482: ('hot_take', 'borderline hot_take/commentary: brief superlative claim about Pistons defense ("elite defense... not an exaggeration"); no stats shown; treated as hot_take'),

    # === SOURCE=COMMENTARY ROWS INCORRECTLY LABELED ===

    # row 7: "Ayo Dosunmu became just the fourth bench player to score at least 40 points in a playoff game since the NBA began tracking starters in 1970-71..."
    # historical stat comparison → analysis (stat is making a point about the feat's rarity)
    7: ('analysis', 'borderline analysis/commentary: historical stat (4th bench player with 40+ in a playoff game since 1970-71) is making a point about the rarity of the achievement; stat is argumentative'),

    # row 23: "Thanks GenAI for summarizing the recent #NBA game for me... Turns out the Blazers won against the Suns, but genAI thinks otherwise"
    # reporting on a game + complaining about AI → commentary
    23: ('commentary', ''),

    # row 29: "Look at this Orlando/Charlotte score. You can't tell me Orlando didn't throw that 76ers game."
    # accusatory conspiracy opinion → hot_take
    29: ('hot_take', ''),

    # row 45: "#NBA #FINALS Game1 Knicks vs. Spurs, 3rd quarter just ended, and the score is tied 76 to 76. I love this game (specifically). (I also constantly switch who I'm cheering for because I want them both to win.)"
    # game recap with fan reaction → commentary
    45: ('commentary', ''),

    # row 77: "Even against the Magic's full-strength defense, they still managed to score 27 points with a 65% TS% percentage. Boston has once again found a gem among two-way contract players."
    # specific stat (65% TS) to make a point about the player → analysis
    77: ('analysis', 'borderline analysis/commentary: specific stat (27 pts, 65% TS%) used to argue player value; "found a gem" is mild opinion but stat is doing the work'),

    # row 100: "33 points for Stephon Castle / 27 points for Dylan Harper / Only one other duo under the age of 21 had ever managed to score 25 points each in a single playoff game... Kevin Durant and Russell Westbrook"
    # historical stat comparison → analysis
    100: ('analysis', 'borderline analysis/commentary: historical comparison (only other <21 duo with 25+ each in a playoff game was KD/Westbrook) makes a point about the rarity; stat is argumentative'),

    # row 195: "Most points by any player in NBA history in their first 50 playoff games with a new franchise they were not drafted by (acquired via trade or signed with in free agency): 1. Jalen Brunson with NY: 1,746 2. Kareem Abdul-Jabbar with LA: 1,472 3. Shaquille O'Neal with LA: 1,446"
    # historical stat leaderboard making a point about Brunson → analysis
    195: ('analysis', ''),

    # row 311: "Every time I read about OKC I think 'This could have been our team' (Seattle). Another thought is 'Holy cow, Clippers, what a stupid trade (all those draft picks for Paul George)' along with 'If you had signed with the Lakers or Clippers instead of OKC, the NBA would be very different right now'."
    # opinion/opinion about team decisions → hot_take
    311: ('hot_take', ''),

    # row 323: "If you just signed a player in this free agency, can you even use them in trades? In the NBA you can't trade them until later in the season"
    # factual answer about trade rules → commentary
    323: ('commentary', ''),

    # row 330: "Cavs would score 150 points per game without turnovers #nba"
    # hyperbolic claim (not a real stat) → hot_take
    330: ('hot_take', 'borderline hot_take/commentary: hyperbolic counterfactual claim about Cavs scoring; treated as hot_take'),

    # row 378: "Every time I hear Landry Shamet I think about one of the best games I've watched, Shockers getting daggered in their final home game / #cbb to #nba"
    # nostalgic fan memory → commentary
    378: ('commentary', ''),

    # row 421: 'June 22, 1979 - "No basketball player is worth $800,000 a year, in my opinion," said Blazers guard Dave Twardzik, referencing the contract Bill Walton recently signed with the San Diego Clippers.'
    # historical quote → commentary (reporting what someone said)
    421: ('commentary', ''),

    # row 457: '#NBA What the everloving motherfuck? Just finished work, looked at the score, and my heart skipped a beat. I\'ve never seen this before.'
    # fan reaction to a game result → commentary
    457: ('commentary', ''),
}

for row_idx, (new_label, new_note) in corrections.items():
    df.at[row_idx, 'label'] = new_label
    df.at[row_idx, 'notes'] = new_note

df.to_csv('nba_posts.csv', index=False)

print('=== FINAL LABEL VALUE COUNTS ===')
print(df['label'].value_counts())
print()
print(f'Total rows: {len(df)}')
print(f'Rows with non-empty notes: {len(df[df["notes"].notna() & (df["notes"] != "")])}')
