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

---

## DÉCISIONS — TRI #1 (suite)

### DEC-024 — Stratégie de triage des articles incertains (Tri #1)
**Date :** 2 mars 2026
**Outil :** screening_app.py
**Décision :** Intégration d'un sélecteur de tri dans les filtres de navigation de l'interface Streamlit. Quatre modes disponibles : Rang (défaut), Priorité incertains, NLP décroissant, TF-IDF décroissant.

Le mode « Priorité incertains » ordonne le pool d'articles non screenés selon la hiérarchie suivante :
1. Articles `uncertain` en premier (par rapport aux autres suggestions)
2. Au sein des incertains, ordre par `nlp_reason` : I2 seul → I4+I2_faible → I4 seul → i4+i2_faibles → score élevé → i2_faible seul → I3 seul → no_abstract
3. Tri secondaire : nlp_score décroissant, puis relevance_score_pct décroissant

**Justification :** À l'issue de 1 179 articles screenés, 711 restants dont une majorité d'incertains (I2 seul=415, I3 seul=245, I4 seul=154). La principale source d'ambiguïté est la frontière I4 : un article peut mentionner un KG sans impliquer de raisonnement symbolique explicite. Le tri par `nlp_reason` permet de regrouper les cas de même nature et de maximiser le rendement en traitant d'abord les incertains à fort signal I2 (les plus susceptibles de basculer en inclusion après lecture de l'abstract).

**Limite reconnue :** Le tri ne modifie pas les décisions — il priorise simplement l'ordre de lecture. La décision finale reste humaine. Les articles `I3 seul` (XAI sans tâche d'appariement explicite) sont traités en dernier car leur probabilité d'inclusion est plus faible sans signal I2/I4.

**Impact PRISMA :** Aucun impact direct sur les chiffres PRISMA. Mentionner dans la section méthodologique : « Un outil de triage automatique a priorisé la lecture des articles incertains par densité de signaux protocole (I2 > I4 > I3), réduisant la charge de décision pour les cas les plus ambigus. »

---

### DEC-023 — Exclusion venue prédatrice : ShodhKosh
**Date :** 1 mars 2026
**Base :** Scopus
**Décision :** Exclusion E1 des 2 articles indexés dans *ShodhKosh: Journal of Visual and Performing Arts* (DOI: 10.29121/shodhkosh.v6.i3s.2025.6777 et 10.29121/shodhkosh.v6.i5s.2025.6879). ShodhKosh est identifiée comme revue prédatrice à portée déclarée ultra-large ; les deux articles concernent le tagging sémantique de collections d'art et la documentation de folklore par NLP — aucun lien avec I2 ni I4.
**Justification :** Capture par les requêtes due à l'utilisation superficielle de termes tendance dans les abstracts. Identification lors de l'analyse bibliométrique des venues (included_by_journal.csv).
**Limite reconnue :** Autres venues prédatrices potentiellement non détectées dans le corpus.
**Impact PRISMA :** Exclusion E1 standard. Mentionner dans les limitations : la présence de venues prédatrices dans les bases commerciales illustre la nécessité du screening humain.

---

### DEC-024 — Dédoublonnage tardif full-text : #86 Wu 2020
**Date :** 14 mars 2026
**Base :** ArXiv / Scopus
**Décision :** Exclusion de l'article #86 (« Ontology Matching by Jointly Encoding Terminological Description and Neighbourhood Structure », Wu et al., 2020) au profit de #79 (« DAEOM: A deep attentional embedding approach for biomedical ontology matching », Wu et al., 2020). Le #86 est la version conférence préliminaire ; le #79 est la version étendue.
**Justification :** Dédoublonnage tardif détecté lors de la revue full-text (Tri #2). Les deux articles partagent la même méthode (DAEOM) et les mêmes auteurs. La version étendue (#79) est plus complète. Pratique standard en SLR : conserver la version la plus aboutie.
**Limite reconnue :** Le dédoublonnage automatique (titre/DOI) n'avait pas détecté ce cas car les titres diffèrent substantiellement.
**Impact PRISMA :** +1 article exclu après full-text review, raison : doublon (version préliminaire). Compteur `fulltext_exclu_doublon` ajouté dans prisma_counts.csv.

---

### DEC-025 — Dédoublonnage tardif Tri #1 : #1188 Cao 2025
**Date :** 14 mars 2026
**Base :** IEEE
**Décision :** Correction de la raison d'exclusion de l'article #1188 (« Personalized learning recommendation system based on DeepSeek algorithm », Cao, 2025) de `E6` à `E_doublon`. Identifié comme doublon lors du Tri #1.
**Justification :** La note de screening mentionnait « Doublon » mais la raison codée était `E6`. Correction pour cohérence avec le code `E_doublon` utilisé pour les dédoublonnages tardifs.
**Limite reconnue :** Le dédoublonnage automatique n'avait pas détecté ce cas.
**Impact PRISMA :** Compteur `fulltext_exclu_doublon` passe de 1 à 2 dans prisma_counts.csv. Le total d'exclusions Tri #1 reste inchangé (l'article était déjà exclu).

---

### DEC-026 — Exclusion pour langue non exploitable (E6) : articles en chinois
**Date :** 15 mars 2026
**Base :** Scopus
**Décision :** Trois articles dont le texte intégral est rédigé en chinois sont exclus avec le motif E6 (langue non exploitable) :
- #216 Tang 2023 — « Entity Alignment Method Combining Iterative Relationship Graph Matching and Attribute Semantic Embedding » (*Computer Science*, 30.9 % sinogrammes)
- #493 Wang 2025 — « Institution Name Alignment Integrating Prompt Engineering and Graph Convolutional Network » (*Data Analysis and Knowledge Discovery*, 51.2 % sinogrammes sur les 2 premières pages)
- #541 Wang 2024 — « Knowledge Fusion Method of High-Speed Train Based on Knowledge Graph » (*Journal of Southwest Jiaotong University*, 37.2 % sinogrammes)
**Justification :** Conformément aux bonnes pratiques PRISMA 2020 (item 6 — critères d'éligibilité), les articles dans une langue non maîtrisée par la chercheuse sont exclus et documentés comme limitation (biais linguistique). Les titres bilingues dans les bases de données masquaient le fait que le contenu intégral est en chinois. Vérification faite par extraction du texte PDF via PyPDF2 et mesure du ratio de sinogrammes.
**Limite reconnue :** Biais linguistique potentiel — trois études pertinentes sont exclues faute de pouvoir en exploiter le contenu. À mentionner dans la section Limitations du mémoire.
**Impact PRISMA :** Nouveau compteur `fulltext_exclu_E6_langue` = 3. Inclus Tri #2 passe de 94 à 91. QA PASS passe de 79 à 76. Total exclusions passe de 11 à 14.


### DEC-034 — Analyse de sensibilité Tri #1 : correction du benchmark et interprétation
**Date :** 16 mars 2026
**Outil :** Python (pandas), analyse rétrospective sur `corpus_scored.csv` et `articles_inclus.csv`
**Décision :** L'analyse de sensibilité du seuil d'exclusion batch au Tri #1 est corrigée. Le benchmark correct est le corpus d'**extraction finale (n = 54)**, et non les 81 articles du Tri #1. Le cas #840, initialement identifié comme faux négatif potentiel au seuil NLP ≤ 2, n'en est pas un au sens du résultat final.

#### Contexte
L'analyse initiale testait la robustesse des seuils NLP pour l'exclusion automatique au Tri #1. Le critère de faux négatif (FN) était : « un article exclu automatiquement au Tri #1 qui aurait dû atteindre l'extraction finale ». Au seuil NLP ≤ 2, un seul FN apparent avait été identifié : l'article #840 (Peña-Larena, *Automated KG Approach for Dataset Metadata Harmonisation*).

#### Cas #840 — Pas un faux négatif
L'investigation a révélé que #840 a été :
1. **Correctement capté au Tri #1** : `decision = include` dans `corpus_scored.csv` (nlp_score = 2).
2. **Légitimement éliminé au Tri #2** : `qa_total = 2.0/5.0`, `qa_pass = non` — exclusion pour qualité insuffisante (seuil QA ≥ 3.0), **pas** pour I4.

Le #840 n'est donc pas un cas limite du système de scoring NLP. C'est un cas qui confirme le bon fonctionnement du pipeline à deux étages : sensibilité élevée au Tri #1 (capture inclusive), sélectivité au Tri #2 (filtrage qualité).

#### Résultats corrigés de l'analyse de sensibilité

| Seuil NLP | Exclus batch | FN (Tri #1, n=81) | FN (Extraction, n=54) | Sûr ? |
|-----------|-------------|--------------------|-----------------------|-------|
| ≤ 0       | 739         | 0                  | 0                     | ✓     |
| ≤ 1       | 961         | 0                  | 0                     | ✓     |
| ≤ 2       | 1 204       | 1 (#840)           | **0**                 | ✓     |
| ≤ 3       | 1 362       | 2                  | **0**                 | ✓     |
| ≤ 4       | 1 489       | 7                  | 5                     | ✗     |

**Conclusion :** Au regard du résultat final (extraction), les seuils NLP ≤ 1, ≤ 2 et même ≤ 3 sont tous sûrs — zéro perte effective dans les trois cas. Les 1–2 FN apparents au niveau Tri #1 (dont #840) ont tous été éliminés au Tri #2 pour qualité insuffisante. Le premier vrai risque n'apparaît qu'à NLP ≤ 4 (5 FN extraction). Le seuil effectivement appliqué (NLP ≤ 2 combiné avec `nlp_suggestion = exclude` et `auto_decision = exclude`) n'a entraîné aucune perte d'article dans le corpus final de 54 études.

#### Implication méthodologique
Ce résultat renforce l'argumentaire PRISMA de la SLR :
- **Entonnoir propre** : 1 888 → 105 (Tri #1) → 81 (full-text) → 54 (QA). Chaque étape a un rôle distinct et documenté.
- **Stratégie conservatrice validée** : Les 24 exclusions full-text sont dominées par E1 (12) et I4 (10), confirmant que le Tri #1 a été appropriément conservateur sur des critères ambigus en titre/abstract.
- **Pipeline à deux étages** : La sensibilité élevée au Tri #1 (capture) combinée à la sélectivité au Tri #2 (QA ≥ 3.0) constitue un filet de sécurité robuste. Même un article de score NLP faible (2) capté au Tri #1 est correctement filtré au Tri #2 si sa qualité est insuffisante.

**Figures :** `results/figures/tri1_seuil_exclusion_batch.png` (mise à jour avec benchmark extraction finale).

---

### DEC-033 — Méthodologie d'exclusion batch au Tri #1 : deux phases avec seuil empirique par saturation
**Date :** 16 mars 2026
**Outil :** preclassify.py, screening_app.py, Python (pandas, analyse rétrospective)
**Décision :** Le processus d'exclusion automatisé au Tri #1 a procédé en deux phases séquentielles, documentées ci-dessous. La justification du seuil de la Phase 2 repose sur un argument empirique de **saturation** : le taux d'inclusion observé tombe à zéro dans la zone ciblée.

#### Phase 1 — Exclusion par triple concordance (n = 264)
**Critère :** `auto_decision = exclude` ET `nlp_suggestion = exclude` ET `nlp_score ≤ 2`
**Principe :** Les trois signaux automatiques convergent vers l'exclusion — le module de scoring TF-IDF, le module de règles NLP et le score composite NLP sont tous en accord. Aucun signal d'inclusion (I2, I4, I3) n'est détecté.
**Validation :** Revue humaine en 5 passes par patterns regex ciblant les faux négatifs potentiels (signaux I2/I4 cachés, vocabulaire matching, termes RQ3, entity linking, ontology work). Résultat : 0 faux négatif identifié (voir DEC-022).
**Résultat :** 264 articles exclus (E1). Taux d'inclusion : 0 %. FN extraction : 0.

#### Phase 2 — Exclusion par seuil de saturation (n = 811)
**Critère :** `(NLP ≤ 2 ET TF-IDF ≤ 15 %) OU NLP ≤ 1`
**Principe :** Après la Phase 1, le screening manuel des articles restants a été conduit par ordre décroissant de TF-IDF. L'analyse de saturation a révélé que :

- **Le taux d'inclusion est strictement nul pour TF-IDF ≤ 15 %** (864 articles, 0 inclusion) : aucun article pertinent n'a été trouvé en dessous de ce seuil, peu importe le score NLP.
- **Le taux d'inclusion est nul pour NLP ≤ 1** (977 articles, 0 inclusion) : aucun article avec un score NLP aussi faible n'a jamais été inclus.
- **La dernière inclusion trouvée en screening descendant** se situe au rang TF-IDF #971 (TF-IDF = 15,8 %, NLP = 5). Au-delà, les 917 articles suivants ne produisent plus aucune inclusion — le rendement marginal est tombé à zéro.
- Parmi les 81 inclusions du Tri #1, les deux avec le NLP le plus bas (NLP = 2 et NLP = 3) ont toutes deux un TF-IDF > 15 % (18,3 % et 17,3 %), et ont **toutes deux échoué au QA** (Tri #2). Aucune n'atteint l'extraction.

La combinaison `(NLP ≤ 2 ET TF-IDF ≤ 15 %) OU NLP ≤ 1` capture **1 075 articles** avec 0 faux négatif (ni au Tri #1, ni à l'extraction), ce qui en fait le seuil sûr le plus large parmi toutes les combinaisons testées.

#### Rendement cumulatif (screening par TF-IDF descendant)

| Articles screenés | Inclusions trouvées | % du total (81) | Marginal |
|------------------:|--------------------:|-----------------:|---------:|
| 100               | 5                   | 6,2 %            | +5       |
| 300               | 31                  | 38,3 %           | +26      |
| 500               | 57                  | 70,4 %           | +26      |
| 800               | 75                  | 92,6 %           | +18      |
| 1 000             | 81                  | 100,0 %          | +6       |
| 1 200–1 888       | 81                  | 100,0 %          | +0       |

**Point de saturation :** 100 % des inclusions sont trouvées après ~1 000 articles screenés. Les 888 articles restants (rang > 1 000 par TF-IDF) n'ont produit aucune inclusion.

#### Comparaison des seuils sûrs (0 FN)

| Seuil | Exclus batch | FN include | FN extraction | Sûr ? |
|---|---:|---:|---:|:---:|
| NLP ≤ 1 seul | 977 | 0 | 0 | ✓ |
| NLP ≤ 2 ET TF ≤ 15 % | 762 | 0 | 0 | ✓ |
| NLP ≤ 3 ET TF ≤ 15 % | 807 | 0 | 0 | ✓ |
| **(NLP ≤ 2 ET TF ≤ 15 %) OU NLP ≤ 1** | **1 075** | **0** | **0** | **✓** |
| NLP ≤ 2 seul | 1 226 | 1 | 0 | ✗ |
| NLP ≤ 3 seul | 1 385 | 2 | 0 | ✗ |

#### Total des exclusions batch Tri #1
- Phase 1 (triple concordance) : 264
- Phase 2 (seuil saturation) : 811 supplémentaires
- **Total : 1 075 articles exclus en batch** (57 % du corpus de 1 888)
- Reste à screener manuellement : 813 articles, contenant les 81 inclusions et les 54 articles d'extraction.

**Justification :** Le seuil se situe exactement à la frontière où le screening manuel cesse de produire des inclusions. C'est un argument de **saturation empirique** : en deçà de (NLP ≤ 2, TF ≤ 15 %) ou NLP ≤ 1, le rendement du screening est nul. L'analyse de sensibilité (DEC-032) confirme que ce seuil ne sacrifie aucun article du corpus final d'extraction (n = 54).
**Limite reconnue :** Seuil déterminé rétrospectivement à partir des données de screening, pas a priori. Atténué par : (1) le double critère combiné qui réduit le risque de surapprentissage, (2) la Phase 1 avec triple concordance + validation humaine en 5 passes, (3) la marge de sécurité — les 2 inclusions les plus proches du seuil sont des QA fail (pas d'extraction perdue).
**Impact PRISMA :** « 1 075 articles exclus en batch au Tri #1 (Phase 1 : 264 par triple concordance auto, Phase 2 : 811 par seuil de saturation empirique). Validation rétrospective : 0 faux négatif au niveau extraction finale (n = 54). »

### DEC-035 — Ajout de FLORA par recommandation du directeur (Other methods — PRISMA)
**Date :** 19 mars 2026
**Source :** Recommandation du directeur de recherche (Pr Étienne Gaël Tajeuna)

**Décision :** L'article FLORA (Peng et al., 2025) est ajouté au corpus via la colonne PRISMA « Identification via other methods — expert recommendation ». Il entre dans le flux de screening standard (Tri #1 → Tri #2 → extraction) et reçoit l'index #1888.

**Référence complète :**

> Peng, Y., Bonald, T., & Suchanek, F. M. (2025). FLORA: Unsupervised Knowledge Graph Alignment by Fuzzy Logic. *arXiv preprint*, arXiv:2510.20467v1. https://arxiv.org/abs/2510.20467

**Raison de l'absence dans le corpus systématique :**

L'article n'a matché aucune des 4 requêtes (R1, R2A, R2B, R3) dans aucune des 4 bases (Scopus, IEEE, ACM, arXiv). Le plafond arXiv `max_results=200` n'est pas en cause (aucune requête n'a atteint 200 résultats). La cause est **purement terminologique** :

- FLORA se positionne comme « Symbolic Reasoning + Fuzzy Logic » — aucune mention de « neuro-symbolic », « neural-symbolic » ou « hybrid neural » dans le titre, l'abstract ou les keywords.
- La composante neurale (language model LaBSE/PEARL pour la similarité de littéraux) n'est mentionnée qu'en Section 5.4 (Implementation Details), absente de l'abstract.
- Les mots-clés de l'article (« Knowledge Graphs, Entity Alignment, Holistic Matching, Symbolic Reasoning, Fuzzy logic ») ne croisent aucun des blocs terminologiques de R1 (harmonisation + NLP/KG), R2A (neuro-symbolic explicite), R2B (hybrid neural+symbolic) ou R3 (M&E + multilingue).

Cette lacune est inhérente à toute recherche par mots-clés et constitue précisément le cas d'usage prévu par PRISMA 2020 pour la colonne « Other methods ». L'article a été identifié par expertise du directeur de recherche, familier avec la littérature en KG alignment et fuzzy logic.

**Décision Tri #1 : include**

| Critère | Évaluation |
|---------|-----------|
| I1 | arXiv oct. 2025 — preprint (accepté via DEC-007). À vérifier si version publiée disponible. |
| I2 | ✅ KG alignment = entity alignment + relation alignment entre KG hétérogènes |
| I3 | ✅ Explicabilité revendiquée : traces de raisonnement interprétables via fuzzy logic |
| I4 | ✅ Fort — fuzzy logic avec garanties formelles (symbolique actif) + language model LaBSE/PEARL (neural) |
| I5 | ✅ 7 datasets (OpenEA, DBP15K, OAEI KG Track), 30+ baselines, P/R/F1/Hit@K/MRR |

**Pertinence pour le mémoire :** Élevée. Couvre les trois RQ — architecture NeSy Type 3 (RQ1), explicabilité par traces symboliques (RQ2), benchmarks multilingues cross-lingual (RQ3). Candidat probable pour le top 10 au Tri #3.

**Entrée corpus (index #1888) :**

```
title:            FLORA: Unsupervised Knowledge Graph Alignment by Fuzzy Logic
abstract:         Knowledge graph alignment is the task of matching equivalent entities (that is, instances and classes) and relations across two knowledge graphs. Most existing methods focus on pure entity-level alignment, computing the similarity of entities in some embedding space. They lack interpretable reasoning and need training data to work. In this paper, we propose FLORA, a simple yet effective method that (1) is unsupervised, i.e., does not require training data, (2) provides a holistic alignment for entities and relations iteratively, (3) is based on fuzzy logic and thus delivers interpretable results, (4) provably converges, (5) allows dangling entities, i.e., entities without a counterpart in the other KG, and (6) achieves state-of-the-art results on major benchmarks.
authors:          Peng, Y.; Bonald, T.; Suchanek, F.M.
year:             2025
doi:              10.48550/arXiv.2510.20467
source:           arXiv preprint
keywords:         Knowledge Graphs; Entity Alignment; Holistic Matching; Symbolic Reasoning; Fuzzy logic
doc_type:         Preprint
citations:        
database:         expert_recommendation
query:            DEC-025
has_abstract:     True
decision:         include
exclusion_reason: 
screener_notes:   Recommandation Pr Tajeuna. KG alignment via fuzzy logic (symbolique actif) + LaBSE/PEARL (neural). I2+I3+I4+I5 satisfaits. Code: github.com/dig-team/FLORA
```

**Impact PRISMA :** Dans le diagramme de flux PRISMA 2020, cet article apparaît dans la colonne de droite « Identification of studies via other methods » → « Records identified from expert recommendation (n = 1) » → screening → inclus. Documenter dans la section méthodologique : « 1 article identifié par recommandation du directeur de recherche, absent du corpus systématique en raison d'un gap terminologique (l'article ne se décrit pas comme neuro-symbolique malgré une architecture hybride fuzzy logic + language model). »

---

### DEC-036 — Exclusion de 3 articles ArXiv retirés (withdrawn)
**Date :** 20 mars 2026
**Source :** Vérification manuelle des PDFs ArXiv lors du téléchargement

**Décision :** Trois articles ArXiv sont retirés du corpus inclus (articles_inclus.csv) car ils portent la mention officielle **« This paper has been withdrawn »** sur ArXiv. Un article retiré par son auteur ne satisfait plus le critère I1 (étude publiée ou preprint accessible) : le contenu n'est plus disponible pour évaluation, et son retrait signale un problème de fiabilité reconnu par l'auteur.

**Articles supprimés :**

| Rang | Auteurs | Année | Titre | ArXiv ID | Motif |
|---:|---|---:|---|---|---|
| 192 | Zhaoming Lv | 2024 | An ontology alignment method with user intervention using compact differential evolution with adaptive parameter control | arXiv:2401.06337v2 | Withdrawn by Zhaoming Lv |
| 373 | Vivek Iyer; Arvind Agarwal; Harshit Kumar | 2020 | Multifaceted Context Representation using Dual Attention for Ontology Alignment | arXiv:2010.11721v2 | Version antérieure de VeeAlign (même auteurs/contenu que #591) |
| 591 | Vivek Iyer; Arvind Agarwal; Harshit Kumar | 2021 | VeeAlign: Multifaceted Context Representation using Dual Attention for Ontology Alignment | arXiv:2102.04081v3 | Withdrawn by Vivek Iyer |

**Note :** Les rangs 373 et 591 sont deux soumissions ArXiv distinctes du même travail (VeeAlign) par les mêmes auteurs. Le rang 373 (arXiv:2010.11721v2, 2020) est la version initiale ; le rang 591 (arXiv:2102.04081v3, 2021) est la version révisée. Les deux sont retirés.

**Corpus après exclusion : 214 articles** (217 − 3).

**Justification :** Conformément aux bonnes pratiques SLR, un preprint retiré (withdrawn) ne peut pas être évalué au Tri #2 (QA) ni inclus dans l'extraction. Le retrait volontaire par l'auteur indique que le contenu ne doit plus être cité. Aucun de ces trois articles n'avait de version publiée dans un venue avec comité de lecture qui pourrait se substituer au preprint.

**Limite reconnue :** Aucune — l'exclusion d'articles retirés est non controversée.
**Impact PRISMA :** Documenter dans le flux PRISMA : « 3 articles exclus — preprints retirés (withdrawn) par les auteurs sur ArXiv ». Ajouter au comptage des exclusions post-screening.

---

### DEC-037 — Exclusion de 2 articles World Scientific inaccessibles
**Date :** 20 mars 2026
**Source :** Tentative de téléchargement des PDF pour le Tri #2

**Décision :** Deux articles publiés par World Scientific sont exclus du corpus inclus car ils sont inaccessibles : aucun accès institutionnel disponible, aucune version OA trouvée, et l'éditeur n'offre pas de PDF libre. Sans accès au texte intégral, l'évaluation QA (Tri #2) est impossible.

**Articles exclus :**

| Rang | Auteurs | Année | Titre | DOI | Source |
|---:|---|---:|---|---|---|
| 29 | Chen, J.; Zheng, H.; et al. | 2023 | Schema Matching Using Interattribute Dependencies | 10.1142/S0218194023500183 | International Journal of Software Engineering and Knowledge Engineering |
| 413 | Xue, X.; Pan, J.-S.; Lu, H. | 2023 | Similarity Features Fusion for Ontology Matching via Genetic Programming | 10.1142/S0218001423520092 | International Journal of Pattern Recognition and Artificial Intelligence |

**Motif :** E_inaccessible — texte intégral non disponible (paywall World Scientific, pas d'accès institutionnel, pas de version OA).

**Mise à jour :** `decision` → `exclude` dans corpus_scored.csv ; lignes supprimées de articles_inclus.csv.

**Corpus après exclusion : 214 → 212 articles** (DEC-036 avait produit 214 ; DEC-037 retire 2 de plus).

**Limite reconnue :** L'exclusion pour inaccessibilité est un biais potentiel mais inévitable ; documentée conformément à PRISMA 2020.
**Impact PRISMA :** « 2 articles exclus — texte intégral non accessible (World Scientific, paywall) ».

---

### DEC-038 — Exclusion de 2 articles de revues chinoises inaccessibles
**Date :** 20 mars 2026
**Source :** Tentative de téléchargement des PDF pour le Tri #2

**Décision :** Deux articles publiés dans des revues chinoises sont exclus car inaccessibles : les DOI renvoient vers des plateformes chinoises (CNKI/Wanfang) nécessitant un accès institutionnel spécifique non disponible. Aucune version OA ou anglophone n'a été trouvée via Unpaywall, Semantic Scholar, ou EuropePMC.

**Articles exclus :**

| Rang | Auteurs | Année | Titre | DOI | Source |
|---:|---|---:|---|---|---|
| 232 | Li, L.; Zhang, Z. | 2021 | Entity alignment method for different knowledge repositories with joint semantic representation | 10.11925/infotech.2096-3467.2021.0143 | Data Analysis and Knowledge Discovery |
| 268 | Wu, Z.-Y.; Li, S.-M.; et al. | 2022 | Ontology Alignment Method Based on Self-attention (基于自注意力模型的本体对齐方法) | 10.11896/jsjkx.210700190 | Computer Science |

**Motif :** E_inaccessible — texte intégral non disponible (revues chinoises, accès CNKI/Wanfang requis, pas d'accès institutionnel).

**Mise à jour :** `decision` → `exclude` dans corpus_scored.csv ; lignes supprimées de articles_inclus.csv.

**Corpus après exclusion : 212 → 210 articles.**

**Limite reconnue :** L'exclusion pour inaccessibilité introduit un biais géographique potentiel ; documentée conformément à PRISMA 2020.
**Impact PRISMA :** « 2 articles exclus — texte intégral non accessible (revues chinoises, CNKI/Wanfang) ».

---

### DEC-039 — Exclusion de 2 articles de revues chinoises inaccessibles (lot 2)
**Date :** 20 mars 2026
**Source :** Tentative de téléchargement des PDF pour le Tri #2

**Décision :** Deux articles supplémentaires publiés dans des revues chinoises sont exclus pour inaccessibilité (même motif que DEC-038).

**Articles exclus :**

| Rang | Auteurs | Année | Titre | DOI | Source |
|---:|---|---:|---|---|---|
| 400 | Zelin, L.; Zhaofeng, L.; et al. | 2024 | Entity Alignment Model Based on Multi-Hop Information Fusion | 10.19678/j.issn.1000-3428.0068946 | Computer Engineering |
| 863 | Rao, W.; Gao, H.; et al. | 2022 | Multi-source Heterogeneous Data Governance Based on Semi-supervised Learning (基于半监督学习的多源异构数据治理) | 10.11908/j.issn.0253-374x.22228 | Tongji Daxue Xuebao |

**Motif :** E_inaccessible — texte intégral non disponible (revues chinoises, accès CNKI/Wanfang requis, pas d'accès institutionnel).

**Mise à jour :** `decision` → `exclude` dans corpus_scored.csv ; lignes supprimées de articles_inclus.csv.

**Corpus après exclusion : 210 → 208 articles.**

**Limite reconnue :** Même biais géographique que DEC-038.
**Impact PRISMA :** « 2 articles exclus — texte intégral non accessible (revues chinoises, CNKI/Wanfang) ». Cumulé avec DEC-038 : 4 articles chinois exclus au total.

---

### DEC-040 — Exclusion de 2 articles inaccessibles (lot 3 : IOP + revue chinoise)
**Date :** 20 mars 2026
**Source :** Tentative de téléchargement des PDF pour le Tri #2

**Décision :** Deux articles supplémentaires sont exclus pour inaccessibilité.

**Articles exclus :**

| Rang | Auteurs | Année | Titre | DOI | Source | Motif |
|---:|---|---:|---|---|---|---|
| 910 | Li, Q.A.; Fang, H. | 2025 | An automatic ontology construction approach for BIM-IoT semantic integration in intelligent operation and maintenance of high-speed railway stations | 10.1088/2631-8695/adbe36 | Engineering Research Express (IOP) | Pas d'accès institutionnel |
| 1001 | Xu, Z.; Guan, W.; Gan, Z.; Fang, Z.; Cai, W. | 2025 | Construction of the CIM hierarchical classification semantic network based on multi-source heterogeneous data | 10.16511/j.cnki.qhdxxb.2025.26.003 | Qinghua Daxue Xuebao / Journal of Tsinghua University | PDF disponible mais texte intégral en chinois uniquement |

**Motif :** E_inaccessible (910 : paywall IOP, pas d'accès) ; E_langue (1001 : contenu exclusivement en chinois, pas de version anglaise disponible).

**Mise à jour :** `decision` → `exclude` dans corpus_scored.csv ; lignes supprimées de articles_inclus.csv.

**Corpus après exclusion : 208 → 206 articles.**

**Limite reconnue :** Biais géographique et linguistique cumulé avec DEC-038/039 (6 articles chinois/inaccessibles au total).
**Impact PRISMA :** Cumulé DEC-037 à DEC-040 : 2 World Scientific + 6 inaccessibles/chinois = 8 articles exclus au stade du texte intégral.

---

### DEC-041 — Snowballing arrière : ajout de 11 articles au corpus final

**Date :** 20 mars 2026
**Base / Outil :** Snowballing (backward) sur surveys et articles inclus

**Décision :** 11 articles issus du snowballing arrière sont ajoutés au corpus final avec qa_pass=oui. Ils sont intégrés dans `articles_inclus.csv` avec des rangs de la forme SV01/BT01–BT24 (code = préfixe du fichier PDF dans `data/fulltext/Snowballing/`). Le fichier `corpus_scored.csv` n'est pas modifié car ces articles sont hors du corpus de recherche initiale et n'ont pas de scores NLP.

**Sources du snowballing :**
- 13 surveys collectés dans `data/fulltext/Surveys/`
- 27 articles inclus du corpus principal

**Processus :** Tri 1 (titre + abstract, critères I1–I6) → Tri 2 (full-text, I4 strict) → QA (Q1–Q5, seuil ≥ 3/5).

**Articles ajoutés :**

| Rang | Auteurs | Année | Titre | QA Total |
|------|---------|-------|-------|----------|
| SV01 | Chen, Jiménez-Ruiz, Horrocks et al. | 2021 | Augmenting Ontology Alignment by Semantic Embedding and Distant Supervision | 4.5 |
| BT01 | Chen, Hu, Jiménez-Ruiz et al. | 2021 | OWL2Vec*: Embedding of OWL Ontologies | 4.0 |
| BT02 | Racharak T. | 2021 | Concept Similarity in DL ELH with Pretrained Word Embedding | 4.5 |
| BT03 | Qi, Zhang, Chen et al. | 2021 | Unsupervised KG Alignment by Probabilistic Reasoning and Semantic Embedding | 4.5 |
| BT06 | Ji, Qi, Yang et al. | 2022 | An Embedding-Based Approach to Repairing OWL Ontologies | 4.0 |
| BT07 | Zhu, Liu, Yao et al. | 2023 | TGR: Neural-Symbolic Ontological Reasoner for Domain Knowledge Graphs | 4.0 |
| BT10 | Jackermeier, Chen, Horrocks | 2023 | Box²EL: Concept and Role Box Embeddings for the Description Logic EL++ | 4.0 |
| BT11 | Li, Ji, Zhang et al. | 2022 | A Graph-Based Method for Interactive Mapping Revision in DL-Lite | 4.5 |
| BT12 | Li Y., Lambrix P. | 2023 | Repairing EL Ontologies Using Weakening and Completing | 3.5 |
| BT16 | Xu, Cheng, Zhang | 2024 | NALA: An Effective and Interpretable Entity Alignment Method | 5.0 |
| BT24 | Ciravegna, Barbiero, Giannini et al. | 2023 | Logic Explained Networks | 4.5 |

**Corpus après ajout : 27 (corpus initial) + 11 (snowballing) = 38 articles inclus (qa_pass=oui).**

**Limite reconnue :** Le snowballing a porté sur les références disponibles dans les PDFs collectés. Des articles pertinents dans des références non accessibles peuvent avoir été manqués. Le snowballing avant (forward) n'a pas été effectué.
**Impact PRISMA :** Documenter les 11 articles dans le flux PRISMA comme issus du snowballing (nœud distinct). Total corpus final = 38 études primaires.