import pandas as pd
import os
import re

pdf_dir = 'data/fulltext/Screening_1_included'
df = pd.read_csv('data/processed/articles_inclus.csv', keep_default_na=False)

# Get all PDFs in the folder
pdfs = os.listdir(pdf_dir)
pdf_files = [f for f in pdfs if f.lower().endswith('.pdf')]

# Build rank->filename map from PDFs
pdf_by_rank = {}
for f in pdf_files:
    m = re.match(r'^(\d+)', f)
    if m:
        rank = int(m.group(1))
        pdf_by_rank[rank] = f

# ACM articles
acm = df[df['database'].str.contains('ACM', case=False, na=False)]
print(f"Articles ACM: {len(acm)}")

# Check each ACM article
renamed = []
updated = []
missing = []
already_ok = []
bad_names = []

for idx, row in acm.iterrows():
    rank = row['rank']
    current_pdf = str(row['pdf_filename']).strip()
    
    # Build expected filename
    authors = str(row['authors'])
    # Get first author last name
    first_author = authors.split(';')[0].strip()
    # Handle "Last, First" or "First Last" formats
    if ',' in first_author:
        last_name = first_author.split(',')[0].strip()
    else:
        parts = first_author.split()
        last_name = parts[-1] if parts else 'Unknown'
    # Clean last name
    last_name = re.sub(r'[^\w]', '', last_name)
    year = row['year']
    rank_str = f"{rank:03d}" if rank < 1000 else str(rank)
    expected = f"{rank_str}_{last_name}_{year}.pdf"
    
    if rank in pdf_by_rank:
        actual = pdf_by_rank[rank]
        if actual == expected:
            if current_pdf == expected:
                already_ok.append(rank)
            else:
                df.at[idx, 'pdf_filename'] = expected
                df.at[idx, 'accessible'] = 'oui'
                updated.append((rank, expected))
        else:
            # Need to rename
            old_path = os.path.join(pdf_dir, actual)
            new_path = os.path.join(pdf_dir, expected)
            # Check for .pdf.pdf
            if actual.endswith('.pdf.pdf'):
                bad_names.append((rank, actual, expected))
            elif actual != expected:
                bad_names.append((rank, actual, expected))
            # Rename
            if not os.path.exists(new_path):
                os.rename(old_path, new_path)
                print(f"  Renommé: {actual} -> {expected}")
            elif old_path != new_path:
                # Target already exists, remove duplicate
                os.remove(old_path)
                print(f"  Doublon supprimé: {actual} (garder {expected})")
            df.at[idx, 'pdf_filename'] = expected
            df.at[idx, 'accessible'] = 'oui'
            renamed.append((rank, actual, expected))
    else:
        missing.append((rank, expected, str(row['title'])[:70], str(row['doi'])))

print(f"\nRésumé ACM:")
print(f"  Déjà OK: {len(already_ok)}")
print(f"  CSV mis à jour (nom correct): {len(updated)}")
print(f"  Renommés: {len(renamed)}")
print(f"  MANQUANTS: {len(missing)}")

if renamed:
    print(f"\nDétails renommages:")
    for rank, old, new in renamed:
        print(f"  rank {rank}: {old} -> {new}")

if missing:
    print(f"\nArticles ACM encore manquants:")
    for rank, expected, title, doi in missing:
        print(f"  rank {rank}: {expected}")
        print(f"    Titre: {title}...")
        print(f"    DOI: {doi}")

df.to_csv('data/processed/articles_inclus.csv', index=False)
print("\nSauvegardé.")
