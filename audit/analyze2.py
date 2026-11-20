import json, re, os
from collections import Counter
import html as htmllib

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(BASE))

def read(p):
    with open(p, encoding='utf-8', errors='replace') as f:
        return f.read()

def text_of(frag):
    t = re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', frag, flags=re.S|re.I)
    t = re.sub(r'<br\s*/?>', '\n', t, flags=re.I)
    t = re.sub(r'</(p|h[1-6]|li|div|tr)>', '\n', t, flags=re.I)
    t = re.sub(r'<[^>]+>', ' ', t)
    t = htmllib.unescape(t)
    t = re.sub(r'[ \t]+', ' ', t)
    return '\n'.join(l.strip() for l in t.splitlines() if l.strip())

GOV_STRICT = ('gov.sa','gov.uk','usa.gov','europa.eu','mofa.gov','mfa.gov','embassy','consulate',
              'schengenvisainfo','iatatravelcentre','icao','un.org','gov','mfa','beac','benin')
OFFICIAL = ('mofa.gov.sa', 'evisa.bj', 'travel.state.gov', 'ceac.state.gov', 'gov.uk',
            'home-affairs.ec.europa.eu', 'punetejashtme.gov.al', 'e-visa.al', 'geoconsul.gov.ge',
            'migration.commission.ge', 'saudi.mfa.gov.ge', 'mofa.go.jp', 'emb-japan.go.jp',
            'mid.ru', 'china-embassy.gov.cn', 'en.nia.gov.cn', 'pdf.visaforchina.cn',
            'consulat.ma', 'diplomatie.ma', 'migration.gov.az', 'evisa.gov.az',
            'iatatravelcentre.com')

feed = json.loads(read(os.path.join(ROOT, 'raw', 'safrn', 'feed-full.json')))
pfeed = json.loads(read(os.path.join(ROOT, 'raw', 'safrn', 'pages-feed.json')))

def analyze(htm, live=''):
    links = re.findall(r'<a[^>]+href=["\']([^"\']+)["\']', htm)
    internal = [l for l in links if 'safrnblog.com' in l]
    external = [l for l in links if l.startswith('http') and 'safrnblog.com' not in l]
    doms = Counter(re.sub(r'^https?://(www\.)?', '', l).split('/')[0].lower() for l in external)
    official = [l for l in external if any(g in l.lower() for g in OFFICIAL)]
    imgs = re.findall(r'<img[^>]*>', htm, re.I)
    noalt = [i for i in imgs if not re.search(r'alt=["\'][^"\']+["\']', i, re.I)]
    heads = re.findall(r'<h([1-6])[^>]*>(.*?)</h\1>', htm, re.S | re.I)
    txt = text_of(htm)
    return dict(
        words=len(txt.split()), chars=len(txt),
        h2=sum(1 for lv, _ in heads if lv == '2'),
        h3=sum(1 for lv, _ in heads if lv == '3'),
        tables=len(re.findall(r'<table', htm, re.I)),
        lists=len(re.findall(r'<li', htm, re.I)),
        iframes=len(re.findall(r'<iframe', htm, re.I)),
        internal=len(internal), internal_urls=sorted(set(internal)),
        external=len(external), domains=dict(doms.most_common(8)),
        official=len(official), official_urls=official[:5],
        images=len(imgs), img_noalt=len(noalt),
        has_sources=bool(re.search(r'المصادر|المصدر الرسمي|المراجع', txt)),
        has_review_date=bool(re.search(r'آخر (مراجعة|تحديث)|تم التحديث|راجع(نا|ه) في', txt)),
        has_disclaimer=bool(re.search(r'قد تتغير|قابل للتغيير|تحقق من الموقع الرسمي', txt)),
        has_cta=bool(re.search(r'احجز|عروض|استفسر|تواصل معنا', txt)),
        company_claim='سفران للسياحة' in htm,
        text=txt,
    )

rows = []
for idx, e in enumerate(feed['feed']['entry'], 1):
    url = [l['href'] for l in e['link'] if l['rel'] == 'alternate'][0]
    a = analyze(e['content']['$t'])
    live = read(os.path.join(BASE, 'posts', '%02d.html' % idx))
    sch = ''.join(re.findall(r'<script type=.application/ld\+json.>(.*?)</script>', live, re.S))
    m = re.search(r'"author"\s*:\s*\{[^}]*?"name"\s*:\s*"([^"]*)"', sch)
    a.pop('text')
    a.update(dict(
        n=idx, url=url, slug=url.rstrip('/').split('/')[-1].replace('.html', ''),
        title=e['title']['$t'], labels=[c['term'] for c in e.get('category', [])],
        published=e['published']['$t'][:10], updated=e['updated']['$t'][:10],
        ads=live.count('adsbygoogle'), author=m.group(1) if m else '',
        faq='"FAQPage"' in sch, postingschema='"BlogPosting"' in sch,
        og_image=bool(re.search(r"property='og:image'", live)),
    ))
    rows.append(a)

dups = []
def sh(t, k=8):
    w = re.findall(r'\w+', t)
    return {' '.join(w[i:i + k]) for i in range(max(0, len(w) - k))}
for e in feed['feed']['entry']:
    pass
# recompute with texts kept separately
texts = {i: analyze(e['content']['$t'])['text'] for i, e in enumerate(feed['feed']['entry'], 1)}
for i in texts:
    for j in texts:
        if j <= i: continue
        A, B = sh(texts[i]), sh(texts[j])
        if not A or not B: continue
        jac = len(A & B) / len(A | B)
        if jac > 0.05:
            dups.append([round(jac * 100, 1), i, j])

pages = []
for pf in pfeed['feed']['entry']:
    url = [l['href'] for l in pf['link'] if l['rel'] == 'alternate'][0]
    a = analyze(pf['content']['$t'])
    a['text'] = a['text'][:900]
    a['title'] = pf['title']['$t']; a['url'] = url
    a['updated'] = pf['updated']['$t'][:10]
    pages.append(a)

# --- classification rules (documented, deterministic) ---
def status(r):
    reasons = []
    if r['words'] < 600: reasons.append('أقل من 600 كلمة')
    if r['official'] == 0: reasons.append('لا مصدر رسمي خارجي')
    if r['internal'] < 3: reasons.append('روابط داخلية < 3')
    if r['images'] == 0: reasons.append('بلا صور')
    score = 0
    score += 2 if r['words'] >= 900 else 0
    score += 2 if r['official'] >= 3 else 0
    score += 1 if r['internal'] >= 5 else 0
    score += 1 if r['images'] >= 1 else 0
    score += 1 if r['has_sources'] else 0
    score += 1 if r['has_review_date'] else 0
    if r['official'] == 0 and r['words'] < 700:
        st = 'HOLD'
    elif score >= 6:
        st = 'KEEP'
    elif score >= 3:
        st = 'IMPROVE'
    else:
        st = 'REVIEW'
    return st, score, reasons

for r in rows:
    r['status'], r['score'], r['reasons'] = status(r)

json.dump(dict(posts=rows, duplicates=dups, pages=pages),
          open(os.path.join(BASE, 'audit-data.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)

print('%-3s %-5s %-16s %5s %4s %4s %4s %3s %3s %3s %3s %-8s %s' % (
    'n','date','status','words','h2','int','ext','off','img','tbl','ads','author','title'))
for r in rows:
    print('%-3d %-5s %-16s %5d %4d %4d %4d %3d %3d %3d %3d %-8s %s' % (
        r['n'], r['updated'][5:], r['status'], r['words'], r['h2'], r['internal'], r['external'],
        r['official'], r['images'], r['tables'], r['ads'], r['author'], r['title'][:70]))
print('\nlabels:', Counter(l for r in rows for l in r['labels']))
print('\nduplicates >5%:', dups)
print('\nPAGES')
for p in pages:
    print(' -', p['title'], '|', p['url'].split('/p/')[-1], '| words', p['words'], '| official', p['official'], '| internal', p['internal'], '| ads', p.get('ads', '-'))
    print('   text:', p['text'][:300].replace('\n', ' | '))
