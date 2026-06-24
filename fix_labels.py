"""
Manual correction pass for edge-case rows after text-based classification.
"""
import pandas as pd

df = pd.read_csv('nba_posts.csv')

# Manual corrections: {row_index: (new_label, new_note)}
corrections = {
    # row 8: 'Paul was already toast defensively...' - critical judgment of team/management decisions
    8: ('hot_take', ''),

    # row 43: 'Tyler Hansbrough. Roy Hibbert...' - narrative opinion about Pacers draft strategy
    43: ('hot_take', ''),

    # row 68: 'You are like one of the 3 smartest guys I know about the NBA...'
    # fan reaction expressing admiration + frustration; not a take on NBA performance
    68: ('commentary', ''),

    # row 130: 'Dick Cheney never got to find out who wins the 2025 Emirates NBA Cup either'
    # humorous political remark, not about NBA performance
    130: ('commentary', 'off-topic: political/humorous remark, not NBA analysis or opinion about players'),

    # row 132: 'Unpopular NBA opinion: Clear path and transition take fouls need to GO'
    132: ('hot_take', ''),

    # row 187: fan intro post with 'Unpopular NBA take: Houston would have beat Chicago in 95'
    187: ('hot_take', ''),

    # row 194: 'Rick Adelman, the NBAs greatest coach who never won a title, died at 79.'
    # 'greatest coach who never won a title' is a subjective judgment claim
    194: ('hot_take', 'borderline hot_take/commentary: tribute to Rick Adelman; "greatest coach who never won a title" is subjective judgment embedded in what otherwise reads as an obituary note'),

    # row 201: '@cbssports Your #1 & #10 need to be swapped. Comically biased listing.'
    201: ('hot_take', ''),

    # row 221: 'Having never played postseason basketball, Tyrese Haliburton now takes his team to the Finals of the NBA Cup...'
    # reporting his achievements (facts) - neutral descriptive
    221: ('commentary', ''),

    # row 241: 'NBA players never seem that excited to win a championship. Their on court celebration is so muted...'
    # subjective opinion comparing NBA to NHL
    241: ('hot_take', ''),

    # row 245: 'New at Celtics On SI: Why the Boston Celtics Are Never Surprised By Wins, Even When Everyone Else Is'
    # article link post
    245: ('commentary', ''),

    # row 270: 'Ziller goes into very specific detail about how it works in the NBA here but this is always a good bet'
    # vague reference to an article, no opinion or stat
    270: ('commentary', ''),

    # row 275: 'It is possible that Georgia Tech basketball will never provide me a moment of joy like this again. I hope Jose wins an NBA title'
    # personal emotional fan reaction - commentary
    275: ('commentary', ''),

    # row 283: 'I know that Twitter probably wins, but dont discount Threads for having the dumbest social media user base.'
    # off-topic about social media
    283: ('commentary', 'off-topic: about social media platforms, not NBA'),

    # row 288: 'Spurs go undefeated in February (11-0), hottest team in the NBA right now'
    # reporting team record with mild opinion tag - borderline commentary
    288: ('commentary', 'borderline commentary/hot_take: reporting 11-0 February record with mild superlative ("hottest team"); predominantly factual'),

    # row 362: political opinion using Knicks win as pretext
    362: ('hot_take', 'off-topic: political opinion using Knicks championship as pretext; not about NBA basketball performance'),

    # row 370: 'Yall complaining about how hard it has been to watch the NBA this year.'
    # subjective opinion about NBA watchability/distribution
    370: ('hot_take', ''),

    # row 382: 'Hall of Famer Lenny Wilkens will never be forgotten by the #NBA community. Wilkens, who died at 88...'
    # tribute/obituary - descriptive with neutral tone
    382: ('commentary', 'borderline commentary/hot_take: tribute to Lenny Wilkens; descriptive tone; treated as commentary'),

    # row 397: 'TOMBSTONE WINS / You will never reconcile those two approaches because the NBA is a 30-team partnership'
    # cryptic argument about NBA competitive structure
    397: ('hot_take', 'borderline: cryptic argument about NBA team competition structure with subjective framing'),

    # row 431: fan intro post with 'Unpopular NBA opinion: Id take drafting Darko + championship over Melo'
    431: ('hot_take', ''),

    # row 442: rawchili.com article - already ruled as commentary via rawchili check but slipped through
    442: ('commentary', ''),

    # row 445: newsletter roundup with multiple topics including NBA finals prediction
    445: ('commentary', 'borderline: newsletter roundup mixing NBA and non-NBA topics; primarily a table of contents post'),

    # row 465: rawchili.com article - already ruled
    465: ('commentary', ''),

    # row 472: 'Unpopular NBA take. Its illegitimate to take a long jumper in a key situation...'
    472: ('hot_take', ''),

    # row 473: 'Leeds were once the biggest club in England. Chicago were once the biggest team in the NBA...'
    # multi-sport opinion about winning and team cycles
    473: ('hot_take', ''),
}

# Corrections for rows incorrectly labeled hot_take (should be analysis or commentary)
analysis_corrections = {
    # row 143: 'In the context of the story, Im referring to Brook Lopezs defensive peak...'
    # analytical clarification using stats reference
    143: ('analysis', 'borderline analysis/commentary: contextual analytical point about defensive peak; stat context doing work'),

    # row 259: 'This is a crudely made Google Docs table I created but yeah, Id say the OKC defense is that good.'
    259: ('analysis', 'borderline analysis/hot_take: "I\'d say" triggers opinion signal but post presents a data table to support the OKC defense claim; treating as analysis'),

    # row 274: 'I think that rumor about Ben Stiller shooting a Knicks NBA Finals documentary on his iPhone are true'
    274: ('commentary', 'off-topic: about a documentary rumor, not NBA performance'),

    # row 334: 'I know scoring efficiency has trended up...but what Kon Knueppel is doing this season is absurd. / 176 players in Bball Reference...'
    334: ('analysis', 'borderline analysis/hot_take: "absurd" triggers opinion signal but the post presents a specific stat comparison (best TS% among 176 rookies averaging 15+ ppg) as the actual argument'),

    # row 427: cites study about player stats (PER, minutes) post-injury
    427: ('analysis', 'borderline analysis/hot_take: "kills me" triggers opinion signal but post cites a study about PER recovery post-injury; stat is doing genuine argumentative work'),

    # row 492: stat translation piece about Jamal Crawford scoring 20 in today\'s NBA
    492: ('analysis', 'borderline analysis/commentary: shares a stat translation comparing per-game stats across eras; the comparison is the point of the post'),
}

# Apply all corrections
for row_idx, (new_label, new_note) in corrections.items():
    df.at[row_idx, 'label'] = new_label
    df.at[row_idx, 'notes'] = new_note

for row_idx, (new_label, new_note) in analysis_corrections.items():
    df.at[row_idx, 'label'] = new_label
    df.at[row_idx, 'notes'] = new_note

df.to_csv('nba_posts.csv', index=False)

print('=== FINAL LABEL VALUE COUNTS ===')
print(df['label'].value_counts())
print()
print(f'Total rows: {len(df)}')
print(f'Rows with notes: {len(df[df["notes"] != ""])}')
print()
print('=== SAMPLE SPOT CHECK ===')
for idx in [8, 43, 132, 187, 241, 259, 334, 427, 472, 491]:
    row = df.iloc[idx]
    t = str(row['text'])[:90].encode('ascii', 'replace').decode()
    print(f'row {idx} label={row["label"]}: {t}')
