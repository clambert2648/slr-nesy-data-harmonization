"""
validate_bulk.py
Tire un échantillon aléatoire des articles inclus en lot (haute confiance NLP)
et génère une fiche de validation pour révision humaine.

Usage :
    python src/validate_bulk.py

Produit :
    data/validation/bulk_include_sample.csv   — échantillon à valider
    data/validation/bulk_include_report.txt   — rapport à compléter
"""

import pandas as pd
import os
import random

CORPUS_PATH = 'data/processed/corpus_scored.csv'
OUTPUT_DIR  = 'data/validation'
SAMPLE_SIZE = 15
SEED        = 42

# Seuils d'acceptation (DEC-021)
THRESHOLD_VALID    = 0.90   # ≥ 90% → lot validé
THRESHOLD_WARNING  = 0.80   # 80-89% → validé avec alerte


def main():
    print("═" * 65)
    print("VALIDATION — Acceptation en lot inclusions haute confiance")
    print("═" * 65)

    df = pd.read_csv(CORPUS_PATH, encoding='utf-8-sig', keep_default_na=False)

    # ── Identifier les articles inclus en lot ─────────────────────────────────
    # Détection par la note "[NLP haute conf.]" ou "[NLP X/10 haute conf.]"
    bulk_mask = (
        (df['decision'] == 'include') &
        (df['screener_notes'].str.contains('haute conf', case=False, na=False))
    )
    bulk_df = df[bulk_mask].copy()
    n_bulk = len(bulk_df)

    if n_bulk == 0:
        print("\n⚠️  Aucun article inclus en lot détecté.")
        print("   Les notes doivent contenir 'haute conf' (ajouté automatiquement par l'app).")
        return

    print(f"\nArticles inclus en lot : {n_bulk}")
    print(f"Taille échantillon     : {SAMPLE_SIZE}")
    print(f"Taux d'échantillonnage : {SAMPLE_SIZE/n_bulk*100:.1f}%")
    print(f"Seed                   : {SEED}")

    # ── Tirage aléatoire ──────────────────────────────────────────────────────
    random.seed(SEED)
    sample_size = min(SAMPLE_SIZE, n_bulk)
    sample_indices = random.sample(list(bulk_df.index), sample_size)
    sample_df = df.loc[sample_indices].copy()

    # Trier par rang pour faciliter la révision
    sample_df = sample_df.sort_values('rank')

    # ── Ajouter colonnes de validation ────────────────────────────────────────
    sample_df['validation_humaine'] = ''       # 'oui' | 'non' | 'incertain'
    sample_df['validation_raison']  = ''       # explication si désaccord
    sample_df['validation_decision_corrigee'] = ''  # si 'non' : quelle décision ?

    # ── Export CSV ────────────────────────────────────────────────────────────
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    export_cols = [
        'rank', 'title', 'year', 'database', 'query',
        'abstract', 'keywords',
        'nlp_suggestion', 'nlp_score', 'nlp_tag',
        'relevance_score_pct',
        'screener_notes',
        'validation_humaine', 'validation_raison', 'validation_decision_corrigee'
    ]
    # Garder seulement les colonnes existantes
    export_cols = [c for c in export_cols if c in sample_df.columns]
    sample_path = os.path.join(OUTPUT_DIR, 'bulk_include_sample.csv')
    sample_df[export_cols].to_csv(sample_path, index=False, encoding='utf-8-sig')

    # ── Rapport texte ─────────────────────────────────────────────────────────
    report_lines = [
        "═" * 65,
        "VALIDATION — Échantillon inclusions haute confiance (DEC-021)",
        "═" * 65,
        f"",
        f"Date de tirage       : 28 février 2026",
        f"Articles en lot      : {n_bulk}",
        f"Échantillon          : {sample_size} articles (seed={SEED})",
        f"Seuil validation     : ≥ {THRESHOLD_VALID*100:.0f}% accord",
        f"Seuil alerte         : {THRESHOLD_WARNING*100:.0f}–{THRESHOLD_VALID*100:.0f}% accord",
        f"",
        "── CONSIGNES ──",
        "",
        "Pour chaque article ci-dessous :",
        "1. Lire le titre et l'abstract",
        "2. Décider : aurais-tu inclus cet article manuellement ?",
        "   - OUI   : I2 ou I3 détecté + I4 détecté → inclusion correcte",
        "   - NON   : ne satisfait pas I2/I3+I4, ou E1/E2 applicable",
        "   - DOUTE : impossible de trancher sur titre/abstract seul",
        "3. Si NON : noter la raison (E1, E2, I2 absent, etc.)",
        "",
        "═" * 65,
        "ÉCHANTILLON",
        "═" * 65,
        "",
    ]

    for i, (_, row) in enumerate(sample_df.iterrows(), 1):
        rank     = int(row.get('rank', 0))
        title    = str(row.get('title', ''))
        year     = str(row.get('year', ''))
        db       = str(row.get('database', ''))
        score    = int(row.get('nlp_score', 0))
        tag      = str(row.get('nlp_tag', ''))
        abstract = str(row.get('abstract', ''))
        kw       = str(row.get('keywords', ''))

        report_lines.extend([
            f"── Article {i}/{sample_size} — Rang #{rank} ──",
            f"",
            f"  Titre    : {title}",
            f"  Année    : {year}",
            f"  Base     : {db}",
            f"  NLP      : {score}/10 — {tag[:80]}",
            f"",
            f"  Abstract : {abstract[:300]}{'...' if len(abstract) > 300 else ''}",
            f"",
            f"  Mots-clés: {kw[:150]}",
            f"",
            f"  ➤ Validation : ______  (OUI / NON / DOUTE)",
            f"  ➤ Si NON — raison : ______________________",
            f"",
        ])

    report_lines.extend([
        "═" * 65,
        "RÉSULTAT",
        "═" * 65,
        "",
        f"  OUI    : __/{sample_size}",
        f"  NON    : __/{sample_size}",
        f"  DOUTE  : __/{sample_size}",
        f"",
        f"  Taux d'accord (OUI+DOUTE) : ____ %",
        f"",
        f"  Conclusion :",
        f"  [ ] ≥ 90% — LOT VALIDÉ",
        f"  [ ] 80-89% — VALIDÉ AVEC ALERTE (désaccords révisés individuellement)",
        f"  [ ] < 80% — LOT INVALIDÉ (119 articles remis en screening manuel)",
        f"",
        f"  Notes : ",
        f"  ",
        f"",
        "══════════════════════════════════════════════════════════════════",
        "Reporter le résultat dans DEC-021 du decisions_log.md",
        "══════════════════════════════════════════════════════════════════",
    ])

    report_path = os.path.join(OUTPUT_DIR, 'bulk_include_report.txt')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))

    # ── Aperçu console ────────────────────────────────────────────────────────
    print(f"\n── Échantillon tiré ({sample_size} articles) ──\n")
    for _, row in sample_df.iterrows():
        rank  = int(row.get('rank', 0))
        score = int(row.get('nlp_score', 0))
        title = str(row.get('title', ''))[:65]
        print(f"  #{rank:4d} [{score}/10] {title}")

    print(f"\n✓ Fichiers générés :")
    print(f"  {sample_path}")
    print(f"  {report_path}")
    print(f"\n── Procédure ──")
    print(f"  1. Ouvre {report_path}")
    print(f"  2. Lis chaque article et note OUI/NON/DOUTE")
    print(f"  3. Calcule le taux d'accord")
    print(f"  4. Reporte le résultat dans DEC-021")
    print(f"  5. Si NON sur certains articles → corrige dans l'onglet Révision")


if __name__ == '__main__':
    main()
