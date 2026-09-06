"""Limited HTTP reachability audit; not a semantic source verification."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json, re, urllib.request, urllib.error

base = Path(__file__).resolve().parents[1]
urls = {}
for path in sorted((base / 'chapters').rglob('*.md')):
    for number, line in enumerate(path.read_text().splitlines(), 1):
        for url in re.findall(r'\]\((https?://[^\s)]+)\)', line):
            urls.setdefault(url, []).append(f'{path.relative_to(base)}:{number}')

def check(item):
    url, refs = item
    result = {'url': url, 'references': refs}
    try:
        request = urllib.request.Request(url, headers={'User-Agent': 'BookReferenceCheck/1.0'}, method='GET')
        with urllib.request.urlopen(request, timeout=18) as response:
            response.read(512)
            result.update(status=response.status, final_url=response.url)
    except urllib.error.HTTPError as exc:
        result.update(status=exc.code, final_url=exc.url, error=str(exc))
    except Exception as exc:
        result.update(status=None, error=f'{type(exc).__name__}: {exc}')
    return result

with ThreadPoolExecutor(max_workers=6) as pool:
    results = list(pool.map(check, urls.items()))
out = base / 'working' / 'link-check-C.json'
out.write_text(json.dumps({'date': '2026-09-05', 'scope': 'HTTP GET, at most 512 bytes read, 18 second timeout, 6 concurrent workers; no retry; HTTP status is not factual verification', 'results': results}, ensure_ascii=False, indent=2))
from collections import Counter
print(json.dumps({'count': len(results), 'statuses': dict(Counter(str(x['status']) for x in results)), 'redirected': sum(x.get('final_url', x['url']) != x['url'] for x in results)}, ensure_ascii=False))
for item in results:
    if item['status'] != 200:
        print(item['status'], item['url'], item.get('error', ''))
