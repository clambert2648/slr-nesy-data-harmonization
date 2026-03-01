"""
normalize.py
Module partagé de normalisation terminologique pour le pipeline SLR.

Charge le thesaurus VOSviewer (label → replace by) et applique les
substitutions sur tout texte avant TF-IDF et avant les règles regex.

Single-pass replacement : toutes les substitutions sont appliquées
en un seul passage via un regex alternation. Cela évite les cascades
(ex. "neurosymbolic" → "neuro-symbolic ai" → "neuro-symbolic artificial
intelligence") qui dégraderaient le texte normalisé.

Principe :
  - Tous les labels sont combinés en un seul pattern (alternation |)
  - Triés par longueur décroissante (greedy : phrases longues d'abord)
  - Un seul re.sub avec callback → chaque position matchée une seule fois
  - Word boundaries pour éviter les remplacements partiels

Usage :
    from normalize import load_thesaurus, normalize_text

    thesaurus = load_thesaurus('results/tables/vosviewer_thesaurus.txt')
    text_norm = normalize_text("neurosymbolic learning with KGs", thesaurus)
    # → "neuro-symbolic ai learning with knowledge graph"
"""

import re
import os
from typing import Dict


class Thesaurus:
    """
    Thesaurus single-pass : compile un unique pattern regex combinant
    toutes les règles, et applique les substitutions en un seul passage.
    """
    def __init__(self, mapping: Dict[str, str]):
        self.mapping = mapping

        if not mapping:
            self._pattern = None
            return

        # Trier par longueur décroissante pour greedy matching
        sorted_labels = sorted(mapping.keys(), key=len, reverse=True)

        # Construire le pattern : chaque label échappé + word boundaries
        alternatives = []
        for label in sorted_labels:
            escaped = re.escape(label)
            alternatives.append(r'\b' + escaped + r'\b')

        combined = '|'.join(alternatives)
        self._pattern = re.compile(combined, re.IGNORECASE)

    def normalize(self, text: str) -> str:
        """Applique toutes les substitutions en un seul passage."""
        if not text or self._pattern is None:
            return text.lower() if text else ''

        text = text.lower()
        return self._pattern.sub(self._replace_match, text)

    def _replace_match(self, match: re.Match) -> str:
        """Callback pour re.sub : retourne le remplacement correspondant."""
        matched = match.group(0).lower()
        return self.mapping.get(matched, matched)

    def __len__(self):
        return len(self.mapping)

    def __bool__(self):
        return len(self.mapping) > 0


def load_thesaurus(path: str = 'results/tables/vosviewer_thesaurus.txt') -> 'Thesaurus':
    """
    Charge le thesaurus VOSviewer et retourne un objet Thesaurus.

    Format attendu (TSV, header "label\\treplace by") :
        neural-symbolic\\tneuro-symbolic ai
        ai\\tartificial intelligence
    """
    if not os.path.exists(path):
        print(f"⚠️  Thesaurus introuvable : {path} — normalisation désactivée")
        return Thesaurus({})

    mapping = {}
    with open(path, 'r', encoding='utf-8') as f:
        header = f.readline()  # skip header
        for line in f:
            line = line.strip()
            if not line or '\t' not in line:
                continue
            parts = line.split('\t', 1)
            if len(parts) != 2:
                continue
            label, replacement = parts[0].strip().lower(), parts[1].strip().lower()
            if not label or not replacement:
                continue
            mapping[label] = replacement

    thesaurus = Thesaurus(mapping)
    print(f"✓ Thesaurus chargé : {len(thesaurus)} règles de normalisation (single-pass)")
    return thesaurus


def normalize_text(text: str, thesaurus: 'Thesaurus') -> str:
    """
    Applique la normalisation single-pass.
    Retourne le texte normalisé en minuscules.
    """
    if not thesaurus:
        return text.lower() if text else ''
    return thesaurus.normalize(text)


def normalize_series(series, thesaurus: 'Thesaurus'):
    """
    Applique la normalisation sur une pandas Series.
    Retourne une Series normalisée.
    """
    return series.fillna('').astype(str).apply(lambda t: normalize_text(t, thesaurus))


# ── Auto-test ─────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else 'results/tables/vosviewer_thesaurus.txt'
    thesaurus = load_thesaurus(path)

    tests = [
        "Neurosymbolic learning for knowledge graphs completion",
        "An XAI approach to ontology matching with GNNs",
        "Neural-symbolic integration for entity alignment using LLMs",
        "A survey of transformers in NLP",
        "Multi-modal entity alignment with knowledge graph embeddings",
        "Explainability in AI systems for schema matching",
        "A hybrid AI framework combining deep neural networks and ontologies",
    ]
    print("\n── Tests de normalisation (single-pass) ──\n")
    for t in tests:
        norm = normalize_text(t, thesaurus)
        if t.lower() != norm:
            print(f"  AVANT : {t}")
            print(f"  APRÈS : {norm}\n")
        else:
            print(f"  INCHANGÉ : {t}\n")
