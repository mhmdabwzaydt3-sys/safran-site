"""Generate docs/ARTICLE-INDEX.csv: Article ID -> source file -> live URL -> editorial state.

The reviewer asked for a mapping between every article ID, its URL and the actual content
file, so the published text can be diffed against the approved text.
"""
import json, csv, os, re, html

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
posts = json.load(open(os.path.join(SITE, 'src', 'data', 'posts.json'), encoding='utf-8'))
out = os.path.join(SITE, 'docs', 'ARTICLE-INDEX.csv')

rows = []
for p in posts:
    text = re.sub(r'<[^>]+>', ' ', p['html'])
    text = html.unescape(text)
    words = len(text.split())
    rows.append({
        'article_id': '%02d' % p['n'],
        'status': p['status'],
        'url_path': '/%s/%s/%s.html' % (p['year'], p['month'], p['slug']),
        'title': p['title'],
        'labels': ' / '.join(p['labels']),
        'published': p['published'],
        'updated': p['updated'],
        'words': words,
        'content_field': 'src/data/posts.json#n=%d.html' % p['n'],
        'live_preview': 'https://safran-preview.pages.dev/%s/%s/%s' % (p['year'], p['month'], p['slug']),
        'notes': 'HOLD: المصدر في Blogger فارغ (0 بايت) — غير منشور' if p['status'] == 'HOLD' else '',
    })

with open(out, 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

print('rows:', len(rows), '| published:', sum(1 for r in rows if r['status'] == 'PUBLISHED'))
print(out)
