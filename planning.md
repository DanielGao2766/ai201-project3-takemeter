# TakeMeter — planning.md

> Complete this document before writing any implementation code.
> Your spec and agent diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Your planning.md will be reviewed as part of your submission.
> Update it before starting any stretch features.

---

## Community

I chose the NBA Basketball community because it has a large, active social media presence driven by ongoing competition, trades, drafts, and player narratives. Posts range from breaking news to heated debate to deep statistical analysis, which creates the natural label variety a classification task needs.

The NBA community is a strong fit for classification because its discourse spans genuinely distinct modes: fans state bold opinions with little evidence, analysts build arguments from box-score data, and reporters relay game outcomes neutrally. These modes are distinct enough to draw a real boundary between them yet close enough that ambiguous posts exist — exactly the kind of variation that makes a classifier useful and non-trivial. A community where every post sounds the same would produce a trivial task; one where every post is unique would produce an impossible one. NBA discourse sits in the productive middle.

---

## Labels

**hot_take**: A post is labeled `hot_take` if it expresses a bold, subjective claim or judgment about a player, team, or league that is not primarily supported by verifiable evidence, or uses accusatory or provocative framing to advance an opinion.

Example 1:
> "I thought the wizards front office was smart now? I don't think I've ever been more surprised by a contract than what Trae just got. 4 years and more annually than his extension was worth and the last year is a player option? Might as well give AD $400 million next."

Example 2:
> "Larry Bird would dominate today's NBA. The league is soft and the analytics crowd would never appreciate what he brought. #NBA"

---

**analysis**: A post is labeled `analysis` if it presents a specific, verifiable statistic or dataset to support or demonstrate a point about player or team performance, where the data is doing genuine argumentative work rather than serving as decoration.

Example 1:
> "During this year's playoffs, Victor Wembanyama recorded 77 defensive stops — no player has recorded more in a single playoff run since the 2010-11 season. Wembanyama now holds both the regular season (2023-24) and postseason (2026) records. Defensive Stops = offensive fouls drawn + charges drawn + steals + blocks recovered by the defense."

Example 2:
> "Steph Curry leads all active players in points-per-game in elimination games at 31.2 PPG, ahead of LeBron (28.8) and Durant (28.3). The numbers say he's at his best when it matters most. #NBAPlayoffs"

---

**commentary**: A post is labeled `commentary` if it reports on events, news, or outcomes in a largely neutral or descriptive manner, without making a subjective judgment or citing statistics to build an argument.

Example 1:
> "THE NEW YORK KNICKS ARE YOUR 2026 NBA CHAMPIONS. The Knicks beat the Spurs 94-90 to secure the NBA championship. Congratulations to the New York Knicks and their fans!"

Example 2:
> "Trae Young plans to sign a four-year, $212 million deal to stay with the Washington Wizards. Player option in Year 4. #NBA"

---

## Hard Edge Cases

**hot_take vs. analysis**: "LeBron is overrated — his playoff win rate against top-seeded opponents is below .500."

Decision rule: If the post provides specific, verifiable evidence that would support the claim even if you removed the opinion framing, label it `analysis`. If the evidence is vague, cherry-picked, or decorative — just enough to sound credible but not genuinely reasoning — label it `hot_take`. The one-stat post above is borderline; the framing is accusatory and the stat is selected for effect rather than as part of an argument. → `hot_take`.

---

**hot_take vs. commentary**: "Can't believe the Celtics gave up that lead in Game 7. Complete choke job, this team has no heart."

Decision rule: If a post about an event includes opinion or judgment words (e.g., "overrated," "trash," "choke," "best ever," "no heart") that express the author's evaluation, label it `hot_take`. If the post describes what happened without a personal verdict on it, label it `commentary`. The example above describes a real event but the "choke job / no heart" judgment makes it `hot_take`.

---

**analysis vs. commentary**: "Nikola Jokic finished the regular season averaging 27.1 PPG, 13.7 RPG, and 10.4 APG — his fourth consecutive season averaging a triple-double."

Decision rule: If a post cites a specific statistic to support a point or draw a conclusion about performance, label it `analysis`. If it reports numbers as part of a factual recap without using them to argue anything, label it `commentary`. The example above reports stats as news without an accompanying argument → `commentary`. If the post added "making him the greatest offensive center in NBA history," the stat would now serve an argument → `analysis`.

---

## Data Collection Plan

I will collect examples from Bluesky using the public search API (`public.api.bsky.app`), which requires no authentication or API key. Reddit and X were originally planned but both block unauthenticated programmatic access.

**Target volume**: 300 total posts collected; label at least 50 per class after filtering.

**Collection strategy** (automated via `collect.py`):
- For `commentary`: Queries like `#NBA game score`, `NBA trade signed`, `NBA injury report` — surface neutral event/news posts.
- For `hot_take`: Queries like `NBA overrated`, `NBA unpopular take`, `NBA never wins` — surface opinion-forward posts.
- For `analysis`: Queries like `NBA stats per game`, `NBA true shooting`, `NBA win shares` — surface stat-backed posts.

The script deduplicates by post text and shuffles the output before saving to `nba_posts.csv`. The `source` column records which query produced each post, which helps identify collection bias during annotation.

**If a label is underrepresented**: If any label has fewer than 50 labelable examples after the annotation pass, add new search queries targeting that label's signal words (e.g., `"NBA advanced stats"` or `"NBA per 36"` for analysis) and re-run `collect.py`. Do not relabel borderline posts just to hit a quota.

---

## Evaluation Metrics

**Primary metric: macro F1** — averages F1 across all three classes, treating each class equally regardless of how many examples it has. This is the right primary metric because the three labels may not be perfectly balanced in the real world, and I don't want the model to look good just by predicting the dominant class.

**Secondary metrics: per-class precision, recall, and F1** — reported separately for `hot_take`, `analysis`, and `commentary`. These let me see where the model specifically struggles. For example, if `analysis` has high precision but low recall, the model is conservative about labeling analysis posts — useful to know for a real deployment where missing analysis posts would be a problem.

**Confusion matrix** — to identify which label pairs the model most often confuses (e.g., `hot_take` vs. `analysis`), which connects back to the hard edge cases identified during design.

Accuracy alone is not enough because a model that always predicts `commentary` could hit 40–50% accuracy if that label is overrepresented, while completely failing on `hot_take` and `analysis`. Macro F1 prevents this by requiring the model to perform across all classes.

---

## Definition of Success

**Minimum bar for "good enough"**: macro F1 ≥ 0.75 with no individual class F1 below 0.65.

**Rationale**: A macro F1 of 0.75 means the model is making useful predictions across all three classes, not just the common ones. The 0.65 per-class floor ensures no label is completely abandoned. Below these thresholds, the model would produce too many errors to be trustworthy in a real community tool where mislabeling a thoughtful `analysis` post as `hot_take` would be visible and frustrating to users.

**Stretch target**: macro F1 ≥ 0.82 — this would indicate the model has genuinely learned the distinction between stat-backed reasoning and opinion, which is the hardest boundary in this task.

**Failure threshold**: If macro F1 is below 0.65 after tuning, the label definitions are likely the problem, not the model — the definitions need to be tightened before retraining.

These criteria are objectively testable: at the end of the project, compute macro F1 and per-class F1 on the held-out test set and compare directly against the thresholds above.

---

## AI Tool Plan

### Label Stress-Testing

Before annotating, I will paste my three label definitions and all three edge case decision rules into Claude and ask it to generate 8–10 posts that sit at each pairwise boundary: `hot_take`/`analysis`, `hot_take`/`commentary`, and `analysis`/`commentary`.

The test: if Claude produces posts I cannot cleanly assign to one label using my written rules, the rules are too vague and need to be tightened before annotation begins. I will revise the definitions in this document until every stress-test post has a clear, defensible answer.

I will specifically ask Claude to try to break the stat-presence rule — e.g., "generate a post that contains a real statistic but reads like a hot take" — since that boundary is where my definitions are most likely to fail.

### Annotation Assistance

I will annotate all 200 examples myself without LLM pre-labeling. Since the annotation task is straightforward (three well-defined labels with decision rules), adding a pre-labeling step would introduce noise I'd have to audit rather than saving meaningful time.

If I fall significantly behind on annotation, I may use Claude to pre-label a batch and then review each label myself before accepting it. If I do this, I will mark those examples with a `pre_labeled` flag in the dataset and disclose it in the AI usage section of the final submission.

### Failure Analysis

After generating predictions on the held-out test set, I will export the list of misclassified examples (predicted label, true label, post text) and feed them to Claude with this prompt: "Here are posts my classifier got wrong. Identify any patterns in what makes these hard — look at post length, presence of statistics, opinion-signal words, tone, and topic. Group them if you see clusters."

I will then verify Claude's patterns manually by reading 5–10 examples from each cluster myself before accepting the pattern as real. Claude's groupings are hypotheses, not ground truth. The verified patterns will directly inform the analysis section of my evaluation writeup.
