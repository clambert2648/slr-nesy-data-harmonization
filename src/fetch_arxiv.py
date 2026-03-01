import arxiv
import pandas as pd
import time
import os

QUERIES = {
    'R1': '(abs:"schema matching" OR abs:"ontology alignment" OR abs:"data harmonization" OR abs:"semantic integration") AND (abs:"knowledge graph" OR abs:"ontology" OR abs:embedding OR abs:transformer OR abs:"language model")',
    
    'R2A': '(abs:"neuro-symbolic" OR abs:neurosymbolic OR abs:"neural-symbolic") AND (abs:"knowledge graph" OR abs:ontology) AND (abs:matching OR abs:alignment OR abs:explainab)',
    
    'R2B': '(ti:hybrid OR ti:integration OR ti:fusion) AND (abs:"knowledge graph" OR abs:ontology) AND (abs:"neural network" OR abs:transformer OR abs:embedding) AND (abs:matching OR abs:alignment)',
    
    'R3':  '(abs:"data harmonization" OR abs:"semantic matching" OR abs:"variable mapping") AND (abs:"monitoring and evaluation" OR abs:multilingual OR abs:"international development") AND (abs:"machine learning" OR abs:NLP OR abs:transformer)'
}

def fetch_arxiv(query_id: str, query: str, 
                output_dir: str, max_results: int = 200) -> pd.DataFrame:
    
    client = arxiv.Client()
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance
    )
    
    records = []
    for result in client.results(search):
        # Filtre année 2020-2025
        year = result.published.year
        if year < 2020 or year > 2025:
            continue
        records.append({
            'title':    result.title,
            'abstract': result.summary.replace('\n', ' '),
            'authors':  '; '.join(str(a) for a in result.authors),
            'year':     year,
            'doi':      result.doi or '',
            'source':   'arXiv:' + result.entry_id.split('/')[-1],
            'keywords': '',
            'doc_type': 'Preprint',
            'citations': '',
            'database': 'ArXiv',
            'query':    query_id
        })
        time.sleep(0.1)  # respecter le rate limit
    
    df = pd.DataFrame(records)
    os.makedirs(output_dir, exist_ok=True)
    df.to_csv(f'{output_dir}/{query_id}_arxiv.csv', 
              index=False, encoding='utf-8-sig')
    print(f"[{query_id}] ArXiv : {len(df)} articles exportés")
    return df

def fetch_all_arxiv(output_dir: str = 'data/raw/arxiv') -> None:
    for qid, query in QUERIES.items():
        fetch_arxiv(qid, query, output_dir)