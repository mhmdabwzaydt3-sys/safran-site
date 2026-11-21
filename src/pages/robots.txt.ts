import type { APIRoute } from 'astro';

export const prerender = true;

export const GET: APIRoute = ({ site }) => {
  const isPreview = import.meta.env.PUBLIC_PREVIEW === '1';
  const body = isPreview
    ? 'User-agent: *\\nDisallow: /\\n'
    : `User-agent: *\\nAllow: /\\n\\nSitemap: ${new URL('/sitemap.xml', site)}\\n`;

  return new Response(body, {
    headers: { 'Content-Type': 'text/plain; charset=utf-8' },
  });
};
