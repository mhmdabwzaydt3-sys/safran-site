import json, os, re, subprocess, html

pr = json.load(open(os.path.join('Hermes-Shared', 'safran-pr1', 'src', 'data', 'posts.json'), encoding='utf-8'))
urls = []
for p in pr:
    img = p.get('image') or ''
    if img:
        urls.append((p['n'], img))

def head(u):
    r = subprocess.run(['curl', '-sSI', '-A', 'Mozilla/5.0 Chrome/131', '--max-time', '20', u],
                       capture_output=True, text=True)
    txt = r.stdout
    code = re.search(r'HTTP/[\d.]+ (\d{3})', txt)
    ctype = re.search(r'(?im)^content-type:\s*([^\r\n]+)', txt)
    clen = re.search(r'(?im)^content-length:\s*(\d+)', txt)
    return (code.group(1) if code else '???', ctype.group(1).strip() if ctype else '-',
            int(clen.group(1)) if clen else 0)

print('%-3s %-4s %-24s %10s %s' % ('n', 'http', 'type', 'bytes', 'host'))
total = 0
hosts = {}
for n, u in urls:
    code, ctype, size = head(u)
    total += size
    h = re.sub(r'^https?://([^/]+).*', r'\1', u)
    hosts[h] = hosts.get(h, 0) + 1
    print('%-3d %-4s %-24s %10s %s' % (n, code, ctype[:24], size, h))
print('\nimages:', len(urls), '| total bytes:', total, '(%.2f MB)' % (total / 1e6))
print('hosts:', hosts)

txt = html.unescape(re.sub(r'<[^>]+>', ' ', pr[0]['html']))
print('\n=== article 1: ETIAS sentences')
for m in re.finditer(r'[^.]*ETIAS[^.]*\.', txt):
    print('  -', re.sub(r'\s+', ' ', m.group(0)).strip()[:220])

a19 = html.unescape(re.sub(r'<[^>]+>', ' ', [x for x in pr if x['n'] == 19][0]['html']))
print('\n=== article 19: fee sentences')
for m in re.finditer(r'[^.]*(?:يورو|رسوم|دولار)[^.]*\.', a19):
    s = re.sub(r'\s+', ' ', m.group(0)).strip()
    if s:
        print('  -', s[:200])
