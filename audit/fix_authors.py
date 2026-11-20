"""Remove invented editorial roles from the Blogger author box (v0.2 fix).

Rationale: SAFRAN v2.1 §4.5 forbids claiming a team, reviewer or expert that does not
verifiably exist. The imported bodies carry a box naming "فريق سفران التحريري" and the
job title "مدقق معلومات السفر" plus a specialisation. Those attributes are replaced by
the publisher identity and a pointer to the editorial policy page.
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SITE = os.path.join(os.path.dirname(ROOT), 'safran-site')
DATA = os.path.join(SITE, 'src', 'data', 'posts.json')

ROLE_LINE = re.compile(r'مدقق معلومات السفر\s*[—-]\s*متخصص[^<]{0,120}')
TEAM_LINE = re.compile(r'فريق سفران التحريري\s*[—-]?\s*(?:قسم التأشيرات)?')
TEAM_LINE2 = re.compile(r'فريق سفران\s*-\s*قسم التأشيرات والوثائق')

NEW_ROLE = 'ناشر: سفران — مدونة معلوماتية عن السفر والتأشيرات'
NEW_TEAM = 'سفران'

posts = json.load(open(DATA, encoding='utf-8'))
changed = []
for p in posts:
    h = p['html']
    before = h
    n_role = len(ROLE_LINE.findall(h))
    h = ROLE_LINE.sub(NEW_ROLE, h)
    h = TEAM_LINE2.sub(NEW_TEAM, h)
    h = TEAM_LINE.sub(NEW_TEAM, h)
    if h != before:
        p['html'] = h
        changed.append((p['n'], n_role))

json.dump(posts, open(DATA, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('posts changed:', len(changed), changed)
left = [p['n'] for p in posts if 'مدقق' in p['html'] or 'فريق سفران التحريري' in p['html']]
print('remaining claims:', left)
