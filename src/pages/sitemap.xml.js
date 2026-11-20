import allPostsData from '../data/posts.json';
const posts = allPostsData.filter((p) => p.status !== 'HOLD');

const staticPages = [
  '/', '/about.html', '/contact.html', '/privacy.html', '/terms.html',
  '/editorial-policy.html', '/corrections.html', '/disclosure.html', '/sitemap.html',
];
const labels = ['visas', 'benin', 'usa', 'uk', 'schengen', 'hungary', 'albania', 'georgia', 'japan', 'russia', 'china', 'morocco', 'azerbaijan', 'guides'];

export function GET() {
  const base = 'https://www.safrnblog.com';
  const urls = [
    ...staticPages.map((u) => ({ loc: base + u, lastmod: '2026-11-20' })),
    ...labels.map((l) => ({ loc: `${base}/label/${l}.html`, lastmod: '2026-11-20' })),
    ...posts.map((p) => ({
      loc: `${base}/${p.year}/${p.month}/${p.slug}.html`,
      lastmod: p.updated,
    })),
  ];
  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls.map((u) => `  <url><loc>${u.loc}</loc><lastmod>${u.lastmod}</lastmod></url>`).join('\n')}
</urlset>`;
  return new Response(xml, { headers: { 'Content-Type': 'application/xml; charset=utf-8' } });
}
