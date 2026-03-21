# HANDOFF.md — Revue systématique de littérature (RSL) NeSy
## Pour reprendre le travail dans un nouveau chat Claude (claude.ai ou Claude Code)

---

## Qui suis-je

Constance Lambert-Tremblay, M.Sc. informatique (IA), UQO.
Directeur : Pr Étienne Gaël Tajeuna.
Thèse : appariement sémantique explicable d'indicateurs multilingues hétérogènes — approche neuro-symbolique avec validation interactive pour l'harmonisation ex-post (Socodevi).

---

## Où j'en suis

### RSL — Méthodologie Carrera Rivera et al. (2022)

| Phase | Statut | Détails |
|-------|--------|---------|
| Corpus brut | ✅ Terminé | 1 890 articles (Scopus, IEEE, ACM, arXiv) → 1 888 après E6 |
| Déduplication | ✅ Terminé | 1 888 → 457 uniques (scoring) → 1 888 total avec doublons tagués |
| Tri #1 (screening) | ✅ Terminé | 217 inclusions, 59 surveys, ~1 612 exclusions |
| Validation inter-éval. | ✅ Terminé | DEC-023/024 : Claude Sonnet comme 2e évaluateur, κ=0.272, 185 changements documentés |
| FLORA (expert rec.) | ✅ Terminé | DEC-025 : 1 article ajouté via PRISMA "Other methods" |
| **Tri #2 (QA full-text)** | **🔄 En cours** | **85/217 complétés, 132 restants** |
| Tri #3 (extraction A.5) | ⬜ À venir | Formulaire v4 prêt |

### État du Tri #2

- **85 articles évalués** : 73 passés (≥ 3/5), 12 échoués
- **132 articles à évaluer** : qa_total vide dans le CSV
- **Score moyen actuel** : 3.59/5, taux de passage 86%
- **PDFs disponibles** : 114/217 avec pdf_filename renseigné
- **Phase 1 (révision des 85 existants)** : pas encore commencée — une session Claude Code a été lancée mais a crashé sur "Prompt is too long" avant de sauvegarder quoi que ce soit. Le CSV n'a pas été modifié.

---

## Fichiers clés du projet

```
SLR_THESIS/
├── data/
│   ├── processed/
│   │   ├── articles_inclus.csv          ← CSV maître Tri #2 (217 articles)
│   │   ├── articles_surveys.csv         ← 59 surveys pour snowballing
│   │   ├── corpus_scored.csv            ← Corpus complet (1888 articles)
│   │   └── articles_extraction.csv      ← Pour le Tri #3 (à créer)
│   └── fulltext/
│       ├── Screening_1_included/        ← PDFs des 217 inclusions Tri #1
│       ├── Screening_2_excluded/        ← PDFs échouant QA
│       ├── Extraction/                  ← PDFs passant QA → études primaires
│       ├── Surveys/                     ← PDFs des surveys
│       └── archive/                     ← PDFs bruts
├── docs/
│   └── instructions_tri2.md            ← Instructions complètes pour le QA
└── logs/
    └── decisions_log.md                ← DEC-001 à DEC-025
```

### Convention de nommage des PDFs
`{Rank}_{AuthorLastName}_{Year}.pdf`
- La colonne `rank` (première colonne de articles_inclus.csv) est l'identifiant unique
- Exemple : `025_Liu_2023.pdf`, `1888_Peng_2025.pdf`

---

## Grille QA (à utiliser pour le Tri #2)

| Q | Question | 0 | 0.5 | 1 |
|---|----------|---|-----|---|
| Q1 | Objectifs et tâche d'appariement clairement définis ? | non | partiellement | oui |
| Q2 | Architecture NeSy reproductible ? | non | décrite mais pas reproductible | oui |
| Q3 | Dataset identifié + métrique standard ? | non | dataset propriétaire ou métrique non standard | oui |
| Q4 | Explications/justifications des décisions ? | absent | scores seulement | traces structurées |
| Q5 | Comparaison à une baseline ? | non | ablation interne seulement | baseline externe |
| Q6 | [BONUS] Limites discutées ? | non | partiellement | oui |

**Calcul :** qa_total = Q1+Q2+Q3+Q4+Q5 (Q6 pas dans la somme)
**Seuil :** qa_pass = "oui" si qa_total ≥ 3

---

## Distinction critique I4 (Tri #2)

Au Tri #1, I4 était lénitif : neural + KG/ontologie dans un contexte de matching suffisait.

**Au Tri #2, I4 est strict :**
- ❌ KG/ontologie utilisé uniquement comme input pour embeddings (GNN, TransE, BERT)
- ✅ Raisonnement symbolique ACTIF : axiomes d'ontologie, clauses de Horn, logique de description, logique floue avec garanties, règles symboliques à l'inférence
- Si I4 strict échoue → article exclu (tous les scores QA à 0)

---

## Décisions méthodologiques clés (résumé)

| DEC | Sujet |
|-----|-------|
| DEC-007 | arXiv inclus comme source primaire (demande du directeur) |
| DEC-014 | I4 lénitif au Tri #1, strict au Tri #2. Exception E1 pour entity alignment inter-KG |
| DEC-023 | Validation inter-évaluateur par LLM (Claude Sonnet), κ=0.272, 1875/1888 traités |
| DEC-024 | 185 changements : 141 réintégrations, 6 exclusions FP, 24 surveys, 7 doublons, 7 reclassements E1→I4 |
| DEC-025 | FLORA (Peng et al. 2025) ajouté par recommandation expert — gap terminologique documenté |

---

## Ce qui reste à faire

### Immédiat : Tri #2
1. **Phase 1** — Réviser les 85 QA existants (Claude Code relit les PDFs, compare ses scores, remplace si meilleurs)
2. **Phase 2** — Évaluer les 132 articles restants (par batches de 10)
3. Télécharger les ~103 PDFs manquants en parallèle
4. Documenter le Tri #2 complet (DEC-026)

### Ensuite : Tri #3 (extraction)
- Formulaire A.5 v4 prêt (PDF généré)
- ~160-180 études primaires estimées après Tri #2
- Extraction recto-verso par article

### Plus tard
- Backward snowballing sur 59 surveys (7 prioritaires + 6 nouveaux haute pertinence)
- Publication : Expert Systems with Applications (SLR) + Knowledge-Based Systems (pipeline)
- Rédaction du mémoire sur Overleaf

---

## Comment utiliser ce fichier

### Dans Claude Code (VS Code)
```
Lis HANDOFF.md pour le contexte complet du projet.
Puis lis docs/instructions_tri2.md pour les instructions détaillées du Tri #2.
Ensuite lis data/processed/articles_inclus.csv pour voir l'état actuel.
Commence par le diagnostic, puis Phase 1 (révision des 85 existants).
```

### Dans claude.ai (nouveau chat)
Uploader ce fichier + articles_inclus.csv et dire :
```
Voici le handoff de ma RSL. Lis HANDOFF.md pour le contexte.
[ta question spécifique]
```

### Gestion du contexte (important)
Claude Code crashe si la conversation devient trop longue (> 20 échanges avec PDFs).
**Après chaque batch de 10 articles**, vérifier que le CSV est sauvegardé.
Si "Prompt is too long" → nouveau chat, le CSV sert de checkpoint.
```
Lis HANDOFF.md et data/processed/articles_inclus.csv.
Reprends le Tri #2 là où tu t'es arrêté — traite seulement les qa_total vides.
```
