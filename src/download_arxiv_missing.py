"""
download_arxiv_missing.py
--------------------------
Télécharge les PDFs arXiv **manquants** pour les articles inclus au tri 2.
Réutilise la même convention que download_arxiv.py :
  {rank:04d}_{PremierAuteur}_{Année}.pdf

Sélection automatique : decision == include + pdf_filename vide + source arXiv.

Usage :
    python src/download_arxiv_missing.py --output data/fulltext/
    python src/download_arxiv_missing.py --output data/fulltext/ --dry-run
"""

import argparse
import os
import re
import sys
import time
import unicodedata

import pandas as pd
import requests


# ── Paramètres ────────────────────────────────────────────────────────────────

DEFAULT_DELAY = 2
ARXIV_PDF_URL = "https://arxiv.org/pdf/{arxiv_id}"
CHUNK_SIZE    = 8192
CORPUS_PATH   = "data/processed/corpus_scored.csv"


# ── Utilitaires (repris de download_arxiv.py) ─────────────────────────────────

def extract_arxiv_id(source: str, doi: str = "") -> str | None:
    """Extrait l'identifiant arXiv depuis source ou doi."""
    # 1) source = "arXiv:2410.04153v2"
    m = re.search(r'arXiv:(\S+)', str(source), re.IGNORECASE)
    if m:
        return m.group(1)
    # 2) doi = "10.48550/arXiv.2510.20467"
    m = re.search(r'arXiv\.(\d{4}\.\d{4,5}(?:v\d+)?)', str(doi), re.IGNORECASE)
    if m:
        return m.group(1)
    # 3) Fallback numérique
    m = re.search(r'(\d{4}\.\d{4,5}(?:v\d+)?)', str(source))
    return m.group(1) if m else None


def clean_name(text: str) -> str:
    nfkd = unicodedata.normalize('NFKD', text)
    ascii_str = nfkd.encode('ascii', 'ignore').decode('ascii')
    clean = re.sub(r'[^a-zA-Z0-9]', '', ascii_str)
    return clean.capitalize() if clean else 'Unknown'


def first_author_lastname(authors: str) -> str:
    """Extrait le nom de famille du premier auteur.
    Gère 'Prénom Nom; ...' et 'Nom, I.; ...'"""
    if not authors or str(authors) == 'nan':
        return 'Unknown'
    first = str(authors).split(';')[0].strip()
    if ',' in first:
        # Format "Nom, Initiale"
        lastname = first.split(',')[0].strip()
    else:
        # Format "Prénom Nom"
        parts = first.split()
        lastname = parts[-1] if parts else first
    return clean_name(lastname)


def build_filename(rank: int, authors: str, year) -> str:
    author = first_author_lastname(str(authors))
    r = int(rank)
    tag = f"{r:03d}" if r < 1000 else str(r)
    return f"{tag}_{author}_{year}.pdf"


def download_pdf(arxiv_id: str, filepath: str, delay: float) -> bool:
    url = ARXIV_PDF_URL.format(arxiv_id=arxiv_id)
    try:
        resp = requests.get(url, stream=True, timeout=30, headers={
            'User-Agent': 'SLR-NeSy-Thesis/1.0 (academic research; contact: student@uqo.ca)'
        })
        if resp.status_code == 200 and 'pdf' in resp.headers.get('content-type', '').lower():
            with open(filepath, 'wb') as f:
                for chunk in resp.iter_content(CHUNK_SIZE):
                    f.write(chunk)
            time.sleep(delay)
            return True
        else:
            print(f"    ✗ HTTP {resp.status_code} (content-type: {resp.headers.get('content-type','')})")
            return False
    except requests.RequestException as e:
        print(f"    ✗ Erreur réseau : {e}")
        return False


# ── Programme principal ────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Téléchargement des PDFs arXiv manquants pour le tri 2")
    parser.add_argument('--output', required=True,
                        help="Dossier de destination des PDFs")
    parser.add_argument('--delay', type=float, default=DEFAULT_DELAY,
                        help=f"Délai entre requêtes (défaut : {DEFAULT_DELAY}s)")
    parser.add_argument('--dry-run', action='store_true',
                        help="Affiche ce qui serait téléchargé sans télécharger")
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    # Charger le corpus et filtrer
    df = pd.read_csv(CORPUS_PATH)
    inc = df[df['decision'] == 'include'].copy()

    # Articles sans pdf_filename
    no_pdf = inc[
        inc['pdf_filename'].isna()
        | (inc['pdf_filename'].astype(str).str.strip() == '')
        | (inc['pdf_filename'].astype(str) == 'nan')
    ]

    # Filtrer ceux provenant d'arXiv (database ou doi)
    is_arxiv = (
        no_pdf['database'].str.contains('arxiv', case=False, na=False)
        | no_pdf['doi'].astype(str).str.contains('arxiv', case=False, na=False)
    )
    targets = no_pdf[is_arxiv].copy()

    print(f"Articles inclus          : {len(inc)}")
    print(f"Sans PDF                 : {len(no_pdf)}")
    print(f"arXiv à télécharger      : {len(targets)}")
    print(f"Dossier de sortie        : {args.output}")
    print(f"Délai entre requêtes     : {args.delay}s")
    if args.dry_run:
        print("MODE DRY-RUN — aucun téléchargement\n")
    print()

    success, skipped, failed = [], [], []

    for idx, row in targets.iterrows():
        rank    = int(row['rank']) if pd.notna(row.get('rank')) else idx
        source  = str(row.get('source', ''))
        doi     = str(row.get('doi', ''))
        authors = str(row.get('authors', ''))
        year    = row.get('year', 'XXXX')
        title   = str(row['title'])[:60]

        arxiv_id = extract_arxiv_id(source, doi)
        if not arxiv_id:
            print(f"  [{idx:04d}] ✗ ID arXiv introuvable | {title}")
            failed.append(idx)
            continue

        filename = build_filename(rank, authors, year)
        filepath = os.path.join(args.output, filename)

        # Déjà téléchargé ?
        if os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
            print(f"  [{idx:04d}] ⏭  Déjà présent → {filename}")
            skipped.append(idx)
            continue

        print(f"  [{idx:04d}] ↓  {filename}  (arXiv:{arxiv_id})")
        print(f"         {title}...")

        if args.dry_run:
            success.append(idx)
            continue

        ok = download_pdf(arxiv_id, filepath, args.delay)
        if ok:
            size_kb = os.path.getsize(filepath) / 1024
            print(f"         ✓ {size_kb:.0f} KB")
            success.append(idx)

            # Mettre à jour pdf_filename dans le DataFrame original
            df.at[idx, 'pdf_filename'] = filename
        else:
            failed.append(idx)

    # Sauvegarder le corpus mis à jour (si pas dry-run et au moins 1 succès)
    if not args.dry_run and success:
        out_path = CORPUS_PATH + ".new"
        df.to_csv(out_path, index=False)
        print(f"\n  corpus_scored.csv.new sauvegardé ({len(success)} pdf_filename mis à jour)")

    # Résumé
    print()
    print("=" * 50)
    print(f"Téléchargés     : {len(success)}")
    print(f"Déjà présents   : {len(skipped)}")
    print(f"Échecs          : {len(failed)}")
    if failed:
        print(f"  Index en échec : {failed}")
    print("=" * 50)


if __name__ == '__main__':
    main()
