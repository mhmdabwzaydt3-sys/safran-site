// Localise inline body images (Blogger content + PR-injected) that still point to external CDNs.
import fs from 'node:fs';
import path from 'node:path';
import sharp from 'sharp';

const DATA = 'src/data/posts.json';
const OUT = 'public/images';
fs.mkdirSync(OUT, { recursive: true });

const posts = JSON.parse(fs.readFileSync(DATA, 'utf8'));
const cache = new Map();
let done = 0;

const localize = async (url, name) => {
  if (cache.has(url)) return cache.get(url);
  const dest = path.join(OUT, name);
  const res = await fetch(url, { headers: { 'user-agent': 'Mozilla/5.0 SafranImageFetch' } });
  if (!res.ok) throw new Error('HTTP ' + res.status);
  const buf = Buffer.from(await res.arrayBuffer());
  const meta = await sharp(buf).metadata();
  const w = Math.min(1200, meta.width || 1200);
  await sharp(buf).resize({ width: w, withoutEnlargement: true }).webp({ quality: 72, effort: 5 }).toFile(dest);
  const src = `/images/${name}`;
  cache.set(url, src);
  done++;
  console.log(`ok ${name} ${Math.round(fs.statSync(dest).size / 1024)} KB (${meta.width}x${meta.height} -> ${w}px)`);
  return src;
};

for (const p of posts) {
  const imgs = [...p.html.matchAll(/<img\b[^>]*>/g)].map((m) => m[0]);
  let i = 0;
  for (const tag of imgs) {
    const srcM = tag.match(/src="(https?:\/\/[^"]+)"/);
    if (!srcM) continue;
    i++;
    const name = `inline-${String(p.n).padStart(2, '0')}-${i}.webp`;
    try {
      const local = await localize(srcM[1], name);
      let newTag = tag.replace(srcM[1], local);
      newTag = newTag.replace(/\s+srcset="[^"]*"/i, '').replace(/\s+sizes="[^"]*"/i, '');
      newTag = newTag.replace(/\s+fetchpriority="[^"]*"/i, '');
      newTag = newTag.replace(/\s+loading="[^"]*"/i, ' loading="lazy"');
      if (!/loading=/.test(newTag)) newTag = newTag.replace('<img', '<img loading="lazy"');
      p.html = p.html.replace(tag, newTag);
    } catch (e) {
      console.log(`!! ${p.n} ${e.message} ${srcM[1].slice(0, 60)}`);
    }
  }
}

fs.writeFileSync(DATA, JSON.stringify(posts, null, 1), 'utf8');
const remote = posts.reduce((acc, p) => acc + [...p.html.matchAll(/<img\b[^>]*src="https?:\/\//g)].length, 0);
console.log(`\nlocalised ${done}; remaining remote <img> in bodies: ${remote}`);
