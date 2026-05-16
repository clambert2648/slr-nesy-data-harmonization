# Liste de lecture — RSL NeSy Appariement sémantique

**Constance Lambert-Tremblay | M. Sc. informatique (IA), UQO**
**Directeur : Pr Etienne Gaël Tajeuna**
*29 études primaires + 18 surveys en lecture*

---

## État au démarrage de l'extraction

**Surveys d'ancrage théorique : COMPLÉTÉS**
- DeLong, Mir & Fleuriot (2025) — taxonomie NeSy × KG reasoning *(via INF-5183, A.6 à recycler)*
- Cotovio, Jiménez-Ruiz & Pesquita (2023) — closest existing work *(A.6 complétée)*
- Portisch, Hladik & Paulheim (2025) — généalogie OM *(A.6 complétée)*

**Glossaire NeSy/KGA v1 disponible** — référence stable pour terminologie pendant l'extraction.

---

## Mode d'emploi

La liste s'ouvre par un **Bloc 0 de calibration** puis se déploie en blocs thématiques par RQ. Les surveys restants sont **différés à l'écriture** des sections concernées de l'ESWA.

**Abréviations Type :**
- **SUR** — Survey
- **PRI** — Étude primaire (incluse aux 29)

**Statuts complémentaires :**
- **[LU]** — Lecture complétée
- **[STBY]** — Cas-frontière I4-strict, standby (rébutals défendus)
- **[CAL]** — Calibration A.5 (Bloc 0)
- **[DIFF]** — Différé à l'écriture

---

## Bloc 0 — Calibration A.5 (séquence ferme)

| # | Type | Rank | Référence | Rôle |
|---|------|------|-----------|------|
| 1 | PRI [CAL] | **1889** | Peng, Bonald & Suchanek (2025) — *FLORA* | Archétype I4-strict + recommandation Étienne (DEC-025). T-normes de Gödel. |
| 2 | PRI [CAL] | **58** | Chen et al. (2024) — *NeuSymEA* | Variante méthodologique (variationnel vs flou). |
| 3 | PRI [CAL] [STBY] | **137** | Jeon et al. (2025) — *SMoG* | Stress-test I4-strict #1. |
| 4 | PRI [CAL] [STBY] | BT-03 | Qi et al. (2021) — *PRASE* | Stress-test I4-strict #2. |
| 5 | PRI [CAL] | BT-16 | Xu et al. (2024) — *NALA* | Non-Axiomatic Logic active. |
| 6 | PRI [CAL] | **474** | Zhu et al. (2025) — *LEAF* | Bascule vers OA — features logiques + fusion adaptative. |

---

## Bloc 1 — Fondements neuro-symboliques (différés à l'écriture)

| Type | Rank | Référence | Quand y revenir |
|------|------|-----------|-----------------|
| SUR [LU] | 7 | DeLong (2025) | **Déjà digérée.** Recycler synthèse INF-5183 pour A.6. |
| SUR [DIFF] | 459 | Breit et al. (2023) — *Combining ML and Semantic Web: SLR* | Section **Methodology** ESWA. |
| SUR [DIFF] | 368 | Belle (2020) — *Symbolic Logic Meets ML* | **Optionnel.** |
| SUR [DIFF] | 76 | Kursuncu et al. (2020) — *K-IL* | **Optionnel.** |
| SUR [DIFF] | 30 | Keber et al. (2024) — *NeSy AI for NLP* | **Optionnel.** |
| SUR [DIFF] | 11 | Cheng et al. (2024) — *NeSy Methods for KG Reasoning* | **Optionnel.** |
| SUR [DIFF] | 70 | Wang & Li (2025) — *Temporal KG Reasoning* | **Optionnel.** |

---

## Bloc 2 — NeSy × Entity Alignment (cœur RQ1)

*FLORA, NeuSymEA, NALA, PRASE déjà couverts au Bloc 0.*

| # | Type | Rank | Référence | NeSy | QA |
|---|------|------|-----------|------|-----|
| 7 | PRI | 379 | Jiang et al. (2022) — *ESEA* | TransE + Horn clauses (AMIE+) + axiomes OWL/RDFS | 4.5 |
| 8 | PRI | 330 | Xiang et al. (2021) — *OntoEA* | owl:disjointWith → CCM + TransE | 4.5 |
| 9 | PRI | 81 | Jiang et al. (2023) — *Symbol Similarities with KGE for EA* | Similarités symboliques + KGE | 3.5 |
| 10 | PRI | 116 | Liu (2025) — *ARJE* | GCN/GAT joint embedding | 4.0 |
| 11 | PRI | 131 | Obraczka & Rahm (2025) — *Symbolic vs Embedding-Based Blocking* | Comparaison systématique | 4.0 |

---

## Bloc 3 — Ontology Matching / Alignment (cœur RQ1)

*Portisch (#56) déjà lue. LEAF déjà couvert au Bloc 0.*

### 3a — Surveys différés

| Type | Rank | Référence | Quand y revenir |
|------|------|-----------|-----------------|
| SUR [LU] | **56** | Portisch et al. (2025) | **Déjà lue.** A.6 complétée. |
| SUR [DIFF] | 264 | Barlaug & Gulla (2021) — *NN for Entity Matching* | Section *Related Work* — baseline neurale. |
| SUR [DIFF] | 265 | Li et al. (2021) — *Deep Entity Matching* | **Optionnel.** |

### 3b — Approches BERT / embedding + logique

| # | Type | Rank | Référence | NeSy | QA |
|---|------|------|-----------|------|-----|
| 12 | PRI | **286** | He et al. (2021) — *BERTMap* | BERT + logic-based mapping repair | 4.5 |
| 13 | PRI | SV-01 | Chen et al. (2021) — *Augmenting OA by Semantic Embedding* | LogMap/AML + Siamese NN | 4.5 |
| 14 | PRI | BT-01 | Chen et al. (2021) — *OWL2Vec\** | HermiT reasoner → random walks → embeddings | 4.0 |
| 15 | PRI | 311 | Tounsi Dhouib et al. (2021) — *Clusters of Labels in Embedding Space* | fastText + règles géométriques | 4.0 |
| 16 | PRI | 147 | Jiménez-Ruiz et al. (2020) — *Dividing OA Task* | Embedding + modules logiques | 4.0 |

### 3c — Approches graph-based et méta-heuristiques

| # | Type | Rank | Référence | NeSy | QA |
|---|------|------|-----------|------|-----|
| 17 | PRI | 315 | Wang & Hu (2022) — *Hybrid GAT Biomedical* | Axiomes OWL → GAT hyperbolique | 4.0 |
| 18 | PRI | 79 | Wu et al. (2020) — *DAEOM* | TBERT + SGAT biomédical | 4.0 |
| 19 | PRI | 93 | Chakraborty et al. (2021) — *OntoConnect* | RNN + méta-données | 3.0 |
| 20 | PRI | 455 | Xue et al. (2024) — *GA for Heuristic Selection in OM* | Algorithme génétique + cohérence | 4.0 |
| 21 | PRI | 263 | Atig et al. (2024) — *Agricultural Ontologies Evolution* | OWL-2 + Pellet, MCUR | 4.0 |

---

## Bloc 4 — Explicabilité, similarité sémantique et raisonnement formel (cœur RQ2)

### 4a — Surveys différés (à consulter à l'écriture du gap RQ2)

| Type | Rank | Référence | Quand y revenir |
|------|------|-----------|-----------------|
| SUR [DIFF] | **119** | Tiddi & Schlobach (2022) — *KGs for Explainable ML* | **Section gap RQ2/B4.** |
| SUR [DIFF] | 2 | Meziane et al. (2025) — *Symbolic Approaches for XAI* | **Optionnel.** |
| SUR [DIFF] | 156 | Zhang et al. (2024) — *ILP for XAI* | **Optionnel.** |

### 4b — Centralement B4 (focus explicabilité/HITL) — argument-clé RQ2

| # | Type | Rank | Référence | NeSy | QA |
|---|------|------|-----------|------|-----|
| 22 | PRI | **211** | Jearanaiwongkul & Racharak (2025) — *Human-Friendly Explanation* | DL similarity + LLM verbalization | 3.5 |
| 23 | PRI | **169** | Racharak & Jearanaiwongkul (2025) — *JSimELHExplainer* | Librairie NeSy ELH | 3.0 |
| 24 | PRI | BT-11 | Li et al. (2022) — *Interactive Mapping Revision in DL-Lite* | DL-Lite + HITL interactif | 4.5 |

### 4c — Similarité sémantique explicable (Q4=1, focus secondaire)

| # | Type | Rank | Référence | NeSy | QA |
|---|------|------|-----------|------|-----|
| 25 | PRI | BT-02 | Racharak (2021) — *Concept Similarity in DL ELH* | DL ELH reasoner + word embeddings | 4.5 |

### 4d — Révision / réparation d'ontologies

| # | Type | Rank | Référence | NeSy | QA |
|---|------|------|-----------|------|-----|
| 26 | PRI | 673 | Ji et al. (2023) — *Ontology Revision via PLMs* | DL reasoner (MIPS) + BERT/PLM | 4.0 |

---

## Bloc 6 — Schema Matching, harmonisation (RQ3)

*SMoG (#137) déjà couvert au Bloc 0.*

### 6a — Surveys différés (à consulter à la discussion / contexte applicatif)

| Type | Rank | Référence | Quand y revenir |
|------|------|-----------|-----------------|
| SUR [DIFF] | **1483** | Peng et al. (2024) — *Metadata-Driven Data Harmonization in Medical Domain* | **Discussion Socodevi** — scoping review FHIR-OMOP. |
| SUR [DIFF] | 466 | Diaz-de-Arcaya et al. (2025) — *Data Harmonization for Data Spaces* | **Discussion Socodevi.** |
| SUR [DIFF] | 358 | Koutras et al. (2021) — *Valentine* | **Optionnel.** |
| SUR [DIFF] | 1079 | Hong & Park (2025) — *LLMs for Semantic Join* | **Optionnel.** |

### 6b — Études primaires appliquées

| # | Type | Rank | Référence | NeSy | QA |
|---|------|------|-----------|------|-----|
| 27 | PRI | **200** | Centelles & Ferran-Ferrer (2025) — *Wikidata's Ontology* | Pipeline ontologie-first + RAG | 4.5 |
| 28 | PRI | **110** | Kumar (2025) — *Multilingual KG Alignment* | Multilingue — seul papier cross-lingual explicite | 3.5 |
| 29 | PRI | 798 | Carbonaro et al. (2025) — *FHIR-based Pipeline* | FHIR, validation sémantique oncologie | 3.5 |

---

## Annexe — Surveys utiles pour snowballing uniquement

| Rank | Référence | Intérêt snowballing |
|------|-----------|---------------------|
| 69 | Alam et al. (2024) — *NeSy Methods for Dynamic KGs* | NeSy + KG dynamiques |
| 547 | Chen et al. (2023) — *LLMs and Knowledge Graphs* | LLM + KG |
| 552 | Singh & Siwach (2022) — *Heterogeneous Data in KGs* | KG hétérogènes |
| 745 | Qiang et al. (2024) — *OAEI-LLM Benchmark* | Benchmark OAEI + LLM |
| 762 | Hertling & Paulheim (2020) — *KG Track at OAEI* | Gold standards OAEI |
| 799 | Hertling et al. (2024) — *OAEI ML Dataset* | Dataset OAEI ML |
| 919 | Qiang et al. (2025) — *OAEI-LLM-T TBox* | Benchmark TBox OAEI |
| 651 | Lambrix (2023) — *Completing and Debugging Ontologies* | Ontology repair |
| 842 | Pardeshi et al. (2024) — *Metaheuristic Algorithms & OM* | Méta-heuristiques + OM |
| 820 | Zengeya & Fonou-Dombeu (2024) — *DL for Ontology Construction* | DL + ontology construction |

---

## Récapitulatif quantitatif

| Catégorie | N |
|-----------|---|
| Études primaires | **29** |
| — cas-frontière I4-strict (standby) | 2 (SMoG, PRASE) |
| Surveys d'ancrage théorique | 3 (tous lus) |
| Surveys différés à l'écriture | 14 |
| — dont déjà digérée (DeLong) | 1 |
| Surveys snowballing seul | 10 |
| **Total liste de lecture** | **47** |

---

## Distribution des 29 primaires par bloc

| Bloc | Description | N |
|------|-------------|---|
| Bloc 0 | Calibration A.5 | 6 |
| Bloc 2 | NeSy × Entity Alignment (hors Bloc 0) | 5 |
| Bloc 3b | OM — BERT/embedding + logique | 5 |
| Bloc 3c | OM — graph-based / méta-heuristiques | 5 |
| Bloc 4b | Explicabilité (centralement B4) | 3 |
| Bloc 4c | Similarité sémantique explicable | 1 |
| Bloc 4d | Révision/réparation | 1 |
| Bloc 6b | Schema matching / harmonisation appliquée | 3 |
| **Total** | | **29** |

---

## Prochaine action

**FLORA (rang 1889)** — extraction A.5.
