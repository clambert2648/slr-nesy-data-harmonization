# Mise en contexte — Prochain chat
## Objectif : améliorer et compléter l'outil de screening (Tri #1)

---

## Projet

Mémoire de maîtrise en informatique (IA), UQO.  
Directeur : Pr Étienne Gaël Tajeuna.  
Sujet : appariement sémantique explicable d'indicateurs multilingues hétérogènes — approche neuro-symbolique avec validation interactive pour l'harmonisation ex-post en suivi-évaluation (Socodevi).

---

## État actuel du RSL

- **Méthodologie** : Carrera Rivera et al. (2022)
- **Corpus** : 1 890 articles bruts (Scopus, IEEE, ACM, arXiv) → 1 888 après exclusion E6 → **457 articles scorés** (dédoublonnage deux passes : DOI exact + fuzzy titre ≥ 95 %)
- **Phase actuelle** : Tri #1 (screening titre/résumé) — **pas encore commencé**, outils prêts
- **Séquence** : Tri #1 → Tri #2 (QA, seuil 3/5) → Tri #3 (extraction A.5)

---

## Critères (version finale après révisions DEC-014 et DEC-017)

**Inclusion** (I2 ou I3 requis + I4 + I5 + I6) :
- I1 : Article/conférence évalué par les pairs, 2020–2025
- I2 : Tâche d'appariement/alignement/harmonisation de données hétérogènes
- I3 : Explicabilité ou interprétabilité des décisions d'appariement (HITL) — **optionnel, I2 ou I3 suffit**
- I4 : Approche neuro-symbolique / hybride neural+symbolique
- I5 : Évaluation empirique (dataset + métrique)
- I6 : Full text accessible

**Exclusion** :
- E1 : Hors tâche (exception : entity alignment inter-KG si I2 explicite)
- E2 : Hors modalités (images/vidéo/audio sans texte)
- E3 : Méthode non algorithmique
- E4 : Pas d'évaluation
- E5 : Type non retenu (thèses, rapports...) — surveys → snowballing
- E6 : Hors période ou langue non exploitable

**QA Tri #2** (seuil 3/5, Q6 bonus) :
- Q1 : Objectifs et tâche clairement définis
- Q2 : Architecture NeSy décrite pour réimplémentation
- Q3 : Dataset identifié + métrique standard
- Q4 : Explications/justifications sur les décisions d'appariement (HITL) ← *couvre RQ2*
- Q5 : Comparaison à une baseline sur le même dataset
- Q6 : [Bonus] Limites discutées

---

## Architecture projet VS Code

```
SLR_thesis/
├── src/
│   ├── scoring.py              # TF-IDF scoring → corpus_scored.csv
│   ├── preclassify.py          # Règles NLP → nlp_suggestion/confidence/tag
│   └── screening_app.py        # Interface Streamlit Tri #1
├── data/
│   ├── raw/                    # Exports bruts par base
│   └── processed/
│       ├── corpus_dedup_final.csv   # 1 888 articles
│       └── corpus_scored.csv        # 457 articles scorés + colonnes NLP
└── docs/
    └── decisions_log.md
```

---

## Structure corpus_scored.csv

Colonnes critiques pour le code :

| Colonne | Type | Valeurs / Notes |
|---|---|---|
| `title`, `abstract`, `keywords` | str | Peut être vide (9 articles ACM sans abstract) |
| `year` | int | 2020–2025 |
| `doi` | str | Absent pour arXiv |
| `doc_type` | str | "Article", "Conference paper", "Preprint", "IEEE Conferences", "Conference Paper", "Journal Article"... |
| `database` | str | scopus / ieee / acm / arxiv |
| `query` | str | R1 / R2A / R2B / R3 (combinés ex. R2A+R2B) |
| `citations` | int | Variable descriptive, pas critère QA |
| `relevance_score_pct` | float | 0–100 % |
| `rank` | int | Tri décroissant par pertinence |
| `decision` | str | **'' / include / exclude / survey / uncertain / skipped** |
| `exclusion_reason` | str | '' / E1 / E2 / E3 / E4 / E5 / E6 |
| `screener_notes` | str | Notes libres |
| `nlp_suggestion` | str | include / exclude / survey / uncertain |
| `nlp_reason` | str | I2+I4 / E1 / E2 / E5s / E6 / I2 seul / I4+I2_faible... |
| `nlp_confidence` | str | high / medium / low |
| `nlp_tag` | str | Ex: "I2: «schema match» \| I4: «neuro-symbolic»" |

**Conventions CSV critiques :**
- Encodage : `utf-8-sig`
- Lecture : **toujours** `keep_default_na=False` + `fillna('')` sur colonnes décision (bug NaN sinon)
- Sauvegarde : `na_rep=''`
- Chemins : relatifs depuis racine projet

---

## Outils existants — état et limites connues

### scoring.py
- TF-IDF cosinus entre chaque article et la requête PICOC
- Titre doublé dans `text_combined` pour lui donner plus de poids
- Produit `relevance_score_pct` (0–100) et `rank`
- ✅ Fonctionnel, tournera avant screening_app.py

### preclassify.py
- Règles regex sur I2 (fort/faible), I4 (fort/faible), I3, E1 (fort/faible), E2, E5, E6
- Produit : `nlp_suggestion`, `nlp_reason`, `nlp_confidence`, `nlp_tag`
- Valeurs `nlp_suggestion` : **include / exclude / survey / uncertain** (mapping strict avec l'app)
- Logique de décision (10 règles prioritaires) :
  1. E6 (hors période) → exclude high
  2. E5 (type doc) → exclude high
  3. Survey (titre) sans I2 → survey high
  4. E2 sans I2 → exclude medium
  5. E1 fort sans I2 → exclude high
  6. E1 faible (2+) sans I2/I4 → exclude medium
  7. I2 fort + I4 (fort ou faible) → **include high** ← cas idéal
  8. I2 fort seul → uncertain medium
  9. I4 fort + I2 faible → uncertain medium
  10. I3 seul → uncertain low
  11. Score ≥ 40 % sans signal → uncertain low
  12. Aucun signal → exclude low
- ✅ Fonctionnel — résultats sur 457 articles : 66 include (14,4%) / 223 uncertain (48,8%) / 4 survey (0,9%) / 164 exclude (35,9%)

### screening_app.py
- Interface Streamlit Tri #1, layout wide
- **Fonctionnalités actuelles :**
  - Affichage article par article trié par `rank`
  - Bandeau NLP coloré (suggestion + confiance + tag)
  - Bouton "Accepter suggestion" si `nlp_confidence == 'high'`
  - Actions en lot sidebar (inclus/surveys/exclus haute confiance)
  - Navigation : saut de rang, reprise incertains, reprise sautés
  - Exports CSV distincts (inclus, surveys, incertains)
  - Barre de progression + métriques (inclus/exclus/surveys/incertains/restants)
  - Résumé final avec taux d'accord NLP/humain
  - Critères I1–I6 et E1–E6 dans la sidebar (expanders)
- **Limites / améliorations possibles identifiées :**
  - Pas de vue "retour en arrière" sur les articles déjà screenés pour les corriger
  - Pas d'affichage de la distribution NLP avant de commencer (aperçu estimé)
  - Pas de filtre par base/requête pour screener par lot thématique
  - Pas de raccourcis clavier
  - Pas de mode "révision rapide" des articles sautés

---

## Ce qui est à faire dans le prochain chat

**Objectif principal : améliorer screening_app.py avant de lancer le Tri #1**

Pistes prioritaires à discuter/implémenter :
1. **Vue de révision** — pouvoir revenir sur un article déjà décidé et changer la décision
2. **Aperçu NLP pré-screening** — afficher la distribution estimée avant de commencer (pour planifier)
3. **Filtre par base ou requête** — screener d'abord les arXiv, ou d'abord les R2A, etc.
4. **Mode batch assisté** — revoir les exclus/inclus NLP haute confiance par page avant d'accepter en lot
5. Toute autre amélioration suggérée après analyse du code

**Fichiers à coller au début du chat :**
- `screening_app.py` (code complet)
- `preclassify.py` (code complet)
- Ce fichier HANDOFF comme contexte initial

---

## Décisions log — dernière entrée : DEC-017
Les DEC-001 à DEC-017 sont documentées. La prochaine décision sera DEC-018.
