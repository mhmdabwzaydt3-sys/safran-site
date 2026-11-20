import json, csv, os

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(BASE))
d = json.load(open(os.path.join(BASE, 'audit-data.json'), encoding='utf-8'))
posts = d['posts']

MERGE_HINT = {2: 'يدمج مع دليل بنين (19)', 3: 'يدمج مع دليل بنين (19)', 4: 'فارغ تمامًا — يُدمج أو يُعاد كتابته',
              5: 'يدمج مع دليل بنين (19)', 6: 'يدمج مع دليل بنين (19)', 7: 'يبقى محورًا: يتحول إلى دليل بنين الشامل',
              19: 'يبقى محورًا: دليل بنين الشامل (يستقبل 2,3,5,6)'}
SPECIAL = {1: 'لا مصادر خارجية ولا روابط داخلية ولا صور؛ الأضعف بين المقالات',
           4: 'المحتوى فارغ (0 بايت) منشور على الإنترنت',
           11: 'صفحة محورية: 18 رابطًا داخليًا، تحتاج تحديثًا دوريًا',
           8: 'يحتاج التحقق من الرسوم والمواعيد', 9: 'ETA البريطانية متغيرة — مراجعة إلزامية',
           10: 'قواعد شنغن متغيرة — مراجعة إلزامية'}

rows = []
for p in posts:
    st = p['status']
    if p['n'] in MERGE_HINT and p['n'] not in (7, 19):
        st = 'MERGE'
    if p['n'] == 4:
        st = 'HOLD'
    notes = [SPECIAL.get(p['n'], '')]
    if p['words'] < 700: notes.append('محتوى أقل من 700 كلمة')
    if p['official'] == 0: notes.append('بلا مصدر رسمي')
    if p['internal'] < 3: notes.append('روابط داخلية ضعيفة')
    if not p['has_review_date']: notes.append('لا تاريخ مراجعة ظاهر')
    if not p['has_sources']: notes.append('لا قسم مصادر')
    notes.append('author=آدمن 19 (بيانات منظمة غير صحيحة)')
    rows.append(dict(
        n='%02d' % p['n'], url=p['url'], title=p['title'],
        category=' / '.join(p['labels']), language='ar',
        published=p['published'], updated=p['updated'],
        words=p['words'], images=p['images'], img_noalt=p['img_noalt'],
        internal=p['internal'], external=p['external'], official_sources=p['official'],
        ads_slots=p['ads'], has_sources=p['has_sources'], has_review_date=p['has_review_date'],
        status=st, score=p['score'], migration='لم يبدأ',
        notes='؛ '.join([n for n in notes if n]),
    ))

out = os.path.join(BASE, 'content-inventory.csv')
with open(out, 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['n', 'url', 'title', 'category', 'language', 'published', 'updated',
                                      'words', 'images', 'img_noalt', 'internal', 'external',
                                      'official_sources', 'ads_slots', 'has_sources', 'has_review_date',
                                      'status', 'score', 'migration', 'notes'])
    w.writeheader(); w.writerows(rows)

from collections import Counter
print('written', out, len(rows))
print(Counter(r['status'] for r in rows))
print('total words', sum(r['words'] for r in rows), 'avg', round(sum(r['words'] for r in rows)/len(rows)))
print('posts with 0 official sources:', [r['n'] for r in rows if r['official_sources'] == 0])
print('posts with <3 internal:', [r['n'] for r in rows if r['internal'] < 3])
print('posts without sources section:', [r['n'] for r in rows if not r['has_sources']])
print('posts without review date:', [r['n'] for r in rows if not r['has_review_date']])
