import requests

doi = "10.4230/TGDK.1.1.2"
print("=== BT06: Ji et al. 2022 ===")
print(f"DOI: {doi}")

# 1) Unpaywall
print("\n--- Unpaywall ---")
try:
    r = requests.get(f"https://api.unpaywall.org/v2/{doi}?email=test@example.com", timeout=15)
    if r.status_code == 200:
        data = r.json()
        oa = data.get("best_oa_location", {})
        print(f"  Title: {data.get('title','?')}")
        print(f"  OA URL: {oa.get('url_for_pdf') if oa else 'None'}")
        print(f"  Landing: {oa.get('url_for_landing_page') if oa else 'None'}")
    else:
        print(f"  Status: {r.status_code}")
except Exception as e:
    print(f"  Error: {e}")

# 2) Semantic Scholar
print("\n--- Semantic Scholar ---")
try:
    r = requests.get(f"https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}?fields=title,openAccessPdf,externalIds", timeout=15)
    if r.status_code == 200:
        data = r.json()
        print(f"  Title: {data.get('title','?')}")
        print(f"  OA PDF: {data.get('openAccessPdf')}")
        print(f"  External IDs: {data.get('externalIds')}")
    else:
        print(f"  Status: {r.status_code}")
except Exception as e:
    print(f"  Error: {e}")

# 3) OpenAlex
print("\n--- OpenAlex ---")
try:
    r = requests.get(f"https://api.openalex.org/works/doi:{doi}", timeout=15)
    if r.status_code == 200:
        data = r.json()
        print(f"  Title: {data.get('title','?')}")
        locs = data.get("locations", [])
        for loc in locs:
            pdf_url = loc.get("pdf_url")
            if pdf_url:
                print(f"  PDF URL: {pdf_url}")
    else:
        print(f"  Status: {r.status_code}")
except Exception as e:
    print(f"  Error: {e}")
