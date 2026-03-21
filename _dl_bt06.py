import requests

urls = [
    "https://drops.dagstuhl.de/storage/documents/00001/TGDK-vol1-issue1-article2/TGDK.1.1.2.pdf",
    "https://drops.dagstuhl.de/opus/volltexte/2023/19087/pdf/TGDK-vol1-issue1-article2.pdf",
    "https://doi.org/10.4230/TGDK.1.1.2",
]

for i, url in enumerate(urls):
    print(f"\nAttempt {i+1}: {url}")
    try:
        r = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"},
                         allow_redirects=True, stream=True)
        ct = r.headers.get("content-type", "")
        print(f"  Status: {r.status_code}, Content-Type: {ct}")
        print(f"  Final URL: {r.url}")
        
        if r.status_code == 200 and "pdf" in ct.lower():
            data = r.content
            print(f"  Size: {len(data)//1024} KB, starts with PDF: {data[:4] == b'%PDF'}")
            if data[:4] == b"%PDF":
                with open(r"data\fulltext\Snowballing\BT06_Ji_2022.pdf", "wb") as f:
                    f.write(data)
                print("  -> SAVED")
                break
        elif r.status_code == 200:
            # HTML page - look for PDF links
            import re
            pdfs = re.findall(r'href="([^"]*\.pdf)"', r.text[:5000])
            print(f"  PDF links in page: {pdfs[:5]}")
    except Exception as e:
        print(f"  Error: {e}")

print("\nDone.")
