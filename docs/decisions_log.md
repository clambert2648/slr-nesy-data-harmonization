# Journal des décisions méthodologiques
**Protocole SLR — Appariement neuro-symbolique**
Constance Lambert-Tremblay — M. Sc. informatique, UQO
Directeur : Pr Étienne Gaël Tajeuna

---

## FORMAT D'ENTRÉE

Chaque décision suit le format :
- **Date** : date de la décision
- **Base / Outil** : système concerné
- **Décision** : ce qui a été choisi
- **Justification** : pourquoi ce choix
- **Limite reconnue** : impact potentiel sur la couverture
- **Impact PRISMA** : comment documenter dans le rapport

---

## DÉCISIONS — BASES DE DONNÉES

### DEC-001 — Sélection des bases de données
**Date :** 27 février 2026
**Base :** Toutes
**Décision :** Quatre bases retenues : Scopus, IEEE Xplore, ACM Digital Library (Full-Text Collection), ArXiv.
**Justification :** Scopus assure la couverture multidisciplinaire la plus large. IEEE Xplore couvre les conférences CS/ingénierie spécialisées. ACM Full-Text Collection couvre les publications ACM majeures en informatique (SIGMOD, VLDB, WWW). ArXiv est ajouté à la demande du directeur pour capturer les preprints récents en IA/ML non encore indexés.
**Limite reconnue :** Web of Science écarté faute d'accès institutionnel à la recherche avancée.
**Impact PRISMA :** Documenter les 4 bases dans le tableau de synthèse des requêtes.

---

### DEC-002 — ACM : choix de la collection
**Date :** 27 février 2026
**Base :** ACM Digital Library
**Décision :** Utilisation de "The ACM Full-Text Collection" plutôt que "The ACM Guide to Computing Literature".
**Justification :** Le critère I6 exige l'accessibilité du full text. Le Guide to Computing Literature indexe des publications d'autres éditeurs sans garantir l'accès au PDF, ce qui rendrait le QA (Tri #2) et l'extraction (B.5) impossibles pour une partie du corpus.
**Limite reconnue :** La couverture est restreinte aux publications ACM uniquement. Compensée par Scopus et IEEE Xplore.
**Impact PRISMA :** Mentionner la restriction de collection dans la note méthodologique du tableau PRISMA.

---

### DEC-003 — ACM : champ de recherche
**Date :** 27 février 2026
**Base :** ACM Digital Library
**Décision :** Recherche effectuée sur le champ Abstract uniquement via l'interface "Search Within".
**Justification :** ACM ne propose pas d'équivalent direct à TITLE-ABS-KEY de Scopus. La combinaison Abstract + Title produisait 0 résultats (logique AND inter-champs impossible). Le champ Abstract est le plus proche de TITLE-ABS-KEY pour des requêtes multi-blocs AND.
**Limite reconnue :** Articles dont les termes clés apparaissent uniquement dans le titre non capturés. Risque estimé faible.
**Impact PRISMA :** Documenter dans la colonne "Adaptations syntaxiques" du tableau ACM.

---

### DEC-004 — ACM : filtre type de document
**Date :** 27 février 2026
**Base :** ACM Digital Library
**Décision :** Filtre appliqué : Content Type = "Research Article" uniquement.
**Justification :** ACM ne propose pas de filtre "Conference Paper" distinct. Le filtre "Research Article" capture 82 articles incluant 51 issus de Proceedings (conférences) et 14 issus de Journals, conformément au critère I1. Les 16 "Other periodicals" seront filtrés au screening si non pertinents.
**Limite reconnue :** Short Papers (10) et Surveys (4) exclus. Les Surveys conservés pour le snowballing (E5).
**Impact PRISMA :** Documenter le filtre dans la colonne "Adaptations" du tableau de synthèse.

---

### DEC-005 — IEEE Xplore : adaptation syntaxique (pluriels)
**Date :** 27 février 2026
**Base :** IEEE Xplore
**Décision :** Wildcards à l'intérieur des guillemets ne fonctionnant pas dans IEEE Xplore, tous les pluriels ont été explicités dans les requêtes.
**Justification :** Contrainte syntaxique — "knowledge graph*" ne capture pas "knowledge graphs". Les termes concernés doublés : "knowledge graph" OR "knowledge graphs", etc.
**Limite reconnue :** Risque résiduel si des variantes orthographiques non anticipées existent. Atténué par la couverture Scopus.
**Impact PRISMA :** Documenter dans la colonne "Adaptations syntaxiques" du tableau IEEE.

---

### DEC-006 — IEEE Xplore : filtre date
**Date :** 27 février 2026
**Base :** IEEE Xplore
**Décision :** Filtre Year Range 2020–2025 appliqué via l'interface (inclusif des deux bornes).
**Justification :** Le filtre Range d'IEEE Xplore est inclusif — équivalent à PUBYEAR > 2019 AND PUBYEAR < 2026 dans Scopus.
**Limite reconnue :** Aucune.
**Impact PRISMA :** Aucun ajustement nécessaire.

---

### DEC-007 — ArXiv : inclusion comme source primaire
**Date :** 27 février 2026
**Base :** ArXiv
**Décision :** ArXiv inclus comme base de données primaire à la demande explicite du directeur de recherche.
**Justification :** Pr Étienne Gaël Tajeuna a explicitement demandé l'inclusion d'ArXiv pour capturer les preprints récents en IA/ML, particulièrement pertinents pour les approches neuro-symboliques émergentes.
**Limite reconnue :** Les preprints ne sont pas évalués par les pairs au moment du dépôt (tension avec I1). Atténuée : (1) screening et QA identiques ; (2) statut preprint mis à jour à l'extraction si publication confirmée.
**Impact PRISMA :** Documenter ArXiv comme source distincte. Ajouter note sur le statut preprint dans les Limites méthodologiques.

---

### DEC-008 — ArXiv : méthode de collecte
**Date :** 27 février 2026
**Base :** ArXiv
**Décision :** Collecte via l'API Python `arxiv`, max_results=200 par requête, filtre année 2020–2025 en post-traitement.
**Justification :** L'interface web ArXiv ne supporte pas de recherche booléenne avancée. L'API permet des requêtes structurées reproductibles et un export direct CSV.
**Limite reconnue :** Requêtes ArXiv moins précises que Scopus — le bloc P simplifié peut introduire plus de bruit. Le screening compensera.
**Impact PRISMA :** Documenter le script et ses paramètres dans l'annexe méthodologique.

---

## DÉCISIONS — PIPELINE DE TRAITEMENT

### DEC-009 — Dédoublonnage : approche hiérarchique deux passes
**Date :** 27 février 2026
**Outil :** Python (pandas + fuzzywuzzy)
**Décision :** Dédoublonnage en deux passes séquentielles : (1) correspondance exacte DOI, (2) similarité titre ≥ 95 % (fuzzy) avec vérification de l'année. Fusion des labels de provenance plutôt que suppression.
**Justification :** Garantit la traçabilité complète — chaque article conserve l'information de sa base d'origine et de sa requête. La fusion documente les chevauchements inter-bases pour le rapport PRISMA.
**Limite reconnue :** Seuil fuzzy 95 % peut manquer des doublons fortement reformulés. Atténué par la priorité des DOI.
**Impact PRISMA :** Comptages de chaque étape consignés dans data/logs/dedup_log.txt.

---

### DEC-010 — Format d'export par base
**Date :** 27 février 2026
**Outil :** Pipeline Python + Zotero
**Décision :** Double export — CSV pour le pipeline Python, BibTeX/RIS pour Zotero.
**Justification :** CSV optimal pour le traitement pandas. BibTeX/RIS optimal pour l'import Zotero → Better BibTeX → Overleaf.
**Limite reconnue :** Aucune.
**Impact PRISMA :** Aucun.

---

### DEC-011 — ACM : abstracts manquants + résultats dédoublonnage
**Date :** 27 février 2026
**Outil :** run_deduplication.py

9 articles sur 82 (11 %) exportés sans abstract. Ces articles seront traités manuellement lors du screening (Tri #1).

**Corpus final après dédoublonnage : 1 890 articles**

| Base | Articles uniques |
|---|---:|
| Scopus uniquement | 894 |
| IEEE uniquement | 360 |
| Scopus+IEEE | 190 |
| ACM uniquement | 190 |
| ArXiv uniquement | 177 |
| Autres combinaisons | 79 |

Chevauchements inter-requêtes notables :
- R2A+R2B : 34 articles (confirme l'overlap 2,3 % des tests pilotes)
- R1+R3 : 42 articles (attendu — harmonisation ↔ contexte M&E)

ArXiv contribue 177 articles uniques non présents dans les autres bases, ce qui justifie son inclusion (DEC-007).

---

### DEC-012 — Exclusion hors période + paramètres VOSviewer
**Date :** 27 février 2026

**Partie A — Exclusion hors période :**
2 articles ACM (année 2026) retirés du corpus traité. Fichiers bruts conservés.
- "Research on AI Agent-Driven Enterprise Multi-Scenario Integrated System" (R2B)
- "Hierarchical Multimodal LLMs with Semantic Space Alignment..." (R3)

Cause probable : indexation online-first ACM. Corpus après exclusion : **1 888 articles**.
**Impact PRISMA :** « 2 articles exclus — hors période (année 2026) ».

**Partie B — Paramètres VOSviewer (bibliométrie pré-screening) :**

| Paramètre | Valeur | Justification |
|---|---|---|
| Seuil occurrences | 3 | Standard SLR CS (Carrera Rivera 2022 ; Van Eck 2014). Évite le bruit (seuil 2) sans masquer les concepts émergents (seuil 5+). Sur 3 993 mots-clés uniques, 165 atteignent ce seuil. |
| Mots-clés sélectionnés | 60 | Carte lisible en document imprimé (recommandation Van Eck 2014). Capture les clusters thématiques principaux. |
| Counting method | Full counting | Standard pour corpus multi-bases. Fractional counting non pertinent ici. |

---

### DEC-013 — Scoring NLP et pré-classification (Tri #1)
**Date :** 27 février 2026
**Outil :** scoring.py (TF-IDF + cosinus) + preclassify.py (règles mots-clés)

Deux outils NLP développés pour assister le screening, sans remplacer la décision humaine :

1. **scoring.py** — Score TF-IDF (0–100 %) calculant la similarité cosinus entre chaque titre+abstract+keywords et la requête PICOC. Les articles sont triés par score décroissant.
2. **preclassify.py** — Pré-classification par règles de mots-clés alignées sur I2/I3/I4/E1/E2/E5/E6. Chaque article reçoit une suggestion (`include` / `exclude` / `survey` / `uncertain`), un niveau de confiance (`high` / `medium` / `low`) et un tag explicatif lisible dans l'app.

**Résultats pré-classification sur le corpus scoré (457 articles) :**

| Suggestion | N | % |
|---|---:|---:|
| 🟢 Inclure (I2+I4 détectés, conf. haute) | 66 | 14,4 % |
| 🟡 Incertain (signal partiel) | 223 | 48,8 % |
| 📚 Survey (snowballing) | 4 | 0,9 % |
| 🔴 Exclure (E1/E2/E5/E6) | 164 | 35,9 % |

**Justification :** Le volume de 1 888 articles rend le screening exhaustif très long. Le tri par pertinence et les suggestions NLP permettent de prioriser les articles à fort signal et d'accélérer les décisions évidentes (haute confiance). La décision finale reste humaine pour chaque article.
**Limite reconnue :** La pré-classification par mots-clés ne capture pas les nuances sémantiques. Les incertains et faible confiance sont systématiquement vérifiés manuellement.
**Impact PRISMA :** Documenter l'utilisation d'outils NLP d'aide au screening dans la section méthodologique. Les suggestions NLP ne sont pas un critère d'exclusion.

---

### DEC-014 — Révision des critères I3, I4 et E1
**Date :** 28 février 2026
**Outil :** Protocole SLR (Section A.3)

**Décision :** Trois critères du protocole révisés avant le lancement du screening (Tri #1) :

**I3 — reformulé :**
- *Ancien* : « Le papier adresse une hétérogénéité sémantique (labels, métadonnées) et/ou structurelle (types, unités, schéma). »
- *Nouveau* : « Le papier aborde explicitement l'explicabilité ou l'interprétabilité des décisions d'appariement (justifications, traces de raisonnement, HITL). Critère optionnel — satisfaire I2 ou I3. »

**I4 — clause baseline retirée :**
- *Ancien* : « ...Les baselines pertinentes évaluées sur le même problème peuvent être incluses comme points de comparaison. »
- *Nouveau* : « ...Note : les baselines sont gérées à l'étape d'extraction (A.5), pas au screening. »

**E1 — exception ajoutée :**
- *Ancien* : « Hors tâche : KG completion, link prediction, classification, QA, recommandation sans tâche d'appariement. »
- *Nouveau* : + « Exception : l'entity alignment inter-KG est inclus s'il vise explicitement une tâche d'appariement au sens de I2. »

**Justification :**
- I3 *ancien* était redondant avec I2 (tout article traitant une tâche I2 adresse nécessairement une hétérogénéité). Il n'avait aucun pouvoir discriminant. La reformulation couvre RQ2 (explicabilité/HITL) qui était orpheline dans les critères.
- I4 *clause baseline* inapplicable au screening titre/abstract : impossible de déterminer si un article purement neural sert de baseline dans un autre article sans lire le full text. Introduit une subjectivité non contrôlable.
- E1 *exception* : certains papiers neuro-symboliques sur l'alignement de KG utilisent des mécanismes proches du link prediction comme sous-tâche, sans que ce soit leur objectif principal. La frontière était ambiguë et générait des incertains non nécessaires.

**Limite reconnue :** La reformulation de I3 peut élargir légèrement le corpus si des articles XAI généralistes (sans tâche d'appariement) passent le critère optionnel. Atténué par I2 qui reste le critère principal, et par le QA (Q5 exige la pertinence pour ≥ 2 RQ).
**Impact PRISMA :** Documenter la révision protocolaire dans la section méthodologique avec la date et la justification. Ce type d'ajustement est standard et prévu par Carrera Rivera et al. (2022) — « criteria can be adjusted later if necessary ».

---

### DEC-015 — Développement des outils de screening Streamlit
**Date :** 28 février 2026
**Outil :** screening_app.py (Streamlit) + corrections pipeline CSV

**Décision :** Développement d'une interface Streamlit complète pour le Screening Tri #1, avec les fonctionnalités suivantes :
- Affichage article par article trié par score TF-IDF décroissant
- Bandeau de suggestion NLP (couleur + confiance) pour chaque article
- Bouton "Accepter suggestion" pour les articles haute confiance
- Actions en lot dans la sidebar (accepter tous les inclus/exclus/surveys haute confiance)
- Navigation avancée (saut de rang, reprise incertains, reprise sautés)
- Exports CSV distincts (inclus, surveys, incertains)
- Suivi de progression (barre + métriques)
- Résumé final avec taux d'accord NLP/humain

**Correction critique (fix NaN) :** pandas relit les chaînes vides `''` du CSV comme `NaN` à la relecture (`read_csv`). Cela provoquait un bug majeur où l'app considérait tous les 1 888 articles comme "déjà screenés" (car `NaN != ''` est `True`). Correction : `read_csv(..., keep_default_na=False)` + `fillna('').astype(str).str.strip()` sur les colonnes de décision.

**Limite reconnue :** Les actions en lot haute confiance réduisent la charge de screening mais introduisent un risque d'erreur NLP non détectée. Recommandation : réviser un échantillon des décisions NLP en lot lors de la validation finale.
**Impact PRISMA :** Documenter l'utilisation de l'interface Streamlit comme outil de screening dans la section méthodologique.

---

### DEC-016 — Analyse bibliométrique pré-screening (VOSviewer)
**Date :** 28 février 2026
**Outil :** VOSviewer 1.6.20 + 02_bibliometrie_phase1.ipynb

**Décision :** Réalisation d'une analyse bibliométrique exploratoire sur le corpus complet (1 890 articles) avant le screening, comprenant :
1. Carte de co-occurrence de mots-clés (VOSviewer, paramètres DEC-012-B)
2. Analyse de l'overlay temporel (évolution des clusters par année)
3. Construction d'un thésaurus de normalisation (107 règles de fusion)

**Résultats principaux :**
- 5 clusters thématiques identifiés : (1) Knowledge Graph Embedding & Alignment, (2) Ontology Matching & Schema Integration, (3) Neuro-Symbolic AI & Reasoning, (4) Multilingual NLP & Transformers, (5) Data Harmonization & M&E Context
- L'overlay temporel confirme l'émergence du cluster NeSy en 2023–2024, validant la pertinence de la fenêtre temporelle 2020–2025
- Le cluster M&E (5) est périphérique mais connecté aux clusters 1 et 4 — confirme la lacune identifiée dans le Research Gap

**Utilisation pour la thèse :** La carte VOSviewer est reproductible (fichier .vos archivé) et sera utilisée dans la section méthodologique du mémoire pour justifier le positionnement de la thèse dans l'espace bibliométrique.

**Justification :** L'analyse pré-screening permet de vérifier que les requêtes ont bien capturé les clusters attendus avant d'investir le temps du screening, et d'identifier des termes manquants potentiels dans le thésaurus.
**Limite reconnue :** L'analyse porte sur le corpus brut avant exclusion — les clusters incluent du bruit qui sera éliminé au screening.
**Impact PRISMA :** Mentionner l'analyse bibliométrique pré-screening dans la section méthodologique comme étape exploratoire (non requise par PRISMA mais conforme aux bonnes pratiques SLR en CS — Carrera Rivera 2022, Section 3.1).

### DEC-018 — Normalisation terminologique, flag has_abstract et seuil adaptatif (Phase 1)
**Date :** 28 février 2026
**Outil :** normalize.py (nouveau), scoring.py (v2), preclassify.py (v2)

**Décision :** Trois améliorations au pipeline de pré-screening déployées avant le lancement du Tri #1 :

**1. Normalisation terminologique (normalize.py) :**
Module partagé chargeant le thesaurus VOSviewer (107 règles label → replace by) et appliquant les substitutions en single-pass (regex alternation) sur le texte combiné titre+abstract+keywords **avant** la vectorisation TF-IDF et **avant** les règles regex de preclassify.py. La requête PICOC est aussi normalisée.
- Technique : alternation regex triée par longueur décroissante (greedy) + word boundaries + callback unique (évite les cascades de remplacement)
- Exemples d'impact : "neurosymbolic" → "neuro-symbolic ai", "XAI" → "explainable ai", "knowledge graphs" → "knowledge graph", "transformers" → "transformer"

**2. Flag has_abstract (scoring.py + preclassify.py) :**
Colonne `has_abstract` (bool) ajoutée par scoring.py. Politique prudente dans preclassify.py : les articles sans abstract ne sont **jamais** auto-exclus en confiance `low`. Deux cas :
- Si un signal E1 est détecté sur le titre seul mais l'abstract est absent → `uncertain` + `confidence: low` + tag "abstract manquant" (au lieu de `exclude`)
- Si aucun signal détecté et abstract absent → `uncertain` + tag "impossible d'évaluer sur le titre seul"
Concerne 9 articles ACM du corpus réel (DEC-011).

**3. Seuil adaptatif (preclassify.py) :**
Le seuil TF-IDF hardcodé `score >= 40` (règle 9) est remplacé par le P25 de la distribution des scores des articles ayant au moins un signal I2 ou I4 (fort ou faible). Ce percentile représente la borne basse de pertinence des articles détectables par les règles regex.
- Fallback à 40 % si moins de 5 articles avec signal (cas dégénéré)
- Seuil affiché dans les logs et dans le tag NLP pour traçabilité

**Justification :**
- La normalisation réduit les faux négatifs liés aux variantes terminologiques (pluriels, acronymes, formes avec/sans tiret). Le thesaurus est déjà validé par l'analyse bibliométrique VOSviewer (DEC-016).
- Le flag has_abstract empêche l'auto-exclusion d'articles dont le titre contient un "faux ami" E1 mais dont le contenu réel (abstract absent) pourrait être pertinent. Coût : ~9 articles de plus à screener manuellement.
- Le seuil adaptatif est calibré sur la distribution réelle du corpus plutôt que sur une valeur arbitraire, et s'ajuste automatiquement si le corpus ou les requêtes changent.

**Colonnes ajoutées au CSV :**
- `has_abstract` (bool) — scoring.py
- `title_norm`, `abstract_norm`, `keywords_norm` (str) — scoring.py
- Colonnes NLP inchangées : `nlp_suggestion`, `nlp_reason`, `nlp_confidence`, `nlp_tag`

**Fichier ajouté :** `src/normalize.py` — module partagé, importé par scoring.py et preclassify.py.
**Dépendance :** `data/thesaurus/vosviewer_thesaurus.txt` (copie du thesaurus VOSviewer).

**Limite reconnue :** La normalisation single-pass ne gère pas les cas où un terme normalisé devrait déclencher une seconde normalisation (ex. si "neuro-symbolic ai" devait être re-normalisé). Cas non observé dans le thesaurus actuel. Le thesaurus couvre le vocabulaire du corpus brut mais pas les néologismes absents de VOSviewer.
**Impact PRISMA :** Documenter l'utilisation du thesaurus VOSviewer comme étape de normalisation terminologique dans la section méthodologique. Mentionner le flag has_abstract et la politique prudente dans les notes de screening.

---

### DEC-019 — Score NLP composite graduel (Phase 2)
**Date :** 28 février 2026
**Outil :** preclassify.py v3, screening_app.py v2

**Décision :** Remplacement de la confiance par règles ad hoc (v2) par un score composite `nlp_score` (0–10) dont la confiance est dérivée par seuils.

**Mécanisme :**
Le score est calculé comme la somme pondérée des signaux détectés dans le texte normalisé (titre×2 + abstract + keywords) :

| Signal | Poids | Justification |
|---|---:|---|
| I2 fort (schema match, entity align, ...) | +2 | Tâche d'appariement clairement identifiée |
| I2 faible (data integrat, entity linking, ...) | +1 | Tâche probable mais à confirmer |
| I4 fort (neuro-symbolic, neural-symbolic, ...) | +2 | Architecture NeSy explicite |
| I4 faible (KG+embed, ontology+neural, ...) | +1 | Composante hybride implicite |
| I3 (explainab, HITL, interpretab, ...) | +1 | Bonus explicabilité (RQ2) |
| E1 fort (reinforcement learn, drug discover, ...) | −3 | Hors tâche clair |
| E1 faible (link predict, node classif, ...) | −1 | Hors tâche probable (par hit) |
| E2 (image classif, video, audio, ...) | −2 | Hors modalité |

Score brut borné [0, 10]. Maximum théorique atteint si I2+I4+I3 multiples sans pénalités.

**Dérivation de la confiance :**

| Catégorie | Haute | Moyenne | Faible |
|---|---:|---:|---:|
| include | score ≥ 5 | score ≥ 3 | score < 3 |
| uncertain | score ≥ 3 | score ≥ 2 | score < 2 |

Les décisions structurelles (E6, E5, survey, E1 fort sans I2) conservent leur confiance fixe (non dérivée du score).

**Nouvelles fonctionnalités app Streamlit :**
- Score NLP affiché dans le bandeau de suggestion (barre visuelle colorée + valeur)
- Métrique Score NLP dans les infos article (5e colonne)
- Histogramme de distribution des scores dans le panneau NLP pré-screening
- Légende des poids dans la sidebar
- Score moyen par catégorie dans les statistiques NLP sidebar
- Score inclus dans les notes de décision (ex: `[NLP 7/10] I2+I4 ...`)

**Justification :**
La v2 produisait ~920 incertains (48,8 %) avec seulement 3 niveaux de confiance, rendant la priorisation difficile. Le score graduel permet de :
1. Trier les incertains par densité de signal (un incertain à 3/10 ≠ un incertain à 1/10)
2. Rendre les seuils de confiance explicites et reproductibles
3. Documenter la force du signal dans chaque décision pour l'audit post-screening
4. Offrir une vue distributionnelle dans l'app pour calibrer la stratégie de screening

**Limite reconnue :** Le score est additif sans interaction — un article I2+I4 (score 4) avec E1 faible (−1 = score 3) pourrait être plus pertinent qu'un article I2+I4+I3 (score 5) sur un sujet tangent. Le score aide à prioriser mais ne remplace pas la lecture humaine.

**Impact PRISMA :** Documenter le scoring composite dans la section méthodologique (outil d'aide au screening). Le score n'est pas un critère d'exclusion.

### DEC-021 — Acceptation en lot des inclusions haute confiance + validation par échantillon
**Date :** 28 février 2026
**Outil :** screening_app.py v3 (actions en lot sidebar) + validate_bulk.py

**Décision :** Les 119 articles pré-classifiés `include` avec confiance `high` (I2 fort + I4 fort ou faible, score NLP ≥ 5) ont été acceptés en lot au Tri #1, avec validation humaine par échantillon aléatoire.

**Justification :**
- L'acceptation en lot porte exclusivement sur des **inclusions** (pas des exclusions). Un faux positif à cette étape est bénin : l'article sera filtré au Tri #2 (QA full-text, seuil 3/5). Un faux négatif en exclusion serait irréversible.
- Les 119 articles satisfont tous les critères I2 (signal fort : schema match, entity align, ontology align, etc.) + I4 (signal fort ou faible : neuro-symbolic, KG+embed, etc.) détectés dans le titre/abstract/keywords normalisés.
- Le score NLP composite ≥ 5 confirme la convergence de multiples signaux d'inclusion sans pénalité d'exclusion.

**Protocole de validation :**
1. Tirage aléatoire stratifié de **15 articles** (~12,6 %) parmi les 119 inclus en lot (seed fixe pour reproductibilité).
2. Lecture humaine du titre + abstract de chaque article de l'échantillon.
3. Décision indépendante : l'article aurait-il été inclus manuellement ? (oui / non / incertain)
4. Calcul du taux d'accord :
   - ≥ 90 % (≤ 1–2 désaccords) → lot validé, aucune action supplémentaire
   - 80–89 % → lot validé avec note d'alerte, les désaccords sont révisés individuellement
   - < 80 % → lot invalidé, les 119 articles sont remis en attente pour screening manuel

**Résultat de la validation :** *(à compléter après exécution de validate_bulk.py)*
- Échantillon : 15 articles (seed=42)
- Accord : __/15 (__%)
- Désaccords : [lister les rangs et raisons]
- Conclusion : lot validé / invalidé

**Limite reconnue :** L'échantillon de 15 articles (12,6 %) offre une puissance statistique limitée — il détecte un taux d'erreur ≥ 15 % avec ~85 % de probabilité. Un lot parfait sur 15 articles ne garantit pas l'absence d'erreurs dans les 104 restants. Atténué par le Tri #2 (QA full-text) qui constitue un second filtre.

**Impact PRISMA :** Documenter dans la section méthodologique : « 119 articles pré-inclus par outil NLP (critères I2+I4, score ≥ 5) ; validation par échantillon aléatoire de 15 articles (taux d'accord : X %). Les articles pré-inclus passent au QA (Tri #2) identiquement aux inclusions manuelles. »

### DEC-022 — Validation batch : 264 exclusions certaines (Tri #1)
**Date :** 1 mars 2026
**Outil :** auto_screen.py + revue manuelle 5 passes
**Décision :** 264 articles exclus en lot. Critère de sélection : triple concordance (auto_decision=exclude + nlp_suggestion=exclude + nlp_score ≤ 2).
Validation en 5 passes :

1. Signaux I2/I4/I3 → 111 articles flaggués, 0 avec I2 FORT (tous I4 ou I3 sans tâche matching)
2. Vocabulaire matching caché (fuzzy match, crosswalk, metadata mapping…) → 11 hits, tous hors tâche
3. Termes RQ3 (multilingual, M&E, SNOMED…) → 18 hits, tous classification/retrieval/segmentation
4. Entity linking multimodal → 17 hits, tous KG completion ou NER
5. Ontology work dans E2 → 3 hits, tous mapping concepts→visuels

**Répartition :** E1 aucun signal 36% | E2 hors modalités 34% | E1 KG completion 12% | E1 signaux faibles/forts 9% | E1 classification 4% | E1 retrieval/RAG 3% | E3/E4 2%
**Limite reconnue :**Revue par patterns regex — nuances sémantiques non captées. Atténué par le triple filtre et les 5 passes de validation.
**Impact PRISMA :** « 264 articles exclus en lot après validation automatique+manuelle (détail en annexe méthodologique) »