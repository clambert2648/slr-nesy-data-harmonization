"""
03_bibliometrie_inclus.py
Analyse bibliométrique des études primaires incluses (Section 4 — article ESWA).

Produit :
  - fig10 : Distribution temporelle des études incluses (N=38, stacked DB/snowball)
  - fig11 : Répartition par type de venue (journal / conférence / preprint)
  - fig12 : Répartition par base de données source
  - fig13 : Delta thématique — corpus identifié (N=1888) vs inclus (N=38)

Usage :
  python 03_bibliometrie_inclus.py

Prérequis :
  - data/processed/corpus_scored.csv        (corpus complet N=1888)
  - data/processed/articles_inclus.csv      (217 articles → 38 avec qa_pass=oui)
  - results/tables/VOS.txt                  (export VOSviewer — clusters)
  - results/tables/vosviewer_thesaurus.txt  (thesaurus normalisation)

Sortie :
  - results/figures/publication/fig10_*.png .. fig13_*.png
  - results/tables/delta_thematique.csv
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import re
import os
import warnings
warnings.filterwarnings('ignore')

# ── Configuration ─────────────────────────────────────────────────────────────
CORPUS_PATH    = 'data/processed/corpus_scored.csv'
INCLUS_PATH    = 'data/processed/articles_inclus.csv'
VOS_PATH       = 'results/tables/VOS.txt'
THESAURUS_PATH = 'results/tables/vosviewer_thesaurus.txt'
FIG_DIR        = 'results/figures/publication'
TABLE_DIR      = 'results/tables'

os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(TABLE_DIR, exist_ok=True)

# ── Style global ──────────────────────────────────────────────────────────────
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.size': 11,
    'axes.titlesize': 13,
    'axes.titleweight': 'bold',
    'figure.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.15,
})
C_PRIMARY   = '#2c5f8a'
C_SECONDARY = '#d4a03c'
C_ACCENT    = '#6b9e6b'
C_LIGHT     = '#a3c4d9'
C_GREY      = '#888888'


# ══════════════════════════════════════════════════════════════════════════════
# 1. CHARGEMENT
# ══════════════════════════════════════════════════════════════════════════════

print("═" * 60)
print("Chargement des données...")
print("═" * 60)

corpus = pd.read_csv(CORPUS_PATH, encoding='utf-8-sig', keep_default_na=False)
corpus['keywords'] = corpus['keywords'].fillna('').astype(str).str.strip()
N_CORPUS = len(corpus)
print(f"  Corpus identifié : {N_CORPUS}")

ai = pd.read_csv(INCLUS_PATH, encoding='utf-8-sig', keep_default_na=False)
inclus = ai[ai['qa_pass'] == 'oui'].copy()
N_INCLUS = len(inclus)

# Identifier DB vs snowball via la colonne decision
# decision='include' → bases de données ; decision='inclus' → snowball
inclus['source_pipeline'] = inclus['decision'].apply(
    lambda d: 'snowballing' if d.strip().lower() == 'inclus' else 'database_search')

n_db = (inclus['source_pipeline'] == 'database_search').sum()
n_sb = (inclus['source_pipeline'] == 'snowballing').sum()
print(f"  Études primaires : {N_INCLUS} (bases={n_db}, snowball={n_sb})")

inclus['keywords'] = inclus['keywords'].fillna('').astype(str).str.strip()
n_kw = inclus['keywords'].ne('').sum()
print(f"  Avec keywords auteurs : {n_kw}/{N_INCLUS}")
print()


# ══════════════════════════════════════════════════════════════════════════════
# 2. THESAURUS + CLUSTERS VOSviewer
# ══════════════════════════════════════════════════════════════════════════════

# ── Thesaurus ─────────────────────────────────────────────────────────────────
thesaurus = {}
if os.path.exists(THESAURUS_PATH):
    th = pd.read_csv(THESAURUS_PATH, sep='\t')
    thesaurus = dict(zip(th['label'].str.lower().str.strip(),
                         th['replace by'].str.lower().str.strip()))

# ── Clusters VOSviewer ────────────────────────────────────────────────────────
vos = pd.read_csv(VOS_PATH, sep='\t')

MACRO_THEMES = {
    'Semantic integration\n& ontology matching':     [1, 4],
    'Deep learning\n& neural architectures':         [2, 9],
    'XAI & symbolic\nreasoning':                     [3],
    'NLP & language\nmodels':                         [5, 6],
    'Knowledge graphs\n& neuro-symbolic':             [7, 8, 10],
}

# Mapping keyword → macro-thème
keyword_to_macro = {}
for macro, cluster_ids in MACRO_THEMES.items():
    for _, row in vos[vos['cluster'].isin(cluster_ids)].iterrows():
        keyword_to_macro[row['label'].lower().strip()] = macro

print(f"  {len(keyword_to_macro)} mots-clés VOSviewer mappés")


# ══════════════════════════════════════════════════════════════════════════════
# 3. ENRICHISSEMENT DES KEYWORDS PAR TITRE + ABSTRACT
# ══════════════════════════════════════════════════════════════════════════════

def normalize_kw(kw):
    return thesaurus.get(kw.lower().strip(), kw.lower().strip())

def extract_vos_keywords_from_text(text):
    """Scanne un texte pour les labels VOSviewer (mots-clés extraits du titre/abstract)."""
    text_lower = text.lower()
    found = set()
    # Trier par longueur décroissante pour matcher d'abord les expressions longues
    for kw in sorted(keyword_to_macro.keys(), key=len, reverse=True):
        # Chercher comme mot complet (boundaries)
        if re.search(r'\b' + re.escape(kw) + r'\b', text_lower):
            found.add(kw)
    # Aussi chercher les formes pré-thesaurus
    for label, canonical in thesaurus.items():
        if canonical in keyword_to_macro and re.search(r'\b' + re.escape(label) + r'\b', text_lower):
            found.add(canonical)
    return found

def assign_macro_themes(row):
    """Assigne les macro-thèmes via keywords auteurs + enrichissement titre/abstract."""
    themes = set()

    # 1. Keywords auteurs (source primaire)
    kws_str = str(row.get('keywords', ''))
    if kws_str.strip():
        for kw in kws_str.replace(';', ',').split(','):
            kw_norm = normalize_kw(kw)
            if kw_norm in keyword_to_macro:
                themes.add(keyword_to_macro[kw_norm])

    # 2. Enrichissement par titre + abstract (source secondaire)
    text = str(row.get('title', '')) + ' ' + str(row.get('abstract', ''))
    vos_kws = extract_vos_keywords_from_text(text)
    for kw in vos_kws:
        if kw in keyword_to_macro:
            themes.add(keyword_to_macro[kw])

    return themes

print("  Assignation macro-thèmes (keywords + titre/abstract)...")
corpus['macro_themes'] = corpus.apply(assign_macro_themes, axis=1)
inclus['macro_themes'] = inclus.apply(assign_macro_themes, axis=1)

n_corpus_assigned = corpus['macro_themes'].apply(len).gt(0).sum()
n_inclus_assigned = inclus['macro_themes'].apply(len).gt(0).sum()
print(f"  Articles avec ≥1 thème : corpus={n_corpus_assigned}/{N_CORPUS}, "
      f"inclus={n_inclus_assigned}/{N_INCLUS}")
print()


# ══════════════════════════════════════════════════════════════════════════════
# 4. CLASSIFICATION PAR TYPE DE VENUE
# ══════════════════════════════════════════════════════════════════════════════

def classify_venue(row):
    dt = str(row.get('doc_type', '')).lower().strip()
    db = str(row.get('database', '')).lower().strip()
    src = str(row.get('source', '')).lower().strip()
    title = str(row.get('title', '')).lower()

    if db == 'arxiv' or dt == 'preprint' or 'arxiv' in src:
        return 'Preprint'
    if any(k in dt for k in ['conference', 'proceeding', 'ieee conferences', 'workshop']):
        return 'Conference'
    if any(k in dt for k in ['article', 'journal', 'review']):
        return 'Journal'
    if any(k in src for k in ['proceedings', 'conference', 'workshop', 'symposium',
                               'lecture notes', 'ceur']):
        return 'Conference'
    # Snowball sans doc_type : inférer depuis le source/title
    if dt == '' and db == '':
        return 'Journal'  # défaut pour snowball (majorité sont des journaux)
    return 'Journal'

inclus['venue_type'] = inclus.apply(classify_venue, axis=1)


# ══════════════════════════════════════════════════════════════════════════════
# 5. FIGURES
# ══════════════════════════════════════════════════════════════════════════════

print("Génération des figures...")

# ── Fig 10 — Distribution temporelle (stacked DB/snowball) ────────────────────
fig, ax = plt.subplots(figsize=(8, 4.5))
all_years = sorted(inclus['year'].unique())
yr_db = inclus[inclus['source_pipeline'] == 'database_search']['year'].value_counts()
yr_sb = inclus[inclus['source_pipeline'] == 'snowballing']['year'].value_counts()
vals_db = [yr_db.get(y, 0) for y in all_years]
vals_sb = [yr_sb.get(y, 0) for y in all_years]

ax.bar(all_years, vals_db, color=C_PRIMARY, label='Database search', zorder=3)
ax.bar(all_years, vals_sb, bottom=vals_db, color=C_SECONDARY, label='Snowballing', zorder=3)
for y, vdb, vsb in zip(all_years, vals_db, vals_sb):
    total = vdb + vsb
    if total > 0:
        ax.text(y, total + 0.2, str(total), ha='center', va='bottom',
                fontweight='bold', fontsize=10)

ax.set_xlabel('Publication year')
ax.set_ylabel('Number of studies')
ax.set_title(f'Temporal distribution of included studies (N={N_INCLUS})')
ax.set_xticks(all_years)
ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
ax.legend(frameon=True, edgecolor='#cccccc')
ax.grid(axis='y', alpha=0.3, zorder=0)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.savefig(os.path.join(FIG_DIR, 'fig10_distribution_temporelle_inclus.png'))
plt.close()
print("  ✓ fig10 — distribution temporelle")

# ── Fig 11 — Type de venue ────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(6, 4.5))
venue_counts = inclus['venue_type'].value_counts()
colors_venue = {'Journal': C_PRIMARY, 'Conference': C_SECONDARY, 'Preprint': C_LIGHT}
bars = ax.barh(venue_counts.index, venue_counts.values,
               color=[colors_venue.get(v, C_GREY) for v in venue_counts.index], zorder=3)
for bar, val in zip(bars, venue_counts.values):
    ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
            f'{val} ({val/N_INCLUS*100:.0f}%)', va='center', fontsize=10)

ax.set_xlabel('Number of studies')
ax.set_title(f'Distribution by venue type (N={N_INCLUS})')
ax.grid(axis='x', alpha=0.3, zorder=0)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.invert_yaxis()

plt.savefig(os.path.join(FIG_DIR, 'fig11_venue_type_inclus.png'))
plt.close()
print("  ✓ fig11 — type de venue")

# ── Fig 12 — Base de données source ───────────────────────────────────────────
fig, ax = plt.subplots(figsize=(7, 4.5))

def simplify_db(row):
    db = str(row.get('database', '')).strip()
    sp = row.get('source_pipeline', '')
    if sp == 'snowballing':
        return 'Snowballing'
    if not db or db.lower() in ['', 'nan']:
        return 'Autre'
    if '+' in db:
        return 'Multi-base'
    if 'scopus' in db.lower():
        return 'Scopus'
    if 'arxiv' in db.lower():
        return 'ArXiv'
    if db.lower() == 'ieee':
        return 'IEEE'
    if db.lower() == 'acm':
        return 'ACM'
    if 'expert' in db.lower():
        return 'Expert'
    return db

inclus['db_display'] = inclus.apply(simplify_db, axis=1)
db_counts = inclus['db_display'].value_counts()
bars = ax.barh(db_counts.index, db_counts.values, color=C_PRIMARY, zorder=3)
for bar, val in zip(bars, db_counts.values):
    ax.text(bar.get_width() + 0.2, bar.get_y() + bar.get_height()/2,
            str(val), va='center', fontsize=10)

ax.set_xlabel('Number of studies')
ax.set_title(f'Distribution by source (N={N_INCLUS})')
ax.grid(axis='x', alpha=0.3, zorder=0)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.invert_yaxis()

plt.savefig(os.path.join(FIG_DIR, 'fig12_source_inclus.png'))
plt.close()
print("  ✓ fig12 — source")


# ══════════════════════════════════════════════════════════════════════════════
# 6. DELTA THÉMATIQUE
# ══════════════════════════════════════════════════════════════════════════════

print()
print("Calcul du delta thématique...")

def count_theme_distribution(dataframe):
    counts = {}
    for themes in dataframe['macro_themes']:
        for t in themes:
            counts[t] = counts.get(t, 0) + 1
    return counts

counts_corpus = count_theme_distribution(corpus)
counts_inclus = count_theme_distribution(inclus)

delta_rows = []
for macro in MACRO_THEMES.keys():
    n_corp = counts_corpus.get(macro, 0)
    n_incl = counts_inclus.get(macro, 0)
    pct_corp = n_corp / N_CORPUS * 100
    pct_incl = n_incl / N_INCLUS * 100
    delta_rows.append({
        'Macro-theme': macro.replace('\n', ' '),
        'N corpus': n_corp,
        '% corpus': round(pct_corp, 1),
        'N included': n_incl,
        '% included': round(pct_incl, 1),
        'Δ (pp)': round(pct_incl - pct_corp, 1)
    })

delta_df = pd.DataFrame(delta_rows)
delta_df.to_csv(os.path.join(TABLE_DIR, 'delta_thematique.csv'), index=False,
                encoding='utf-8-sig')
print()
print("  Tableau delta thématique :")
print(delta_df.to_string(index=False))
print()

# ── Fig 13 — Grouped bar chart ────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 5.5))

themes_labels = [m.replace('\n', ' ') for m in MACRO_THEMES.keys()]
themes_short = list(MACRO_THEMES.keys())
x = np.arange(len(themes_labels))
width = 0.35

pct_corpus = [delta_df.loc[delta_df['Macro-theme'] == t, '% corpus'].values[0]
              for t in themes_labels]
pct_inclus = [delta_df.loc[delta_df['Macro-theme'] == t, '% included'].values[0]
              for t in themes_labels]

bars1 = ax.bar(x - width/2, pct_corpus, width,
               label=f'Identified corpus (N={N_CORPUS})',
               color=C_LIGHT, edgecolor='white', zorder=3)
bars2 = ax.bar(x + width/2, pct_inclus, width,
               label=f'Included studies (N={N_INCLUS})',
               color=C_PRIMARY, edgecolor='white', zorder=3)

for i, (pc, pi) in enumerate(zip(pct_corpus, pct_inclus)):
    delta_val = pi - pc
    sign = '+' if delta_val > 0 else ''
    color = C_ACCENT if delta_val > 0 else '#c44e52'
    y_pos = max(pc, pi) + 1.5
    ax.annotate(f'{sign}{delta_val:.1f} pp', xy=(x[i], y_pos),
                ha='center', va='bottom', fontsize=9, fontweight='bold', color=color)

ax.set_ylabel('Proportion of articles (%)')
ax.set_title('Thematic delta — identified corpus vs. included studies')
ax.set_xticks(x)
ax.set_xticklabels(themes_short, ha='center', fontsize=9)
ax.legend(loc='upper right', frameon=True, edgecolor='#cccccc')
ax.grid(axis='y', alpha=0.3, zorder=0)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.set_ylim(0, max(max(pct_corpus), max(pct_inclus)) + 8)

plt.savefig(os.path.join(FIG_DIR, 'fig13_delta_thematique.png'))
plt.close()
print("  ✓ fig13 — delta thématique")


# ══════════════════════════════════════════════════════════════════════════════
# 7. RÉSUMÉ
# ══════════════════════════════════════════════════════════════════════════════

print()
print("═" * 60)
print("RÉSUMÉ")
print("═" * 60)

# Articles sans aucun thème même après enrichissement
no_theme = inclus[inclus['macro_themes'].apply(len) == 0]
if len(no_theme) > 0:
    print(f"\n⚠  {len(no_theme)} études sans macro-thème même après enrichissement :")
    for _, row in no_theme.iterrows():
        print(f"   - [{row['year']}] {str(row['title'])[:80]}...")

print(f"""
Figures dans {FIG_DIR}/ :
  fig10_distribution_temporelle_inclus.png  (N={N_INCLUS}, stacked DB/snowball)
  fig11_venue_type_inclus.png
  fig12_source_inclus.png
  fig13_delta_thematique.png

Tableau : {TABLE_DIR}/delta_thematique.csv

Méthode d'enrichissement :
  Les macro-thèmes sont assignés via les keywords auteurs (si disponibles)
  PLUS extraction automatique des labels VOSviewer depuis le titre et l'abstract.
  Ceci compense l'absence de keywords pour ArXiv (100%) et certains Scopus.
  → À mentionner dans la section 4.3 comme limite méthodologique.
""")
