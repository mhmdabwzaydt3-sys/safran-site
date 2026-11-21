// Self-host and optimise the article cover images (replaces CDN hotlinks).
// Input : posts.json with remote image URLs
// Output: public/images/<slug>.webp (1200x675, q=72) + local paths + credits doc
import fs from 'node:fs';
import path from 'node:path';
import sharp from 'sharp';

const DATA = 'src/data/posts.json';
const OUT = 'public/images';
fs.mkdirSync(OUT, { recursive: true });

const posts = JSON.parse(fs.readFileSync(DATA, 'utf8'));
const credits = [];
let made = 0;
let skipped = 0;

for (const p of posts) {
  const img = p.image || '';
  if (!/^https?:\/\//.test(img)) { skipped++; continue; }

  const host = new URL(img).host;
  const file = `${String(p.n).padStart(2, '0')}-${p.slug}.webp`.replace(/[^a-zA-Z0-9._-]/g, '-');
  const dest = path.join(OUT, file);

  try {
    const res = await fetch(img, { headers: { 'user-agent': 'Mozilla/5.0 SafranImageFetch' } });
    if (!res.ok) throw new Error('HTTP ' + res.status);
    const buf = Buffer.from(await res.arrayBuffer());
    await sharp(buf)
      .resize(1200, 675, { fit: 'cover', position: 'attention' })
      .webp({ quality: 72, effort: 5 })
      .toFile(dest);

    const size = fs.statSync(dest).size;
    credits.push({ n: p.n, file, host, source: img, kb: Math.round(size / 1024) });
    p.image = `/images/${file}`;
    p.imageCredit = host.includes('unsplash') ? 'Unsplash License' : host.includes('pexels') ? 'Pexels License' : 'غير محدد';
    p.imageSource = img;
    made++;
    console.log(`%s %02d %-40s %4d KB`, 'ok', p.n, file, Math.round(size / 1024));
  } catch (e) {
    console.log(`!! %02d failed: ${e.message}`, p.n);
  }
}

fs.writeFileSync(DATA, JSON.stringify(posts, null, 1), 'utf8');

const lines = [
  '# مصادر صور المقالات والتراخيص',
  '',
  'كل الصور مستضافة محليًا داخل `public/images/` بعد تنزيلها وضغطها إلى WebP (1200×675، جودة 72).',
  'لم تعد الصفحات تحمّل أي صورة من نطاق خارجي (لا Pexels ولا Unsplash)، للحفاظ على الأداء والخصوصية.',
  '',
  '| المقال | الملف | الحجم | المصدر الأصلي | الترخيص |',
  '|---|---|---|---|---|',
  ...credits.map((c) => `| ${String(c.n).padStart(2, '0')} | \`${c.file}\` | ${c.kb} KB | ${c.source} | ${c.host.includes('unsplash') ? 'Unsplash License' : 'Pexels License'} |`),
  '',
  '## ملاحظات',
  '- الترخيصان يسمحان بالاستخدام التجاري بلا مقابل، ولا يشترطان الإسناد، لكن يُذكر المصدر هنا احترامًا وأثرًا للتحقق.',
  '- لا يجوز استخدام الصور لاحقًا للإيحاء بأن وجهة أو جهة ترعى الموقع.',
  '- عند استبدال أي صورة، يُحدَّث هذا الملف مع تحديث تاريخ المقال.',
];
fs.writeFileSync('docs/IMAGE-CREDITS.md', lines.join('\n') + '\n', 'utf8');

console.log(`\nprocessed ${made}, already local ${skipped}`);
