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
import os
from datetime import datetime

CORPUS_PATH = 'data/processed/corpus_scored.csv'

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


# ══════════════════════════════════════════════════════════════════════════════
# CHARGEMENT & SAUVEGARDE
# ══════════════════════════════════════════════════════════════════════════════

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
        fc1, fc2, fc3, fc4, fc5 = st.columns(5)
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

        fc5, fc6 = st.columns(2)
        with fc5:
            filt_no_abs = st.checkbox('Abstract manquant seulement', key='filt_no_abs')
        with fc6:
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

    any_filter = bool(filt_sug or filt_conf or filt_score_min > 0 or filt_score_max < 10 or filt_db
                       or filt_no_abs or filt_text.strip())
    if any_filter:
        st.caption(f'🔍 Filtre actif — **{len(pool)}** articles correspondent '
                   f'(sur {remaining} restants)')

    # ── Vérifier s'il reste des articles ──────────────────────────────────────
    if pool.empty:
        if remaining == 0:
            st.success('🎉 Screening Tri #1 terminé !')
            st.balloons()
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
        st.markdown(
            f"""<div style="background:{nlp_cfg['color']};padding:10px 16px;border-radius:6px;
            margin-bottom:12px;border-left:4px solid #666;">
            <strong>Suggestion :</strong> {nlp_cfg['icon']} {nlp_cfg['label']} &nbsp;|&nbsp;
            Confiance : {CONF_LABEL.get(nlp_conf, nlp_conf)} &nbsp;|&nbsp;
            <strong>Score : {nlp_score}/10</strong>
            {bar_html}
            <em style="font-size:0.85em;">{nlp_tag}</em>
            </div>""",
            unsafe_allow_html=True
        )

    col_article, col_decision = st.columns([3, 1])

    # ── Article ───────────────────────────────────────────────────────────────
    with col_article:
        pos_in_pool = f' (#{list(pool.index).index(current_idx)+1}/{len(pool)} filtrés)' if any_filter else ''
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

        notes = st.text_area('Notes', key=f'notes_{current_idx}', height=60,
                             placeholder='Ex: pertinent RQ1, dataset OAEI...',
                             label_visibility='collapsed')

        if has_nlp and nlp_conf == 'high':
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
                    'exclusion_reason', 'title', 'year', 'database']
    avail_cols = [c for c in display_cols if c in view.columns]
    display_df = view[avail_cols].copy()
    col_map = {'rank': '#', 'decision': 'Décision', 'nlp_suggestion': 'NLP',
               'nlp_score': 'Score', 'exclusion_reason': 'Raison',
               'title': 'Titre', 'year': 'Année', 'database': 'Base'}
    display_df.columns = [col_map.get(c, c) for c in avail_cols]
    if 'Titre' in display_df.columns:
        display_df['Titre'] = display_df['Titre'].str[:80]

    dec_icons = {'include': '✅', 'exclude': '❌', 'survey': '📚',
                 'uncertain': '❓', 'skipped': '⏭️'}
    if 'Décision' in display_df.columns:
        display_df['Décision'] = display_df['Décision'].map(
            lambda d: f"{dec_icons.get(d, '')} {d}")

    st.dataframe(display_df, use_container_width=True, height=400, hide_index=True)

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

        if st.button('💾 Enregistrer la modification', key='save_rev'):
            if new_dec == '— remettre en attente —':
                df = save_decision(df, sel_idx, '', '', '')
            else:
                df = save_decision(df, sel_idx, new_dec, new_reason, new_notes)
            st.success(f'Article #{selected_rank} mis à jour.')
            _save_and_reload(df)


# ══════════════════════════════════════════════════════════════════════════════
# ONGLET 3 — DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════

def render_dashboard_tab(df):
    total = len(df)
    screened = (df['decision'] != '').sum()

    # ── Inclus par requête (présence, gère les combinaisons R1+R2B) ─────────
    st.subheader('Inclus par requête')
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
                .reset_index(name='N inclus')
            )
            query_stats['% des inclus'] = (
                query_stats['N inclus'] / total_included * 100
            ).round(2)

            st.dataframe(query_stats, use_container_width=True, hide_index=True)
            st.caption(
                f'Total inclus: {total_included}. '
                'Attribution par présence de requête; la somme des pourcentages peut dépasser 100% '
                'si un article est tagué avec plusieurs requêtes.'
            )
        else:
            st.caption('Aucune requête exploitable dans les articles inclus.')
    else:
        st.caption('Aucun article inclus pour le moment.')

    # ── Pré-classification NLP ────────────────────────────────────────────────
    st.subheader('Pré-classification NLP')

    s1, s2, s3, s4 = st.columns(4)
    s1.metric('🟢 Inclure',  (df['nlp_suggestion'] == 'include').sum())
    s2.metric('🟡 Incertain', (df['nlp_suggestion'] == 'uncertain').sum())
    s3.metric('📚 Survey',   (df['nlp_suggestion'] == 'survey').sum())
    s4.metric('🔴 Exclure',  (df['nlp_suggestion'] == 'exclude').sum())

    # Tableau croisé confiance × suggestion
    conf_data = []
    for sug in ['include', 'uncertain', 'survey', 'exclude']:
        for lvl in ['high', 'medium', 'low']:
            n = ((df['nlp_suggestion'] == sug) & (df['nlp_confidence'] == lvl)).sum()
            if n > 0:
                avg = df[(df['nlp_suggestion'] == sug) &
                         (df['nlp_confidence'] == lvl)]['nlp_score'].mean()
                conf_data.append({'Suggestion': sug, 'Confiance': lvl,
                                  'N': n, 'Score moy.': round(avg, 1)})
    if conf_data:
        cdf = pd.DataFrame(conf_data)
        pivot_n = cdf.pivot_table(index='Suggestion', columns='Confiance',
                                  values='N', fill_value=0, aggfunc='sum')
        for col in ['high', 'medium', 'low']:
            if col not in pivot_n.columns:
                pivot_n[col] = 0
        st.dataframe(pivot_n[['high', 'medium', 'low']], use_container_width=True)

    # ── Distribution score NLP ────────────────────────────────────────────────
    st.subheader('Distribution score NLP (0–10)')
    chart_data = pd.DataFrame({
        'Score NLP': range(11),
        'Articles': [int((df['nlp_score'] == s).sum()) for s in range(11)]
    })
    st.bar_chart(chart_data, x='Score NLP', y='Articles', height=200)

    # ── Raisons exclusion NLP ─────────────────────────────────────────────────
    st.subheader('Raisons d\'exclusion suggérées')
    excl_nlp = df[df['nlp_suggestion'] == 'exclude']
    if len(excl_nlp) > 0:
        reason_counts = excl_nlp['nlp_reason'].value_counts()
        st.bar_chart(reason_counts, height=200)

    # ── Progression ───────────────────────────────────────────────────────────
    if screened > 0:
        st.subheader('Progression du screening')

        p1, p2, p3 = st.columns(3)
        p1.metric('Screenés', f'{screened}/{total}')
        p2.metric('Progression', f'{screened/total*100:.1f}%')
        p3.metric('Restants', total - screened)

        dec_with_nlp = df[(df['decision'] != '') & (df['nlp_suggestion'] != '')]
        if len(dec_with_nlp) > 0:
            accord = (dec_with_nlp['decision'] == dec_with_nlp['nlp_suggestion']).sum()
            st.metric('Accord NLP/humain', f'{accord/len(dec_with_nlp)*100:.1f}%')

        st.subheader('Répartition des décisions')
        dec_counts = df[df['decision'] != '']['decision'].value_counts()
        st.bar_chart(dec_counts, height=200)

    # ── Exports ───────────────────────────────────────────────────────────────
    st.subheader('Exports')
    col_e1, col_e2, col_e3, col_e4 = st.columns(4)
    with col_e1:
        inc_df = df[df['decision'] == 'include']
        st.download_button(f'⬇️ Inclus ({len(inc_df)})',
            inc_df.to_csv(index=False, encoding='utf-8-sig'),
            'corpus_tri1_inclus.csv', 'text/csv', use_container_width=True)
    with col_e2:
        srv_df = df[df['decision'] == 'survey']
        st.download_button(f'⬇️ Surveys ({len(srv_df)})',
            srv_df.to_csv(index=False, encoding='utf-8-sig'),
            'corpus_tri1_surveys.csv', 'text/csv', use_container_width=True)
    with col_e3:
        unc_df = df[df['decision'] == 'uncertain']
        st.download_button(f'⬇️ Incertains ({len(unc_df)})',
            unc_df.to_csv(index=False, encoding='utf-8-sig'),
            'corpus_tri1_incertains.csv', 'text/csv', use_container_width=True)
    with col_e4:
        st.download_button(f'⬇️ Corpus complet ({total})',
            df.to_csv(index=False, encoding='utf-8-sig'),
            'corpus_complet.csv', 'text/csv', use_container_width=True)


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
        dec_map = df[df['nlp_suggestion'] != ''].copy()
        accord = (dec_map['decision'] == dec_map['nlp_suggestion']).sum()
        total_nlp = len(dec_map[dec_map['decision'] != ''])
        if total_nlp > 0:
            st.divider()
            ca1, ca2 = st.columns(2)
            ca1.metric('Accord NLP/humain', f'{accord/total_nlp*100:.1f}%')
            ca2.metric('Score NLP moyen (inclus)',
                      f"{df[df['decision']=='include']['nlp_score'].mean():.1f}/10"
                      if inc > 0 else '—')


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    st.set_page_config(page_title='Screening Tri #1', page_icon='📄', layout='wide')
    _init_session()

    # CSS — compacte la colonne Décision
    st.markdown('''
    <style>
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
    </style>
    ''', unsafe_allow_html=True)

    df = load_corpus()
    render_sidebar(df)

    st.title('Screening Tri #1 — Titre & Résumé')
    st.caption("RSL : Appariement sémantique neuro-symbolique d'indicateurs multilingues hétérogènes")

    tab_screen, tab_review, tab_dash = st.tabs([
        '📝 Screening', '🔍 Révision', '📊 Dashboard'
    ])

    with tab_screen:
        render_screening_tab(df)

    with tab_review:
        render_review_tab(df)

    with tab_dash:
        render_dashboard_tab(df)


if __name__ == '__main__':
    main()
