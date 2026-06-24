"""
Label NBA posts CSV with hot_take / analysis / commentary.
Classification is based purely on post text content, following the definitions
in planning.md and the task prompt decision rules.

hot_take:  Bold subjective claim/judgment not primarily supported by verifiable
           evidence, OR provocative/accusatory framing. Presence of opinion words
           ("overrated", "trash", "choke", "worst", "never wins", "best ever")
           strongly signal hot_take.

analysis:  Presents a specific, verifiable statistic/dataset to support or
           demonstrate a point about player or team performance, where the data is
           doing genuine argumentative work — not just decorating a sentence.
           The stat must BE the point, not window dressing.

commentary: Reports on events, news, or outcomes in a largely neutral/descriptive
            manner — no subjective judgment and no stat-based argument. Game recaps,
            injury reports, trade news, score updates.
"""

import pandas as pd
import re

df = pd.read_csv('nba_posts.csv')

# ============================================================================
# SIGNAL WORD LISTS
# ============================================================================

# Hot-take opinion signals — words that strongly indicate a subjective judgment
OPINION_WORDS = [
    'overrated', 'underrated', 'trash', 'choke', 'never wins',
    'best ever', 'greatest of all time', 'greatest ever',
    'unpopular take', 'unpopular opinion', 'hot take',
    'die on the hill', 'no heart', 'washed', 'overhyped',
    'is soft', 'is the worst', 'the worst contract',
    'most overrated', 'most underrated', 'douchebag',
    'phuck', 'fuck off', 'never been more parity',
    'never cared less', 'is a nothing', 'completely wrong',
    'shouldn\'t be', 'should never', 'will never recover',
    'conspiracy brain', 'cooked', 'most miserable',
    'never happy', 'boring', 'most overrated',
    'biggest douchebag', 'ridiculous', 'stupid trade',
    'obvious', 'painfully obvious',
]

# Strong opinion phrases (multi-word)
OPINION_PHRASES = [
    'i think', 'i believe', 'in my opinion', 'my take is',
    'my opinion is', 'die on the hill', 'i will forever',
    'will forever', 'i\'ve never seen', 'i never watch',
    'i don\'t need', 'i\'m old enough to remember',
    'i don\'t think', "i can't see", "i can't believe",
    "i cannot believe", "i\'d say", "i\'d take",
    'could have been', 'this is the problem',
    'is the most overrated', 'is the most underrated',
    'is clearly', 'proves that', 'shows that',
    "it's about time", "it's time to stop",
    "no one outside of", "no idea of the context",
    "never get", "he has never", "she has never",
    "he will never", "she will never",
    "you can't tell me", "can't tell me",
    "doesn't deserve", "never deserved",
    "is absurd", "is absolutely", "is painfully",
    "absolutely sending me", "this team has no",
    "i\'m not interested", "i don\'t want",
    "glad his true nature is",
    "weird framing", "clearly been overrated",
    "clearly the best", "clearly been",
    "this team doesn't belong",
    "i hope he never", "i hope they never",
    "he will always be", "she will always be",
    "legacy secured", "i joke but",
    "i\'d have to look at",
    "probably the most",
    "never got them a title",
    "never got him a title",
    "never a radical notion",
    "should be a", "should have been a",
    "if you just signed", "i stg",
    "fuck off forever",
    "if i had to guess",
    "let me tell you",
    "everybody loses",
    "obviously", "absurd",
    "is the land of",
    "that shit is",
    "give me", "save that shit",
    "this team is fun",
    "good on them",
    "went all in on the righteous",
    "is overrated", "are overrated",
    "is underrated", "are underrated",
    "has no heart", "had no heart",
    "complete choke", "choke job",
    "is a cheat", "cheater",
    "is a gem", "found a gem",  # "gem" can be opinion
    "you say this as if",
    "i was never one of those people",
    "another thought is",
    "every time i",
    "for those who don't remember",
    "for those who don",
    "can assure you",
    "i am trying to figure out",
    "i can assure",
    "i love", "i hate",
    "bizarrely", "extremely dumb",
    "looks even worse",
    "is bad news",
    "sounds too convenient",
    "gets even better",
    "bad news for",
    "disappoints fans",
    "brutally obvious",
    "wrong to say",
    "the best news from the nba",
    "is the most efficient",
    "is a good bet",
    "great offenses before",
    "before masai",
    "biggest collapse",
    "vindicating wins in nba history",
]

# Stat/analysis signal patterns
STAT_PATTERNS = [
    r'\b\d+\.?\d*\s*%',                          # percentages
    r'\b\d+\.\d+\s*(ppg|rpg|apg|spg|bpg)',       # per-game stats
    r'true shooting',                              # TS%
    r'win shares',                                 # Win Shares
    r'ts%',                                        # TS% abbreviation
    r'efg%',                                       # eFG%
    r'per 48',                                     # per-48
    r'per 36',                                     # per-36
    r'per 100',                                    # per-100
    r'box plus.?minus|bpm',                        # BPM
    r'value over replacement|vorp',                # VORP
    r'player efficiency|per\b',                    # PER
    r'defensive rating|offensive rating|net rating', # ratings
    r'win shares/48|ws/48',                        # win shares per 48
    r'\b\d+/\d+/\d+\b',                           # slash lines
    r'points per game|rebounds per game|assists per game',
    r'field goal percentage|fg%',
    r'three.?point percentage|3p%|3pt%',
    r'free throw percentage|ft%',
    r'leads (the|all) nba',
    r'first in nba history|second in nba history|third in nba history',
    r'in nba history',
    r'highest.*nba|lowest.*nba',
    r'ranked (first|second|third|#\d)',
    r'averaging \d+',
    r'\d+ (points?|rebounds?|assists?|steals?|blocks?) (per game|a game|on)',
    r'\d+\s*(pts?|reb|ast|stl|blk)\b',
    r'number \d+ in',
    r'\d+\s*wins?\b.*\d+\s*losses?\b',             # win-loss record
    r'career high',
    r'all.?time (record|high|low)',
    r'nba record',
    r'since.*\d{4}',                               # "since 2015"
]

def has_opinion_signal(text_lower):
    """Check for opinion/hot-take language."""
    if any(w in text_lower for w in OPINION_WORDS):
        return True
    if any(ph in text_lower for ph in OPINION_PHRASES):
        return True
    return False

def has_stat_argument(text):
    """Check for stats that might be doing argumentative work."""
    tl = text.lower()
    return any(re.search(p, tl) for p in STAT_PATTERNS)

def count_stat_patterns(text):
    tl = text.lower()
    return sum(1 for p in STAT_PATTERNS if re.search(p, tl))

def is_rawchili_article(text):
    """Check if this is a rawchili.com article repost (headline + URL)."""
    return 'rawchili.com' in text and bool(re.search(r'https?://', text))


def classify(text):
    """Returns (label, note) based on text content only."""

    if pd.isna(text) or str(text).strip() == '':
        return 'commentary', 'empty text'

    text = str(text)
    tl = text.lower()

    # =========================================================================
    # STEP 0: Off-topic / noise — classify as closest fit with note
    # =========================================================================
    if 'nba jam is the most overrated game' in tl:
        return 'hot_take', 'off-topic: about the NBA Jam video game, not NBA players/teams'

    if ('gta 5' in tl or 'gta5' in tl) and 'absurd game for' in tl:
        return 'commentary', 'off-topic: appears to be about a video game'

    if 'ff7 sucks' in tl or ('far too long on this' in tl and 'ff7' in tl):
        return 'commentary', 'off-topic: about video game rankings, not NBA'

    if 'about me: video games' in tl:
        return 'commentary', 'off-topic: personal intro post unrelated to NBA'

    if 'retro games' in tl and 'mario kart' in tl:
        return 'commentary', 'off-topic: about gaming/entertainment, not NBA'

    if ('twitter probably wins' in tl or 'twitter' in tl) and 'dumbest social media user base' in tl:
        return 'commentary', 'off-topic: about social media platforms, not NBA'

    if 'spacex shares climb' in tl or 'jaxa schedules h3 rocket' in tl:
        return 'commentary', 'off-topic: multi-topic news aggregator post'

    if 'monday mailbag' in tl and 'masters' in tl and 'overrated' in tl:
        return 'commentary', 'borderline: newsletter roundup with multiple non-NBA topics; predominantly descriptive'

    # "Saw this on the skyline and figured it might be fun." — unclear context
    if 'saw this on the skyline and figured it might be fun' in tl:
        return 'commentary', 'off-topic or unclear: very short post with no NBA content visible'

    # "Oh this one is good. Will I stand by these tomorrow? Unknowable / MANY NOTES AND CAVEATS"
    if 'will i stand by these tomorrow' in tl and 'unknowable' in tl:
        return 'commentary', 'off-topic: about personal rankings of unspecified items, not NBA'

    # "This took some time, but it was really fun! About me: video games"
    if 'about me: video games' in tl or ('took some time' in tl and 'grids.fun' in tl):
        return 'commentary', 'off-topic: personal intro/video game grid, not NBA'

    # =========================================================================
    # STEP 1: rawchili.com article reposts → commentary in almost all cases
    # =========================================================================
    if is_rawchili_article(text):
        # These are article headline + URL reposts
        # Even if "overrated" is in the headline, the POST itself is just reporting
        # on an article — not the author expressing their own opinion.
        # Exception: if the post adds personal commentary beyond the headline/URL.
        lines = [l.strip() for l in text.strip().split('\n') if l.strip()]
        # Check if there's personal commentary beyond the headline + URL + snippet
        # Personal commentary: "i think", "i believe", first person opinion beyond 1 line
        personal_lines = []
        for line in lines:
            ll = line.lower()
            if any(ph in ll for ph in ['i think', 'i believe', 'in my opinion', 'i can assure',
                                         "couldn't disagree more", "i disagree", "here's my",
                                         "i\'d say", "i personally"]):
                personal_lines.append(line)
        if personal_lines:
            # Has personal opinion → could be hot_take
            # But still anchored in an article repost → commentary
            # Per task: "rawnba.bsky.social posts are article headline + URL reposts, nearly always commentary"
            pass
        return 'commentary', ''

    # =========================================================================
    # STEP 2: Identify stat presence and opinion presence
    # =========================================================================
    has_stat = has_stat_argument(text)
    stat_count = count_stat_patterns(text)
    has_opinion = has_opinion_signal(tl)

    # =========================================================================
    # STEP 3: Injury report posts → commentary (unless personal opinion added)
    # =========================================================================
    injury_signals = [
        'injury report', 'listed as', 'questionable to play', 'doubtful to play',
        'is out for', 'out for the', 'on the injury report', 'injury update',
        'injury designation', 'injury status',
    ]
    is_injury_post = any(sig in tl for sig in injury_signals)

    if is_injury_post and not has_opinion:
        return 'commentary', ''

    # =========================================================================
    # STEP 4: Trade news posts → commentary
    # =========================================================================
    trade_news_signals = [
        'trade deadline', 'trade season', 'eligible to be traded',
        'officially eligible to be traded', 'trade rumors',
        'trade block', 'trade target', 'trade package', 'signed over the summer',
        '82 nba players who signed', 'became eligible to be traded',
        'marks the unofficial start of the nba trade season',
        '10-day deal', '10-day contract', 'two-way contract',
        'buyout market', 'waive', 'no-trade clause',
        'officially eligible', 'players who signed this past offseason',
    ]
    is_trade_news = any(sig in tl for sig in trade_news_signals)

    if is_trade_news and not has_opinion and not has_stat:
        return 'commentary', ''

    # =========================================================================
    # STEP 5: Pure live game commentary → commentary
    # =========================================================================
    live_game_exclamation = [
        'and that will do it', 'advances to the next round', 'wins the series',
        'wins the game', 'wins game', 'wins the thriller',
        'knicks win', 'spurs win', 'cavs win', 'pistons win', 'blazers win',
        'rockets win', 'magic win', 'thunder win', 'warriors win',
        'AND THAT WILL DO IT',
        'final score', 'final score game',
        'buckle up', '#postseason', '#nbaplayoffs', '#nbafinals', '#thefinals',
        'off we go', 'with that, off we go',
        'and it\'s a', 'point lead', 'point game',
        'and that forces', 'timeout',
        'and halftime', "that's it for the half",
        "that's it for the first quarter",
        "that's it for the third quarter",
        "that's the end of the",
        "and that's the end",
        "first quarter", "third quarter",
        "AND OFF WE GO",
    ]
    is_live_game = any(sig in tl for sig in live_game_exclamation) or \
                   any(sig in text for sig in live_game_exclamation)

    # If clearly a live game post with exclamation marks and no stat argument
    exclamation_count = text.count('!')
    if is_live_game and exclamation_count >= 2 and not has_opinion:
        return 'commentary', ''
    if is_live_game and not has_opinion and not has_stat:
        return 'commentary', ''

    # =========================================================================
    # STEP 6: Score/result announcements → commentary
    # =========================================================================
    score_result_signals = [
        r'\b\d+-\d+\b',   # scores like 94-90
    ]
    has_score = any(re.search(p, tl) for p in score_result_signals)
    if has_score and is_live_game and not has_opinion:
        return 'commentary', ''

    # =========================================================================
    # STEP 7: Analysis vs hot_take vs commentary — main decision logic
    # =========================================================================

    # --- Stat present + Opinion present → need to determine which dominates ---
    if has_stat and has_opinion:
        # Per the decision rule:
        # "If you remove the opinion framing and the stat still stands as a real argument → analysis"
        # "If the stat is cherry-picked, vague, or just there to sound credible → hot_take"

        # Count strong opinion indicators
        strong_opinion_count = sum(1 for w in [
            'overrated', 'underrated', 'trash', 'worst', 'choke', 'best ever',
            'greatest ever', 'greatest of all time', 'goat', 'washed',
            'i think', 'i believe', 'unpopular', 'hot take', 'die on the hill',
            'should never', 'is the problem', 'no heart', 'most miserable',
            'is soft', 'absurd', 'ridiculous', 'most overrated',
        ] if w in tl)

        # High stat count + low opinion count → analysis
        if stat_count >= 4 and strong_opinion_count <= 1:
            return 'analysis', ''
        if stat_count >= 3 and strong_opinion_count == 0:
            return 'analysis', ''

        # Low stat count + high opinion count → hot_take
        if stat_count <= 1 and strong_opinion_count >= 2:
            return 'hot_take', ''

        # Mixed: check if opinion leads (hot_take) or stat leads (analysis)
        first_150 = tl[:150]
        opinion_leads = any(w in first_150 for w in [
            'overrated', 'underrated', 'i think', 'i believe', 'unpopular',
            'die on the hill', 'hot take', 'worst', 'trash', 'choke',
            'greatest', 'goat', 'best ever', 'washed', 'is soft',
            'most overrated', 'most underrated', 'cooked',
        ])

        if opinion_leads and stat_count <= 2:
            return 'hot_take', 'borderline hot_take/analysis: opinion framing leads; stat present but serves as support/decoration for the opinion'
        elif not opinion_leads and stat_count >= 2:
            return 'analysis', 'borderline analysis/hot_take: stat-first structure with opinion conclusion; stat is doing genuine argumentative work'
        elif opinion_leads and stat_count >= 3:
            return 'analysis', 'borderline analysis/hot_take: multiple specific stats present despite opinion framing; stats do genuine argumentative work'
        else:
            return 'hot_take', 'borderline hot_take/analysis: both opinion and stat present; opinion framing appears to dominate'

    # --- Stat present, no opinion → likely analysis ---
    if has_stat and not has_opinion:
        # Check if stat is being used to argue a point, or just reported as news
        # "Jokic averaged 27/13/10" alone = commentary
        # "Jokic's 27/13/10 makes him the greatest center ever" = analysis

        # Signals that stat is ARGUMENTATIVE (analysis):
        argumentative_signals = [
            r'makes (him|her|them|it)',
            r'(is|are|was|were) the (best|greatest|worst|most|highest|lowest|first|second|third|only)',
            r'proves?', r'shows?', r'demonstrates?',
            r'(ever|in nba history|all.?time)',
            r'surpass(ing|es|ed)',
            r'most efficient',
            r'ahead of',
            r'compared to',
            r'higher than',
            r'greater than',
            r'more than',
            r'(record|streak|consecutive)',
            r'no (player|team|coach) (has|have)',
            r'only (player|team|coach)',
            r'first (player|team|coach)',
            r'ranks (first|second|third|#)',
            r'leads (all|the) nba',
            r'top \d+',
            r'since \d{4}',
            r'since (the|last)',
            r'best.*rookie',
            r'worthy of',
            r'deserves?',
        ]
        has_argumentative = any(re.search(p, tl) for p in argumentative_signals)

        # Signals that stat is just NEWS (commentary):
        news_signals = [
            'failed to score', 'last night', 'tonight', 'this morning',
            'is averaging', 'posted a', 'scored.*points', 'had.*points',
            'is officially', 'has been removed', 'is listed',
            'is probable', 'is questionable',
        ]
        has_news_framing = any(sig in tl for sig in news_signals)

        if has_argumentative:
            return 'analysis', ''
        elif has_news_framing and not has_argumentative:
            return 'commentary', 'borderline analysis/commentary: stat reported as news/recap without explicit argument'
        elif stat_count >= 3:
            # Multiple stats, likely doing real work
            return 'analysis', ''
        else:
            # Single stat, not clearly argumentative → commentary
            return 'commentary', 'borderline analysis/commentary: stat present but no clear argumentative use; treating as recap'

    # --- Opinion present, no stats → hot_take ---
    if has_opinion and not has_stat:
        return 'hot_take', ''

    # --- No stats, no opinion → commentary ---
    return 'commentary', ''


# ============================================================================
# Apply to all rows
# ============================================================================
labels = []
notes = []

for _, row in df.iterrows():
    label, note = classify(row['text'])
    labels.append(label)
    notes.append(note)

df['label'] = labels
df['notes'] = notes

df.to_csv('nba_posts.csv', index=False)

print("=== LABEL VALUE COUNTS ===")
print(df['label'].value_counts())
print()
print(f"Total rows: {len(df)}")
print(f"Rows with notes: {len(df[df['notes'] != ''])}")
