import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://www.safrnblog.com',
  build: { format: 'file' },
  trailingSlash: 'never',
});
