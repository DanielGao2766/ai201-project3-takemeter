"""
Second correction pass:
Fix rows incorrectly labeled 'commentary' with the note
'borderline analysis/commentary: stat present but no clear argumentative use'
Many of these are actually clear 'analysis' posts (Win Shares lists, stat comparisons, etc.)
"""
import pandas as pd

df = pd.read_csv('nba_posts.csv')

BAD_NOTE = 'borderline analysis/commentary: stat present but no clear argumentative use; treating as recap'
ALSO_BAD = 'borderline analysis/commentary: stat reported as news/recap without explicit argument'

borderline_rows = df[
    (df['notes'] == BAD_NOTE) | (df['notes'] == ALSO_BAD)
].copy()

print(f"Rows to review: {len(borderline_rows)}")

# For each row, we'll decide: keep as commentary or switch to analysis
# Decision: if the post is presenting stats to make a point or comparing players → analysis
# If the post is just a game score/recap with incidental stat → commentary

def reclassify_borderline(row):
    text = str(row['text'])
    tl = text.lower()

    # Win Shares lists from gm-associate type posts → analysis (stat IS the point)
    if 'win shares' in tl and ('most productive' in tl or 'per basketball reference' in tl):
        return 'analysis', ''

    # Offensive/defensive rating breakdowns with comparisons → analysis
    if ('offrtg' in tl or 'defrtg' in tl or 'offensive rating' in tl or 'defensive rating' in tl) and '%' in text:
        return 'analysis', ''

    # True Shooting comparisons, historical stat lists → analysis
    if 'true shooting' in tl and ('history' in tl or 'all.?time' in tl or 'consecutive' in tl or 'highest' in tl or 'lowest' in tl):
        return 'analysis', ''

    # Posts that present a stat leaderboard/ranking as their main content → analysis
    if any(phrase in tl for phrase in [
        'leads the nba', 'ranks first', 'ranks second', 'ranks third',
        'top true shooting', 'most productive', 'highest true shooting',
        'per 48', 'per 36', 'per 100', 'win shares/36', 'win shares/48',
        'all-time record', 'nba history', 'in nba history',
        'first player to', 'only player to', 'only team to',
        'surpassing', 'passing', 'topped',
        'since 19', 'since 20',  # "since 1976", "since 2015"
    ]):
        return 'analysis', ''

    # Posts with multiple specific stats used to paint a picture → analysis
    stat_count = sum(1 for s in [
        '%', 'pts', 'ppg', 'rpg', 'apg', 'spg', 'blk', 'fg', '3p', 'ft',
        'points per game', 'rebounds per game', 'assists per game',
        'win shares', 'true shooting', 'per game',
    ] if s in tl)

    if stat_count >= 3:
        return 'analysis', ''

    # "Games evolve. In the 1987 playoffs, teams averaged 5.5 3PT attempts per game." → analysis (stat makes a point)
    if '3pt' in tl or '3-point' in tl or '3p attempts' in tl:
        return 'analysis', ''

    # "Seven NBA teams have more bench points per game than the Lakers and Knicks combined" → analysis
    if 'more bench points' in tl or 'bench points per game' in tl:
        return 'analysis', ''

    # "also the NBA is unique in where for the most part we look at per game stats" → analysis/commentary
    if 'per game stats more so than total accumulation' in tl:
        return 'analysis', 'borderline analysis/commentary: analytical observation about NBA stat conventions, no specific player stats; treated as analysis'

    # "Because these results were so unusual, I compared the NBA game books..." with specific stat mention → analysis
    if 'game books' in tl and 'dunks' in tl:
        return 'analysis', ''

    # Pistons hustle stats per game this season (very short, just a tag) → analysis
    if 'pistons hustle stats per game' in tl:
        return 'analysis', ''

    # "They've fallen off lately but still currently tied for highest scoring offense" → analysis (stat claim)
    if 'highest scoring offense' in tl or 'tied for highest' in tl:
        return 'analysis', ''

    # "It's situationally dependent. NBA teams often have four guys on the court shooting 35% or better from 3" → analysis
    if 'shooting 35%' in tl or '35% or better' in tl:
        return 'analysis', ''

    # "Keaton Wagler (blue) vs Tyrese Haliburton (purple) / NBA Draft Stat Visualization Tool" → analysis
    if 'stat visualization' in tl or 'nbadraftcomp' in tl:
        return 'analysis', ''

    # "RE: that talent, it's time to repost my favorite stat... only 12 players in NBA history to be over .600 TS%" → analysis
    if '.600 ts%' in tl or 'only 12 players' in tl:
        return 'analysis', ''

    # "At least in the WNBA and NBA, from what I remember, top guard stat criteria: 55+% Effective Field Goal" → analysis
    if 'effective field goal' in tl and '55+%' in tl:
        return 'analysis', ''

    # "Career Allen .201 / Career Curry .195 / Take time to read about Win Shares" → analysis
    if 'career allen' in tl or ('career curry' in tl and 'win shares' in tl):
        return 'analysis', ''

    # "Might be inventing a guy to get mad at but I feel like Pistol Pete... avg 24/4/5 over a ten year NBA career"
    # Has opinion phrasing + stat → this is actually a hot_take (opinion with stat as decoration)
    if 'might be inventing a guy' in tl or 'pistol pete' in tl:
        return 'hot_take', 'borderline hot_take/analysis: opinion framing leads ("might be inventing a guy to get mad at"); stat (24/4/5) is present but functions as supporting decoration for the opinion'

    # If none of the above matched, keep as commentary
    return 'commentary', BAD_NOTE


for idx in borderline_rows.index:
    row = df.loc[idx]
    new_label, new_note = reclassify_borderline(row)
    df.at[idx, 'label'] = new_label
    df.at[idx, 'notes'] = new_note

df.to_csv('nba_posts.csv', index=False)

print('=== UPDATED LABEL VALUE COUNTS ===')
print(df['label'].value_counts())
print()
print(f'Total rows: {len(df)}')
print(f'Rows with non-empty notes: {len(df[df["notes"].notna() & (df["notes"] != "")])}')
