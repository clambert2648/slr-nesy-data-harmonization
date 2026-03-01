# run_deduplication.py
import os
import pandas as pd
from src.deduplication import run_full_deduplication

files = {
    'scopus': {
        'R1':  'data/raw/scopus/R1_scopus.csv',
        'R2A': 'data/raw/scopus/R2A_scopus.csv',
        'R2B': 'data/raw/scopus/R2B_scopus.csv',
        'R3':  'data/raw/scopus/R3_scopus.csv',
    },
    'ieee': {
        'R1':  'data/raw/ieee/R1_ieee.csv',
        'R2A': 'data/raw/ieee/R2A_ieee.csv',
        'R2B': 'data/raw/ieee/R2B_ieee.csv',
        'R3':  'data/raw/ieee/R3_ieee.csv',
    },
    'acm': {
        'R1':  'data/raw/acm/R1_acm.bib',
        'R2A': 'data/raw/acm/R2A_acm.bib',
        'R2B': 'data/raw/acm/R2B_acm.bib',
        'R3':  'data/raw/acm/R3_acm.bib',
    },
    'arxiv': {
        'R1':  'data/raw/arxiv/R1_arxiv.csv',
        'R2A': 'data/raw/arxiv/R2A_arxiv.csv',
        'R2B': 'data/raw/arxiv/R2B_arxiv.csv',
        'R3':  'data/raw/arxiv/R3_arxiv.csv',
    }
}

df = run_full_deduplication(files, output_dir='data/processed')

# ── Outputs ──────────────────────────────────────────────────────────────────
import os
os.makedirs('results/tables', exist_ok=True)

# PRISMA counts — CSV pour le pipeline
prisma = pd.read_csv('data/processed/prisma_counts.csv')

# Excel pour le mémoire et le directeur
prisma.to_excel('results/tables/prisma_counts.xlsx', index=False)

print("\n✓ data/processed/corpus_dedup_final.csv  → prêt pour le screening")
print("✓ data/processed/prisma_counts.csv        → comptages PRISMA (pipeline)")
print("✓ results/tables/prisma_counts.xlsx       → tableau PRISMA (mémoire)")
print(f"\nTotal articles à screener : {len(df)}")