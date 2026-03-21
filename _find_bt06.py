import requests, re

r = requests.get('https://drops.dagstuhl.de/entities/document/10.4230/TGDK.1.1.2', 
                 timeout=30, headers={'User-Agent': 'Mozilla/5.0'})
print('Status:', r.status_code)

# Find all href links
links = re.findall(r'href="([^"]+)"', r.text)
for l in links:
    if any(k in l.lower() for k in ['pdf', 'download', 'storage', 'tgdk']):
        print('  ', l)
