import pandas as pd
from fuzzywuzzy import fuzz
import logging
import os
import re

os.makedirs('data/logs', exist_ok=True)
logging.basicConfig(
    filename='data/logs/dedup_log.txt',
    level=logging.INFO,
    format='%(asctime)s — %(message)s'
)

# ─── 1. CHARGEMENT ────────────────────────────────────────────────────────────

def load_scopus(filepath: str, query_id: str) -> pd.DataFrame:
    df = pd.read_csv(filepath, encoding='utf-8-sig')
    return pd.DataFrame({
        'title':     df.get('Title', pd.Series(dtype=str)).fillna('').str.strip(),
        'abstract':  df.get('Abstract', pd.Series(dtype=str)).fillna(''),
        'authors':   df.get('Authors', pd.Series(dtype=str)).fillna(''),
        'year':      df.get('Year', pd.Series(dtype=str)).fillna(''),
        'doi':       df.get('DOI', pd.Series(dtype=str)).fillna('').str.lower().str.strip(),
        'source':    df.get('Source title', pd.Series(dtype=str)).fillna(''),
        'keywords':  df.get('Author Keywords', pd.Series(dtype=str)).fillna(''),
        'doc_type':  df.get('Document Type', pd.Series(dtype=str)).fillna(''),
        'citations': df.get('Cited by', pd.Series(dtype=str)).fillna(''),
        'database':  'Scopus',
        'query':     query_id
    })

def load_ieee(filepath: str, query_id: str) -> pd.DataFrame:
    df = pd.read_csv(filepath, encoding='utf-8-sig')
    return pd.DataFrame({
        'title':     df.get('Document Title', pd.Series(dtype=str)).fillna('').str.strip(),
        'abstract':  df.get('Abstract', pd.Series(dtype=str)).fillna(''),
        'authors':   df.get('Authors', pd.Series(dtype=str)).fillna(''),
        'year':      df.get('Publication Year', pd.Series(dtype=str)).fillna(''),
        'doi':       df.get('DOI', pd.Series(dtype=str)).fillna('').str.lower().str.strip(),
        'source':    df.get('Publication Title', pd.Series(dtype=str)).fillna(''),
        'keywords':  df.get('Author Keywords', pd.Series(dtype=str)).fillna(''),
        'doc_type':  df.get('Document Identifier', pd.Series(dtype=str)).fillna(''),
        'citations': df.get('Article Citation Count', pd.Series(dtype=str)).fillna(''),
        'database':  'IEEE',
        'query':     query_id
    })

def load_arxiv(filepath: str, query_id: str) -> pd.DataFrame:
    """ArXiv est déjà exporté dans le format standard du pipeline."""
    df = pd.read_csv(filepath, encoding='utf-8-sig')
    return pd.DataFrame({
        'title':     df.get('title', pd.Series(dtype=str)).fillna('').str.strip(),
        'abstract':  df.get('abstract', pd.Series(dtype=str)).fillna(''),
        'authors':   df.get('authors', pd.Series(dtype=str)).fillna(''),
        'year':      df.get('year', pd.Series(dtype=str)).fillna(''),
        'doi':       df.get('doi', pd.Series(dtype=str)).fillna('').str.lower().str.strip(),
        'source':    df.get('source', pd.Series(dtype=str)).fillna(''),
        'keywords':  df.get('keywords', pd.Series(dtype=str)).fillna(''),
        'doc_type':  df.get('doc_type', pd.Series(dtype=str)).fillna('Preprint'),
        'citations': df.get('citations', pd.Series(dtype=str)).fillna(''),
        'database':  'ArXiv',
        'query':     query_id
    })

def _parse_bibtex_field(entry: str, field: str) -> str:
    """Extrait la valeur d'un champ BibTeX."""
    pattern = rf'{field}\s*=\s*[{{"](.+?)[}}"]\s*[,}}]'
    match = re.search(pattern, entry, re.IGNORECASE | re.DOTALL)
    if match:
        value = match.group(1).strip()
        value = re.sub(r'[{}]', '', value)
        value = re.sub(r'\s+', ' ', value)
        return value
    return ''

def _parse_bibtex_abstract(entry: str) -> str:
    """Extraction robuste de l'abstract BibTeX (peut contenir des accolades)."""
    match = re.search(r'abstract\s*=\s*\{(.*?)\}\s*[,\n]',
                      entry, re.IGNORECASE | re.DOTALL)
    if match:
        return re.sub(r'\s+', ' ', match.group(1).strip())
    return ''

def load_acm_bib(filepath: str, query_id: str) -> pd.DataFrame:
    """
    Charge un fichier BibTeX ACM et le normalise vers le format standard.
    Exclut automatiquement les @inbook (critère E5 du protocole).
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    entries = re.split(r'\n(?=@)', content)
    entries = [e.strip() for e in entries if e.strip()]

    records = []
    excluded_inbook = 0

    for entry in entries:
        type_match = re.match(r'@(\w+)\s*\{', entry)
        if not type_match:
            continue
        entry_type = type_match.group(1).lower()

        if entry_type == 'inbook':
            excluded_inbook += 1
            continue

        title    = _parse_bibtex_field(entry, 'title')
        abstract = _parse_bibtex_abstract(entry)
        authors  = _parse_bibtex_field(entry, 'author')
        year     = _parse_bibtex_field(entry, 'year')
        doi      = _parse_bibtex_field(entry, 'doi').lower().strip()
        source   = _parse_bibtex_field(entry, 'booktitle') or \
                   _parse_bibtex_field(entry, 'journal')
        keywords = _parse_bibtex_field(entry, 'keywords')
        doc_type = 'Conference Paper' if entry_type == 'inproceedings' \
                   else 'Journal Article'

        records.append({
            'title':     title,
            'abstract':  abstract,
            'authors':   authors,
            'year':      year,
            'doi':       doi,
            'source':    source,
            'keywords':  keywords,
            'doc_type':  doc_type,
            'citations': '',
            'database':  'ACM',
            'query':     query_id
        })

    logging.info(f"[ACM {query_id}] {len(records)} articles chargés "
                 f"({excluded_inbook} @inbook exclus automatiquement)")
    return pd.DataFrame(records)


# ─── 2. UTILITAIRE — FUSION DE LABELS ─────────────────────────────────────────

def merge_labels(a: str, b: str, order: list) -> str:
    parts = set(str(a).split('+') + str(b).split('+'))
    return '+'.join([x for x in order if x in parts])


# ─── 3. DÉDOUBLONNAGE OPTIMISÉ ────────────────────────────────────────────────

def deduplicate(df: pd.DataFrame,
                merge_col: str,
                merge_order: list,
                label: str,
                threshold: int = 95) -> pd.DataFrame:
    """
    Dédoublonnage en deux passes optimisées :
      Passe 1 — DOI exact   : O(n) via groupby
      Passe 2 — Fuzzy titre : O(m²) uniquement sur articles SANS DOI
    """
    df = df.copy().reset_index(drop=True)
    df['title_norm'] = df['title'].fillna('').str.lower().str.strip()
    df['doi_norm']   = df['doi'].fillna('').str.lower().str.strip()

    to_drop       = set()
    merge_updates = {}

    # ── Passe 1 : DOI exact (rapide) ────────────────────────────────────────
    has_doi = df[df['doi_norm'] != ''].copy()
    for doi_val, group in has_doi.groupby('doi_norm'):
        if len(group) > 1:
            idxs = group.index.tolist()
            keep = idxs[0]
            for dup in idxs[1:]:
                current = merge_updates.get(keep, df.loc[keep, merge_col])
                merged  = merge_labels(current, df.loc[dup, merge_col], merge_order)
                merge_updates[keep] = merged
                to_drop.add(dup)
                logging.info(
                    f"[{label}] DOI doublon → '{df.loc[keep,'title']}' "
                    f"| {merge_col} : {merged}"
                )

    doi_removed = len(to_drop)
    logging.info(f"[{label}] Passe 1 (DOI) : {doi_removed} doublons détectés")

    # ── Passe 2 : Fuzzy titre sur articles SANS DOI uniquement ──────────────
    no_doi_mask = (df['doi_norm'] == '') & (~df.index.isin(to_drop))
    no_doi_df   = df[no_doi_mask].reset_index()

    fuzzy_removed = 0
    for i in range(len(no_doi_df)):
        orig_i = no_doi_df.loc[i, 'index']
        if orig_i in to_drop:
            continue
        for j in range(i + 1, len(no_doi_df)):
            orig_j = no_doi_df.loc[j, 'index']
            if orig_j in to_drop:
                continue

            score = fuzz.ratio(
                no_doi_df.loc[i, 'title_norm'],
                no_doi_df.loc[j, 'title_norm']
            )
            yr_i = str(no_doi_df.loc[i, 'year'])
            yr_j = str(no_doi_df.loc[j, 'year'])

            if score >= threshold and (yr_i == yr_j or 'nan' in [yr_i, yr_j]):
                current = merge_updates.get(orig_i, df.loc[orig_i, merge_col])
                merged  = merge_labels(current, df.loc[orig_j, merge_col], merge_order)
                merge_updates[orig_i] = merged
                to_drop.add(orig_j)
                fuzzy_removed += 1
                logging.info(
                    f"[{label}] Fuzzy ({score}%) → "
                    f"'{no_doi_df.loc[i,'title']}' | "
                    f"'{no_doi_df.loc[j,'title']}' | {merge_col} : {merged}"
                )

    logging.info(f"[{label}] Passe 2 (Fuzzy) : {fuzzy_removed} doublons détectés")

    for idx, val in merge_updates.items():
        df.loc[idx, merge_col] = val

    result = df[~df.index.isin(to_drop)].drop(columns=['title_norm', 'doi_norm'])
    logging.info(f"[{label}] {len(df)} → {len(result)} "
                 f"(supprimés : {doi_removed + fuzzy_removed})")
    return result.reset_index(drop=True)


# ─── 4. PRISMA COUNTS ─────────────────────────────────────────────────────────

def _save_prisma_counts(counts: dict, output_dir: str):
    """Sauvegarde les comptages PRISMA dans un CSV traçable."""
    rows = [{'etape': k, 'n': v} for k, v in counts.items()]
    pd.DataFrame(rows).to_csv(
        f'{output_dir}/prisma_counts.csv',
        index=False, encoding='utf-8-sig'
    )
    logging.info("PRISMA counts sauvegardés.")

    # Résumé lisible dans le terminal
    print("\n=== PRISMA COUNTS ===")
    print(f"{'Étape':<40} {'N':>6}")
    print("-" * 47)

    sections = [
        ('BRUTS PAR BASE',        'brut_'),
        ('APRÈS DÉDUP INTRA',     'intra_dedup_'),
        ('INTER-BASES',           'corpus_'),
        ('RÉPARTITION BASES',     'database_'),
        ('RÉPARTITION REQUÊTES',  'query_'),
    ]

    for section_label, prefix in sections:
        section_rows = [(k, v) for k, v in counts.items() if k.startswith(prefix)]
        if section_rows:
            print(f"\n  {section_label}")
            for k, v in section_rows:
                label = k.replace(prefix, '')
                print(f"  {'  ' + label:<38} {v:>6}")


# ─── 5. PIPELINE PRINCIPAL ────────────────────────────────────────────────────

def run_full_deduplication(files: dict, output_dir: str) -> pd.DataFrame:
    """
    files = {
        'scopus': {'R1': 'path/R1_scopus.csv', ...},
        'ieee':   {'R1': 'path/R1_ieee.csv',   ...},
        'acm':    {'R1': 'path/R1_acm.bib',    ...},
        'arxiv':  {'R1': 'path/R1_arxiv.csv',  ...}
    }
    """
    os.makedirs(output_dir, exist_ok=True)
    query_order    = ['R1', 'R2A', 'R2B', 'R3']
    database_order = ['Scopus', 'IEEE', 'ACM', 'ArXiv']

    loaders = {
        'scopus': load_scopus,
        'ieee':   load_ieee,
        'acm':    load_acm_bib,
        'arxiv':  load_arxiv
    }

    all_dedup_frames = []
    prisma = {}

    # ── Étapes 1-4 : dédoublonnage intra par base ───────────────────────────
    for db_name, load_fn in loaders.items():
        if db_name not in files or not files[db_name]:
            continue

        logging.info(f"=== Dédoublonnage intra-{db_name.upper()} ===")

        frames = [
            load_fn(path, qid)
            for qid, path in files[db_name].items()
            if os.path.exists(path)
        ]
        if not frames:
            logging.info(f"[{db_name}] Aucun fichier trouvé, ignoré.")
            continue

        df_raw = pd.concat(frames, ignore_index=True)
        prisma[f'brut_{db_name}'] = len(df_raw)
        logging.info(f"[{db_name}] Brut : {len(df_raw)} articles")

        df_dedup = deduplicate(
            df_raw,
            merge_col='query',
            merge_order=query_order,
            label=f'Intra-{db_name.upper()}'
        )
        df_dedup.to_csv(
            f'{output_dir}/{db_name}_dedup.csv',
            index=False, encoding='utf-8-sig'
        )
        prisma[f'intra_dedup_{db_name}'] = len(df_dedup)
        logging.info(f"[{db_name}] Après dédoublonnage : {len(df_dedup)} articles")
        all_dedup_frames.append(df_dedup)

    # ── Étape finale : dédoublonnage inter-bases ────────────────────────────
    logging.info("=== Dédoublonnage inter-bases ===")
    df_combined = pd.concat(all_dedup_frames, ignore_index=True)
    prisma['corpus_avant_inter'] = len(df_combined)
    logging.info(f"Combiné avant inter-bases : {len(df_combined)} articles")

    df_final = deduplicate(
        df_combined,
        merge_col='database',
        merge_order=database_order,
        label='Inter-bases'
    )
    df_final.to_csv(
        f'{output_dir}/corpus_dedup_final.csv',
        index=False, encoding='utf-8-sig'
    )
    prisma['corpus_final'] = len(df_final)

    # Répartition par base
    for db_combo, count in df_final['database'].value_counts().items():
        prisma[f'database_{db_combo}'] = int(count)

    # Répartition par requête
    for q_combo, count in df_final['query'].value_counts().items():
        prisma[f'query_{q_combo}'] = int(count)

    # Sauvegarder les comptages PRISMA
    _save_prisma_counts(prisma, output_dir)

    logging.info(f"Corpus final : {len(df_final)} articles")
    logging.info("=== FIN ===")

    return df_final