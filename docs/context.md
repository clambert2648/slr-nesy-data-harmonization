# Contexte technique — Projet RSL NeSy

## Architecture VS Code
```
SLR_thesis/
├── run_deduplication.py     # Script de lancement dédoublonnage
├── run_fetch_arxiv.py       # Script de lancement collecte arXiv
├── src/
│   ├── deduplication.py      # Fonctions dédoublonnage (DOI + fuzzy)
│   ├── fetch_arxiv.py        # Collecte API arXiv
│   ├── normalize.py          # Normalisation champs inter-bases
│   ├── scoring.py            # TF-IDF scoring, produit corpus_scored.csv
│   ├── preclassify.py        # Règles NLP → nlp_suggestion/confidence/tag
│   ├── screening_app.py      # Interface Streamlit Tri #1
│   ├── validate_bulk.py      # Validation actions en lot screening
│   └── generate_thesaurus.py # Génération thésaurus VOSviewer
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
│   ├── figures/            # Fichiers VOSviewer et figures
│   ├── qa/                 # Résultats Tri #2
│   └── tables/             # Tables exportées (VOS, overlap, top auteurs...)
├── notebooks/
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

## Interprétation méthodologique des scores (Tri #1)

Le pipeline distingue explicitement deux niveaux d'évaluation complémentaires.

- **`relevance_score_pct` (TF-IDF, 0–100 %)** : mesure une **proximité lexicale/statistique** entre le texte de l'article (titre×2 + résumé + mots-clés, après normalisation par thesaurus) et la requête PICOC.
- **`nlp_score` (règles, 0–10)** : mesure une **densité de signaux protocole** (I2/I4/I3) pénalisée par des signaux d'exclusion (E1/E2), pour soutenir la décision de tri.

Conséquence méthodologique :
- le TF-IDF sert principalement à la **priorisation** (ordre de lecture),
- le score NLP sert à l'**aide à la décision** (include / uncertain / exclude / survey),
- l'ensemble reste **semi-automatique** : la décision finale demeure humaine dans `screening_app.py`.

Cette séparation réduit le risque de confusion entre « similarité thématique » et « conformité aux critères d'inclusion/exclusion », ce qui améliore la traçabilité et la validité du protocole.

## Stratégie d'exclusion batch (Tri #1)

Le screening a combiné exclusions automatisées et screening manuel en deux phases :

**Phase 1 — Triple concordance (264 articles) :**
Critère : `auto_decision = exclude` ET `nlp_suggestion = exclude` ET `nlp_score ≤ 2`. Les trois signaux automatiques convergent vers l'exclusion. Validé par revue humaine en 5 passes regex (DEC-022).

**Phase 2 — Seuil de saturation empirique (811 articles supplémentaires) :**
Critère : `(NLP ≤ 2 ET TF-IDF ≤ 15 %) OU NLP ≤ 1`. Justification : le screening manuel descendant (par TF-IDF) a atteint la saturation — le taux d'inclusion tombe à zéro dans cette zone. La dernière inclusion se situe au rang TF-IDF #971 (TF = 15,8 %). Au-delà, 0 inclusion sur 917 articles screenés. Validation rétrospective : 0 faux négatif au niveau extraction (n = 54). Voir DEC-033.

**Total : 1 075 exclusions batch** (57 % du corpus). 813 articles screenés manuellement, contenant l'intégralité des 81 inclusions et 54 articles d'extraction.

## Conventions de code

- Encodage CSV : `utf-8-sig` (BOM pour Excel)
- Lecture CSV : toujours `keep_default_na=False` + `fillna('')` sur colonnes décision
- Chemins : relatifs depuis la racine du projet (ex. `data/processed/corpus_scored.csv`)
- Sauvegarde CSV : `na_rep=''` pour éviter NaN résiduel
- Streamlit : `@st.cache_data(ttl=0)` + `st.cache_data.clear()` après chaque save

## Dépendances (requirements.txt)

- `requirements.txt` est un **freeze complet de l'environnement** (beaucoup plus large que le pipeline minimal).
- Dépendances coeur pipeline : `pandas`, `scikit-learn`, `fuzzywuzzy`, `python-Levenshtein`, `streamlit`, `arxiv`, `openpyxl`.
- Pour la reproductibilité stricte : installer tout le `requirements.txt`.