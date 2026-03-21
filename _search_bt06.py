import requests

# Search for the real Ji et al. 2022 paper
print("=== Searching for Ji et al. - Embedding-Based Approach to Repairing OWL Ontologies ===\n")

# OpenAlex search
print("--- OpenAlex ---")
try:
    r = requests.get("https://api.openalex.org/works", 
                     params={"search": "embedding-based approach repairing OWL ontologies", "per_page": 5},
                     timeout=15)
    if r.status_code == 200:
        for w in r.json().get("results", []):
            print(f"  Title: {w['title']}")
            print(f"  DOI: {w.get('doi','?')}")
            print(f"  Year: {w.get('publication_year','?')}")
            authors = [a.get("author",{}).get("display_name","?") for a in w.get("authorships",[])]
            print(f"  Authors: {', '.join(authors[:4])}")
            locs = w.get("locations", [])
            for loc in locs:
                pdf = loc.get("pdf_url")
                if pdf:
                    print(f"  PDF: {pdf}")
            print()
except Exception as e:
    print(f"  Error: {e}")

# Semantic Scholar search
print("--- Semantic Scholar ---")
try:
    r = requests.get("https://api.semanticscholar.org/graph/v1/paper/search",
                     params={"query": "embedding-based approach repairing OWL ontologies Ji", "limit": 5,
                             "fields": "title,year,authors,openAccessPdf,externalIds"},
                     timeout=15)
    if r.status_code == 200:
        for p in r.json().get("data", []):
            print(f"  Title: {p.get('title')}")
            print(f"  Year: {p.get('year')}")
            authors = [a.get("name","?") for a in p.get("authors",[])]
            print(f"  Authors: {', '.join(authors[:4])}")
            print(f"  OA PDF: {p.get('openAccessPdf')}")
            print(f"  IDs: {p.get('externalIds')}")
            print()
    else:
        print(f"  Status: {r.status_code}")
except Exception as e:
    print(f"  Error: {e}")
