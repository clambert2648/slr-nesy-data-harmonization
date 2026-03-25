"""
04_prisma_diagram.py
Génère un diagramme PRISMA 2020 conforme au protocole (Section B.6).

Usage : python 04_prisma_diagram.py
Sortie : results/figures/publication/fig3_prisma_flow.png
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os

FIG_DIR = 'results/figures/publication'
os.makedirs(FIG_DIR, exist_ok=True)

# ══════════════════════════════════════════════════════════════════════════════
# Configuration
# ══════════════════════════════════════════════════════════════════════════════

fig, ax = plt.subplots(figsize=(16, 20))
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis('off')

# Couleurs
C_ID     = '#d6eaf8'   # bleu pâle — identification
C_SCREEN = '#d5f5e3'   # vert pâle — screening
C_ELIG   = '#fef9e7'   # jaune pâle — éligibilité
C_INCL   = '#fadbd8'   # rose pâle — inclusion
C_EXCL   = '#f2f3f4'   # gris — exclusions
C_SNOW   = '#e8daef'   # violet pâle — snowballing
C_BORDER = '#2c3e50'
C_ARROW  = '#5d6d7e'

# ── Fonctions utilitaires ─────────────────────────────────────────────────────

def draw_box(x, y, w, h, text, facecolor='white', fontsize=9, bold=False,
             edgecolor=C_BORDER, lw=1.2, alpha=1.0):
    rect = mpatches.FancyBboxPatch(
        (x - w/2, y - h/2), w, h,
        boxstyle="round,pad=0.3", facecolor=facecolor,
        edgecolor=edgecolor, linewidth=lw, alpha=alpha,
        transform=ax.transData, zorder=2)
    ax.add_patch(rect)
    weight = 'bold' if bold else 'normal'
    ax.text(x, y, text, ha='center', va='center', fontsize=fontsize,
            fontweight=weight, wrap=True, zorder=3,
            linespacing=1.3)

def arrow(x1, y1, x2, y2, style='->', color=C_ARROW, lw=1.5):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle=style, color=color, lw=lw),
                zorder=1)

def side_arrow(x1, y1, x2, y2):
    """Flèche latérale (vers les exclusions)."""
    arrow(x1, y1, x2, y2, color='#95a5a6', lw=1.2)

# ── Phase labels (bandes latérales) ───────────────────────────────────────────
phases = [
    (2.5, 88, 'IDENTIFICATION', C_ID),
    (2.5, 68, 'SCREENING', C_SCREEN),
    (2.5, 48, 'ELIGIBILITY', C_ELIG),
    (2.5, 22, 'INCLUDED', C_INCL),
]
for px, py, label, color in phases:
    rect = mpatches.FancyBboxPatch(
        (0.5, py - 9), 5, 18,
        boxstyle="round,pad=0.2", facecolor=color,
        edgecolor=C_BORDER, linewidth=0.8, alpha=0.7)
    ax.add_patch(rect)
    ax.text(px, py, label, ha='center', va='center', fontsize=7,
            fontweight='bold', rotation=90, color='#2c3e50')

# ══════════════════════════════════════════════════════════════════════════════
# IDENTIFICATION
# ══════════════════════════════════════════════════════════════════════════════

# Bases de données
draw_box(28, 96, 22, 5,
         'Records identified from databases\n'
         'Scopus (n=1,219) · IEEE (n=594)\n'
         'ACM (n=268) · arXiv (n=189)\n'
         'Total: N = 2,270',
         facecolor=C_ID, fontsize=8)

# Intra-dedup
draw_box(28, 88, 22, 4,
         'After intra-database\ndeduplication: N = 2,164',
         facecolor=C_ID, fontsize=8)
arrow(28, 93.5, 28, 90)

# Inter-dedup
draw_box(28, 81.5, 22, 4,
         'After inter-database\ndeduplication: N = 1,890',
         facecolor=C_ID, fontsize=8)
arrow(28, 86, 28, 83.5)

# Exclusion E6
draw_box(55, 81.5, 18, 3.5,
         'Excluded E6\n(out-of-period): n = 2',
         facecolor=C_EXCL, fontsize=7.5)
side_arrow(39, 81.5, 46, 81.5)

# Doublons retirés
draw_box(55, 88, 18, 3.5,
         'Duplicates removed\n(DOI + fuzzy ≥ 95%): n = 274',
         facecolor=C_EXCL, fontsize=7.5)
side_arrow(39, 88, 46, 88)

# Corpus screening
draw_box(28, 75, 22, 4,
         'Records screened\n(title + abstract)\nN = 1,888',
         facecolor=C_SCREEN, fontsize=8.5, bold=True)
arrow(28, 79.5, 28, 77)

# ══════════════════════════════════════════════════════════════════════════════
# SCREENING (Tri #1)
# ══════════════════════════════════════════════════════════════════════════════

# Exclusions Tri 1
draw_box(55, 72, 18, 6,
         'Excluded (n = 1,613)\n'
         'E1: off-task (n ≈ 910)\n'
         'E2: wrong modality (n ≈ 430)\n'
         'E3–E5: other (n ≈ 273)',
         facecolor=C_EXCL, fontsize=7)
side_arrow(39, 75, 46, 72)

# Surveys
draw_box(55, 64, 18, 3.5,
         'Surveys identified\nfor snowballing: n = 59',
         facecolor=C_SNOW, fontsize=7.5)
side_arrow(39, 70, 46, 64)

# Résultat Tri 1
draw_box(28, 66, 22, 4,
         'Included after Tri #1: n = 216\n'
         'Withdrawn (retracted): −3\n'
         'Expert recommendation: +1',
         facecolor=C_SCREEN, fontsize=8)
arrow(28, 73, 28, 68)

# Vers Tri 2
draw_box(28, 58, 22, 4,
         'Records for Tri #2\n(full-text assessment)\nN = 214',
         facecolor=C_ELIG, fontsize=8.5, bold=True)
arrow(28, 64, 28, 60)

# ══════════════════════════════════════════════════════════════════════════════
# ELIGIBILITY (Tri #2)
# ══════════════════════════════════════════════════════════════════════════════

# Inaccessibles
draw_box(55, 56, 18, 3.5,
         'Full-text not retrieved\n(inaccessible): n = 8',
         facecolor=C_EXCL, fontsize=7.5)
side_arrow(39, 58, 46, 56)

# QA évalués
draw_box(28, 51, 22, 4,
         'Assessed for quality\n(QA grid Q1–Q5): n = 206',
         facecolor=C_ELIG, fontsize=8)
arrow(28, 56, 28, 53)

# QA exclus
draw_box(55, 48, 18, 3.5,
         'Excluded QA < 3/5\nn = 179',
         facecolor=C_EXCL, fontsize=7.5)
side_arrow(39, 51, 46, 48)

# Résultat Tri 2 DB
draw_box(28, 43.5, 22, 4,
         'Primary studies from\ndatabase search\nn = 27',
         facecolor=C_ELIG, fontsize=8.5, bold=True)
arrow(28, 49, 28, 45.5)

# ══════════════════════════════════════════════════════════════════════════════
# SNOWBALLING (branche droite)
# ══════════════════════════════════════════════════════════════════════════════

# Surveys lus
draw_box(80, 64, 16, 3.5,
         'Surveys screened\nfor snowballing: n = 13',
         facecolor=C_SNOW, fontsize=7.5)
arrow(64, 64, 72, 64)

# Articles identifiés
draw_box(80, 57, 16, 4,
         'References identified\nfrom surveys\nn = 50',
         facecolor=C_SNOW, fontsize=7.5)
arrow(80, 62.25, 80, 59)

# Snowball Tri 1
draw_box(80, 50, 16, 4,
         'Snowball Tri #1\nIncluded: n = 19\nExcl: 25 · Dup: 6',
         facecolor=C_SNOW, fontsize=7.5)
arrow(80, 55, 80, 52)

# Snowball Tri 2
draw_box(80, 43.5, 16, 4,
         'Snowball Tri #2\nQA ≥ 3/5: n = 11\nQA < 3/5: n = 8',
         facecolor=C_SNOW, fontsize=7.5, bold=False)
arrow(80, 48, 80, 45.5)

# ══════════════════════════════════════════════════════════════════════════════
# INCLUSION
# ══════════════════════════════════════════════════════════════════════════════

# Flèches convergentes
arrow(28, 41.5, 42, 33)
arrow(80, 41.5, 58, 33)

# Boîte finale
draw_box(50, 30, 28, 6,
         'PRIMARY STUDIES INCLUDED\n'
         'in systematic review\n\n'
         'Database search: n = 27\n'
         'Snowballing: n = 11\n'
         'Total: N = 38',
         facecolor='#f9e79f', fontsize=9.5, bold=True,
         edgecolor='#d4ac0d', lw=2.0)

# ── Note méthodologique ───────────────────────────────────────────────────────
ax.text(50, 24, 
        'Screening tools: TF-IDF scoring (scoring.py) + NLP pre-classification (preclassify.py)\n'
        '+ Streamlit interface. Final decisions: human reviewer.\n'
        'QA grid: Q1–Q5, threshold ≥ 3/5. Methodology: Carrera Rivera et al. (2022).',
        ha='center', va='top', fontsize=7, style='italic', color='#7f8c8d',
        linespacing=1.4)

# ── Titre ─────────────────────────────────────────────────────────────────────
ax.text(50, 99.5, 'PRISMA 2020 Flow Diagram', ha='center', va='center',
        fontsize=14, fontweight='bold', color='#2c3e50')

plt.savefig(os.path.join(FIG_DIR, 'fig3_prisma_flow.png'),
            dpi=300, bbox_inches='tight', pad_inches=0.3,
            facecolor='white')
plt.close()
print(f"✓ PRISMA diagram saved to {FIG_DIR}/fig3_prisma_flow.png")
