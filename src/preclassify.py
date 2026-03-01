"""
preclassify.py
Pré-classification automatique des articles du corpus basée sur des règles
de mots-clés alignées avec les critères I1-I6 / E1-E6 du protocole SLR.

[v3 — Phase 2] Score NLP graduel (DEC-019) :
  - Score composite nlp_score (0–10) basé sur le nombre et la force des
    signaux I2/I4/I3 détectés, avec pénalités E1/E2
  - Confiance dérivée du score (seuils absolus) au lieu de règles ad hoc
  - Le score est visible dans l'app et permet un tri secondaire au sein
    de chaque catégorie (surtout les 900+ incertains)

Colonnes produites :
  - nlp_suggestion : 'include' | 'uncertain' | 'survey' | 'exclude'
  - nlp_reason     : code critère (I2+I4, E1, E2, E5, E6, ...)
  - nlp_confidence : 'high' | 'medium' | 'low'
  - nlp_score      : 0–10 (score composite graduel)
  - nlp_tag        : explication lisible

Usage :
    python src/preclassify.py
"""

import pandas as pd
import re
import os

from normalize import load_thesaurus, normalize_text

CORPUS_PATH = 'data/processed/corpus_scored.csv'
THESAURUS_PATH = 'data/thesaurus/vosviewer_thesaurus.txt'

# ══════════════════════════════════════════════════════════════════════════════
# DICTIONNAIRES DE MOTS-CLÉS (inchangés depuis v2)
# ══════════════════════════════════════════════════════════════════════════════

I2_STRONG = [
    r'schema match', r'ontology match', r'ontology align',
    r'entity align', r'entity resolution', r'record linkage',
    r'data harmoniz', r'data harmonis',
    r'variable match', r'variable mapp', r'variable align', r'variable harmoniz',
    r'semantic match', r'semantic align', r'semantic harmoniz',
    r'knowledge align', r'knowledge match',
    r'indicator.*match', r'indicator.*harmoniz', r'indicator.*align',
    r'survey.*harmoniz', r'cross.?lingual.*match', r'multilingual.*match',
    r'heterogeneous.*match', r'heterogeneous.*align',
    r'column match', r'attribute match', r'table match',
    r'inter.?operab.*match', r'schema.*integrat',
]

I2_WEAK = [
    r'data integrat', r'semantic integrat', r'knowledge integrat',
    r'entity linking', r'entity match',
    r'cross.?lingual.*align', r'multilingual.*align',
    r'mapping.*hetero', r'heterogeneous.*integrat',
    r'semantic interoperab', r'data.*align',
]

I4_STRONG = [
    r'neuro.?symbolic', r'neural.?symbolic', r'neurosymbolic',
    r'hybrid.*neural.*symbol', r'hybrid.*symbol.*neural',
    r'neural.*symbolic.*reason', r'symbolic.*reason.*neural',
    r'logic.*neural.*network', r'neural.*logic.*rule',
]

I4_WEAK = [
    r'knowledge graph.*embed', r'embed.*knowledge graph',
    r'ontology.*neural', r'neural.*ontology',
    r'ontology.*transform', r'transform.*ontology',
    r'ontology.*bert', r'bert.*ontology',
    r'ontology.*embed', r'embed.*ontolog',
    r'knowledge.*guid.*neural', r'graph neural.*ontolog',
    r'knowledge.*enrich.*match', r'knowledge.*enhanc.*match',
    r'knowledge.*constrain.*neural', r'rule.*guid.*embed',
    r'logic.*guid.*learn', r'logic.*tensor',
]

I3_PATTERNS = [
    r'explainab', r'interpretab',
    r'human.?in.?the.?loop', r'\bhitl\b',
    r'justificat', r'reasoning trace', r'proof.*match',
    r'transparen.*match', r'transparen.*align',
    r'explain.*match', r'explain.*align',
    r'interpret.*match', r'interpret.*align',
    r'interactive.*feedback', r'user.*feedback.*match',
]

E1_STRONG = [
    r'reinforcement learn', r'deep reinforcement',
    r'drug discover', r'drug target', r'molecule.*property',
    r'protein.*fold', r'protein.*function',
    r'autonomous driv', r'self.?driving',
    r'game.*play', r'game.*agent', r'\batari\b',
    r'medical.*imag.*segment', r'tumor.*segment',
    r'fault.*diagnos(?!.*match)', r'anomaly.*detect(?!.*match)',
    r'speech.*recogn', r'voice.*recogn',
    r'cyber.*securit(?!.*match)', r'intrusion.*detect',
    r'code.*generat', r'program.*synth',
    r'style.*transfer', r'image.*generat',
    r'text.*generat(?!.*match)(?!.*align)',
    r'machine.*translat(?!.*match)',
    r'question.*answer(?!.*match)',
    r'visual.*question.*answer',
    r'sentiment.*analy(?!.*match)',
    r'fake.*news', r'misinformat',
    r'power.*grid(?!.*match)', r'smart.*grid(?!.*match)',
    r'traffic.*flow', r'energy.*forecast',
]

E1_WEAK = [
    r'link.*predict(?!.*match)(?!.*align)',
    r'knowledge graph.*complet',
    r'triple.*classif', r'relation.*classif(?!.*match)',
    r'node.*classif', r'graph.*classif',
    r'text.*classif(?!.*match)', r'named.*entity.*recogn',
    r'recommendat(?!.*match)',
    r'retriev(?!.*match)(?!.*align)',
    r'summar(?!.*match)',
    r'translat(?!.*match)',
    r'predict(?!.*match)(?!.*align)(?!.*harmoniz)',
]

E2_PATTERNS = [
    r'image.*recogn', r'image.*classif', r'image.*retriev',
    r'video.*classif', r'video.*recogn',
    r'audio.*classif', r'speech.*classif',
    r'point.*cloud', r'\blidar\b', r'\bradar\b',
    r'\becg\b', r'\beeg\b', r'biosignal',
    r'image.*segment(?!.*text)(?!.*semantic)',
    r'visual.*ground(?!.*match)',
    r'scene.*graph(?!.*match)(?!.*align)',
]

E5_DOC_TYPES = [
    r'thesis', r'dissertation', r'report(?!.*technical)',
    r'poster', r'abstract.*only', r'editorial',
    r'letter.*editor', r'preface', r'foreword',
    r'chapter', r'book.*review',
]

SURVEY_TITLE = [
    r'\bsurvey\b', r'\breview\b',
    r'state.?of.?the.?art', r'systematic.*review',
    r'literature.*review', r'comprehensive.*overview',
    r'taxonomy.*of', r'benchmark.*of', r'comparison.*of.*method',
]

DEFAULT_SCORE_THRESHOLD = 40

# ══════════════════════════════════════════════════════════════════════════════
# SCORE COMPOSITE (Phase 2)
# ══════════════════════════════════════════════════════════════════════════════

# Poids des signaux pour le score composite
WEIGHTS = {
    'i2_strong': 2,   # Tâche matching clairement identifiée
    'i2_weak':   1,   # Tâche matching probable
    'i4_strong': 2,   # Architecture NeSy explicite
    'i4_weak':   1,   # Composante hybride implicite
    'i3':        1,   # Explicabilité / HITL (bonus RQ2)
    'e1_strong': -3,  # Hors tâche clair
    'e1_weak':   -1,  # Hors tâche probable (par hit)
    'e2':        -2,  # Hors modalité
}

# Seuils de confiance basés sur le score composite
# Pour include : article déjà classé pertinent → seuils plus exigeants
CONF_THRESHOLDS_INCLUDE = {'high': 5, 'medium': 3}
# Pour uncertain : seuils plus bas car le but est de prioriser
CONF_THRESHOLDS_UNCERTAIN = {'high': 3, 'medium': 2}


def compute_nlp_score(n_i2s, n_i2w, n_i4s, n_i4w, n_i3, n_e1s, n_e1w, n_e2):
    """
    Calcule le score composite NLP (0–10).

    Le score reflète la densité et la force des signaux d'inclusion
    détectés, pénalisés par les signaux d'exclusion. Il permet de
    discriminer finement au sein de chaque catégorie de suggestion.

    Formule : Σ(signaux_inclusion × poids) + Σ(signaux_exclusion × pénalité)
    Borné [0, 10].
    """
    raw = (
        n_i2s * WEIGHTS['i2_strong'] +
        n_i2w * WEIGHTS['i2_weak'] +
        n_i4s * WEIGHTS['i4_strong'] +
        n_i4w * WEIGHTS['i4_weak'] +
        n_i3  * WEIGHTS['i3'] +
        n_e1s * WEIGHTS['e1_strong'] +
        n_e1w * WEIGHTS['e1_weak'] +
        n_e2  * WEIGHTS['e2']
    )
    return max(0, min(10, raw))


def _score_to_confidence(nlp_score, thresholds):
    """Dérive le niveau de confiance du score composite."""
    if nlp_score >= thresholds['high']:
        return 'high'
    elif nlp_score >= thresholds['medium']:
        return 'medium'
    return 'low'


# ══════════════════════════════════════════════════════════════════════════════
# MATCHING + SEUIL ADAPTATIF (inchangés depuis v2)
# ══════════════════════════════════════════════════════════════════════════════

def _hits(text: str, patterns: list) -> list:
    return [p for p in patterns if re.search(p, text, re.IGNORECASE)]


def compute_adaptive_threshold(df: pd.DataFrame) -> float:
    """P25 des scores TF-IDF des articles avec signal I2/I4."""
    all_i2_patterns = I2_STRONG + I2_WEAK
    all_i4_patterns = I4_STRONG + I4_WEAK

    has_signal = []
    for _, row in df.iterrows():
        title    = str(row.get('title_norm', row.get('title', ''))).lower()
        abstract = str(row.get('abstract_norm', row.get('abstract', ''))).lower()
        keywords = str(row.get('keywords_norm', row.get('keywords', ''))).lower()
        text = f"{title} {title} {abstract} {keywords}"
        i2_hits = _hits(text, all_i2_patterns)
        i4_hits = _hits(text, all_i4_patterns)
        has_signal.append(len(i2_hits) > 0 or len(i4_hits) > 0)

    signal_scores = df.loc[has_signal, 'relevance_score_pct']
    if len(signal_scores) < 5:
        print(f"  ⚠️  Seulement {len(signal_scores)} articles avec signal"
              f" — fallback seuil = {DEFAULT_SCORE_THRESHOLD}")
        return DEFAULT_SCORE_THRESHOLD

    threshold = signal_scores.quantile(0.25)
    print(f"  Seuil adaptatif : {threshold:.1f}%"
          f" (P25 de {len(signal_scores)} articles avec signal I2/I4)")
    return float(threshold)


# ══════════════════════════════════════════════════════════════════════════════
# LOGIQUE DE DÉCISION (v3 — scoring graduel)
# ══════════════════════════════════════════════════════════════════════════════

def preclassify(row: pd.Series, score_threshold: float = DEFAULT_SCORE_THRESHOLD) -> dict:
    """
    Retourne un dict avec suggestion, reason, confidence, nlp_score, tag.

    [v3] Le score composite nlp_score (0–10) est toujours calculé.
    La confiance est dérivée du score pour les catégories include/uncertain.
    Les décisions structurelles (E6, E5, survey) conservent leur confiance fixe.
    """
    # ── Texte normalisé ───────────────────────────────────────────────────────
    title    = str(row.get('title_norm', row.get('title', ''))).lower()
    abstract = str(row.get('abstract_norm', row.get('abstract', ''))).lower()
    keywords = str(row.get('keywords_norm', row.get('keywords', ''))).lower()
    doc_type = str(row.get('doc_type', '')).lower()
    year     = row.get('year', 0)
    tfidf    = float(row.get('relevance_score_pct', 0))
    has_abs  = bool(row.get('has_abstract', True))

    text = f"{title} {title} {abstract} {keywords}"

    # ── Détection de tous les signaux ─────────────────────────────────────────
    i2_strong = _hits(text, I2_STRONG)
    i2_weak   = _hits(text, I2_WEAK)
    i4_strong = _hits(text, I4_STRONG)
    i4_weak   = _hits(text, I4_WEAK)
    i3_hits   = _hits(text, I3_PATTERNS)
    e1_strong = _hits(text, E1_STRONG)
    e1_weak   = _hits(text, E1_WEAK)
    e2_hits   = _hits(text, E2_PATTERNS)

    # ── Score composite (toujours calculé) ────────────────────────────────────
    nlp_score = compute_nlp_score(
        len(i2_strong), len(i2_weak),
        len(i4_strong), len(i4_weak),
        len(i3_hits),
        len(e1_strong), len(e1_weak),
        len(e2_hits)
    )

    # Raccourcis booléens
    has_i2      = len(i2_strong) >= 1
    has_i2_weak = len(i2_weak) >= 1
    has_i4      = len(i4_strong) >= 1
    has_i4_weak = len(i4_weak) >= 1
    has_i3      = len(i3_hits) >= 1
    has_e1_strong = len(e1_strong) >= 1
    has_e1_weak   = len(e1_weak) >= 2
    has_e2      = len(e2_hits) >= 1

    # ── Détail des signaux pour le tag ────────────────────────────────────────
    def _signal_summary():
        """Construit un résumé lisible des signaux détectés."""
        parts = []
        if i2_strong: parts.append(f"I2×{len(i2_strong)}")
        if i2_weak:   parts.append(f"i2×{len(i2_weak)}")
        if i4_strong: parts.append(f"I4×{len(i4_strong)}")
        if i4_weak:   parts.append(f"i4×{len(i4_weak)}")
        if i3_hits:   parts.append(f"I3×{len(i3_hits)}")
        if e1_strong: parts.append(f"E1×{len(e1_strong)}")
        if e1_weak:   parts.append(f"e1×{len(e1_weak)}")
        if e2_hits:   parts.append(f"E2×{len(e2_hits)}")
        return ' '.join(parts) if parts else 'aucun signal'

    def _result(suggestion, reason, confidence, detail):
        """Construit le dict résultat avec le score et le tag."""
        signals = _signal_summary()
        tag = f"[{nlp_score}/10] {detail} | {signals}"
        return dict(
            suggestion=suggestion, reason=reason, confidence=confidence,
            nlp_score=nlp_score, tag=tag
        )

    # ══════════════════════════════════════════════════════════════════════════
    # RÈGLES DE DÉCISION (même structure que v2, confiance dérivée du score)
    # ══════════════════════════════════════════════════════════════════════════

    # ── Structurel : E6 — hors période ────────────────────────────────────────
    try:
        yr = int(year)
        if yr < 2020 or yr > 2025:
            return _result('exclude', 'E6', 'high',
                           f"Hors période : {yr}")
    except (ValueError, TypeError):
        pass

    # ── Structurel : E5 — type de document ────────────────────────────────────
    e5_hits = _hits(title + ' ' + doc_type, E5_DOC_TYPES)
    if e5_hits:
        return _result('exclude', 'E5', 'high',
                        f"Type non retenu : {e5_hits[0]}")

    # ── Structurel : Survey ───────────────────────────────────────────────────
    survey_hits = _hits(title, SURVEY_TITLE)
    if survey_hits and not has_i2:
        return _result('survey', 'E5s', 'high',
                        f"Survey «{survey_hits[0]}» → snowballing")

    # ── E2 : hors modalité sans I2 ───────────────────────────────────────────
    if has_e2 and not has_i2:
        return _result('exclude', 'E2', 'medium',
                        f"Hors modalités : {e2_hits[0]}")

    # ── E1 fort sans I2 ──────────────────────────────────────────────────────
    if has_e1_strong and not has_i2:
        if not has_abs:
            return _result('uncertain', 'E1?+no_abstract', 'low',
                           f"E1 «{e1_strong[0]}» mais abstract manquant")
        return _result('exclude', 'E1', 'high',
                        f"Hors tâche : «{e1_strong[0]}»")

    # ── E1 faible (2+) sans I2/I4 ────────────────────────────────────────────
    if has_e1_weak and not has_i2 and not has_i2_weak and not has_i4:
        if not has_abs:
            return _result('uncertain', 'E1?+no_abstract', 'low',
                           f"E1 faible + abstract manquant")
        return _result('exclude', 'E1', 'medium',
                        f"Hors tâche probable : {', '.join(e1_weak[:2])}")

    # ══════════════════════════════════════════════════════════════════════════
    # ZONE POSITIVE — confiance dérivée du score composite
    # ══════════════════════════════════════════════════════════════════════════

    # ── INCLUDE : I2 fort + I4 (fort ou faible) ──────────────────────────────
    if has_i2 and (has_i4 or has_i4_weak):
        i4_label = i4_strong[0] if has_i4 else i4_weak[0]
        conf = _score_to_confidence(nlp_score, CONF_THRESHOLDS_INCLUDE)
        detail = f"I2: «{i2_strong[0]}» + I4: «{i4_label}»"
        if has_i3:
            detail += f" + I3: «{i3_hits[0]}»"
        return _result('include', 'I2+I4', conf, detail)

    # ── UNCERTAIN : I2 fort seul ──────────────────────────────────────────────
    if has_i2:
        conf = _score_to_confidence(nlp_score, CONF_THRESHOLDS_UNCERTAIN)
        detail = f"I2: «{i2_strong[0]}» | I4 non détecté → vérifier méthode"
        if has_i3:
            detail += f" | I3: «{i3_hits[0]}»"
        return _result('uncertain', 'I2 seul', conf, detail)

    # ── UNCERTAIN : I4 fort + I2 faible ───────────────────────────────────────
    if has_i4 and has_i2_weak:
        conf = _score_to_confidence(nlp_score, CONF_THRESHOLDS_UNCERTAIN)
        detail = f"I4: «{i4_strong[0]}» + I2 faible: «{i2_weak[0]}» → vérifier tâche"
        return _result('uncertain', 'I4+I2_faible', conf, detail)

    # ── UNCERTAIN : I4 faible + I2 faible ─────────────────────────────────────
    if has_i4_weak and has_i2_weak:
        conf = _score_to_confidence(nlp_score, CONF_THRESHOLDS_UNCERTAIN)
        detail = f"i4: «{i4_weak[0]}» + i2: «{i2_weak[0]}» → signaux faibles, vérifier"
        return _result('uncertain', 'i4+i2_faibles', conf, detail)

    # ── UNCERTAIN : I3 seul ───────────────────────────────────────────────────
    if has_i3 and not has_e1_strong:
        conf = _score_to_confidence(nlp_score, CONF_THRESHOLDS_UNCERTAIN)
        detail = f"I3: «{i3_hits[0]}» | I2/I4 non détectés"
        return _result('uncertain', 'I3 seul', conf, detail)

    # ── UNCERTAIN : I4 seul (fort ou faible, sans aucun I2) ───────────────────
    if has_i4 or has_i4_weak:
        conf = _score_to_confidence(nlp_score, CONF_THRESHOLDS_UNCERTAIN)
        i4_label = i4_strong[0] if has_i4 else i4_weak[0]
        detail = f"I4: «{i4_label}» | I2 absent → vérifier tâche"
        return _result('uncertain', 'I4 seul', conf, detail)

    # ── UNCERTAIN : I2 faible seul ────────────────────────────────────────────
    if has_i2_weak:
        conf = _score_to_confidence(nlp_score, CONF_THRESHOLDS_UNCERTAIN)
        detail = f"i2 faible: «{i2_weak[0]}» | I4 absent → vérifier"
        return _result('uncertain', 'i2_faible seul', conf, detail)

    # ── UNCERTAIN : score TF-IDF élevé sans signal ────────────────────────────
    if tfidf >= score_threshold:
        return _result('uncertain', 'score élevé', 'low',
                        f"TF-IDF {tfidf:.0f}% ≥ seuil {score_threshold:.0f}%"
                        f" mais aucun signal détecté")

    # ── UNCERTAIN : abstract manquant ─────────────────────────────────────────
    if not has_abs:
        return _result('uncertain', 'no_abstract', 'low',
                        f"Abstract manquant — impossible d'évaluer")

    # ── EXCLUDE : aucun signal ────────────────────────────────────────────────
    return _result('exclude', 'E1', 'low',
                    f"Aucun signal — score TF-IDF {tfidf:.0f}%")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    print("═" * 65)
    print("PRÉ-CLASSIFICATION AUTOMATIQUE — Tri #1 (v3 — scoring graduel)")
    print("═" * 65)

    df = pd.read_csv(CORPUS_PATH, encoding='utf-8-sig', keep_default_na=False)
    print(f"\nCorpus chargé : {len(df)} articles")

    # ── Thesaurus ─────────────────────────────────────────────────────────────
    thesaurus = load_thesaurus(THESAURUS_PATH)

    # ── Normalisation (si pas déjà fait) ──────────────────────────────────────
    if 'title_norm' not in df.columns:
        print("Normalisation terminologique...")
        df['title_norm']    = df['title'].fillna('').astype(str).apply(
            lambda t: normalize_text(t, thesaurus))
        df['abstract_norm'] = df['abstract'].fillna('').astype(str).apply(
            lambda t: normalize_text(t, thesaurus))
        df['keywords_norm'] = df['keywords'].fillna('').astype(str).apply(
            lambda t: normalize_text(t, thesaurus))

    if 'has_abstract' not in df.columns:
        abstract_raw = df['abstract'].fillna('').astype(str).str.strip()
        df['has_abstract'] = ~abstract_raw.isin(['', 'nan', 'NaN', 'None'])

    n_no_abs = (~df['has_abstract'].astype(bool)).sum()
    if n_no_abs > 0:
        print(f"  ⚠️  {n_no_abs} articles sans abstract — politique prudente")

    # ── Seuil adaptatif ───────────────────────────────────────────────────────
    print("\nSeuil adaptatif...")
    score_threshold = compute_adaptive_threshold(df)

    # ── Pré-classification ────────────────────────────────────────────────────
    print(f"\nScoring graduel (seuil TF-IDF = {score_threshold:.1f}%)...\n")
    results = df.apply(lambda row: preclassify(row, score_threshold), axis=1)
    df['nlp_suggestion'] = [r['suggestion']  for r in results]
    df['nlp_reason']     = [r['reason']      for r in results]
    df['nlp_confidence'] = [r['confidence']  for r in results]
    df['nlp_score']      = [r['nlp_score']   for r in results]
    df['nlp_tag']        = [r['tag']         for r in results]

    # ══════════════════════════════════════════════════════════════════════════
    # RAPPORT
    # ══════════════════════════════════════════════════════════════════════════
    total = len(df)

    cat_labels = {
        'include':  '🟢 Inclure',
        'uncertain':'🟡 Incertain',
        'survey':   '📚 Survey',
        'exclude':  '🔴 Exclure',
    }
    conf_labels = {'high': 'haute', 'medium': 'moyenne', 'low': 'faible'}

    print("── Répartition par suggestion ──\n")
    for cat, label in cat_labels.items():
        subset = df[df['nlp_suggestion'] == cat]
        n = len(subset)
        pct = n / total * 100
        scores = subset['nlp_score']
        score_info = f"  score moyen={scores.mean():.1f}" if n > 0 else ""
        print(f"  {label:<18} : {n:4d}  ({pct:5.1f}%){score_info}")
        for conf in ['high', 'medium', 'low']:
            n_conf = (subset['nlp_confidence'] == conf).sum()
            if n_conf > 0:
                sub_scores = subset[subset['nlp_confidence'] == conf]['nlp_score']
                print(f"    └ {conf_labels[conf]:<8} : {n_conf:4d}"
                      f"  (score {sub_scores.min():.0f}–{sub_scores.max():.0f})")

    print(f"\n  {'TOTAL':<18} : {total}")

    # ── Distribution globale des scores ───────────────────────────────────────
    print(f"\n── Distribution nlp_score (0–10) ──\n")
    for s in range(11):
        n = (df['nlp_score'] == s).sum()
        bar = '█' * (n // 10) + '░' * max(0, 5 - n // 10)
        print(f"  {s:2d} : {bar} {n:4d}")

    # ── Raisons d'exclusion ───────────────────────────────────────────────────
    excl = df[df['nlp_suggestion'] == 'exclude']
    if len(excl) > 0:
        print("\n── Raisons d'exclusion ──\n")
        for reason, count in excl['nlp_reason'].value_counts().items():
            print(f"  {reason:<20} : {count}")

    # ── Top exemples ──────────────────────────────────────────────────────────
    print("\n── Exemples (top 3 par catégorie, triés par score) ──")
    for cat in ['include', 'uncertain', 'survey', 'exclude']:
        subset = df[df['nlp_suggestion'] == cat].sort_values('nlp_score', ascending=False).head(3)
        if len(subset) == 0:
            continue
        print(f"\n  {cat_labels[cat]}")
        for _, row in subset.iterrows():
            abs_flag = '📄' if row.get('has_abstract', True) else '⚠️'
            print(f"    {abs_flag} [{row['nlp_score']}/10] {str(row['title'])[:65]}")
            print(f"      {row['nlp_tag'][:80]}")

    # ── Sauvegarde ────────────────────────────────────────────────────────────
    df.to_csv(CORPUS_PATH, index=False, encoding='utf-8-sig', na_rep='')
    print(f"\n✓ Sauvegardé : {CORPUS_PATH}")
    print(f"  Nouvelle colonne : nlp_score (0–10)")
    print(f"  Seuil adaptatif : {score_threshold:.1f}%")
    print(f"\n  → streamlit run src/screening_app.py")


if __name__ == '__main__':
    main()
