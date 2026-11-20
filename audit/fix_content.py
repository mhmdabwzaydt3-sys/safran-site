"""One-off editorial fixes applied to the extracted Blogger content (v0.2).

All changes are deterministic and documented in reports/SAFRAN-INITIAL-BUILD-ar.md.
The raw Blogger feed copy in raw/safrn/feed-full.json is never modified.
"""
import json, re, os, html as H

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SITE = os.path.join(os.path.dirname(ROOT), 'safran-site')
DATA = os.path.join(SITE, 'src', 'data', 'posts.json')

LABEL_SLUG = {
    'تأشيرات': 'visas', 'بنين': 'benin', 'أمريكا': 'usa', 'بريطانيا': 'uk',
    'شنغن': 'schengen', 'المجر': 'hungary', 'ألبانيا': 'albania', 'جورجيا': 'georgia',
    'اليابان': 'japan', 'روسيا': 'russia', 'الصين': 'china', 'المغرب': 'morocco',
    'أذربيجان': 'azerbaijan', 'دليل شامل': 'guides',
}
PAGE_MAP = {
    '/p/about.html': '/about.html',
    '/p/contact-us.html': '/contact.html',
    '/p/blog-page.html': '/privacy.html',
    '/p/privacy-policy-for-arabic-web-de-if-you.html': '/privacy.html',
    '/p/blog-page_25.html': '/search.html',
}

ETIAS_OLD_H2 = '<h2>2. نظام ETIAS الجديد - أواخر 2026</h2>'
ETIAS_NEW_H2 = '<h2>2. ETIAS: غير مُشغَّل حتى 20 نوفمبر 2026</h2>'
ETIAS_OLD_P = '<p>ابتداءً من أواخر 2026، سيصبح ETIAS إلزاميًا للمسافرين المعفيين من التأشيرة مثل أمريكا وبريطانيا وكندا.</p>'
ETIAS_NEW_P = ('<p>حتى 20 نوفمبر 2026، نظام ETIAS <strong>لم يبدأ العمل</strong>: لا تُستقبل طلبات، ولم يُعلن تاريخ '
               'تشغيل محدد. الاتحاد الأوروبي يقول إنه يتوقع تشغيله في الربع الأخير من 2026، وإن التاريخ الدقيق '
               'سيُعلن قبل أشهر من الإطلاق على الموقع الرسمي travel-europe.europa.eu. '
               'وهو يخص المعفيين من التأشيرة (مثل مواطني أمريكا وبريطانيا وكندا)، ولا ينطبق على من يحتاج تأشيرة شنغن.</p>')
ETIAS_OLD_FAQ = '<div> <strong>س: هل ETIAS إلزامي الآن؟</strong><br> ج: حتى أواخر 2026 ليس قيد التشغيل بعد حسب الاتحاد الأوروبي، لكنه سيصبح إلزامي برسوم 20 يورو للمعفيين. </div>'
ETIAS_NEW_FAQ = '<div> <strong>س: هل ETIAS إلزامي الآن؟</strong><br> ج: لا. حتى 20 نوفمبر 2026 لم يبدأ التشغيل ولا تُقبل طلبات، ولم يُعلن تاريخ محدد. عند تشغيله سيُطلب من المعفيين من التأشيرة برسوم 20 يورو حسب الموقع الرسمي. </div>'

JUNK_PARA = re.compile(r'<p>\s*<strong>\s*روابط مقترحة داخلية.{0,600}?</p>', re.S)


def fix_html(h: str) -> tuple[str, list[str]]:
    notes = []
    before = h

    n_comments = len(re.findall(r'<!--.*?-->', h, re.S))
    h = re.sub(r'<!--.*?-->', '', h, flags=re.S)
    if n_comments:
        notes.append('%d تعليقًا برمجيًا محذوفًا' % n_comments)

    n_ent = len(re.findall(r'【entity-[^】]*】', h))
    h = re.sub(r'【entity-[^】]*】', '', h)
    if n_ent:
        notes.append('%d وسم 【entity-…】 محذوف' % n_ent)

    if JUNK_PARA.search(h):
        h = JUNK_PARA.sub('', h)
        notes.append('فقرة «روابط مقترحة داخلية» (ملاحظة تحرير داخلية) محذوفة')

    # legacy page + label links
    for old, new in PAGE_MAP.items():
        for prefix in ('https://www.safrnblog.com', 'http://www.safrnblog.com', 'https://safrnblog.com'):
            h = h.replace(prefix + old, new)

    def label_sub(m):
        raw = m.group(1)
        lab = H.unescape(raw).replace('+', ' ')
        slug = LABEL_SLUG.get(lab)
        return '/label/%s.html' % slug if slug else m.group(0)

    h = re.sub(r'https?://(?:www\.)?safrnblog\.com/search/label/([^"\'<>\s]+)', label_sub, h)

    n_abs = len(re.findall(r'https?://(?:www\.)?safrnblog\.com', h))
    h = re.sub(r'https?://(?:www\.)?safrnblog\.com', '', h)
    if n_abs:
        notes.append('%d رابط داخلي مطلق حُوّل إلى نسبي' % n_abs)

    if ETIAS_OLD_H2 in h:
        h = h.replace(ETIAS_OLD_H2, ETIAS_NEW_H2)
        notes.append('عنوان ETIAS صُحّح')
    if ETIAS_OLD_P in h:
        h = h.replace(ETIAS_OLD_P, ETIAS_NEW_P)
        notes.append('ادعاء ETIAS صُحّح حسب الموقع الرسمي')
    if ETIAS_OLD_FAQ in h:
        h = h.replace(ETIAS_OLD_FAQ, ETIAS_NEW_FAQ)
        notes.append('جواب ETIAS في الأسئلة صُحّح')

    h = re.sub(r'\n{3,}', '\n\n', h).strip()
    if not notes and h != before:
        notes.append('تنظيف عام')
    return h, notes


posts = json.load(open(DATA, encoding='utf-8'))
report = []
for p in posts:
    new, notes = fix_html(p['html'])
    if notes:
        report.append({'n': p['n'], 'slug': p['slug'], 'notes': notes})
        p['html'] = new
    p['status'] = 'HOLD' if p['n'] == 4 else 'PUBLISHED'

json.dump(posts, open(DATA, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

for r in report:
    print('%02d %-42s %s' % (r['n'], r['slug'], '؛ '.join(r['notes'])))
print('\nposts:', len(posts), '| held:', [p['n'] for p in posts if p['status'] == 'HOLD'])

# sanity: no leftovers
bad = []
for p in posts:
    html = p['html']
    for pat, label in [(r'<!--', 'تعليق'), (r'【entity', 'entity'), (r'https?://(?:www\.)?safrnblog\.com', 'رابط مطلق'),
                       (r'روابط مقترحة داخلية', 'فقرة ملاحظة')]:
        if re.search(pat, html):
            bad.append((p['n'], label))
print('leftovers:', bad)
