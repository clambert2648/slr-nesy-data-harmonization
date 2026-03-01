"""
scoring.py
Calcule un score de pertinence TF-IDF pour chaque article
en le comparant à la requête PICOC de la thèse.

[v2 — Phase 1] Améliorations :
  - Normalisation terminologique via thesaurus VOSviewer (DEC-018)
  - Flag has_abstract pour gestion explicite des abstracts manquants
  - Requête PICOC normalisée avec le même thesaurus
"""

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os

from normalize import load_thesaurus, normalize_text

# ── Chemin thesaurus ──────────────────────────────────────────────────────────
THESAURUS_PATH = 'results/tables/vosviewer_thesaurus.txt'

# ── Requête PICOC — termes de référence de la thèse ──────────────────────────
# Concentre les concepts clés des 3 questions de recherche.
# Note : la normalisation thesaurus sera appliquée à cette requête aussi,
# donc les variantes (ex. "neurosymbolic", "knowledge graphs") seront
# automatiquement mappées vers les formes canoniques.
PICOC_QUERY = """
neuro-symbolic semantic matching multilingual indicators heterogeneous
knowledge graph ontology explainable explainability interpretable justification
harmonization data integration monitoring evaluation
human-in-the-loop interactive validation expert feedback HITL
transformer embeddings BERT multilingual similarity
schema matching ontology matching ontology alignment entity alignment entity resolution
ex-post harmonization development indicators variable mapping
neuro-symbolic AI symbolic reasoning neural network hybrid neural symbolic
knowledge representation structured constraints logic rules
interpretability transparency reasoning traces
"""
# Note : I3 révisé — l'explicabilité/HITL est un critère d'inclusion à part entière.
# La query PICOC est renforcée sur ces termes pour mieux scorer les articles RQ2.


def compute_relevance_scores(
    corpus_path: str = 'data/processed/corpus_dedup_final.csv',
    output_path: str = 'data/processed/corpus_scored.csv',
    thesaurus_path: str = THESAURUS_PATH
) -> pd.DataFrame:
    """
    Charge le corpus, applique la normalisation terminologique,
    calcule le score TF-IDF de chaque article par rapport à la
    requête PICOC normalisée, et sauvegarde le résultat trié.
    """

    # ── Chargement du thesaurus ───────────────────────────────────────────────
    thesaurus = load_thesaurus(thesaurus_path)

    print("Chargement du corpus...")
    df = pd.read_csv(corpus_path, encoding='utf-8-sig')
    print(f"  {len(df)} articles chargés")

    # ── Flag has_abstract ─────────────────────────────────────────────────────
    # Identifie les articles sans abstract pour traitement prudent en aval.
    # Un abstract est considéré manquant si vide, NaN, ou "nan".
    abstract_raw = df['abstract'].fillna('').astype(str).str.strip()
    df['has_abstract'] = ~abstract_raw.isin(['', 'nan', 'NaN', 'None'])
    n_no_abs = (~df['has_abstract']).sum()
    if n_no_abs > 0:
        print(f"  ⚠️  {n_no_abs} articles sans abstract — flag has_abstract=False")

    # ── Normalisation terminologique ──────────────────────────────────────────
    # Appliquée sur titre, abstract et keywords avant la vectorisation TF-IDF.
    # Cela réduit les faux négatifs dus aux variantes terminologiques
    # (ex. "neurosymbolic" → "neuro-symbolic ai", "KGs" → "knowledge graph").
    print("Normalisation terminologique (thesaurus VOSviewer)...")

    df['title_norm']    = df['title'].fillna('').astype(str).apply(
        lambda t: normalize_text(t, thesaurus))
    df['abstract_norm'] = df['abstract'].fillna('').astype(str).apply(
        lambda t: normalize_text(t, thesaurus))
    df['keywords_norm'] = df['keywords'].fillna('').astype(str).apply(
        lambda t: normalize_text(t, thesaurus))

    # ── Texte combiné normalisé ───────────────────────────────────────────────
    # Titre doublé pour lui donner plus de poids dans le vecteur TF-IDF.
    df['text_combined'] = (
        df['title_norm'] + ' ' +
        df['title_norm'] + ' ' +
        df['abstract_norm'] + ' ' +
        df['keywords_norm']
    ).str.strip()

    # ── Normalisation de la requête PICOC ─────────────────────────────────────
    picoc_norm = normalize_text(PICOC_QUERY, thesaurus)
    print(f"  Requête PICOC normalisée ({len(picoc_norm.split())} tokens)")

    # ── TF-IDF vectorisation ──────────────────────────────────────────────────
    print("Calcul des scores TF-IDF...")
    vectorizer = TfidfVectorizer(
        max_features=15000,
        ngram_range=(1, 2),     # unigrammes + bigrammes
        stop_words='english',
        min_df=1
    )

    # Corpus + requête PICOC ensemble pour vectorisation cohérente
    all_texts = df['text_combined'].tolist() + [picoc_norm]
    tfidf_matrix = vectorizer.fit_transform(all_texts)

    # Vecteur de la requête PICOC (dernier élément)
    query_vector  = tfidf_matrix[-1]
    corpus_matrix = tfidf_matrix[:-1]

    # Score cosinus entre chaque article et la requête
    scores = cosine_similarity(corpus_matrix, query_vector).flatten()
    df['relevance_score'] = scores

    # ── Normalisation 0-100 pour lisibilité ───────────────────────────────────
    min_s, max_s = scores.min(), scores.max()
    if max_s > min_s:
        df['relevance_score_pct'] = ((scores - min_s) / (max_s - min_s) * 100).round(1)
    else:
        df['relevance_score_pct'] = 50.0

    # ── Tri décroissant par pertinence ────────────────────────────────────────
    df = df.sort_values('relevance_score', ascending=False).reset_index(drop=True)
    df['rank'] = df.index + 1

    # ── Colonnes screening (vides au départ) ──────────────────────────────────
    if 'decision' not in df.columns:
        df['decision'] = ''
    if 'exclusion_reason' not in df.columns:
        df['exclusion_reason'] = ''
    if 'screener_notes' not in df.columns:
        df['screener_notes'] = ''

    # ── Sauvegarde ────────────────────────────────────────────────────────────
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    for col in ['decision', 'exclusion_reason', 'screener_notes']:
        df[col] = df[col].fillna('')
    df.to_csv(output_path, index=False, encoding='utf-8-sig', na_rep='')

    # ── Rapport ───────────────────────────────────────────────────────────────
    print(f"\n✓ Corpus scoré et sauvegardé : {output_path}")
    print(f"  Colonnes ajoutées : has_abstract, title_norm, abstract_norm, keywords_norm")

    print(f"\n── Top 10 articles les plus pertinents ──")
    for _, row in df.head(10).iterrows():
        abs_flag = '📄' if row['has_abstract'] else '⚠️'
        print(f"  #{row['rank']:4d} [{row['relevance_score_pct']:5.1f}%] {abs_flag} {str(row['title'])[:75]}")

    print(f"\n── Distribution des scores ──")
    print(f"  Score moyen  : {df['relevance_score_pct'].mean():.1f}%")
    print(f"  Score médian : {df['relevance_score_pct'].median():.1f}%")
    print(f"  > 50%        : {(df['relevance_score_pct'] > 50).sum()} articles")
    print(f"  > 30%        : {(df['relevance_score_pct'] > 30).sum()} articles")
    print(f"  > 10%        : {(df['relevance_score_pct'] > 10).sum()} articles")

    # ── Impact thesaurus — articles sans abstract ─────────────────────────────
    if n_no_abs > 0:
        no_abs_df = df[~df['has_abstract']]
        print(f"\n── Articles sans abstract ({n_no_abs}) ──")
        for _, row in no_abs_df.iterrows():
            print(f"  #{row['rank']:4d} [{row['relevance_score_pct']:5.1f}%] {str(row['title'])[:75]}")

    return df


if __name__ == '__main__':
    df = compute_relevance_scores()
