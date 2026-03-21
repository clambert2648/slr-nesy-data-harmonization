# Tri #2 QA — Instructions Claude Code

## Contexte
RSL mémoire maîtrise IA/UQO. Appariement sémantique explicable d'indicateurs multilingues (NeSy).

## Fichiers
- `data/processed/articles_inclus.csv` : CSV maître. Col 1 = `rank` (ID unique).
- `data/fulltext/Screening_1_included/` : PDFs nommés `{rank}_{Author}_{Year}.pdf`

## Grille QA — scoring 0/0.5/1, seuil 3/5

| Q | Critère | 0.5 = |
|---|---------|-------|
| Q1 | Objectifs et tâche clairement définis | partiellement |
| Q2 | Architecture NeSy reproductible (composantes, intégration, hyperparamètres) | décrite mais pas reproductible |
| Q3 | Dataset nommé+taille + métrique standard (F1/P/R/MRR/Hit@k) | dataset proprio non divulgué OU métriques non standard |
| Q4 | Explications des décisions d'appariement (traces, scores, viz, HITL) | scores seuls, sans justification structurée |
| Q5 | Comparaison à baseline externe | ablation interne seulement |
| Q6 | [BONUS, hors total] Limites discutées | partiellement |

`qa_total = Q1+Q2+Q3+Q4+Q5` | `qa_pass = "oui" si ≥ 3`

## I4 strict (critère d'inclusion)

**✅ Passe** : raisonnement symbolique ACTIF couplé au neural — axiomes OWL, clauses de Horn, logique de description, logique floue formelle, règles symboliques appliquées à l'inférence.

**❌ Échoue** : KG/ontologie utilisé UNIQUEMENT comme input pour embeddings (GNN, TransE, BERT).

**Si I4 échoue** → tous les scores à 0, `qa_pass="non"`, documenter dans `qa_notes_q2` :
`[I4 STRICT ÉCHOUÉ] Ancien score : Q1=X…total=X pass=X. Raison : [explication]. Scores remis à 0.`
Préfixer `qa_notes_q1` avec `[REVISE CC]` quand même.

## Marquage
Toujours préfixer `qa_notes_q1` par `[REVISE CC]` (changé ou non).
- Changé : `[REVISE CC] Scores modifiés. [justification]`
- Inchangé : `[REVISE CC] Scores confirmés.`

Reprendre là où `qa_notes_q1` ne commence PAS par `[REVISE CC]`.

## Phase 1 — Révision des QA existants (qa_total rempli)
1. Lire PDF → évaluer Q1-Q6 indépendamment
2. Comparer avec scores CSV :
   - Écart ≤ 0.5 → garder, noter `[REVISE CC] Scores confirmés.`
   - Écart > 0.5 → analyser justifications → garder la mieux étayée
3. Présenter tableau, **attendre validation avant d'écrire le CSV**

Tableau Phase 1 : `Rank | Titre | QA exist. | QA révisé | Changé? | Raison`

PDF absent → `comment = "pdf_absent_phase1"`, passer.

## Phase 2 — Évaluation des articles sans QA (qa_total vide)
1. Vérifier I4 strict
2. Si ❌ → scores 0, documenter
3. Si ✅ → évaluer Q1-Q6
4. Présenter tableau, **attendre validation avant d'écrire le CSV**

Tableau Phase 2 : `Rank | Titre | I4 | Q1 | Q2 | Q3 | Q4 | Q5 | Q6 | Total | Pass`

PDF absent → `comment = "a_telecharger"`, passer.
"continue" = rescanner le dossier et traiter les nouveaux PDFs.

## Ordre d'exécution
1. Diagnostic : décompte CSV + PDFs disponibles
2. Phase 1 (batches de 5)
3. Phase 2 (batches de 5)
4. Rapport final
