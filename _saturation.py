"""Analyse de saturation: à partir de quel score le screening manuel 
ne produit plus d'inclusions? C'est la justification empirique du seuil."""
import pandas as pd

scored = pd.read_csv("data/processed/corpus_scored.csv")
scored["nlp_score"] = pd.to_numeric(scored["nlp_score"], errors="coerce")
scored["relevance_score_pct"] = pd.to_numeric(scored["relevance_score_pct"], errors="coerce")

# Only articles that were actually screened (have a decision)
screened = scored[scored["decision"].isin(["include", "exclude", "survey"])].copy()

print("=" * 80)
print("ANALYSE DE SATURATION — Rendement du screening par strate de score")
print("=" * 80)

# --- A) Par NLP score ---
print("\n── A) Rendement par score NLP ──")
print(f"{'NLP':>4} | {'Total':>6} | {'Include':>7} | {'Exclude':>7} | {'Survey':>6} | {'Taux incl.':>10}")
print("-" * 60)
for nlp in range(11):
    subset = screened[screened["nlp_score"] == nlp]
    n = len(subset)
    inc = (subset["decision"] == "include").sum()
    exc = (subset["decision"] == "exclude").sum()
    sur = (subset["decision"] == "survey").sum()
    rate = f"{inc/n*100:.1f}%" if n > 0 else "—"
    marker = " ←" if inc > 0 else ""
    print(f"  {nlp:>2}  | {n:>5}  | {inc:>6}  | {exc:>6}  | {sur:>5}  | {rate:>9}{marker}")

# --- B) Par TF-IDF bins ---
print("\n── B) Rendement par tranche TF-IDF ──")
bins = [(0, 5), (5, 10), (10, 15), (15, 20), (20, 25), (25, 30), (30, 40), (40, 50), (50, 100)]
print(f"{'TF-IDF':>10} | {'Total':>6} | {'Include':>7} | {'Exclude':>7} | {'Survey':>6} | {'Taux incl.':>10}")
print("-" * 65)
for lo, hi in bins:
    subset = screened[(screened["relevance_score_pct"] > lo) & (screened["relevance_score_pct"] <= hi)]
    if lo == 0:
        subset = screened[screened["relevance_score_pct"] <= hi]
    n = len(subset)
    inc = (subset["decision"] == "include").sum()
    exc = (subset["decision"] == "exclude").sum()
    sur = (subset["decision"] == "survey").sum()
    rate = f"{inc/n*100:.1f}%" if n > 0 else "—"
    marker = " ←" if inc > 0 else ""
    print(f"  {lo:>2}–{hi:<3}%  | {n:>5}  | {inc:>6}  | {exc:>6}  | {sur:>5}  | {rate:>9}{marker}")

# --- C) Croisé NLP × TF-IDF ---
print("\n── C) Matrice de saturation NLP × TF-IDF (inclusions / total) ──")
tf_bins = [(0, 15), (15, 25), (25, 40), (40, 100)]
nlp_bins = [(0, 1), (2, 3), (4, 5), (6, 7), (8, 10)]

header = f"{'NLP':>8} |"
for lo, hi in tf_bins:
    header += f" {'TF ' + str(lo) + '-' + str(hi) + '%':>14} |"
print(header)
print("-" * (10 + 17 * len(tf_bins)))

for nlp_lo, nlp_hi in nlp_bins:
    row = f"  {nlp_lo}–{nlp_hi:>2}   |"
    for tf_lo, tf_hi in tf_bins:
        subset = screened[
            (screened["nlp_score"] >= nlp_lo) & (screened["nlp_score"] <= nlp_hi) &
            (screened["relevance_score_pct"] > tf_lo) & (screened["relevance_score_pct"] <= tf_hi)
        ]
        if tf_lo == 0:
            subset = screened[
                (screened["nlp_score"] >= nlp_lo) & (screened["nlp_score"] <= nlp_hi) &
                (screened["relevance_score_pct"] <= tf_hi)
            ]
        n = len(subset)
        inc = (subset["decision"] == "include").sum()
        if inc > 0:
            row += f" {inc:>3}/{n:<4} ({inc/n*100:>4.0f}%) |"
        else:
            row += f"   0/{n:<4}   —   |"
    print(row)

# --- D) Point de saturation pour screening descendant ---
print("\n── D) Screening descendant : dernière inclusion trouvée ──")
# Sort by relevance_score_pct descending (how screening typically proceeds)
by_rank = screened.sort_values("rank")  # rank = TF-IDF rank
includes = by_rank[by_rank["decision"] == "include"]
if len(includes) > 0:
    last_inc = includes.iloc[-1]
    print(f"  Dernière inclusion par rang TF-IDF: rank #{int(last_inc['rank'])}")
    print(f"    TF-IDF: {last_inc['relevance_score_pct']:.1f}%")
    print(f"    NLP:    {int(last_inc['nlp_score'])}")
    print(f"    Titre:  {last_inc['title'][:80]}")

# Last inclusion by NLP score (lowest NLP among includes)
lowest_nlp_inc = includes.nsmallest(5, "nlp_score")
print(f"\n  5 inclusions avec NLP le plus bas:")
for _, r in lowest_nlp_inc.iterrows():
    print(f"    rank={int(r['rank']):>5} NLP={int(r['nlp_score'])} TF={r['relevance_score_pct']:.1f}% {r['title'][:60]}")

lowest_tf_inc = includes.nsmallest(5, "relevance_score_pct")
print(f"\n  5 inclusions avec TF-IDF le plus bas:")
for _, r in lowest_tf_inc.iterrows():
    print(f"    rank={int(r['rank']):>5} NLP={int(r['nlp_score'])} TF={r['relevance_score_pct']:.1f}% {r['title'][:60]}")

# --- E) Yield curve: cumulative inclusions found as screening progresses ---
print("\n── E) Courbe de rendement cumulatif (screening par rang TF-IDF) ──")
by_rank_all = screened.sort_values("rank")
cumul_inc = 0
total_inc = (screened["decision"] == "include").sum()
checkpoints = [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1200, 1400, 1600, 1800, 1888]
print(f"  {'Screenés':>10} | {'Inclusions':>10} | {'% du total':>10} | {'Rendement marginal'}")
print("-" * 65)
last_printed = 0
for i, (_, row) in enumerate(by_rank_all.iterrows(), 1):
    if row["decision"] == "include":
        cumul_inc += 1
    if i in checkpoints or i == len(by_rank_all):
        marginal = cumul_inc - last_printed
        print(f"  {i:>8}   | {cumul_inc:>8}   | {cumul_inc/total_inc*100:>8.1f}%  | +{marginal} depuis dernier checkpoint")
        last_printed = cumul_inc
