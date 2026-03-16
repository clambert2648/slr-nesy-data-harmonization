"""
screening_app.py
Interface Streamlit pour le Screening Tri #1 (titre + résumé).

[v3 — Phase 3] Améliorations interface :
  - Onglets Screening / Révision / Dashboard
    - Barre de filtres (suggestion NLP, confiance, score min/max, base, abstract)
  - Tableau de révision searchable avec modification inline
  - Stats de session (articles/heure, temps restant estimé)
  - Navigation améliorée (filtres appliqués au flux séquentiel)

Lancement :
    streamlit run src/screening_app.py

Prérequis :
    python src/scoring.py        (scores TF-IDF)
    python src/preclassify.py    (suggestions NLP + nlp_score)
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os
from datetime import datetime

CORPUS_PATH = 'data/processed/corpus_scored.csv'
INCLUS_PATH = 'data/processed/articles_inclus.csv'

INCLUSION_CRITERIA = {
    'I1': 'Article de revue (ar) ou acte de conférence (cp), évalué par les pairs. Période : 2020–2025.',
    'I2': "Traite d'une tâche d'appariement / alignement / mapping / harmonisation de données hétérogènes.",
    'I3': "Aborde explicitement l'explicabilité ou l'interprétabilité des décisions d'appariement. [Optionnel — I2 ou I3 requis]",
    'I4': "Propose ou évalue une approche neuro-symbolique / hybride neural+symbolique. [Baselines → extraction A.5]",
    'I5': 'Évaluation empirique minimale : dataset + métrique.',
    'I6': 'Full text accessible.',
}

EXCLUSION_REASONS = {
    'E1': "E1 — Hors tâche : KG completion, link prediction, classification, QA, recommandation. [Exception : entity alignment inter-KG si I2]",
    'E2': 'E2 — Hors modalités : images/vidéo/audio/signaux sans composante textuelle.',
    'E3': 'E3 — Méthode non algorithmique : harmonisation manuelle, discussion conceptuelle.',
    'E4': "E4 — Pas d'évaluation : pas de résultats, pas de métriques, papier position/vision.",
    'E5': 'E5 — Type non retenu : thèse, rapport, chapitre, éditorial, poster, brevet. [Surveys → bouton dédié]',
    'E6': 'E6 — Hors période (< 2020 ou > 2025) ou langue sans abstract exploitable.',
}

NLP_CONFIG = {
    'include':   {'icon': '🟢', 'label': 'Inclure suggéré',   'color': '#d4edda'},
    'uncertain': {'icon': '🟡', 'label': 'Incertain',          'color': '#fff3cd'},
    'survey':    {'icon': '📚', 'label': 'Survey détecté',     'color': '#cce5ff'},
    'exclude':   {'icon': '🔴', 'label': 'Exclusion suggérée', 'color': '#f8d7da'},
    '':          {'icon': '⬜', 'label': 'Non analysé',        'color': '#f8f9fa'},
}
CONF_LABEL = {'high': 'haute ●●●', 'medium': 'moyenne ●●○', 'low': 'faible ●○○', '': '—'}

UNCERTAIN_REASON_ORDER = {
    'I2 seul': 0,
    'I4+I2_faible': 1,
    'I4 seul': 2,
    'i4+i2_faibles': 3,
    'score élevé': 4,
    'i2_faible seul': 5,
    'I3 seul': 6,
    'no_abstract': 7,
    'E1?+no_abstract': 7,
}

FULLTEXT_DIR = 'data/fulltext'

def _find_pdf(rank):
    """Retourne le nom du PDF correspondant au rank, ou None."""
    r = int(rank)
    prefix = f"{r:04d}_" if r >= 1000 else f"{r:03d}_"
    if os.path.isdir(FULLTEXT_DIR):
        for f in os.listdir(FULLTEXT_DIR):
            if f.startswith(prefix) and f.endswith('.pdf'):
                return f
    return None

# ══════════════════════════════════════════════════════════════════════════════
# QUALITY ASSESSMENT — Tri #2
# ══════════════════════════════════════════════════════════════════════════════

QA_CRITERIA = {
    'Q1': {
        'label': 'Objectifs & tâche',
        'question': "Les objectifs de recherche et la tâche d'appariement/harmonisation sont-ils clairement définis ?",
        'scored': True,
    },
    'Q2': {
        'label': 'Architecture reproductible',
        'question': "L'architecture neuro-symbolique proposée est-elle décrite avec suffisamment de détail pour être reproduite ?",
        'scored': True,
    },
    'Q3': {
        'label': 'Dataset & métriques',
        'question': "L'évaluation utilise-t-elle un dataset identifié (nom+taille) et au moins une métrique standard ?",
        'scored': True,
    },
    'Q4': {
        'label': 'Explicabilité / HITL',
        'question': "L'article fournit-il des explications ou justifications sur les décisions d'appariement ?",
        'scored': True,
    },
    'Q5': {
        'label': 'Comparaison baseline',
        'question': "Les résultats sont-ils comparés à au moins une baseline externe sur le même dataset ?",
        'scored': True,
    },
    'Q6': {
        'label': 'Limites (bonus)',
        'question': "Les limites de l'approche ou menaces à la validité sont-elles discutées ?",
        'scored': False,
    },
}
QA_THRESHOLD = 3.0
QA_MAX_SCORE = 5.0  # Q1-Q5 only
QA_OPTIONS = {0.0: 'Non (0)', 0.5: 'Partiellement (0.5)', 1.0: 'Oui (1)'}
QA_COLS = [f'qa_q{i}' for i in range(1, 7)]
QA_NOTE_COLS = [f'qa_notes_q{i}' for i in range(1, 7)]
QA_ALL_COLS = QA_COLS + QA_NOTE_COLS + ['qa_total', 'qa_pass']


def _ensure_qa_columns(df):
    """Ajoute les colonnes QA au DataFrame si absentes."""
    for col in QA_COLS:
        if col not in df.columns:
            df[col] = ''
    for col in QA_NOTE_COLS:
        if col not in df.columns:
            df[col] = ''
    if 'qa_total' not in df.columns:
        df['qa_total'] = ''
    if 'qa_pass' not in df.columns:
        df['qa_pass'] = ''
    return df


def _qa_score_color(score, threshold=QA_THRESHOLD):
    if score >= threshold + 1:
        return '#28a745'  # vert
    elif score >= threshold:
        return '#ffc107'  # jaune — juste au seuil
    else:
        return '#dc3545'  # rouge


def _score_bar(score, max_score=10):
    pct = score / max_score * 100
    if score >= 5:   color = '#28a745'
    elif score >= 3: color = '#ffc107'
    elif score >= 1: color = '#fd7e14'
    else:            color = '#dc3545'
    return (
        f'<div style="background:#e9ecef;border-radius:4px;height:12px;width:100%;margin:2px 0;">'
        f'<div style="background:{color};border-radius:4px;height:12px;width:{pct}%;"></div></div>'
    )


def _sort_screening_pool(pool: pd.DataFrame, sort_mode: str) -> pd.DataFrame:
    if pool.empty:
        return pool

    p = pool.copy()
    p['rank'] = pd.to_numeric(p.get('rank', p.index + 1), errors='coerce').fillna(10**9)
    p['nlp_score'] = pd.to_numeric(p.get('nlp_score', 0), errors='coerce').fillna(0)
    p['relevance_score_pct'] = pd.to_numeric(p.get('relevance_score_pct', 0), errors='coerce').fillna(0)

    if sort_mode == 'Priorité incertains':
        p['is_uncertain'] = (p['nlp_suggestion'] == 'uncertain').astype(int)
        p['uncertain_reason_rank'] = (
            p['nlp_reason'].map(UNCERTAIN_REASON_ORDER).fillna(99)
        )
        return p.sort_values(
            by=['is_uncertain', 'uncertain_reason_rank', 'nlp_score', 'relevance_score_pct', 'rank'],
            ascending=[False, True, False, False, True]
        )

    if sort_mode == 'NLP décroissant':
        return p.sort_values(
            by=['nlp_score', 'relevance_score_pct', 'rank'],
            ascending=[False, False, True]
        )

    if sort_mode == 'TF-IDF décroissant':
        return p.sort_values(
            by=['relevance_score_pct', 'nlp_score', 'rank'],
            ascending=[False, False, True]
        )

    return p.sort_values(by=['rank'], ascending=[True])


# ══════════════════════════════════════════════════════════════════════════════
# MÉTRIQUES DE PERFORMANCE NLP
# ══════════════════════════════════════════════════════════════════════════════

def compute_nlp_metrics(df, score_threshold=5):
    """Calcule les métriques de performance du système NLP par rapport aux
    décisions humaines. Ne considère que les articles screenés avec une
    suggestion NLP non vide."""
    ev = df[(df['decision'] != '') & (df['nlp_suggestion'] != '')].copy()
    m = {}  # dict de résultats

    m['n_evaluated'] = len(ev)
    if m['n_evaluated'] == 0:
        return m

    human_inc = ev['decision'] == 'include'
    nlp_inc   = ev['nlp_suggestion'] == 'include'
    nlp_exc   = ev['nlp_suggestion'] == 'exclude'
    nlp_unc   = ev['nlp_suggestion'] == 'uncertain'

    tp = (human_inc & nlp_inc).sum()
    fn_strict = (human_inc & ~nlp_inc).sum()
    fp = (~human_inc & nlp_inc).sum()

    # 1. Recall strict
    n_human_inc = int(human_inc.sum())
    m['n_human_inc'] = n_human_inc
    m['recall_strict'] = tp / n_human_inc if n_human_inc else None
    m['tp'] = int(tp)

    # 1b. Recall opérationnel (inclure OU incertain avec score >= seuil)
    nlp_operational = nlp_inc | (nlp_unc & (ev['nlp_score'] >= score_threshold))
    tp_op = (human_inc & nlp_operational).sum()
    m['recall_operational'] = tp_op / n_human_inc if n_human_inc else None
    m['tp_operational'] = int(tp_op)

    # 2. Precision sur "inclure"
    n_nlp_inc = int(nlp_inc.sum())
    m['n_nlp_inc'] = n_nlp_inc
    m['precision'] = tp / n_nlp_inc if n_nlp_inc else None

    # 3. Faux négatifs critiques
    fn_crit = (human_inc & nlp_exc).sum()
    m['fn_critical'] = int(fn_crit)
    m['fn_critical_pct'] = fn_crit / n_human_inc * 100 if n_human_inc else 0

    # 4. Couverture par score
    m['coverage'] = {}
    inc_scores = ev.loc[human_inc, 'nlp_score']
    for thr in [5, 6, 7, 8]:
        above = (inc_scores >= thr).sum()
        m['coverage'][thr] = above / n_human_inc * 100 if n_human_inc else 0

    # Top X% coverage
    all_scores_sorted = ev['nlp_score'].sort_values(ascending=False)
    for pct in [10, 20, 30]:
        cutoff_idx = max(1, int(len(all_scores_sorted) * pct / 100))
        top_scores = set(all_scores_sorted.index[:cutoff_idx])
        inc_in_top = human_inc.loc[human_inc.index.isin(top_scores)].sum()
        m['coverage'][f'top{pct}'] = inc_in_top / n_human_inc * 100 if n_human_inc else 0

    # 5. Taux d'incertitude
    m['uncertainty_rate'] = nlp_unc.sum() / m['n_evaluated'] * 100

    # 6. Matrice de confusion
    dec_labels = ['include', 'exclude', 'survey', 'uncertain']
    nlp_labels = ['include', 'exclude', 'survey', 'uncertain']
    present_dec = [l for l in dec_labels if (ev['decision'] == l).any()]
    present_nlp = [l for l in nlp_labels if (ev['nlp_suggestion'] == l).any()]
    confusion = pd.crosstab(
        ev['decision'], ev['nlp_suggestion'],
        rownames=['Décision humaine'], colnames=['Suggestion NLP']
    )
    for col in present_nlp:
        if col not in confusion.columns:
            confusion[col] = 0
    for row in present_dec:
        if row not in confusion.index:
            confusion.loc[row] = 0
    cols_order = [c for c in nlp_labels if c in confusion.columns]
    rows_order = [r for r in dec_labels if r in confusion.index]
    m['confusion'] = confusion.loc[rows_order, cols_order] if rows_order and cols_order else confusion

    # 7. Scores par décision humaine (pour box/violin)
    m['scores_by_decision'] = {
        dec: ev.loc[ev['decision'] == dec, 'nlp_score'].tolist()
        for dec in present_dec
    }

    # Accord global (secondaire)
    m['accord_global'] = (ev['decision'] == ev['nlp_suggestion']).sum() / m['n_evaluated'] * 100

    return m


# ══════════════════════════════════════════════════════════════════════════════
# CHARGEMENT & SAUVEGARDE
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=0)
def load_inclus():
    """Charge articles_inclus.csv (source QA à jour)."""
    if not os.path.exists(INCLUS_PATH):
        return None
    df = pd.read_csv(INCLUS_PATH, encoding='utf-8-sig', keep_default_na=False)
    df = _ensure_qa_columns(df)
    return df


@st.cache_data(ttl=0)
def load_corpus():
    if not os.path.exists(CORPUS_PATH):
        st.error(f"Fichier introuvable : {CORPUS_PATH}\nLance d'abord : python src/scoring.py")
        st.stop()
    df = pd.read_csv(CORPUS_PATH, encoding='utf-8-sig', keep_default_na=False)
    for col in ['decision', 'exclusion_reason', 'screener_notes',
                'nlp_suggestion', 'nlp_reason', 'nlp_confidence', 'nlp_tag']:
        if col in df.columns:
            df[col] = df[col].fillna('').astype(str).str.strip()
        else:
            df[col] = ''
    if 'nlp_score' in df.columns:
        df['nlp_score'] = pd.to_numeric(df['nlp_score'], errors='coerce').fillna(0).astype(int)
    else:
        df['nlp_score'] = 0
    df = _ensure_qa_columns(df)
    return df


def save_decision(df, idx, decision, reason, notes):
    df.loc[idx, 'decision']         = decision
    df.loc[idx, 'exclusion_reason'] = reason
    df.loc[idx, 'screener_notes']   = notes
    df.to_csv(CORPUS_PATH, index=False, encoding='utf-8-sig', na_rep='')
    return df


def _save_and_reload(df):
    st.cache_data.clear()
    st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE — stats de session
# ══════════════════════════════════════════════════════════════════════════════

def _init_session():
    if 'session_start' not in st.session_state:
        st.session_state['session_start'] = datetime.now()
    if 'session_decisions' not in st.session_state:
        st.session_state['session_decisions'] = 0


def _record_decision():
    st.session_state['session_decisions'] = st.session_state.get('session_decisions', 0) + 1


def _session_stats():
    start = st.session_state.get('session_start', datetime.now())
    n = st.session_state.get('session_decisions', 0)
    elapsed = (datetime.now() - start).total_seconds()
    rate = (n / elapsed * 3600) if elapsed > 60 and n > 0 else None
    return n, elapsed, rate


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════

def render_sidebar(df):
    with st.sidebar:
        # ── Session stats ─────────────────────────────────────────────────────
        n_session, elapsed, rate = _session_stats()
        if n_session > 0:
            mins = elapsed / 60
            st.markdown('## 📊 Session')
            st.caption(f'Décisions : **{n_session}** en {mins:.0f} min')
            if rate:
                remaining = (df['decision'] == '').sum()
                eta_hours = remaining / rate if rate > 0 else 0
                st.caption(f'Vitesse : **{rate:.0f}** art./h')
                st.caption(f'Restant : ~{eta_hours:.1f}h ({remaining} articles)')
            st.markdown('---')

        # ── Critères (condensés) ──────────────────────────────────────────────
        with st.expander('📋 Critères inclusion', expanded=False):
            for cid, text in INCLUSION_CRITERIA.items():
                st.caption(f'**{cid}** — {text}')
        with st.expander('🚫 Critères exclusion', expanded=False):
            for code, text in EXCLUSION_REASONS.items():
                st.caption(f'**{code}** — {text.split(" — ")[1]}')

        st.info('**I4** : Inclure si NS explicite ou NS vs baseline sur tâche I2')

        # ── Score NLP légende ─────────────────────────────────────────────────
        if df['nlp_score'].any():
            with st.expander('🎯 Score NLP (0–10)', expanded=False):
                st.caption(
                    '**5+** 🟢 Fort (I2+I4+I3)\n\n'
                    '**3–4** 🟡 Moyen\n\n'
                    '**1–2** 🟠 Faible\n\n'
                    '**0** 🔴 Aucun signal\n\n'
                    '*I2/I4 fort=+2, faible=+1, I3=+1, E1 fort=−3, E1w=−1, E2=−2*'
                )

        # ── Stats NLP globales ────────────────────────────────────────────────
        if df['nlp_suggestion'].any():
            st.markdown('---')
            st.markdown('## Suggestions NLP')
            for key, cfg in NLP_CONFIG.items():
                if key == '':
                    continue
                n = (df['nlp_suggestion'] == key).sum()
                if n > 0:
                    avg_s = df[df['nlp_suggestion'] == key]['nlp_score'].mean()
                    st.caption(f"{cfg['icon']} {cfg['label']} : **{n}** (moy. {avg_s:.1f})")

        # ── Seuils dashboard ──────────────────────────────────────────────
        with st.expander('⚙️ Seuils performance NLP', expanded=False):
            st.session_state['dash_score_threshold'] = st.slider(
                'Score min. recall opérationnel', 3, 8, 5, key='cfg_score_thr')

        # ── Actions en lot ────────────────────────────────────────────────────
        if df['nlp_suggestion'].any():
            st.markdown('---')
            st.markdown('## Actions en lot')
            st.caption('Haute confiance non screenées :')

            for sug, label, reason_col in [
                ('include', '✅ Inclure', ''),
                ('survey',  '📚 Survey', 'E5s'),
                ('exclude', '🔴 Exclure', None),
            ]:
                bulk = df[
                    (df['nlp_suggestion'] == sug) &
                    (df['nlp_confidence'] == 'high') &
                    (df['decision'] == '')
                ]
                if len(bulk) > 0:
                    if st.button(f'{label} {len(bulk)} haute conf.', use_container_width=True,
                                 key=f'bulk_{sug}'):
                        for idx in bulk.index:
                            tag = df.loc[idx, 'nlp_tag']
                            sc  = df.loc[idx, 'nlp_score']
                            if reason_col is None:
                                r = df.loc[idx, 'nlp_reason']
                            else:
                                r = reason_col
                            df = save_decision(df, idx, sug, r,
                                             f'[NLP {sc}/10 haute conf.] {tag}')
                        _save_and_reload(df)


# ══════════════════════════════════════════════════════════════════════════════
# ONGLET 1 — SCREENING
# ══════════════════════════════════════════════════════════════════════════════

def render_screening_tab(df):
    total     = len(df)
    screened  = (df['decision'] != '').sum()
    included  = (df['decision'] == 'include').sum()
    excluded  = (df['decision'] == 'exclude').sum()
    surveys   = (df['decision'] == 'survey').sum()
    uncertain = (df['decision'] == 'uncertain').sum()
    remaining = (df['decision'] == '').sum()
    skipped   = (df['decision'] == 'skipped').sum()

    progress = screened / total if total > 0 else 0
    st.progress(progress, text=f'{screened}/{total} screenés ({progress*100:.1f}%)')

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric('Inclus',     included)
    c2.metric('Exclus',     excluded)
    c3.metric('Surveys',    surveys)
    c4.metric('Incertains', uncertain)
    c5.metric('Restants',   remaining)

    # ── Filtres ───────────────────────────────────────────────────────────────
    with st.expander('🔍 Filtres de navigation', expanded=False):
        fc1, fc2, fc3, fc4, fc5, fc6 = st.columns(6)
        with fc1:
            filt_sug = st.multiselect(
                'Suggestion NLP',
                options=['include', 'uncertain', 'survey', 'exclude'],
                default=[], key='filt_sug'
            )
        with fc2:
            filt_conf = st.multiselect(
                'Confiance',
                options=['high', 'medium', 'low'],
                default=[], key='filt_conf'
            )
        with fc3:
            filt_score_min = st.slider(
                'Score NLP min', 0, 10, 0, key='filt_score_min'
            )
        with fc4:
            filt_score_max = st.slider(
                'Score NLP max', 0, 10, 10, key='filt_score_max'
            )
        with fc5:
            databases = sorted(df['database'].dropna().unique().tolist()) if 'database' in df.columns else []
            filt_db = st.multiselect('Base', options=databases, default=[], key='filt_db')
        with fc6:
            sort_mode = st.selectbox(
                'Tri',
                options=['Rang (défaut)', 'Priorité incertains', 'NLP décroissant', 'TF-IDF décroissant'],
                index=0,
                key='filt_sort_mode'
            )

        fc7, fc8 = st.columns(2)
        with fc7:
            filt_no_abs = st.checkbox('Abstract manquant seulement', key='filt_no_abs')
        with fc8:
            filt_text = st.text_input('Recherche titre', '', key='filt_text')

    # Appliquer filtres sur non-screenés
    pool = df[df['decision'] == ''].copy()
    if filt_sug:
        pool = pool[pool['nlp_suggestion'].isin(filt_sug)]
    if filt_conf:
        pool = pool[pool['nlp_confidence'].isin(filt_conf)]
    if filt_score_min > filt_score_max:
        filt_score_min, filt_score_max = filt_score_max, filt_score_min
    if filt_score_min > 0:
        pool = pool[pool['nlp_score'] >= filt_score_min]
    if filt_score_max < 10:
        pool = pool[pool['nlp_score'] <= filt_score_max]
    if filt_db:
        pool = pool[pool['database'].isin(filt_db)]
    if filt_no_abs:
        abs_col = pool.get('has_abstract', pd.Series([True] * len(pool)))
        pool = pool[abs_col.astype(str).str.lower().isin(['false', '0', ''])]
    if filt_text.strip():
        pool = pool[pool['title'].str.contains(filt_text.strip(), case=False, na=False)]

    pool = _sort_screening_pool(pool, sort_mode)

    any_filter = bool(filt_sug or filt_conf or filt_score_min > 0 or filt_score_max < 10 or filt_db
                       or filt_no_abs or filt_text.strip())
    sort_active = sort_mode != 'Rang (défaut)'
    if any_filter or sort_active:
        parts = []
        if any_filter:
            parts.append(f'🔍 Filtre actif — **{len(pool)}** articles (sur {remaining} restants)')
        if sort_active:
            parts.append(f'🔢 Tri : **{sort_mode}**')
        st.caption(' &nbsp;|&nbsp; '.join(parts))

    # ── Vérifier s'il reste des articles ──────────────────────────────────────
    if pool.empty:
        if remaining == 0:
            st.success('🎉 Screening Tri #1 terminé !')
            _show_summary(df)
        elif any_filter:
            st.info('Aucun article restant ne correspond aux filtres.')
        return

    current_idx = pool.index[0]
    row = df.loc[current_idx]

    tfidf_score = float(row.get('relevance_score_pct', 0))
    rank        = int(row.get('rank', current_idx + 1))
    score_icon  = '🟢' if tfidf_score >= 50 else '🟡' if tfidf_score >= 25 else '🔴'

    # ── Bandeau NLP ───────────────────────────────────────────────────────────
    nlp_sug   = str(row.get('nlp_suggestion', ''))
    nlp_conf  = str(row.get('nlp_confidence', ''))
    nlp_tag   = str(row.get('nlp_tag', ''))
    nlp_score = int(row.get('nlp_score', 0))
    nlp_cfg   = NLP_CONFIG.get(nlp_sug, NLP_CONFIG[''])

    has_nlp = nlp_sug != ''
    if has_nlp:
        bar_html = _score_bar(nlp_score)
        triage_hint = ''
        if nlp_sug == 'uncertain' and sort_mode == 'Priorité incertains':
            ord_rank = int(UNCERTAIN_REASON_ORDER.get(str(row.get('nlp_reason', '')), 99)) + 1
            triage_hint = f' &nbsp;|&nbsp; <strong>Priorité incertain : P{ord_rank}</strong>'
        nlp_html = (
            f'<div style="background:{nlp_cfg["color"]};padding:10px 16px;border-radius:6px;'
            f'margin-bottom:12px;border-left:4px solid #666;">'
            f'<strong>Suggestion :</strong> {nlp_cfg["icon"]} {nlp_cfg["label"]} &nbsp;|&nbsp;'
            f'Confiance : {CONF_LABEL.get(nlp_conf, nlp_conf)} &nbsp;|&nbsp;'
            f'<strong>Score : {nlp_score}/10</strong>{triage_hint}'
            f'{bar_html}'
            f'<em style="font-size:0.85em;">{nlp_tag}</em>'
            f'</div>'
        )
        st.markdown(nlp_html, unsafe_allow_html=True)

    col_article, col_decision = st.columns([3, 1])

    # ── Article ───────────────────────────────────────────────────────────────
    with col_article:
        pos_in_pool = f' (#{list(pool.index).index(current_idx)+1}/{len(pool)} filtrés)' if (any_filter or sort_active) else ''
        st.markdown(f'### Article #{rank} / {total}{pos_in_pool} &nbsp; {score_icon} TF-IDF : {tfidf_score:.1f}%')
        st.markdown(f'## {row["title"]}')

        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric('Année',     str(row.get('year', '—')))
        m2.metric('Base',      str(row.get('database', '—')))
        m3.metric('Requête',   str(row.get('query', '—')))
        m4.metric('Type',      str(row.get('doc_type', '—'))[:25])
        m5.metric('Score NLP', f'{nlp_score}/10')

        source = str(row.get('source', ''))
        if source and source not in ('', 'nan'):
            st.caption(f'*{source}*')

        doi = str(row.get('doi', ''))
        if doi and doi not in ('', 'nan'):
            st.caption(f'[Voir article complet →](https://doi.org/{doi})')

        has_abs = str(row.get('has_abstract', 'True')).lower() not in ('false', '0', '')
        if not has_abs:
            st.warning('⚠️ **Abstract manquant** — évaluation sur titre + mots-clés uniquement.')

        st.divider()

        abstract = str(row.get('abstract', ''))
        if abstract and abstract not in ('', 'nan'):
            st.markdown('**Résumé**')
            st.markdown(abstract)
        elif has_abs:
            st.warning('Aucun résumé disponible.')

        keywords = str(row.get('keywords', ''))
        if keywords and keywords not in ('', 'nan'):
            st.divider()
            st.caption(f'Mots-clés : {keywords}')

    # ── Décision ──────────────────────────────────────────────────────────────
    with col_decision:
        st.markdown('<p style="font-weight:600;font-size:1rem;margin-bottom:4px">Décision</p>', unsafe_allow_html=True)

        notes = st.text_area('Notes', key=f'notes_{current_idx}', height=68,
                             placeholder='Ex: pertinent RQ1, dataset OAEI...',
                             label_visibility='collapsed')

        if has_nlp and nlp_conf == 'hEnigh':
            label_btn = f"{nlp_cfg['icon']} Accepter ({nlp_sug})"
            if st.button(label_btn, use_container_width=True, key=f'accept_nlp_{current_idx}'):
                reason = '' if nlp_sug == 'include' else 'E5s' if nlp_sug == 'survey' else str(row.get('nlp_reason', 'E1'))
                df = save_decision(df, current_idx, nlp_sug, reason,
                                 f'[NLP {nlp_score}/10] {nlp_tag}')
                _record_decision()
                _save_and_reload(df)

        if st.button('✅ Inclure', use_container_width=True, type='primary',
                     key=f'inc_{current_idx}'):
            df = save_decision(df, current_idx, 'include', '', notes)
            _record_decision()
            _save_and_reload(df)

        if st.button('📚 Survey → snowballing', use_container_width=True,
                     key=f'srv_{current_idx}'):
            df = save_decision(df, current_idx, 'survey', 'E5s', notes)
            _record_decision()
            _save_and_reload(df)

        if st.button('❓ Incertain', use_container_width=True,
                     key=f'unc_{current_idx}'):
            df = save_decision(df, current_idx, 'uncertain', '', notes)
            _record_decision()
            _save_and_reload(df)

        st.markdown('<p style="font-weight:600;font-size:0.8rem;margin:4px 0 2px">❌ Exclure</p>', unsafe_allow_html=True)

        for code, label in EXCLUSION_REASONS.items():
            short = label.split(' — ')[1]
            short = short[:42] + '…' if len(short) > 42 else short
            is_suggested = (nlp_sug == 'exclude' and str(row.get('nlp_reason', '')) == code)
            btn_label = f'⚡ {code} — {short}' if is_suggested else f'{code} — {short}'
            if st.button(btn_label, use_container_width=True,
                        key=f'excl_{code}_{current_idx}'):
                df = save_decision(df, current_idx, 'exclude', code, notes)
                _record_decision()
                _save_and_reload(df)

    # ── Navigation rapide ─────────────────────────────────────────────────────
    st.divider()
    nav1, nav2, nav3 = st.columns(3)

    with nav1:
        if st.button('⏭️ Passer (skipped)', key=f'skip_{current_idx}'):
            df = save_decision(df, current_idx, 'skipped', '', '')
            _save_and_reload(df)

    with nav2:
        if uncertain > 0:
            if st.button(f'🔄 Revoir {uncertain} incertains', key='review_unc'):
                df.loc[df['decision'] == 'uncertain', 'decision'] = ''
                df.to_csv(CORPUS_PATH, index=False, encoding='utf-8-sig', na_rep='')
                _save_and_reload(df)

    with nav3:
        if skipped > 0:
            if st.button(f'🔄 Reprendre {skipped} sautés', key='review_skip'):
                df.loc[df['decision'] == 'skipped', 'decision'] = ''
                df.to_csv(CORPUS_PATH, index=False, encoding='utf-8-sig', na_rep='')
                _save_and_reload(df)


# ══════════════════════════════════════════════════════════════════════════════
# ONGLET 2 — RÉVISION
# ══════════════════════════════════════════════════════════════════════════════

def render_review_tab(df):
    screened_df = df[df['decision'] != ''].copy()

    if len(screened_df) == 0:
        st.info('Aucun article encore screené. Commence dans l\'onglet Screening.')
        return

    st.markdown(f'**{len(screened_df)}** articles screenés')

    # ── Filtres révision ──────────────────────────────────────────────────────
    rc1, rc2, rc3 = st.columns(3)
    with rc1:
        rev_dec = st.multiselect(
            'Décision', ['include', 'exclude', 'survey', 'uncertain', 'skipped'],
            default=[], key='rev_dec'
        )
    with rc2:
        rev_text = st.text_input('Recherche titre', '', key='rev_text')
    with rc3:
        reasons_list = [r for r in screened_df['exclusion_reason'].unique().tolist() if r]
        rev_reason = st.multiselect(
            'Raison exclusion', options=sorted(reasons_list),
            default=[], key='rev_reason'
        )

    view = screened_df.copy()
    if rev_dec:
        view = view[view['decision'].isin(rev_dec)]
    if rev_text.strip():
        view = view[view['title'].str.contains(rev_text.strip(), case=False, na=False)]
    if rev_reason:
        view = view[view['exclusion_reason'].isin(rev_reason)]

    if len(view) == 0:
        st.caption('Aucun résultat.')
        return

    # ── Tableau ───────────────────────────────────────────────────────────────
    display_cols = ['rank', 'decision', 'nlp_suggestion', 'nlp_score',
                    'exclusion_reason', 'accessible', 'title', 'year', 'database']
    avail_cols = [c for c in display_cols if c in view.columns]
    display_df = view[avail_cols].copy()

    # Lien DOI
    if 'doi' in view.columns:
        display_df['Lien'] = view['doi'].apply(
            lambda d: f"https://doi.org/{d}" if pd.notna(d) and str(d).strip() not in ('', 'nan') else '')

    col_map = {'rank': '#', 'decision': 'Décision', 'nlp_suggestion': 'NLP',
               'nlp_score': 'Score', 'exclusion_reason': 'Raison',
               'accessible': 'Accès', 'title': 'Titre', 'year': 'Année',
               'database': 'Base'}
    display_df.columns = [col_map.get(c, c) for c in display_df.columns]
    if 'Titre' in display_df.columns:
        display_df['Titre'] = display_df['Titre'].str[:80]

    dec_icons = {'include': '✅', 'exclude': '❌', 'survey': '📚',
                 'uncertain': '❓', 'skipped': '⏭️'}
    if 'Décision' in display_df.columns:
        display_df['Décision'] = display_df['Décision'].map(
            lambda d: f"{dec_icons.get(d, '')} {d}")

    st.dataframe(
        display_df, use_container_width=True, height=400, hide_index=True,
        column_config={'Lien': st.column_config.LinkColumn('Lien', display_text='🔗')}
    )

    # ── Révision individuelle ─────────────────────────────────────────────────
    st.markdown('---')
    st.markdown('#### Modifier une décision')

    rank_options = sorted(view['rank'].astype(int).tolist())
    if rank_options:
        selected_rank = st.selectbox(
            'Sélectionner par rang',
            options=rank_options,
            format_func=lambda r: f"#{r} — {df[df['rank']==r]['title'].values[0][:60]}",
            key='rev_select'
        )

        sel_idx = df[df['rank'] == selected_rank].index[0]
        sel_row = df.loc[sel_idx]

        # ── Détails article ────────────────────────────────────────────
        rc_i1, rc_i2 = st.columns(2)
        with rc_i1:
            st.caption(f"**Décision actuelle :** {sel_row['decision']}")
            st.caption(f"**Raison :** {sel_row['exclusion_reason']}")
            st.caption(f"**NLP :** {sel_row['nlp_suggestion']} ({sel_row['nlp_score']}/10)")
            st.caption(f"**Année :** {sel_row.get('year', '—')} | **Base :** {sel_row.get('database', '—')}")
        with rc_i2:
            st.caption(f"**Notes :** {sel_row['screener_notes']}")
            doi = str(sel_row.get('doi', ''))
            if doi and doi not in ('', 'nan'):
                st.caption(f"[Voir article →](https://doi.org/{doi})")

        # Abstract (essentiel pour modifier en connaissance de cause)
        sel_abstract = str(sel_row.get('abstract', ''))
        sel_keywords = str(sel_row.get('keywords', ''))
        with st.expander('📄 Titre, abstract et mots-clés', expanded=True):
            st.markdown(f"**{sel_row['title']}**")
            if sel_abstract and sel_abstract not in ('', 'nan'):
                st.markdown(sel_abstract)
            else:
                st.warning('Abstract manquant.')
            if sel_keywords and sel_keywords not in ('', 'nan'):
                st.caption(f'Mots-clés : {sel_keywords}')

        new_dec = st.selectbox(
            'Nouvelle décision',
            ['include', 'exclude', 'survey', 'uncertain', '— remettre en attente —'],
            key='new_dec'
        )

        new_reason = ''
        if new_dec == 'exclude':
            new_reason = st.selectbox('Raison', list(EXCLUSION_REASONS.keys()), key='new_reason')

        new_notes = st.text_input('Nouvelles notes', value=str(sel_row['screener_notes']),
                                  key='new_notes')

        cur_access = str(sel_row.get('accessible', ''))
        new_accessible = st.selectbox(
            'Source accessible ?',
            ['', 'oui', 'non'],
            index=['', 'oui', 'non'].index(cur_access) if cur_access in ('', 'oui', 'non') else 0,
            key='new_accessible'
        )

        if st.button('💾 Enregistrer la modification', key='save_rev'):
            if new_dec == '— remettre en attente —':
                df = save_decision(df, sel_idx, '', '', '')
            else:
                df = save_decision(df, sel_idx, new_dec, new_reason, new_notes)
            df.loc[sel_idx, 'accessible'] = new_accessible
            df.to_csv(CORPUS_PATH, index=False, encoding='utf-8-sig', na_rep='')
            st.success(f'Article #{selected_rank} mis à jour.')
            _save_and_reload(df)


# ══════════════════════════════════════════════════════════════════════════════
# ONGLET 3 — DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════

def render_dashboard_tab(df):
    total = len(df)
    screened = (df['decision'] != '').sum()
    inc_n = (df['decision'] == 'include').sum()
    exc_n = (df['decision'] == 'exclude').sum()
    srv_n = (df['decision'] == 'survey').sum()
    unc_n = (df['decision'] == 'uncertain').sum()
    pct = screened / total * 100 if total else 0

    score_thr = st.session_state.get('dash_score_threshold', 5)
    m = compute_nlp_metrics(df, score_threshold=score_thr)
    hi_unscreened = len(df[(df['nlp_confidence'] == 'high') & (df['decision'] == '')])

    # ══════════════════════════════════════════════════════════════════════════
    # A. BANDEAU KPI  (lecture en 5 s)
    # ══════════════════════════════════════════════════════════════════════════
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric('Screenés', f'{screened} / {total}')
    k2.metric('Progression', f'{pct:.1f} %')
    k3.metric('Restants', total - screened)

    if m.get('recall_strict') is not None:
        k4.metric('Rappel inclus', f"{m['recall_strict']*100:.0f} %")
    else:
        k4.metric('Rappel inclus', '—')

    if m.get('fn_critical') is not None:
        k5.metric('⚠ Faux négatifs', m['fn_critical'])
    else:
        k5.metric('Faux négatifs', '—')

    if hi_unscreened > 0:
        k6.metric('⚠ Haute conf. restante', hi_unscreened)
    else:
        k6.metric('Inclus', inc_n)

    # ══════════════════════════════════════════════════════════════════════════
    # B. DÉCISIONS DE SCREENING
    # ══════════════════════════════════════════════════════════════════════════
    st.markdown('#### Décisions de screening')

    col_dec, col_detail = st.columns([3, 2])

    with col_dec:
        if screened > 0:
            dec_counts = df[df['decision'] != '']['decision'].value_counts()
            st.bar_chart(dec_counts, height=180)
        else:
            st.caption('Aucun article screené.')

        if exc_n > 0:
            st.markdown('**Raisons d\'exclusion**')
            reasons = df[df['decision'] == 'exclude']['exclusion_reason'].value_counts()
            for code, count in reasons.items():
                label = EXCLUSION_REASONS.get(code, code)
                parts = label.split(' — ')
                desc = parts[1][:50] if len(parts) > 1 else label[:50]
                st.caption(f'**{code}** ({count}) — {desc}')

    with col_detail:
        st.markdown('**Inclus par requête**')
        included_df = df[df['decision'] == 'include'].copy()
        total_included = len(included_df)
        if total_included > 0 and 'query' in included_df.columns:
            query_parts = (
                included_df['query'].astype(str)
                .str.replace(' ', '', regex=False)
                .str.split('+')
                .explode()
                .str.strip()
            )
            query_parts = query_parts[query_parts != '']
            if len(query_parts) > 0:
                query_stats = (
                    query_parts.value_counts()
                    .rename_axis('Requête')
                    .reset_index(name='N')
                )
                query_stats['%'] = (
                    query_stats['N'] / total_included * 100
                ).round(1)
                st.dataframe(query_stats, hide_index=True, use_container_width=True,
                             height=min(35 * len(query_stats) + 38, 200))
                st.caption(f'{total_included} inclus. Somme > 100 % si multi-requêtes.')
            else:
                st.caption('Aucune requête exploitable.')
        else:
            st.caption('Aucun article inclus.')

    # ══════════════════════════════════════════════════════════════════════════
    # C. PERFORMANCE NLP
    # ══════════════════════════════════════════════════════════════════════════
    if m.get('n_evaluated', 0) == 0:
        st.markdown('#### Performance NLP')
        st.caption('Pas assez de données (screenez des articles avec suggestion NLP).')
    else:
        st.markdown('#### Performance NLP')

        # ── C1. KPI de performance (2 lignes) ────────────────────────────────
        m1, m2, m3, m4 = st.columns(4)

        recall_s = m.get('recall_strict')
        m1.metric(
            'Rappel strict « inclure »',
            f'{recall_s*100:.1f} %' if recall_s is not None else '—',
            help='Parmi les inclus humains, % détectés comme « inclure » par le NLP'
        )
        if recall_s is not None:
            if recall_s >= 0.8:
                m1.caption('✅ Le système détecte bien les articles pertinents.')
            elif recall_s >= 0.5:
                m1.caption('🟡 Détection partielle — vérifier les manqués.')
            else:
                m1.caption('🔴 Le système manque beaucoup d\'inclus.')

        recall_op = m.get('recall_operational')
        m2.metric(
            f'Rappel opérationnel (≥ {score_thr})',
            f'{recall_op*100:.1f} %' if recall_op is not None else '—',
            help=f'Inclure OU incertain avec score ≥ {score_thr}'
        )
        if recall_op is not None:
            m2.caption(f"{m['tp_operational']} / {m['n_human_inc']} retrouvés.")

        prec = m.get('precision')
        m3.metric(
            'Précision « inclure »',
            f'{prec*100:.1f} %' if prec is not None else '—',
            help='Parmi les suggestions « inclure » NLP, % réellement inclus'
        )
        if prec is not None:
            if prec >= 0.7:
                m3.caption('✅ Les suggestions d\'inclusion sont fiables.')
            elif prec >= 0.4:
                m3.caption('🟡 Bruit modéré dans les suggestions.')
            else:
                m3.caption('🔴 Beaucoup de fausses suggestions d\'inclusion.')

        m4.metric(
            'Taux d\'incertitude',
            f"{m['uncertainty_rate']:.1f} %",
            help='Part des articles renvoyés à la revue humaine'
        )
        if m['uncertainty_rate'] > 30:
            m4.caption('🟡 Le modèle hésite souvent — charge de travail élevée.')
        else:
            m4.caption(f"Part déléguée à la revue humaine.")

        # Accord global (secondaire)
        st.caption(
            f"Accord global NLP/humain : **{m['accord_global']:.1f} %** "
            f"(sur {m['n_evaluated']} articles comparés)"
        )

        # ── C2. Risques — faux négatifs critiques ────────────────────────────
        st.markdown('**⚠ Risques — faux négatifs critiques**')
        fn = m.get('fn_critical', 0)
        fn_pct = m.get('fn_critical_pct', 0)
        n_hi = m.get('n_human_inc', 0)

        if fn == 0:
            st.caption('✅ Aucun article inclus n\'a été suggéré « exclure » par le NLP.')
        else:
            st.warning(
                f'**{fn}** article(s) inclus par l\'humain ont été suggérés « exclure » '
                f'par le NLP ({fn_pct:.1f} % des {n_hi} inclus). '
                f'Ces articles auraient été perdus en mode automatique.'
            )
            # List the actual false negatives
            fn_df = df[
                (df['decision'] == 'include') &
                (df['nlp_suggestion'] == 'exclude')
            ][['rank', 'title', 'nlp_score', 'nlp_reason']].copy()
            if len(fn_df) > 0:
                fn_df['title'] = fn_df['title'].str[:70]
                fn_df.columns = ['#', 'Titre', 'Score NLP', 'Raison NLP']
                st.dataframe(fn_df, hide_index=True, use_container_width=True,
                             height=min(35 * len(fn_df) + 38, 180))

        # ── C3. Valeur opérationnelle — couverture par score ─────────────────
        col_cov, col_box = st.columns(2)

        with col_cov:
            st.markdown('**Valeur opérationnelle — couverture des inclus**')
            cov = m.get('coverage', {})

            cov_data = []
            for thr in [5, 6, 7, 8]:
                if thr in cov:
                    cov_data.append({
                        'Seuil': f'Score ≥ {thr}',
                        '% inclus retrouvés': f"{cov[thr]:.1f} %"
                    })
            for p in [10, 20, 30]:
                key = f'top{p}'
                if key in cov:
                    cov_data.append({
                        'Seuil': f'Top {p} % des scores',
                        '% inclus retrouvés': f"{cov[key]:.1f} %"
                    })

            if cov_data:
                st.dataframe(pd.DataFrame(cov_data), hide_index=True,
                             use_container_width=True,
                             height=min(35 * len(cov_data) + 38, 300))
                best_thr = max((cov.get(t, 0), t) for t in [5, 6, 7, 8])
                st.caption(
                    f'Au seuil ≥ {best_thr[1]}, {best_thr[0]:.0f} % des inclus '
                    f'sont retrouvés. Le score NLP peut guider la priorisation.'
                )

        # ── C4. Distribution des scores par décision (box plot) ──────────────
        with col_box:
            st.markdown('**Scores NLP par décision humaine**')
            scores_by_dec = m.get('scores_by_decision', {})
            if scores_by_dec:
                fig = go.Figure()
                colors = {
                    'include': '#28a745', 'exclude': '#dc3545',
                    'survey': '#007bff', 'uncertain': '#ffc107'
                }
                labels = {
                    'include': 'Inclus', 'exclude': 'Exclus',
                    'survey': 'Survey', 'uncertain': 'Incertain'
                }
                for dec in ['include', 'exclude', 'survey', 'uncertain']:
                    vals = scores_by_dec.get(dec, [])
                    if vals:
                        fig.add_trace(go.Box(
                            y=vals, name=labels.get(dec, dec),
                            marker_color=colors.get(dec, '#888'),
                            boxmean=True
                        ))
                fig.update_layout(
                    height=280, margin=dict(l=0, r=0, t=10, b=0),
                    yaxis_title='Score NLP', showlegend=False,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                )
                fig.update_yaxes(range=[-0.5, 10.5], dtick=2, gridcolor='#eee')
                st.plotly_chart(fig, use_container_width=True)

                # Interprétation
                inc_scores = scores_by_dec.get('include', [])
                exc_scores = scores_by_dec.get('exclude', [])
                if inc_scores and exc_scores:
                    inc_med = float(np.median(inc_scores))
                    exc_med = float(np.median(exc_scores))
                    gap = inc_med - exc_med
                    if gap >= 3:
                        st.caption(
                            f'✅ Bonne séparation (méd. inclus={inc_med:.0f}, '
                            f'exclus={exc_med:.0f}). Le score discrimine bien.'
                        )
                    elif gap >= 1:
                        st.caption(
                            f'🟡 Séparation partielle (méd. inclus={inc_med:.0f}, '
                            f'exclus={exc_med:.0f}).'
                        )
                    else:
                        st.caption(
                            f'🔴 Faible séparation (méd. inclus={inc_med:.0f}, '
                            f'exclus={exc_med:.0f}). Le score seul ne suffit pas.'
                        )

        # ── C5. Matrice de confusion ─────────────────────────────────────────
        confusion = m.get('confusion')
        if confusion is not None and not confusion.empty:
            col_mat, col_nlp_dist = st.columns(2)
            with col_mat:
                st.markdown('**Matrice de confusion**')
                label_map = {'include': '✅ Inclus', 'exclude': '❌ Exclus',
                             'survey': '📚 Survey', 'uncertain': '❓ Incertain'}
                disp = confusion.copy()
                disp.index = [label_map.get(i, i) for i in disp.index]
                disp.columns = [label_map.get(c, c) for c in disp.columns]
                st.dataframe(disp, use_container_width=True)
                st.caption('Lignes = décision humaine, colonnes = suggestion NLP.')

            with col_nlp_dist:
                st.markdown('**Confiance × Suggestion NLP**')
                ev_full = df[df['nlp_suggestion'] != '']
                conf_data = []
                for sug in ['include', 'uncertain', 'survey', 'exclude']:
                    for lvl in ['high', 'medium', 'low']:
                        n = ((ev_full['nlp_suggestion'] == sug) & (ev_full['nlp_confidence'] == lvl)).sum()
                        if n > 0:
                            conf_data.append({'Suggestion': sug, 'Confiance': lvl, 'N': n})
                if conf_data:
                    cdf = pd.DataFrame(conf_data)
                    pivot_n = cdf.pivot_table(index='Suggestion', columns='Confiance',
                                              values='N', fill_value=0, aggfunc='sum')
                    for c in ['high', 'medium', 'low']:
                        if c not in pivot_n.columns:
                            pivot_n[c] = 0
                    st.dataframe(pivot_n[['high', 'medium', 'low']], use_container_width=True)

    # ══════════════════════════════════════════════════════════════════════════
    # D. ACTIONS & EXPORTS (compact)
    # ══════════════════════════════════════════════════════════════════════════
    st.markdown('---')
    with st.expander('⬇️ Exports', expanded=False):
        ce1, ce2, ce3, ce4 = st.columns(4)
        with ce1:
            inc_df = df[df['decision'] == 'include']
            st.download_button(f'Inclus ({len(inc_df)})',
                inc_df.to_csv(index=False, encoding='utf-8-sig'),
                'corpus_tri1_inclus.csv', 'text/csv', use_container_width=True)
        with ce2:
            srv_df = df[df['decision'] == 'survey']
            st.download_button(f'Surveys ({len(srv_df)})',
                srv_df.to_csv(index=False, encoding='utf-8-sig'),
                'corpus_tri1_surveys.csv', 'text/csv', use_container_width=True)
        with ce3:
            unc_df = df[df['decision'] == 'uncertain']
            st.download_button(f'Incertains ({len(unc_df)})',
                unc_df.to_csv(index=False, encoding='utf-8-sig'),
                'corpus_tri1_incertains.csv', 'text/csv', use_container_width=True)
        with ce4:
            st.download_button(f'Complet ({total})',
                df.to_csv(index=False, encoding='utf-8-sig'),
                'corpus_complet.csv', 'text/csv', use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# ONGLET 4 — TRI #2 / QUALITY ASSESSMENT
# ══════════════════════════════════════════════════════════════════════════════

def _save_qa(df, idx, scores, notes):
    """Sauvegarde les scores QA pour un article."""
    for i, qid in enumerate(QA_COLS):
        df.loc[idx, qid] = scores[i]
    for i, nid in enumerate(QA_NOTE_COLS):
        df.loc[idx, nid] = notes[i]
    # Total = Q1-Q5 only (Q6 bonus)
    scored_vals = [float(s) for s in scores[:5] if s != '']
    total = sum(scored_vals) if scored_vals else ''
    df.loc[idx, 'qa_total'] = total
    df.loc[idx, 'qa_pass'] = ('oui' if total >= QA_THRESHOLD else 'non') if total != '' else ''
    df.to_csv(INCLUS_PATH, index=False, encoding='utf-8-sig', na_rep='')
    return df


def render_qa_tab(_corpus_df):
    # Charger depuis articles_inclus.csv (source QA à jour)
    df = load_inclus()
    if df is None or len(df) == 0:
        st.info('Fichier articles_inclus.csv introuvable. Complète le screening d\'abord.')
        return

    included = df[df['decision'] == 'include'].copy()

    if len(included) == 0:
        st.info('Aucun article inclus au Tri #1. Complète le screening d\'abord.')
        return

    # ── Statistiques résumées ─────────────────────────────────────────────────
    n_included = len(included)
    n_evaluated = len(included[included['qa_total'] != ''])
    n_remaining = n_included - n_evaluated

    evaluated_df = included[included['qa_total'] != ''].copy()
    if len(evaluated_df) > 0:
        evaluated_df['qa_total'] = pd.to_numeric(evaluated_df['qa_total'], errors='coerce')
        n_pass = (evaluated_df['qa_total'] >= QA_THRESHOLD).sum()
        n_fail = (evaluated_df['qa_total'] < QA_THRESHOLD).sum()
    else:
        n_pass = n_fail = 0

    progress = n_evaluated / n_included if n_included > 0 else 0
    st.progress(progress, text=f'{n_evaluated}/{n_included} évalués ({progress*100:.1f}%)')

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric('Inclus Tri #1', n_included)
    k2.metric('Évalués QA', n_evaluated)
    k3.metric('Restants', n_remaining)
    k4.metric('✅ Passent (≥3/5)', n_pass)
    k5.metric('❌ Échouent (<3/5)', n_fail)

    # ── Sous-onglets : Évaluation | Dashboard ────────────────────────────────
    qa_eval, qa_dash = st.tabs(['🔬 Évaluation', '📊 Tableau de bord QA'])

    # ══════════════════════════════════════════════════════════════════════════
    # ÉVALUATION
    # ══════════════════════════════════════════════════════════════════════════
    with qa_eval:
        # ── Mode de navigation ────────────────────────────────────────────────
        nav_mode = st.radio(
            'Navigation',
            ['Séquentiel (non évalués)', 'Sélection manuelle'],
            horizontal=True, key='qa_nav_mode'
        )

        if nav_mode == 'Séquentiel (non évalués)':
            unevaluated = included[included['qa_total'] == ''].sort_values(
                by='rank', ascending=True
            )
            if unevaluated.empty:
                st.success('🎉 Tous les articles inclus ont été évalués !')
                return
            current_idx = unevaluated.index[0]
            pos_label = f"#{list(unevaluated.index).index(current_idx)+1}/{len(unevaluated)} restants"
        else:
            rank_options = sorted(included['rank'].astype(int).tolist())
            if not rank_options:
                st.info('Aucun article inclus.')
                return

            def _format_qa_rank(r):
                row_t = df[df['rank'] == r]
                if row_t.empty:
                    return f"#{r}"
                title = row_t['title'].values[0][:55]
                qa_val = row_t['qa_total'].values[0]
                status = ''
                if qa_val != '' and qa_val != '':
                    try:
                        status = f' — QA {float(qa_val):.1f}/5'
                    except (ValueError, TypeError):
                        pass
                else:
                    status = ' — ⏳'
                return f"#{r}{status} — {title}"

            selected_rank = st.selectbox(
                'Article', options=rank_options,
                format_func=_format_qa_rank, key='qa_select_rank'
            )
            current_idx = df[df['rank'] == selected_rank].index[0]
            pos_label = ''

        row = df.loc[current_idx]
        rank = int(row.get('rank', current_idx + 1))

        # ── Affichage article ─────────────────────────────────────────────────
        st.markdown(f'### Article #{rank} {pos_label}')
        st.markdown(f'## {row["title"]}')

        m1, m2, m3, m4 = st.columns(4)
        m1.metric('Année', str(row.get('year', '—')))
        m2.metric('Base', str(row.get('database', '—')))
        m3.metric('Score NLP', f"{int(row.get('nlp_score', 0))}/10")
        m4.metric('TF-IDF', f"{float(row.get('relevance_score_pct', 0)):.1f}%")

        doi = str(row.get('doi', ''))
        if doi and doi not in ('', 'nan'):
            st.caption(f'[Voir article complet →](https://doi.org/{doi})')

        # Lien vers le PDF local
        pdf_file = _find_pdf(rank)
        if pdf_file:
            st.caption(f'📂 PDF local : **{pdf_file}**')
        else:
            st.caption('📂 PDF local : _non disponible_')

        with st.expander('📄 Abstract & mots-clés', expanded=False):
            abstract = str(row.get('abstract', ''))
            if abstract and abstract not in ('', 'nan'):
                st.markdown(abstract)
            else:
                st.warning('Abstract manquant.')
            keywords = str(row.get('keywords', ''))
            if keywords and keywords not in ('', 'nan'):
                st.caption(f'Mots-clés : {keywords}')

        screener_notes = str(row.get('screener_notes', ''))
        if screener_notes and screener_notes not in ('', 'nan'):
            st.caption(f'📝 Notes Tri #1 : {screener_notes}')

        st.divider()

        # ── Grille QA ─────────────────────────────────────────────────────────
        st.markdown('#### Grille Quality Assessment')

        # Charger valeurs existantes
        existing_scores = []
        existing_notes = []
        for i in range(6):
            val = row.get(QA_COLS[i], '')
            if val != '' and val is not None:
                try:
                    existing_scores.append(float(val))
                except (ValueError, TypeError):
                    existing_scores.append(None)
            else:
                existing_scores.append(None)
            existing_notes.append(str(row.get(QA_NOTE_COLS[i], '') or ''))

        scores = []
        notes = []
        running_total = 0.0

        for i, (qid, qinfo) in enumerate(QA_CRITERIA.items()):
            bonus_tag = ' 🏷️ *bonus*' if not qinfo['scored'] else ''
            st.markdown(f"**{qid} — {qinfo['label']}**{bonus_tag}")
            st.caption(qinfo['question'])

            col_score, col_note = st.columns([1, 2])

            with col_score:
                options_list = list(QA_OPTIONS.keys())
                if existing_scores[i] is not None and existing_scores[i] in options_list:
                    default_idx = options_list.index(existing_scores[i])
                else:
                    default_idx = 0  # Non (0) par défaut

                score_val = st.radio(
                    f'{qid}', options=options_list,
                    format_func=lambda x: QA_OPTIONS[x],
                    index=default_idx,
                    horizontal=True, key=f'qa_score_{qid}_{current_idx}',
                    label_visibility='collapsed'
                )
                scores.append(score_val)
                if qinfo['scored']:
                    running_total += score_val

            with col_note:
                note_val = st.text_input(
                    f'Note {qid}', value=existing_notes[i],
                    placeholder=f'Justification {qid}...',
                    key=f'qa_note_{qid}_{current_idx}',
                    label_visibility='collapsed'
                )
                notes.append(note_val)

        # ── Score total temps réel ────────────────────────────────────────────
        st.divider()
        color = _qa_score_color(running_total)
        pass_label = '✅ PASSE' if running_total >= QA_THRESHOLD else '❌ ÉCHOUE'
        q6_val = scores[5] if len(scores) > 5 else 0

        score_html = (
            f'<div style="background:{color};color:white;padding:16px 20px;'
            f'border-radius:8px;text-align:center;margin:8px 0;">'
            f'<span style="font-size:2rem;font-weight:700;">{running_total:.1f} / {QA_MAX_SCORE:.0f}</span>'
            f'&nbsp;&nbsp;<span style="font-size:1.4rem;">{pass_label}</span>'
            f'<br/><span style="font-size:0.85rem;opacity:0.9;">Seuil : {QA_THRESHOLD:.0f}/{QA_MAX_SCORE:.0f}'
            f' &nbsp;|&nbsp; Q6 bonus : {q6_val:.1f}</span>'
            f'</div>'
        )
        st.markdown(score_html, unsafe_allow_html=True)

        # ── Boutons d'action ──────────────────────────────────────────────────
        btn1, btn2, btn3 = st.columns(3)
        with btn1:
            if st.button('💾 Sauvegarder', use_container_width=True, key=f'qa_save_{current_idx}'):
                df = _save_qa(df, current_idx, scores, notes)
                st.success(f'Article #{rank} — QA enregistré ({running_total:.1f}/5).')
                _save_and_reload(df)

        with btn2:
            if st.button('💾 Sauvegarder et suivant →', use_container_width=True,
                        type='primary', key=f'qa_next_{current_idx}'):
                df = _save_qa(df, current_idx, scores, notes)
                _record_decision()
                _save_and_reload(df)

        with btn3:
            if st.button('⏭️ Passer', use_container_width=True, key=f'qa_skip_{current_idx}'):
                _save_and_reload(df)

    # ══════════════════════════════════════════════════════════════════════════
    # TABLEAU DE BORD QA
    # ══════════════════════════════════════════════════════════════════════════
    with qa_dash:
        if n_evaluated == 0:
            st.info('Aucun article évalué. Commence l\'évaluation QA.')
            return

        st.markdown('#### Distribution des scores QA')

        # ── Histogramme des scores ────────────────────────────────────────────
        eval_scores = pd.to_numeric(evaluated_df['qa_total'], errors='coerce').dropna()

        col_hist, col_by_q = st.columns(2)

        with col_hist:
            bins = [0, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5]
            fig_hist = go.Figure()
            fig_hist.add_trace(go.Histogram(
                x=eval_scores, xbins=dict(start=0, end=5.5, size=0.5),
                marker_color=['#dc3545' if b < QA_THRESHOLD else '#28a745'
                              for b in bins],
                marker_line_color='white', marker_line_width=1,
            ))
            fig_hist.add_vline(x=QA_THRESHOLD, line_dash='dash', line_color='#333',
                              annotation_text=f'Seuil {QA_THRESHOLD:.0f}/5')
            fig_hist.update_layout(
                height=280, margin=dict(l=0, r=0, t=30, b=0),
                xaxis_title='Score QA (Q1-Q5)', yaxis_title='N articles',
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                bargap=0.1,
            )
            fig_hist.update_xaxes(dtick=0.5, range=[-0.25, 5.75])
            st.plotly_chart(fig_hist, use_container_width=True)

        # ── Score moyen par critère ───────────────────────────────────────────
        with col_by_q:
            st.markdown('**Score moyen par critère**')
            q_means = []
            for i, (qid, qinfo) in enumerate(QA_CRITERIA.items()):
                vals = pd.to_numeric(evaluated_df[QA_COLS[i]], errors='coerce').dropna()
                mean_val = vals.mean() if len(vals) > 0 else 0
                q_means.append({
                    'Critère': f'{qid}',
                    'Label': qinfo['label'],
                    'Moyenne': f'{mean_val:.2f}',
                    'N': len(vals),
                    'Bonus': '🏷️' if not qinfo['scored'] else '',
                })
            st.dataframe(pd.DataFrame(q_means), hide_index=True, use_container_width=True)

        # ── Statistiques résumées ─────────────────────────────────────────────
        st.markdown('#### Statistiques')
        s1, s2, s3, s4 = st.columns(4)
        s1.metric('Score moyen', f'{eval_scores.mean():.2f}/5')
        s2.metric('Score médian', f'{eval_scores.median():.1f}/5')
        s3.metric('Taux passage', f'{n_pass/n_evaluated*100:.0f}%' if n_evaluated else '—')
        s4.metric('Corpus projeté', f'{n_pass} articles')

        # ── Tableau détaillé ──────────────────────────────────────────────────
        st.markdown('#### Articles évalués')
        detail_cols = ['rank', 'title', 'qa_total', 'qa_pass'] + QA_COLS
        avail = [c for c in detail_cols if c in evaluated_df.columns]
        detail = evaluated_df[avail].copy()
        detail['title'] = detail['title'].str[:65]

        col_rename = {
            'rank': '#', 'title': 'Titre', 'qa_total': 'Score',
            'qa_pass': 'Résultat',
            'qa_q1': 'Q1', 'qa_q2': 'Q2', 'qa_q3': 'Q3',
            'qa_q4': 'Q4', 'qa_q5': 'Q5', 'qa_q6': 'Q6',
        }
        detail.columns = [col_rename.get(c, c) for c in detail.columns]
        detail = detail.sort_values('Score', ascending=False)
        st.dataframe(detail, hide_index=True, use_container_width=True, height=400)

        # ── Export ────────────────────────────────────────────────────────────
        st.markdown('---')
        ex1, ex2, ex3 = st.columns(3)
        with ex1:
            pass_df = included[included['qa_pass'] == 'oui']
            st.download_button(
                f'✅ Passent QA ({len(pass_df)})',
                pass_df.to_csv(index=False, encoding='utf-8-sig'),
                'corpus_tri2_pass.csv', 'text/csv', use_container_width=True
            )
        with ex2:
            fail_df = included[included['qa_pass'] == 'non']
            st.download_button(
                f'❌ Échouent QA ({len(fail_df)})',
                fail_df.to_csv(index=False, encoding='utf-8-sig'),
                'corpus_tri2_fail.csv', 'text/csv', use_container_width=True
            )
        with ex3:
            st.download_button(
                f'📊 Complet ({n_included})',
                included.to_csv(index=False, encoding='utf-8-sig'),
                'corpus_tri2_complet.csv', 'text/csv', use_container_width=True
            )


# ══════════════════════════════════════════════════════════════════════════════
# RÉSUMÉ FINAL
# ══════════════════════════════════════════════════════════════════════════════

def _show_summary(df):
    st.subheader('Résumé — Screening Tri #1')
    tot = len(df)
    inc = (df['decision'] == 'include').sum()
    exc = (df['decision'] == 'exclude').sum()
    srv = (df['decision'] == 'survey').sum()
    unc = (df['decision'] == 'uncertain').sum()

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
| Décision | N | % |
|---|---:|---:|
| ✅ Inclus | {inc} | {inc/tot*100:.1f}% |
| 📚 Surveys | {srv} | {srv/tot*100:.1f}% |
| ❓ Incertains | {unc} | {unc/tot*100:.1f}% |
| ❌ Exclus | {exc} | {exc/tot*100:.1f}% |
| **Total** | **{tot}** | **100%** |
        """)

    with col2:
        st.markdown('**Raisons exclusion :**')
        reasons = df[df['decision'] == 'exclude']['exclusion_reason'].value_counts()
        if reasons.empty:
            st.caption('Aucune exclusion enregistrée.')
        else:
            for code, count in reasons.items():
                label = EXCLUSION_REASONS.get(code, code)
                parts = label.split(' — ')
                desc = parts[1][:55] if len(parts) > 1 else label[:55]
                st.markdown(f'- **{code}** ({count}) — {desc}')

    if df['nlp_suggestion'].any():
        m = compute_nlp_metrics(df)
        if m.get('n_evaluated', 0) > 0:
            st.divider()
            ca1, ca2, ca3 = st.columns(3)
            ca1.metric('Rappel inclus',
                       f"{m['recall_strict']*100:.1f}%" if m.get('recall_strict') is not None else '—')
            ca2.metric('Faux négatifs critiques', m.get('fn_critical', 0))
            ca3.metric('Accord global', f"{m['accord_global']:.1f}%")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    st.set_page_config(page_title='SLR — Screening & QA', page_icon='📄', layout='wide')
    _init_session()

    # CSS — compact layout
    st.markdown('''
    <style>
    /* Screening tab — boutons compacts */
    div[data-testid="column"]:last-child .stButton {
        margin-bottom: -6px;
    }
    div[data-testid="column"]:last-child .stButton > button {
        padding-top: 4px !important;
        padding-bottom: 4px !important;
        min-height: 32px !important;
        font-size: 0.82rem !important;
    }
    div[data-testid="column"]:last-child textarea {
        min-height: 55px !important;
    }
    /* Dashboard — réduction espacement vertical */
    [data-testid="stMetric"] {
        padding: 8px 12px;
    }
    h4 { margin-top: 0.8rem !important; margin-bottom: 0.3rem !important; }
    hr { margin: 0.5rem 0 !important; }
    </style>
    ''', unsafe_allow_html=True)

    df = load_corpus()
    render_sidebar(df)

    st.title('SLR — Screening & Quality Assessment')
    st.caption("Appariement sémantique neuro-symbolique d'indicateurs multilingues hétérogènes")

    tab_screen, tab_review, tab_dash, tab_qa = st.tabs([
        '📝 Screening (Tri #1)', '🔍 Révision', '📊 Dashboard', '🔬 Tri #2 / QA'
    ])

    with tab_screen:
        render_screening_tab(df)

    with tab_review:
        render_review_tab(df)

    with tab_dash:
        render_dashboard_tab(df)

    with tab_qa:
        render_qa_tab(df)


if __name__ == '__main__':
    main()
