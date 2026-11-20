import json, re, os, html

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SITE = os.path.join(os.path.dirname(ROOT), 'safran-site')
os.makedirs(os.path.join(SITE, 'src', 'data'), exist_ok=True)

feed = json.load(open(os.path.join(ROOT, 'raw', 'safrn', 'feed-full.json'), encoding='utf-8'))
pfeed = json.load(open(os.path.join(ROOT, 'raw', 'safrn', 'pages-feed.json'), encoding='utf-8'))

LABELS = {
    'تأشيرات': 'visas', 'بنين': 'benin', 'أمريكا': 'usa', 'بريطانيا': 'uk',
    'شنغن': 'schengen', 'المجر': 'hungary', 'ألبانيا': 'albania', 'جورجيا': 'georgia',
    'اليابان': 'japan', 'روسيا': 'russia', 'الصين': 'china', 'المغرب': 'morocco',
    'أذربيجان': 'azerbaijan', 'دليل شامل': 'guides',
}

def clean(h):
    h = re.sub(r'<h1(\s[^>]*)?>(.*?)</h1>', r'<h2\1>\2</h2>', h, flags=re.S | re.I)
    h = re.sub(r'<script.*?</script>', '', h, flags=re.S | re.I)
    h = re.sub(r'<style.*?</style>', '', h, flags=re.S | re.I)
    h = re.sub(r'<ins[^>]*adsbygoogle.*?</ins>', '', h, flags=re.S | re.I)
    h = re.sub(r'<iframe.*?</iframe>', '', h, flags=re.S | re.I)
    h = re.sub(r'<div[^>]*class="[^"]*separator[^"]*"[^>]*>\s*</div>', '', h)
    h = re.sub(r'\s*class="[^"]*"', '', h)          # astro styles its own
    h = re.sub(r'\s*style="[^"]*"', '', h)
    h = re.sub(r'\s*(width|height)="[^"]*"', '', h)
    h = re.sub(r'<br\s*/?>', '<br>', h)
    h = re.sub(r'\n{3,}', '\n\n', h)
    return h.strip()

def plain(h):
    t = re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', h, flags=re.S | re.I)
    t = re.sub(r'<[^>]+>', ' ', t)
    t = html.unescape(t)
    return re.sub(r'\s+', ' ', t).strip()

posts = []
for i, e in enumerate(feed['feed']['entry'], 1):
    url = [l['href'] for l in e['link'] if l['rel'] == 'alternate'][0]
    m = re.search(r'/(\d{4})/(\d{2})/([^/]+)\.html$', url)
    y, mo, slug = m.group(1), m.group(2), m.group(3)
    body = clean(e['content']['$t'])
    txt = plain(body)
    imgs = re.findall(r'<img[^>]+src="([^"]+)"', body)
    labels = [c['term'] for c in e.get('category', [])]
    posts.append(dict(
        n=i, slug=slug, year=y, month=mo, url=url,
        title=e['title']['$t'],
        published=e['published']['$t'][:10], updated=e['updated']['$t'][:10],
        labels=labels, labelSlugs=[LABELS.get(l, 'other') for l in labels],
        image=imgs[0] if imgs else '',
        excerpt=txt[:180],
        words=len(txt.split()),
        html=body,
    ))

pages = []
for e in pfeed['feed']['entry']:
    url = [l['href'] for l in e['link'] if l['rel'] == 'alternate'][0]
    slug = url.rsplit('/p/', 1)[-1].replace('.html', '')
    pages.append(dict(slug=slug, url=url, title=e['title']['$t'], html=clean(e['content']['$t'])))

json.dump(posts, open(os.path.join(SITE, 'src', 'data', 'posts.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(pages, open(os.path.join(SITE, 'src', 'data', 'blogger-pages.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

index = [dict(t=p['title'], u='/%s/%s/%s.html' % (p['year'], p['month'], p['slug']),
              e=p['excerpt'][:150], l=p['labels']) for p in posts]
json.dump(index, open(os.path.join(SITE, 'public', 'search-index.json') if os.path.isdir(os.path.join(SITE, 'public')) else os.path.join(SITE, 'src', 'data', 'search-index.json'), 'w', encoding='utf-8'), ensure_ascii=False)

from collections import Counter
print('posts', len(posts), 'pages', len(pages))
print('labels', Counter(l for p in posts for l in p['labels']))
print('bodies empty:', [p['n'] for p in posts if not p['html'].strip()])
print('sample word counts:', [p['words'] for p in posts])
print('sample html head:', posts[0]['html'][:300].replace('\n', ' '))
