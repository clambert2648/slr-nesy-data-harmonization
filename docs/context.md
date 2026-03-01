# Contexte technique — Projet RSL NeSy

## Architecture VS Code
```
SLR_thesis/
├── src/
│   ├── scoring.py          # TF-IDF scoring, produit corpus_scored.csv
│   ├── preclassify.py      # Règles NLP → nlp_suggestion/confidence/tag
│   ├── screening_app.py    # Interface Streamlit Tri #1
│   └── run_deduplication.py
├── data/
│   ├── raw/
│   │   ├── scopus/         # CSV exports par requête (R1, R2A, R2B, R3)
│   │   ├── ieee/
│   │   ├── acm/
│   │   └── arxiv/
│   ├── processed/
│   │   ├── corpus_dedup_final.csv   # 1 888 articles après E6
│   │   └── corpus_scored.csv        # 457 articles scorés + colonnes NLP
│   └── logs/
│       └── dedup_log.txt
├── results/
│   ├── screening/          # Exports Tri #1 (inclus, surveys, incertains)
│   ├── qa/                 # Résultats Tri #2
│   └── extraction/         # Formulaires A.5 remplis
├── notebooks/
│   ├── 01_deduplication.ipynb
│   └── 02_bibliometrie_phase1.ipynb
├── docs/
│   └── decisions_log.md
└── requirements.txt
```

## Structure corpus_scored.csv (colonnes critiques)

| Colonne | Type | Description |
|---|---|---|
| `title` | str | Titre de l'article |
| `abstract` | str | Résumé (peut être vide — 9 articles ACM) |
| `authors` | str | Auteurs |
| `year` | int | Année de publication (2020–2025) |
| `doi` | str | DOI (absent pour arXiv) |
| `source` | str | Journal/conférence |
| `keywords` | str | Mots-clés auteurs |
| `doc_type` | str | Article / Conference paper / Preprint / IEEE Conferences... |
| `database` | str | scopus / ieee / acm / arxiv |
| `query` | str | R1 / R2A / R2B / R3 (peut être combiné ex. R2A+R2B) |
| `citations` | int | Nombre de citations |
| `text_combined` | str | titre×2 + abstract + keywords (input scoring) |
| `relevance_score` | float | Score cosinus brut TF-IDF |
| `relevance_score_pct` | float | Score normalisé 0–100 % |
| `rank` | int | Rang par pertinence décroissante |
| `decision` | str | '' / include / exclude / survey / uncertain / skipped |
| `exclusion_reason` | str | '' / E1 / E2 / E3 / E4 / E5 / E6 |
| `screener_notes` | str | Notes libres screeneur |
| `nlp_suggestion` | str | include / exclude / survey / uncertain |
| `nlp_reason` | str | Code critère (I2+I4 / E1 / E2 / E5 / E6 / I2 seul...) |
| `nlp_confidence` | str | high / medium / low |
| `nlp_tag` | str | Explication lisible (ex: "I2: «schema match» | I4: «neuro-symbolic»") |

## Conventions de code

- Encodage CSV : `utf-8-sig` (BOM pour Excel)
- Lecture CSV : toujours `keep_default_na=False` + `fillna('')` sur colonnes décision
- Chemins : relatifs depuis la racine du projet (ex. `data/processed/corpus_scored.csv`)
- Sauvegarde CSV : `na_rep=''` pour éviter NaN résiduel
- Streamlit : `@st.cache_data(ttl=0)` + `st.cache_data.clear()` après chaque save

## Dépendances (requirements.txt)

pandas, scikit-learn, fuzzywuzzy, python-Levenshtein,
streamlit, arxiv, openpyxl