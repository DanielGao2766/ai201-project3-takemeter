from atproto import Client
from dotenv import dotenv_values
import pandas as pd
import time

config = dotenv_values("env")
client = Client()
client.login(config["BLUESKY_HANDLE"], config["BLUESKY_APP_PASSWORD"])
print("Logged in successfully\n")

def fetch(query, tag, limit=80):
    rows, cursor = [], None

    while len(rows) < limit:
        params = {"q": query, "limit": 100, "lang": "en"}
        if cursor:
            params["cursor"] = cursor

        response = client.app.bsky.feed.search_posts(params)

        for post in response.posts:
            text = post.record.text.strip()
            if len(text) < 20:
                continue
            rkey = post.uri.split("/")[-1]
            rows.append({
                "text": text,
                "source": tag,
                "url": f"https://bsky.app/profile/{post.author.handle}/post/{rkey}",
                "label": ""
            })

        cursor = response.cursor
        if not cursor or not response.posts:
            break

        time.sleep(1)

    print(f"  [{tag}] {min(len(rows), limit)} posts collected")
    return rows[:limit]

rows = []

# commentary — neutral event and news posts
rows += fetch("#NBA game score",    "commentary_game",    80); time.sleep(3)
rows += fetch("NBA trade signed",   "commentary_trade",   60); time.sleep(3)
rows += fetch("NBA injury report",  "commentary_injury",  60); time.sleep(3)

# hot_take — bold opinions
rows += fetch("NBA overrated",      "hottake_overrated",  60); time.sleep(3)
rows += fetch("NBA unpopular take", "hottake_opinion",    60); time.sleep(3)
rows += fetch("NBA never wins",     "hottake_critique",   60); time.sleep(3)

# analysis — stat-backed posts
rows += fetch("NBA stats per game", "analysis_stats",     60); time.sleep(3)
rows += fetch("NBA true shooting",  "analysis_shooting",  60); time.sleep(3)
rows += fetch("NBA win shares",     "analysis_advanced",  60)

df = pd.DataFrame(rows).drop_duplicates(subset=["text"])
df = df.sample(frac=1, random_state=42).reset_index(drop=True)
df.to_csv("nba_posts.csv", index=False)

print(f"\nSaved {len(df)} total posts to nba_posts.csv")
if not df.empty:
    print(df["source"].value_counts().to_string())
