"""
download_arxiv.py
-----------------
Télécharge les PDFs arXiv des articles inclus dans le corpus SLR.
Convention de nommage : {rank:03d}_{PremierAuteur}_{Année}.pdf

Usage :
    python download_arxiv.py --csv articles_inclus.csv --output data/fulltext/
    python download_arxiv.py --csv articles_inclus.csv --output data/fulltext/ --delay 3

Dépendances :
    pip install requests pandas

Note : arXiv demande une pause entre les requêtes (par défaut 2s).
"""

import argparse
import os
import re
import time
import unicodedata
import pandas as pd
import requests


# ── Paramètres ────────────────────────────────────────────────────────────────

DEFAULT_DELAY = 2        # secondes entre chaque téléchargement (politesse arXiv)
ARXIV_PDF_URL = "https://arxiv.org/pdf/{arxiv_id}"
CHUNK_SIZE    = 8192


# ── Utilitaires ───────────────────────────────────────────────────────────────

def extract_arxiv_id(source: str) -> str | None:
    """
    Extrait l'identifiant arXiv depuis la colonne source.
    Exemples acceptés :
      arXiv:2410.04153v2  →  2410.04153v2
      arXiv:2003.05370v1  →  2003.05370v1
    """
    match = re.search(r'arXiv:(\S+)', source, re.IGNORECASE)
    if match:
        return match.group(1)
    # Fallback : format numérique seul (XXXX.XXXXXvN)
    match = re.search(r'(\d{4}\.\d{4,5}(?:v\d+)?)', source)
    return match.group(1) if match else None


def clean_name(text: str) -> str:
    """
    Normalise un nom pour usage dans un nom de fichier.
    - Supprime les accents
    - Garde lettres et chiffres seulement
    - Capitalise la première lettre
    """
    nfkd = unicodedata.normalize('NFKD', text)
    ascii_str = nfkd.encode('ascii', 'ignore').decode('ascii')
    clean = re.sub(r'[^a-zA-Z0-9]', '', ascii_str)
    return clean.capitalize() if clean else 'Unknown'


def first_author_lastname(authors: str) -> str:
    """
    Extrait le nom de famille du premier auteur.
    Format attendu : 'Prénom Nom; Prénom Nom; ...'
    """
    if not authors:
        return 'Unknown'
    first = authors.split(';')[0].strip()
    parts = first.split()
    lastname = parts[-1] if parts else first
    return clean_name(lastname)


def build_filename(rank: int, authors: str, year: str | int) -> str:
    """
    Construit le nom de fichier selon la convention :
    {rank:03d}_{PremierAuteurNom}_{Année}.pdf
    """
    author = first_author_lastname(authors)
    return f"{rank:03d}_{author}_{year}.pdf"


def download_pdf(arxiv_id: str, filepath: str, delay: float = DEFAULT_DELAY) -> bool:
    """
    Télécharge un PDF arXiv et le sauvegarde.
    Retourne True si succès, False sinon.
    """
    url = ARXIV_PDF_URL.format(arxiv_id=arxiv_id)
    try:
        response = requests.get(url, stream=True, timeout=30, headers={
            'User-Agent': 'SLR-NeSy-Thesis/1.0 (academic research; contact: student@uqo.ca)'
        })
        if response.status_code == 200:
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(CHUNK_SIZE):
                    f.write(chunk)
            time.sleep(delay)
            return True
        else:
            print(f"    ✗ HTTP {response.status_code}")
            return False
    except requests.RequestException as e:
        print(f"    ✗ Erreur réseau : {e}")
        return False


# ── Programme principal ────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Téléchargement batch PDFs arXiv — SLR NeSy")
    parser.add_argument('--csv',    required=True,  help="Chemin vers articles_inclus.csv")
    parser.add_argument('--output', required=True,  help="Dossier de destination des PDFs")
    parser.add_argument('--delay',  type=float, default=DEFAULT_DELAY,
                        help=f"Délai entre requêtes en secondes (défaut : {DEFAULT_DELAY})")
    parser.add_argument('--dry-run', action='store_true',
                        help="Affiche ce qui serait téléchargé sans télécharger")
    args = parser.parse_args()

    # Créer le dossier de sortie
    os.makedirs(args.output, exist_ok=True)

    # Charger le CSV
    df = pd.read_csv(args.csv, keep_default_na=False)

    # Filtrer les articles arXiv
    arxiv_df = df[df['database'].str.lower() == 'arxiv'].copy()
    print(f"Articles arXiv identifiés : {len(arxiv_df)}")
    print(f"Dossier de sortie         : {args.output}")
    print(f"Délai entre requêtes      : {args.delay}s")
    if args.dry_run:
        print("MODE DRY-RUN — aucun téléchargement effectué\n")
    print()

    success, skipped, failed = [], [], []

    for _, row in arxiv_df.sort_values('rank').iterrows():
        rank    = int(row['rank'])
        source  = row['source']
        authors = row.get('authors', '')
        year    = row.get('year', 'XXXX')
        title   = row['title'][:55]

        arxiv_id = extract_arxiv_id(source)
        if not arxiv_id:
            print(f"  [{rank:04d}] ✗ ID arXiv non trouvé dans '{source}'")
            failed.append(rank)
            continue

        filename = build_filename(rank, authors, year)
        filepath = os.path.join(args.output, filename)

        # Sauter si déjà téléchargé
        if os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
            print(f"  [{rank:04d}] ⏭  Déjà présent → {filename}")
            skipped.append(rank)
            continue

        print(f"  [{rank:04d}] ↓  {filename}")
        print(f"         {title}...")

        if args.dry_run:
            success.append(rank)
            continue

        ok = download_pdf(arxiv_id, filepath, args.delay)
        if ok:
            size_kb = os.path.getsize(filepath) / 1024
            print(f"         ✓ {size_kb:.0f} KB")
            success.append(rank)
        else:
            failed.append(rank)

    # Résumé
    print()
    print("=" * 50)
    print(f"Téléchargés : {len(success)}")
    print(f"Déjà présents (ignorés) : {len(skipped)}")
    print(f"Échecs : {len(failed)}")
    if failed:
        print(f"  Ranks en échec : {failed}")
    print("=" * 50)


if __name__ == '__main__':
    main()
