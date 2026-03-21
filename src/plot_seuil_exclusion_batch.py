"""
plot_seuil_exclusion_batch.py
Analyse de sensibilité du seuil d'exclusion batch avec 4 populations :
  - extraction   (qa_pass=oui)  : corpus final
  - QA fail      (qa_pass=non)  : éliminés au QA
  - full-text exclu             : decision=include + comment E1/I4/E-I4/E6
  - en attente   (qa_pass vide) : pas encore évalués au QA

Usage :
    python plot_seuil_exclusion_batch.py
    → results/figures/tri1_seuil_exclusion_batch.png
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ── Chargement ──
df = pd.read_csv("data/processed/corpus_scored.csv", keep_default_na=False)
df["nlp_score"] = pd.to_numeric(df["nlp_score"], errors="coerce")
df["relevance_score_pct"] = pd.to_numeric(df["relevance_score_pct"], errors="coerce")
screened = df[df["decision"].isin(["include", "exclude", "survey"])].copy()

# ── Populations ──
ft_pattern = r"^(E1|I4|E-I4|E6)"
includes_raw = screened[screened["decision"] == "include"].copy()
includes_raw["ft_excluded"] = includes_raw["comment"].str.match(ft_pattern, na=False)

ft_exclu    = includes_raw[includes_raw["ft_excluded"]]
includes    = includes_raw[~includes_raw["ft_excluded"]]  # vrais inclus
extraction  = includes[includes["qa_pass"] == "oui"]
qa_fail     = includes[includes["qa_pass"] == "non"]
en_attente  = includes[includes["qa_pass"] == ""]

n_ft   = len(ft_exclu)
n_inc  = len(includes)
n_extr = len(extraction)
n_qaf  = len(qa_fail)
n_att  = len(en_attente)

print("=" * 60)
print("POPULATIONS")
print("=" * 60)
print(f"  Full-text exclus :  {n_ft:>4}  (NLP min={ft_exclu['nlp_score'].min():.0f})")
print(f"  Vrais inclus :     {n_inc:>4}")
print(f"    extraction :     {n_extr:>4}  (qa=oui)")
print(f"    QA fail :        {n_qaf:>4}  (qa=non)")
print(f"    en attente :     {n_att:>4}  (qa vide)")
print()

# ── FN par seuil NLP ──
seuils = range(11)
fn_inclus = []   # benchmark = vrais inclus (sans ft_exclu)
fn_extr = []     # benchmark = extraction seulement
exclus_cumul = []

for s in seuils:
    excluded_zone = screened[screened["nlp_score"] <= s]
    exclus_cumul.append(len(excluded_zone))
    fn_inclus.append(len(includes[includes["nlp_score"] <= s]))
    fn_extr.append(len(extraction[extraction["nlp_score"] <= s]))

# ── #840 ──
r840 = screened[screened["rank"] == 840]
has_840 = len(r840) > 0
if has_840:
    r840 = r840.iloc[0]
    nlp_840 = r840["nlp_score"]
    tf_840 = r840["relevance_score_pct"]
    qa_840 = r840.get("qa_total", "?")
    print(f"#840: nlp={nlp_840:.0f}, tf={tf_840:.1f}%, qa_pass={r840['qa_pass']}, qa={qa_840}")

# ════════════════════════════════════════════════
# FIGURE
# ════════════════════════════════════════════════
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7),
                                gridspec_kw={"width_ratios": [1, 1]})
fig.suptitle(
    "Analyse de sensibilité — Seuil d'exclusion batch NLP (Tri #1)\n"
    f"Benchmark corrigé : extraction finale (n = {n_extr})"
    f" | inclus sans ft_exclu (n = {n_inc})",
    fontsize=13, fontweight="bold", y=0.98
)

# ════════════════════════════════════════════════
# A) Faux négatifs par seuil NLP
# ════════════════════════════════════════════════

# Zone sûre (0 FN extraction)
safe_extr = max((s for s in seuils if fn_extr[s] == 0), default=0)
ax1.axvspan(-0.5, safe_extr + 0.5, alpha=0.12, color="green",
            label="Zone sûre (0 FN)")

# Barres cumulatives
ax1.bar(list(seuils), exclus_cumul, color="#ffcccc", alpha=0.5, width=0.8,
        label="Articles exclus (cumulatif)")

# Courbe FN inclus (sans ft_exclu)
ax1.plot(list(seuils), fn_inclus, "rs--", markersize=8, linewidth=2,
         label=f"FN (Tri #1 corrigé, n={n_inc})", zorder=5)

# Courbe FN extraction
ax1.plot(list(seuils), fn_extr, "go-", markersize=8, linewidth=2.5,
         label=f"FN (Extraction, n={n_extr})", zorder=5)

# Annotation seuil optimal (inclus)
safe_inc = max((s for s in seuils if fn_inclus[s] == 0), default=0)
ax1.annotate(
    f"Score ≤ {safe_inc}\n{exclus_cumul[safe_inc]} exclus\n0 inclus perdu\n→ SEUIL OPTIMAL",
    xy=(safe_inc, fn_inclus[safe_inc]),
    xytext=(safe_inc + 1.5, max(fn_inclus) * 0.4 + 5),
    fontsize=9, fontweight="bold",
    bbox=dict(boxstyle="round,pad=0.4", facecolor="#d4edda", edgecolor="green"),
    arrowprops=dict(arrowstyle="->", color="green", lw=1.5)
)

# Annotation #840
if has_840:
    first_fn = min((s for s in seuils if fn_inclus[s] > 0), default=None)
    if first_fn is not None:
        ax1.annotate(
            f"#840 : FN Tri #1 = {fn_inclus[first_fn]}\nmais FN extraction = {fn_extr[first_fn]}",
            xy=(first_fn, fn_inclus[first_fn]),
            xytext=(first_fn + 0.5, fn_inclus[first_fn] + max(fn_inclus) * 0.1),
            fontsize=8,
            bbox=dict(boxstyle="round,pad=0.3", facecolor="#fff3e0", edgecolor="orange"),
            arrowprops=dict(arrowstyle="->", color="orange", lw=1.2)
        )

ax1.set_xlabel("Seuil NLP Score (≤ x → exclusion batch)")
ax1.set_ylabel("Nombre d'articles exclus", color="red")
ax1_twin = ax1.twinx()
ax1_twin.set_ylabel("Articles inclus perdus (FN)", color="green")
ax1.set_title("A) Faux négatifs par seuil NLP")
ax1.legend(loc="upper left", fontsize=7)
ax1.set_xticks(range(11))
ax1.set_xlim(-0.5, 10.5)
ax1.set_ylim(0, max(exclus_cumul) * 1.05)
ax1_twin.set_ylim(0, max(max(fn_inclus), 1) * 1.3)

# ════════════════════════════════════════════════
# B) Scatter NLP × TF-IDF des articles inclus
# ════════════════════════════════════════════════

# Fond : exclus (gris)
excludes = screened[screened["decision"] == "exclude"]
ax2.scatter(excludes["nlp_score"], excludes["relevance_score_pct"],
            c="#eeeeee", s=5, alpha=0.2, label=f"exclude (n={len(excludes)})")

# Surveys
surveys = screened[screened["decision"] == "survey"]
ax2.scatter(surveys["nlp_score"], surveys["relevance_score_pct"],
            c="orange", s=30, alpha=0.6, marker="s",
            label=f"survey (n={len(surveys)})")

# Full-text exclus (croix rouges)
if n_ft > 0:
    ax2.scatter(ft_exclu["nlp_score"], ft_exclu["relevance_score_pct"],
                c="#c0392b", s=50, alpha=0.8, marker="X",
                edgecolors="darkred", linewidths=0.8,
                label=f"exclu full-text (n={n_ft})", zorder=6)

# Extraction (cercles verts pleins)
if n_extr > 0:
    ax2.scatter(extraction["nlp_score"], extraction["relevance_score_pct"],
                c="#2e8b57", s=55, alpha=0.8, marker="o",
                edgecolors="darkgreen", linewidths=0.8,
                label=f"Extraction (n={n_extr})", zorder=7)

# QA fail (triangles orange)
if n_qaf > 0:
    ax2.scatter(qa_fail["nlp_score"], qa_fail["relevance_score_pct"],
                c="#e67e22", s=50, alpha=0.8, marker="^",
                edgecolors="darkorange", linewidths=0.8,
                label=f"QA fail (n={n_qaf})", zorder=6)

# En attente (cercles verts ouverts)
if n_att > 0:
    ax2.scatter(en_attente["nlp_score"], en_attente["relevance_score_pct"],
                c="none", s=45, alpha=0.6, marker="o",
                edgecolors="#2e8b57", linewidths=1.2,
                label=f"en attente QA (n={n_att})", zorder=5)

# Seuils
ax2.axvline(x=1.5, color="blue", linestyle=":", alpha=0.5,
            label=f"Seuil NLP ≤ 1")
ax2.axvline(x=2.5, color="red", linestyle="--", alpha=0.4,
            label="Seuil NLP ≤ 2")

# Zone NLP ≤ 3 ET TF ≤ 15%
rect = plt.Rectangle((-0.5, -1), 4, 16, alpha=0.08, color="blue", zorder=0)
ax2.add_patch(rect)
ax2.text(1.5, 14, "Sûr: NLP ≤ 3\nET TF ≤ 15%", fontsize=7,
         ha="center", color="blue", alpha=0.7)

# Annotation #840
if has_840:
    ax2.plot(nlp_840, tf_840, "rX", markersize=15, markeredgewidth=2.5, zorder=10)
    ax2.annotate(
        f"#840 (QA {qa_840}/5)\nPlus bas inclus",
        xy=(nlp_840, tf_840), xytext=(nlp_840 + 1.5, tf_840 - 4),
        fontsize=8, color="red", fontweight="bold",
        arrowprops=dict(arrowstyle="->", color="red", lw=1)
    )

ax2.set_xlabel("Score NLP composite (0–10)")
ax2.set_ylabel("Score TF-IDF (%)")
ax2.set_title("B) Articles inclus Tri #1 : NLP × TF-IDF")
ax2.legend(loc="upper left", fontsize=6.5, ncol=1)
ax2.set_xlim(-0.5, 11)
ax2.set_ylim(-2, 105)

plt.tight_layout(rect=[0, 0, 1, 0.93])
plt.savefig("results/figures/tri1_seuil_exclusion_batch.png",
            dpi=150, bbox_inches="tight")
print(f"\n✓ Sauvegardé : results/figures/tri1_seuil_exclusion_batch.png")
plt.show()
