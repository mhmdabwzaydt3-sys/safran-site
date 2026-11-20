import json, os, re, html

TMP = os.environ.get('TMPDIR', '/tmp')
main = json.load(open(os.path.join(TMP, 'posts-main.json'), encoding='utf-8'))
pr = json.load(open(os.path.join('Hermes-Shared', 'safran-pr1', 'src', 'data', 'posts.json'), encoding='utf-8'))

def words(h):
    t = html.unescape(re.sub(r'<[^>]+>', ' ', h))
    return len(t.split())

print('%-3s %-8s %7s %7s  %-30s %s' % ('n', 'status', 'main_w', 'pr_w', 'new fields', 'images'))
for a, b in zip(main, pr):
    newf = sorted(set(b.keys()) - set(a.keys()))
    imgs = len(re.findall(r'<img', b['html']))
    flag = ''
    if a['html'] != b['html']:
        flag += ' TEXT'
    if newf:
        flag += ' FIELDS'
    print('%-3d %-8s %7d %7d  %-30s %d%s' % (b['n'], b.get('status'), words(a['html']), words(b['html']),
                                             ','.join(newf)[:30], imgs, flag))

print('\n=== article 1 (Budapest) external links')
for u in sorted(set(re.findall(r'href="(https?://[^"]+)"', pr[0]['html']))):
    print('  ', u)
print('\n=== article 19 (Benin) external links')
a19 = [x for x in pr if x['n'] == 19][0]
for u in sorted(set(re.findall(r'href="(https?://[^"]+)"', a19['html']))):
    print('  ', u)
print('\n=== images in rebuilt articles')
for x in pr:
    for m in re.finditer(r'<img[^>]*>', x['html']):
        print('  %02d %s' % (x['n'], m.group(0)[:220]))
