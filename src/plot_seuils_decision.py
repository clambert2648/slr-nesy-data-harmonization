"""
plot_seuils_decision.py
Dashboard 4 quadrants du Tri #1 avec distinction :
  - exclude Tri #1  : decision=exclude
  - exclu full-text  : decision=include + comment E1/I4/E-I4/E6
  - survey           : decision=survey
  - include          : decision=include sans exclusion full-text

Usage :
    python plot_seuils_decision.py
    → results/figures/tri1_seuils_decision.png
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ── Chargement ──
df = pd.read_csv("data/processed/corpus_scored.csv", keep_default_na=False)
df["nlp_score"] = pd.to_numeric(df["nlp_score"], errors="coerce")
df["relevance_score_pct"] = pd.to_numeric(df["relevance_score_pct"], errors="coerce")
screened = df[df["decision"].isin(["include", "exclude", "survey"])].copy()

# ── Full-text exclusions (decision=include mais comment = E1/I4/E-I4/E6) ──
ft_pattern = r"^(E1|I4|E-I4|E6)"
screened["ft_excluded"] = (
    (screened["decision"] == "include") &
    screened["comment"].str.match(ft_pattern, na=False)
)

screened["decision_corr"] = screened["decision"]
screened.loc[screened["ft_excluded"], "decision_corr"] = "ft_exclude"

n_ft = screened["ft_excluded"].sum()
print(f"Screened: {len(screened)}")
print(f"  exclude Tri #1: {(screened['decision_corr']=='exclude').sum()}")
print(f"  exclu full-text: {n_ft}")
print(f"  survey:          {(screened['decision_corr']=='survey').sum()}")
print(f"  include:         {(screened['decision_corr']=='include').sum()}")

# ── Couleurs ──
DEC_COLORS = {
    "exclude": "#ffcccc", "ft_exclude": "#c0392b",
    "survey": "#ff8c00", "include": "#2e8b57"
}
DEC_LABELS = {
    "exclude": "exclude Tri #1", "ft_exclude": "exclu full-text",
    "survey": "survey", "include": "include",
}
DEC_ORDER = ["exclude", "ft_exclude", "survey", "include"]

SUG_COLORS = {
    "uncertain": "#cccccc", "exclude": "#ffcccc",
    "survey": "#ff8c00", "include": "#2e8b57"
}
SUG_ORDER = ["uncertain", "exclude", "survey", "include"]

fig, axes = plt.subplots(2, 2, figsize=(16, 13))
fig.suptitle("Tri #1 — Seuils de décision : NLP Score × TF-IDF × Confiance",
             fontsize=16, fontweight="bold", y=0.98)

# ════════════════════════════════════════════════
# HAUT GAUCHE : Scatter par décision corrigée
# ════════════════════════════════════════════════
ax = axes[0, 0]
plot_cfg = {
    "exclude":    {"alpha": 0.15, "s": 15,  "marker": "o", "edge": "none",  "z": 1},
    "ft_exclude": {"alpha": 0.8,  "s": 45,  "marker": "X", "edge": "darkred", "z": 5},
    "survey":     {"alpha": 0.7,  "s": 40,  "marker": "s", "edge": "gray",  "z": 3},
    "include":    {"alpha": 0.7,  "s": 50,  "marker": "o", "edge": "gray",  "z": 4},
}
for dec in DEC_ORDER:
    sub = screened[screened["decision_corr"] == dec]
    if len(sub) == 0:
        continue
    c = plot_cfg[dec]
    ax.scatter(sub["nlp_score"], sub["relevance_score_pct"],
               c=DEC_COLORS[dec], s=c["s"], alpha=c["alpha"],
               marker=c["marker"], edgecolors=c["edge"], linewidths=0.5,
               label=f"{DEC_LABELS[dec]} (n={len(sub)})", zorder=c["z"])

ax.axvline(x=5, color="green", linestyle="--", alpha=0.5, label="Seuil include auto (≥5)")
ax.axvline(x=2, color="red", linestyle="--", alpha=0.5, label="Seuil exclude auto (≤2)")
ax.set_xlabel("NLP Composite Score (0–10)")
ax.set_ylabel("TF-IDF Relevance Score (%)")
ax.set_title("Score NLP × TF-IDF par décision finale")
ax.legend(loc="upper left", fontsize=7)
ax.set_xlim(-0.5, 11)

# ════════════════════════════════════════════════
# HAUT DROIT : Distribution NLP par décision
# ════════════════════════════════════════════════
ax = axes[0, 1]
hist_decs = ["exclude", "ft_exclude", "include", "survey"]
offsets = {"exclude": -0.3, "ft_exclude": -0.1, "include": 0.1, "survey": 0.3}
width = 0.2
for dec in hist_decs:
    sub = screened[screened["decision_corr"] == dec]
    if len(sub) == 0:
        continue
    counts = sub["nlp_score"].value_counts().sort_index()
    scores = range(11)
    vals = [counts.get(s, 0) for s in scores]
    ax.bar([s + offsets[dec] for s in scores], vals, width=width,
           color=DEC_COLORS[dec], alpha=0.8,
           label=f"{DEC_LABELS[dec]} (n={len(sub)})",
           edgecolor="gray", linewidth=0.3)

ax.axvline(x=2, color="red", linestyle="--", alpha=0.5)
ax.axvline(x=5, color="green", linestyle="--", alpha=0.5)
ax.set_xlabel("NLP Composite Score")
ax.set_ylabel("Nombre d'articles")
ax.set_title("Distribution du score NLP par décision")
ax.legend(fontsize=7)

# ════════════════════════════════════════════════
# BAS GAUCHE : Scatter par suggestion NLP
# ════════════════════════════════════════════════
ax = axes[1, 0]
sug_cfg = {
    "uncertain": {"alpha": 0.1, "s": 10, "marker": "o", "edge": "none",  "z": 1},
    "exclude":   {"alpha": 0.1, "s": 10, "marker": "o", "edge": "none",  "z": 1},
    "survey":    {"alpha": 0.7, "s": 35, "marker": "s", "edge": "gray",  "z": 3},
    "include":   {"alpha": 0.7, "s": 40, "marker": "o", "edge": "gray",  "z": 3},
}
for sug in SUG_ORDER:
    sub = screened[screened["nlp_suggestion"] == sug]
    if len(sub) == 0:
        continue
    c = sug_cfg[sug]
    ax.scatter(sub["nlp_score"], sub["relevance_score_pct"],
               c=SUG_COLORS[sug], s=c["s"], alpha=c["alpha"],
               marker=c["marker"], edgecolors=c["edge"], linewidths=0.5,
               label=f"{sug} (n={len(sub)})", zorder=c["z"])

ax.axvline(x=5, color="green", linestyle="--", alpha=0.5)
ax.axvline(x=2, color="red", linestyle="--", alpha=0.5)
ax.set_xlabel("NLP Composite Score (0–10)")
ax.set_ylabel("TF-IDF Relevance Score (%)")
ax.set_title("Score NLP × TF-IDF par suggestion NLP")
ax.legend(loc="upper left", fontsize=8)
ax.set_xlim(-0.5, 11)

# ════════════════════════════════════════════════
# BAS DROIT : Matrice de confusion
# ════════════════════════════════════════════════
ax = axes[1, 1]
sug_labels = ["include", "uncertain", "survey", "exclude"]
dec_mat = ["include", "survey", "ft_exclude", "exclude"]
dec_mat_disp = ["include\n(décision)", "survey\n(décision)", "exclu\nfull-text", "exclude\n(décision)"]

matrix = np.zeros((len(sug_labels), len(dec_mat)), dtype=int)
for i, sug in enumerate(sug_labels):
    for j, dec in enumerate(dec_mat):
        matrix[i, j] = len(screened[(screened["nlp_suggestion"] == sug) &
                                     (screened["decision_corr"] == dec)])

im = ax.imshow(matrix, cmap="YlOrRd", aspect="auto")
for i in range(len(sug_labels)):
    for j in range(len(dec_mat)):
        val = matrix[i, j]
        color = "white" if val > matrix.max() * 0.7 else "black"
        ax.text(j, i, str(val), ha="center", va="center", fontsize=11,
                fontweight="bold", color=color)

ax.set_xticks(range(len(dec_mat)))
ax.set_xticklabels(dec_mat_disp, fontsize=8)
ax.set_yticks(range(len(sug_labels)))
ax.set_yticklabels([f"{s}\n(suggestion)" for s in sug_labels], fontsize=8)
ax.set_title("Suggestion NLP → Décision finale (corrigée)")
plt.colorbar(im, ax=ax, shrink=0.8)

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig("results/figures/tri1_seuils_decision.png", dpi=150, bbox_inches="tight")
print("✓ Sauvegardé : results/figures/tri1_seuils_decision.png")
plt.show()
