export default {
  async fetch() {
    return new Response('bootstrap', { headers: { 'content-type': 'text/plain' } });
  },
};
