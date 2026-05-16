# Pipeline d'extraction LLM — RSL NeSy (v3)

## Vue d'ensemble

Script Python pour l'extraction assistée par LLM des données de la RSL NeSy.
PDF → pré-traitement structurel → Claude API (Opus 4.6) → JSON → Excel + CSV

**v3 (DEC-028)** : prompt système recadré en mode **descriptif** (suppression du gating I4-strict, qui n'a plus sa place en extraction puisqu'il a été appliqué aux Tri #2 et Tri #3). Ajout de trois vocabulaires contrôlés D2/D6/D7 issus de la grille de codage v2 (DEC-027). Suppression des champs décisionnels `role` et `i4_strict_assessment`. Filtrage par `status` (`included` / `standby` / `retired`) dans `block_mapping.csv` v3.

## Installation

```powershell
pip install anthropic pypdf openpyxl pandas tqdm
$env:ANTHROPIC_API_KEY = "sk-ant-api03-..."
```

## Corpus actif

Après la révision post-screening avec le directeur (DEC-026) :

| Type | Statut | N |
|------|--------|---|
| Études primaires (PS) | `included` | 27 |
| Études primaires (PS) | `standby` (SMoG, PRASE — rébutals défendus) | 2 |
| Études primaires (PS) | `retired` (sortis par audit full-text) | 9 |
| Surveys (SV) | `included` | 18 |
| **Corpus actif extraction** | included + standby | **47** |
| **Traçabilité PRISMA** | toutes statuts | **56** |

Le script v3 traite par défaut les 27 included + 2 standby = **29 PS + 18 SV**. Les 9 retired sont ignorés sauf si `--include-retired` (mode audit).

## Structure des dossiers

```
SLR_thesis/data/fulltext/
├── Extraction/          ← PS (PDF)
├── Surveys/             ← SV (PDF)

SLR_thesis/data/extraction_output/   ← Créé automatiquement
├── extraction_SLR_YYYYMMDD_HHMM.xlsx
├── block_mapping.csv    ← v3 avec colonne status (à placer ici)
├── csv/
│   ├── extraction_A5_*.csv
│   └── extraction_A6_*.csv
├── json/                ← JSON brut (fidélité complète)
├── checkpoints/         ← 1 JSON par article (reprise crash)
├── debug/               ← Réponses LLM échouées
├── id_map_PS.csv        ← Mapping PS-001 → filename.pdf
├── id_map_SV.csv
└── extraction.log
```

## Utilisation

```powershell
python extract_slr.py --test 3                # Calibration descriptive (obligatoire d'abord)
python extract_slr.py                         # Extraction complète séquentielle (29 PS + 18 SV)
python extract_slr.py --batch                 # Batch API (−50% coût)
python extract_slr.py --resume                # Reprendre après crash/interruption
python extract_slr.py --article "peng"        # Extraire un seul article
python extract_slr.py --primary-only          # Études primaires seulement
python extract_slr.py --include-retired       # Audit : inclure aussi les 9 retired
python extract_slr.py --exclude-standby       # Exclure SMoG et PRASE
```

## Partage des rôles (DEC-027)

Point méthodologique central de la v3. Trois outils, trois champs d'action distincts :

| Outil | Ce qu'il produit |
|-------|------------------|
| **xlsx première passe** (déjà existante) | Hypothèse D1–D7 basée sur abstracts + QA notes. Point de départ de lecture. |
| **Pipeline LLM** (ce script) | A.5 factuel (architecture, datasets, métriques, baselines, reproductibilité) + vocabulaires contrôlés **D2, D6, D7**. |
| **Lecture papier** (chercheuse) | Codage manuel **D1, D3, D4, D5** sur fiche A.5 papier, en confrontation avec l'hypothèse xlsx. |

Le LLM **ne produit pas** D1, D3, D4 ni D5 — ce sont les dimensions architecturales publiables (D1, D3, D5) ou descriptives sensibles (D4) qui demandent ton jugement à la lecture. Cette séparation évite le piège du *validation theater* (deux passes automatiques qui s'accordent pour la mauvaise raison).

## Pré-traitement structurel

Avant envoi à Claude, le texte extrait du PDF passe par un détecteur de sections qui insère des marqueurs explicites :

```
[METHODOLOGY]
3 Proposed Method
We propose a neuro-symbolic framework that combines...

[RESULTS]
5 Experiments
5.1 Datasets
We evaluate on three benchmarks...
```

**Comment ça marche** : des regex détectent les patterns de titres de sections (numérotés, romains, ALL CAPS) puis classifient chaque heading dans une catégorie canonique (ABSTRACT, METHODOLOGY, RESULTS, etc.).

**Pourquoi c'est utile** : le system prompt dit à Claude où chercher chaque type d'information. L'architecture NeSy est dans METHODOLOGY, les métriques dans RESULTS, les limites dans CONCLUSION/LIMITATIONS.

**Catégories détectées** : ABSTRACT, INTRODUCTION, BACKGROUND, METHODOLOGY, RESULTS, DISCUSSION, CONCLUSION, LIMITATIONS, DATASETS, ABLATION, IMPLEMENTATION, OTHER.

## Schéma A.5 v3 (changements vs v2)

**Champs supprimés** (DEC-028, décisions de tri, plus pertinents à l'extraction) :
- `role` (NeSy core / hybrid / Non-NeSy baseline / Context-benchmark)
- `i4_strict_assessment` (PASS / FAIL)

**Champs ajoutés / refactorés** :
- `section_1_architecture.symbolic_inference_evidence` — remplace `i4_strict_assessment`. Champ descriptif : où exactement le symbolique opère à l'inférence, dans quelle phase du pipeline. **Pas de verdict**.
- `section_4_explainability.D6_hitl_explainability` — 4 niveaux : `None | Trace | Interactive | Native explainability`
- `section_5_context_D7` — objet structuré `{domain, multilingual, n_languages, dataset_scale, heterogeneity_type}` (remplace `section_5_context` aplati)
- `section_6_knowledge_source_D2` — `D2_knowledge_source_type` + `specific_sources`

**Colonnes manuelles dans l'Excel final** (à remplir à la lecture) :
- `D1_manual`, `D3_manual`, `D4_manual`, `D5_manual` — laissées vides par le script
- `validation_status`, `notes_revision` — pour le suivi de validation par article

## Filtrage par statut (DEC-028)

Le script lit `block_mapping.csv` v3 et applique un filtre par `status` avant d'envoyer les PDFs au LLM. Le matching PDF → entrée CSV se fait par premier auteur + année dans le nom de fichier (ex. `peng_2025_FLORA.pdf` → clé `PS_peng_2025`).

| Statut | Comportement par défaut | Override |
|--------|--------------------------|----------|
| `included` | Traité | — |
| `standby` | Traité | `--exclude-standby` pour skipper SMoG et PRASE |
| `retired` | Skippé | `--include-retired` pour mode audit |
| (filename non matché) | Traité avec warning | — |

## Workflow recommandé

### Étape 1 — Calibration descriptive
```powershell
python extract_slr.py --test 3
```
Trois articles couvrant les trois axes principaux du prompt :
- **Peng et al. 2025 (FLORA, rank 1889)** — NeSy core, logique floue formelle, test de `symbolic_inference_evidence` et de la triple D2/D6/D7
- **He et al. 2021 (BERTMap, rank 286)** — hybride BERT + repair logique, test du champ `symbolic_component` et `D6 = Trace`
- **Li et al. 2022 (BT-11)** — DL-Lite + HITL interactif, test de `D6 = Interactive` et du remplissage `hitl_details`

Vérifie : `symbolic_inference_evidence` (sans verdict), `nesy_type_kautz`, `D6_hitl_explainability` cohérent, `D2_knowledge_source_type` cohérent, `metrics_best_result` correct.

**Si le LLM produit encore des verdicts (« This article fails I4 »)** : ajuster le SYSTEM_PROMPT pour renforcer la consigne descriptive.

### Étape 2 — Extraction complète
```powershell
python extract_slr.py
```
≈ 47 articles traités (29 PS + 18 SV). Coût attendu : voir tableau ci-dessous.

### Étape 3 — Lecture papier + validation
Sur la fiche A.5 papier, tu remplis D1, D3, D4, D5 en confrontant à l'hypothèse xlsx. Tu valides ou corriges les champs LLM (Architecture, D2, D6, D7, métriques, limites).

Dans l'Excel final, tu remplis :
- `validation_status` : `confirmed` / `corrected` / `to_review`
- `notes_revision` : commentaire libre
- `D1_manual`, `D3_manual`, `D4_manual`, `D5_manual` : codage final issu de la lecture

### Étape 4 — Enrichissement (NotebookLM)
Requêtes croisées sur le corpus pour les champs interprétatifs :
- Quels articles partagent la même configuration D1 × D3 ?
- Quels gaps sont récurrents dans les surveys ?

## Coût estimé (47 articles, Opus 4.6)

| Scénario | Coût |
|---|---|
| Test (3 articles) | ~0,50 $ |
| Complet séquentiel (47 articles) | ~7–9 $ |
| Complet batch (−50%) | ~4–5 $ |

## Checkpoints, retry, parsing robuste

Inchangé par rapport à v2 :
- Chaque extraction réussie est sauvegardée individuellement dans `checkpoints/`. Crash à l'article 25/47 → `--resume` skippe automatiquement les 24 premiers.
- Erreurs API (rate limit, timeout) retentées 3× avec backoff exponentiel (5s, 10s, 20s).
- Parsing JSON robuste : markdown fences, trailing commas, texte autour du bloc JSON.
- `id_map_PS.csv` / `id_map_SV.csv` : retrouver quel PDF correspond à quel ID.

## Enrichissement thématique par blocs

Le fichier `block_mapping.csv` v3 associe chaque article à son bloc thématique (B1–B6), son ordre de lecture, et son `status` (`included` / `standby` / `retired`). Le matching automatique se fait par premier auteur + année.

Cinq colonnes ajoutées dans l'Excel final : `block`, `block_label`, `list_order`, `status`, et le rank d'origine. Permet de filtrer / trier par bloc pour l'analyse croisée dans la Discussion ESWA.

## Disclosure ESWA (mise à jour v3)

> Data extraction was assisted by Claude Opus 4.6 (Anthropic) using structured prompts
> aligned with the v3 A.5 / A.6 extraction forms. Articles underwent structural pre-processing
> (automated section detection and labelling) before submission. The LLM operated in a strictly
> descriptive role: it produced narrative A.5 fields and three controlled-vocabulary fields
> (D2 knowledge source type, D6 HITL/explainability level, D7 application context) from the
> 7-dimension coding grid. The four remaining grid dimensions (D1 NeSy infusion level,
> D3 exploitation strategy, D4 linking strategy, D5 symbolic role) — including the publishable
> dimensions D1, D3, D5 — were coded exclusively by the first author at full-text reading time,
> on the paper A.5 form, in confrontation with a first-pass coding hypothesis (xlsx) produced
> from abstracts and quality-assessment notes.
>
> All 47 LLM extractions (29 primary studies + 18 surveys) were manually validated by the
> first author. Each LLM-produced field was marked as confirmed, corrected, or requiring
> review. The I4-strict inclusion criterion was applied at the screening stages (Tri #2 +
> Tri #3 audit, DEC-026) and was not re-applied during extraction. Nine primary studies
> were retired during the post-screening audit; two cases (SMoG, PRASE) were retained as
> documented standby items with rebuttals on file.

## Rôle des trois outils

| Outil | Rôle | Phase |
|---|---|---|
| **Script API** (ce script) | Extraction batch systématique (A.5 narratif + D2/D6/D7) | Extraction |
| **Claude Code** | Calibration des prompts, corrections interactives | Calibration + Corrections |
| **NotebookLM** | Requêtes croisées corpus, champs interprétatifs | Enrichissement |

## Routage automatique PS / SV

Le script route chaque PDF vers le bon prompt selon son dossier source :
- `Extraction/` → prompt A.5 v3 (8 sections + D2/D6/D7 contrôlés)
- `Surveys/` → prompt A.6 (5 sections : scope, taxonomie, findings, gaps, synthèse — inchangé)

L'ordre de traitement est alphabétique par nom de fichier. L'ordre de lecture thématique (blocs B1–B6) n'a pas d'impact sur l'extraction — chaque article est envoyé indépendamment.

## Fichiers livrés (v3)

| Fichier | Description |
|---|---|
| `extract_slr.py` v3 | Script principal (~700 lignes) — DEC-028 |
| `block_mapping.csv` v3 | Mapping + colonne `status` (56 entrées) — DEC-026 |
| `README_extraction.md` v3 | Cette documentation |
| `decisions_log_patch_DEC-026-027-028.md` | À appender au `decisions_log.md` du projet |

## Références méthodologiques

- DEC-026 — Réduction du corpus 38 → 29 PS
- DEC-027 — Adoption de la grille à 7 dimensions D1–D7
- DEC-028 — Refonte v3 du pipeline LLM (descriptif uniquement)
- `schema_codage_v2.docx` — Spécification complète de la grille D1–D7
- `liste_lecture_RSL_v6.md` — Liste de lecture active
