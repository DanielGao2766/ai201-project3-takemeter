"""
Fourth correction pass: final targeted fixes.
"""
import pandas as pd

df = pd.read_csv('nba_posts.csv')

corrections = {
    # row 205: OG Anunoby stat line with "second-highest true shooting percentage (93.5%) in a 30-point game in NBA Finals history"
    # historical stat comparison making a point → analysis
    205: ('analysis', 'borderline analysis/commentary: specific stats (33 pts, 10-15 FG, 7-9 3P, 93.5% TS) with historical claim (2nd highest TS% in 30-point NBA Finals game history); stat is doing argumentative work'),

    # row 228: "2nd year in the nba, first as a real starter, putting up great per game stats & cumulative stats but has some trouble against top talents at his position... Totally agreed, we can let this one cook! DC gonna be a beast"
    # analytical observation about player development → analysis
    228: ('analysis', 'borderline analysis/commentary: analytical observation about player development trajectory with mild opinion ("gonna be a beast"); treating as analysis since the developmental assessment is stat-based'),

    # row 50: "Cameron Payne put up the 3rd most efficient 30-point game in NBA history based on true shooting percentage (1.266)"
    # from rawchili, but the text itself is a historical stat claim making a point → analysis
    50: ('analysis', ''),
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
