import pandas as pd

for f in ['data/processed/snowballing.csv', 'data/processed/articles_inclus.csv', 
          'data/processed/articles_surveys.csv', 'data/processed/corpus_scored.csv']:
    try:
        d = pd.read_csv(f)
        col = 'authors' if 'authors' in d.columns else 'Authors' if 'Authors' in d.columns else None
        if not col:
            continue
        m = d[d[col].str.contains('Peng', case=False, na=False)]
        if not m.empty:
            print(f"\n=== {f} ({len(m)} matches) ===")
            for _, r in m.iterrows():
                rid = r.get('id', r.get('rank', r.get('Rank', '?')))
                title = str(r.get('title', r.get('Title', '?')))[:70]
                decision = r.get('decision_snowball', r.get('decision', r.get('tri1', '')))
                survey = r.get('is_survey', '')
                print(f"  {rid} | {r[col][:50]} | {title} | {decision} | survey={survey}")
    except Exception as e:
        print(f"Error {f}: {e}")
