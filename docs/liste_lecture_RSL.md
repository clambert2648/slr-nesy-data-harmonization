# Liste de lecture — RSL NeSy Appariement sémantique

**Constance Lambert-Tremblay | M. Sc. informatique (IA), UQO**
**Directeur : Pr Étienne Gaël Tajeuna**
*Générée le 24 mars 2026 — 38 études primaires + 18 surveys pertinents*

---

## Mode d'emploi

La liste est organisée en **7 blocs thématiques**, chacun avec un ordre de lecture interne (surveys de cadrage → études primaires). L'ordre des blocs suit une logique d'entonnoir : fondements NeSy → appariement/alignment (cœur RQ1) → explicabilité/HITL (RQ2) → contextes appliqués (RQ3).

**Légende :** 📚 Survey | 📄 Étude primaire (incluse aux 38)

---

## Bloc 1 — Fondements neuro-symboliques

*Cadre théorique NeSy : taxonomies d'intégration, positionnement dans le paysage IA.*
*Lire en premier pour stabiliser le vocabulaire et la taxonomie NeSy utilisée dans le mémoire.*

| # | Type | Rank | Référence | Pourquoi |
|---|------|------|-----------|----------|
| 1 | 📚 | 459 | Breit et al. (2023) — *Combining ML and Semantic Web: A Systematic Mapping Study* | Cartographie NeSy + Semantic Web la plus complète. Fournit la taxonomie des modes d'intégration (pipeline, joint, hybrid). |
| 2 | 📚 | 368 | Belle (2020) — *Symbolic Logic Meets ML: A Brief Survey in Infinite Domains* | Fondements formels de l'articulation logique symbolique / apprentissage. |
| 3 | 📚 | 76 | Kursuncu, Gaur & Sheth (2020) — *Knowledge Infused Learning (K-IL)* | Cadre K-IL pour l'injection de connaissances dans le DL — niveaux d'infusion. |
| 4 | 📚 | 30 | Keber et al. (2024) — *A Review on NeSy AI Improvements to NLP* | NeSy + NLP — utile pour le volet multilingue et traitement du langage. |
| 5 | 📄 | BT-24 | Ciravegna et al. (2023) — *Logic Explained Networks* | FOL active pour expliquer les réseaux neuronaux. Référence méthodologique transversale. |

---

## Bloc 2 — NeSy × KG Reasoning et Entity Alignment (cœur RQ1)

*Le noyau dur : surveys spécialisés NeSy+KG puis les études primaires d'entity alignment inter-KG.*
*C'est le bloc le plus dense — commencer par les 3 surveys pour avoir la vue d'ensemble avant les papiers techniques.*

### 2a — Surveys de cadrage

| # | Type | Rank | Référence | Pourquoi |
|---|------|------|-----------|----------|
| 6 | 📚 | **20** | Cotovio, Jimenez-Ruiz & Pesquita (2023) — *What can KG alignment gain with NeSy learning approaches?* | **Survey-pivot.** Pose exactement ta question RQ1 : que gagne l'alignement KG avec le NeSy? |
| 7 | 📚 | 7 | DeLong, Mir & Fleuriot (2025) — *Neurosymbolic AI for Reasoning Over KGs: A Survey* | Taxonomie NeSy+KG reasoning complète, GNN + règles logiques. |
| 8 | 📚 | 11 | Cheng et al. (2024) — *Neural-Symbolic Methods for KG Reasoning: A Survey* | Complémentaire au #7, focus sur les méthodes de raisonnement. |
| 9 | 📚 | 70 | Wang & Li (2025) — *Temporal KG Reasoning: ...Neural-Symbolic Hybrid Methods* | Utile pour la taxonomie des hybrides rule-based + embedding. |

### 2b — Entity alignment NeSy (études primaires)

*Lire dans cet ordre : non supervisé symbolique → hybride embedding+règles → variationnel.*

| # | Type | Rank | Référence | NeSy | QA |
|---|------|------|-----------|------|-----|
| 10 | 📄 | **1889** | Peng, Bonald & Suchanek (2025) — *FLORA: Unsupervised KG Alignment by Fuzzy Logic* | Logique floue formelle (Gödel T-norms) | 5.0 |
| 11 | 📄 | BT-03 | Qi, Zhang, Chen et al. (2021) — *Unsupervised KG Alignment by Probabilistic Reasoning and Semantic Embedding* | PARIS (prob. symbolique) + KG embeddings itératifs | 4.5 |
| 12 | 📄 | 379 | Jiang et al. (2022) — *Combining embedding-based and symbol-based methods for EA* | TransE + Horn clauses (AMIE+) + axiomes OWL/RDFS | 4.5 |
| 13 | 📄 | 330 | Xiang et al. (2021) — *OntoEA: Ontology-guided EA via Joint KG Embedding* | owl:disjointWith → Class Conflict Matrix + TransE | 4.5 |
| 14 | 📄 | **58** | Chen et al. (2024) — *Neuro-Symbolic EA via Variational Inference (NeuSymEA)* | MRF + règles logiques + EM variationnel | 5.0 |
| 15 | 📄 | BT-16 | Xu et al. (2024) — *NALA: Effective and Interpretable EA* | Non-Axiomatic Logic (NAL), Hits@1 0.98+ | 5.0 |
| 16 | 📄 | 81 | Jiang et al. (2023) — *Integrating Symbol Similarities with KGE for EA: Unsupervised* | Similarités symboliques (string, sémantique, path) + KGE | 3.5 |
| 17 | 📄 | 116 | Liu (2025) — *Attribute-Relationship Joint Embedding for KG EA* | GCN/GAT joint embedding attributs-relations | 4.0 |
| 18 | 📄 | 131 | Obraczka & Rahm (2025) — *Comparing Symbolic and Embedding-Based Approaches for Relational Blocking* | Comparaison systématique symbolique vs. embedding pour blocking KG | 4.0 |

---

## Bloc 3 — Ontology Matching / Alignment (cœur RQ1)

*Deuxième pilier de I2 : l'ontology matching. Survey de cadrage puis études par sous-approche.*

### 3a — Surveys de cadrage

| # | Type | Rank | Référence | Pourquoi |
|---|------|------|-----------|----------|
| 19 | 📚 | **56** | Portisch, Hladik & Paulheim (2025) — *Background knowledge in ontology matching: A survey* | Rôle du background knowledge (KG, corpus) dans l'OM. Directement pertinent pour ta composante symbolique. |
| 20 | 📚 | 264 | Barlaug & Gulla (2021) — *Neural Networks for Entity Matching: A Survey* | Panorama complet des approches neurales pour EM — ta baseline neurale. |
| 21 | 📚 | 265 | Li et al. (2021) — *Deep Entity Matching: Challenges and Opportunities* | Complémentaire au #20 : deep learning + EM, challenges ouverts. |

### 3b — Approches BERT / embedding + logique (études primaires)

| # | Type | Rank | Référence | NeSy | QA |
|---|------|------|-----------|------|-----|
| 22 | 📄 | **286** | He et al. (2021) — *BERTMap: A BERT-based Ontology Alignment System* | BERT + logic-based mapping repair (axiomes propositionnels) | 4.5 |
| 23 | 📄 | SV-01 | Chen et al. (2021) — *Augmenting OA by Semantic Embedding and Distant Supervision* | LogMap/AML (reasoneurs symboliques) + Siamese NN | 4.5 |
| 24 | 📄 | BT-01 | Chen et al. (2021) — *OWL2Vec*: Embedding of OWL Ontologies* | HermiT reasoner actif → random walks → embeddings | 4.0 |
| 25 | 📄 | **474** | Zhu et al. (2025) — *LEAF: Logic-Enhanced Adaptive Fusion for Large-Scale OA* | Features logiques (Qwen2.5) + fusion adaptative | 5.0 |
| 26 | 📄 | 311 | Tounsi Dhouib et al. (2021) — *Measuring Clusters of Labels in Embedding Space to Refine Relations in OA* | fastText + règles géométriques symboliques | 4.0 |
| 27 | 📄 | 147 | Jiménez-Ruiz et al. (2020) — *Dividing the OA Task with Semantic Embeddings and Logic-based Modules* | Embedding neural + modules logiques pour diviser la tâche | 4.0 |

### 3c — Approches graph-based et méta-heuristiques (études primaires)

| # | Type | Rank | Référence | NeSy | QA |
|---|------|------|-----------|------|-----|
| 28 | 📄 | 315 | Wang & Hu (2022) — *Matching Biomedical Ontologies via a Hybrid GAT* | Axiomes OWL transforment le graphe → GAT hyperbolique | 4.0 |
| 29 | 📄 | 79 | Wu et al. (2020) — *DAEOM: Deep Attentional Embedded OM* | TBERT + SGAT (graph attention) biomédical | 4.0 |
| 30 | 📄 | 871 | Li et al. (2021) — *Combining FCA-Map with Representation Learning for Aligning Large Biomedical Ontologies* | FCA (raisonnement symbolique) + SBERT | 4.5 |
| 31 | 📄 | 93 | Chakraborty et al. (2021) — *OntoConnect: Unsupervised OA with Recursive NN* | Pipeline extraction méta-données + RNN | 3.0 |
| 32 | 📄 | 455 | Xue et al. (2024) — *Compact Multitasking Multichromosome GA for Heuristic Selection in OM* | Algorithme génétique + cohérence locale symbolique | 4.0 |
| 33 | 📄 | 263 | Atig et al. (2024) — *Impact of Agricultural Ontologies Evolution on Alignment Preservative Adaptation* | OWL-2 + Pellet reasoner, algorithme MCUR | 4.0 |

### 3d — Outils et infrastructure OM

| # | Type | Rank | Référence | NeSy | QA |
|---|------|------|-----------|------|-----|
| 34 | 📄 | **665** | He et al. (2023) — *DeepOnto: A Python Package for Ontology Engineering with Deep Learning* | HermiT/ELK reasoners + DL — outil de référence | 4.5 |

---

## Bloc 4 — Explicabilité, similarité sémantique et raisonnement formel (RQ2)

*Couvre RQ2 : comment rendre les décisions d'appariement explicables et interprétables.*

### 4a — Surveys de cadrage

| # | Type | Rank | Référence | Pourquoi |
|---|------|------|-----------|----------|
| 35 | 📚 | **119** | Tiddi & Schlobach (2022) — *KGs as tools for explainable ML: A survey* | KG + XAI — cadre conceptuel pour ta validation interactive. |
| 36 | 📚 | 2 | Meziane et al. (2025) — *Symbolic Approaches for XAI* | Approches symboliques pour l'explicabilité — fondements. |
| 37 | 📚 | 156 | Zhang, Yilmaz & Liu (2024) — *ILP Techniques for XAI* | ILP = raisonnement symbolique inductif + explicabilité. |

### 4b — Similarité sémantique explicable en DL (études primaires)

| # | Type | Rank | Référence | NeSy | QA |
|---|------|------|-----------|------|-----|
| 38 | 📄 | BT-02 | Racharak (2021) — *Concept Similarity in DL ELH with Pretrained Word Embedding* | DL ELH reasoner + word embeddings, explication par degré | 4.5 |
| 39 | 📄 | **169** | Racharak & Jearanaiwongkul (2025) — *JSimELHExplainer: Explainable Semantic Similarity for ELH DL* | Librairie NeSy ELH, explicabilité formelle | 3.0 |
| 40 | 📄 | **211** | Jearanaiwongkul & Racharak (2025) — *Human-Friendly Explanation for Ontology-based Concept Similarity* | DL similarity + word embeddings + LLM verbalization | 3.5 |

### 4c — Révision / réparation d'ontologies (études primaires)

| # | Type | Rank | Référence | NeSy | QA |
|---|------|------|-----------|------|-----|
| 41 | 📄 | 673 | Ji et al. (2023) — *Ontology Revision based on Pre-trained LMs* | DL reasoner (MIPS detection) + BERT/PLM | 4.0 |
| 42 | 📄 | BT-06 | Ji et al. (2022) — *Embedding-Based Approach to Repairing OWL Ontologies* | Détection conflits OWL + embeddings pour repair | 4.0 |
| 43 | 📄 | BT-12 | Li & Lambrix (2023) — *Repairing EL Ontologies Using Weakening and Completing* | EL reasoning symbolique (weakening + completing) | 3.5 |
| 44 | 📄 | BT-11 | Li et al. (2022) — *Graph-Based Interactive Mapping Revision in DL-Lite* | **DL-Lite reasoning + HITL interactif** — le plus pertinent RQ2 | 4.5 |

---

## Bloc 5 — Raisonnement ontologique et embeddings (RQ1 — fondations formelles)

*Papiers plus théoriques sur l'embedding de logiques de description — bases formelles pour ta composante symbolique.*

| # | Type | Rank | Référence | NeSy | QA |
|---|------|------|-----------|------|-----|
| 45 | 📄 | BT-10 | Jackermeier et al. (2023) — *Box²EL: Concept and Role Box Embeddings for DL EL++* | Axiomes DL EL++ contraignent géométriquement l'espace | 4.0 |
| 46 | 📄 | BT-07 | Zhu et al. (2023) — *TGR: Neural-Symbolic Ontological Reasoner for Domain KGs* | OWL+SWRL compilés en réseaux neuronaux | 4.0 |

---

## Bloc 6 — Schema Matching, annotation tabulaire et harmonisation (RQ3)

*Contextes d'application plus proches de ton cas Socodevi : données tabulaires, schémas hétérogènes, harmonisation.*

### 6a — Surveys de cadrage

| # | Type | Rank | Référence | Pourquoi |
|---|------|------|-----------|----------|
| 47 | 📚 | **1483** | Peng et al. (2024) — *Metadata-Driven Approaches for Data Harmonization in the Medical Domain* | Le plus proche de ton contexte applicatif : harmonisation ex-post de données hétérogènes multi-sites. |
| 48 | 📚 | 466 | Diaz-de-Arcaya et al. (2025) — *Data Harmonization as a Keystone for Data Spaces* | Cadrage harmonisation de données — challenges et techniques. |
| 49 | 📚 | 358 | Koutras et al. (2021) — *Valentine: Evaluating Matching Techniques for Dataset Discovery* | Benchmark de techniques de matching — référence méthodologique. |
| 50 | 📚 | 1079 | Hong & Park (2025) — *LLMs for Semantic Join: A Comprehensive Survey* | Semantic join ≈ variante de ta tâche; couverture LLM. |

### 6b — Études primaires appliquées

| # | Type | Rank | Référence | NeSy | QA |
|---|------|------|-----------|------|-----|
| 51 | 📄 | **137** | Jeon et al. (2025) — *SMoG: Schema Matching on Graph — Iterative Graph Exploration for Explainable Data Integration* | KG + SPARQL 1-hop itératif, **explicable** | 4.5 |
| 52 | 📄 | **121** | Mehryar & Çelebi (2023) — *Semantic Annotation of Tabular Data via Neuro-Symbolic Anchoring* | NeSy anchoring, données tabulaires | 3.5 |
| 53 | 📄 | **200** | Centelles & Ferran-Ferrer (2025) — *Using Wikidata's Ontology: A NeSy Workflow for Integrating Humanities Datasets* | Pipeline ontologie-first + RAG, intégration de datasets | 4.5 |
| 54 | 📄 | **110** | Kumar (2025) — *Semantic Alignment of Multilingual KGs via Contextualized Vector Projections* | **Multilingue** — le seul papier cross-lingual explicite | 3.5 |
| 55 | 📄 | 1170 | Yang et al. (2025) — *PhenoAlign: Hybrid Data-Knowledge-Driven Approach for Aligning Phenotype Information* | BERT + association rules, domaine médical | 4.0 |
| 56 | 📄 | 798 | Carbonaro et al. (2025) — *From raw data to research-ready: A FHIR-based transformation pipeline* | Pipeline FHIR, validation sémantique en oncologie | 3.5 |

---

## Annexe — Surveys utiles pour snowballing uniquement

*Pas en lecture prioritaire, mais à consulter pour extraire des références supplémentaires si le corpus final est insuffisant.*

| Rank | Référence | Intérêt snowballing |
|------|-----------|---------------------|
| 69 | Alam et al. (2024) — *Neurosymbolic Methods for Dynamic KGs* | NeSy + KG dynamiques |
| 547 | Chen et al. (2023) — *LLMs and Knowledge Graphs* | LLM + KG |
| 552 | Singh & Siwach (2022) — *Handling Heterogeneous Data in KGs* | KG hétérogènes |
| 745 | Qiang et al. (2024) — *OAEI-LLM: Benchmark for LLM Hallucinations in OM* | Benchmark OAEI + LLM |
| 762 | Hertling & Paulheim (2020) — *The KG Track at OAEI* | Gold standards OAEI |
| 799 | Hertling et al. (2024) — *OAEI ML Dataset for Online Model Generation* | Dataset OAEI ML |
| 919 | Qiang et al. (2025) — *OAEI-LLM-T: TBox Benchmark* | Benchmark TBox OAEI |
| 651 | Lambrix (2023) — *Completing and Debugging Ontologies* | Ontology repair |
| 842 | Pardeshi et al. (2024) — *Metaheuristic Algorithms & Ontology Integration* | Méta-heuristiques + OM |
| 820 | Zengeya & Fonou-Dombeu (2024) — *DL Models for Ontology Construction* | DL + ontology construction |

---

## Résumé quantitatif

| Catégorie | N |
|-----------|---|
| Études primaires (38) | 38 |
| Surveys en lecture (Tier 1 + 2) | 18 |
| Surveys snowballing seul | 10 |
| Surveys non pertinents (exclus de la liste) | 31 |
| **Total liste de lecture** | **56** |
