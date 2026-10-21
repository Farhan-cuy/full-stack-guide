import { createStore } from './store.js';

export function createApp(store = createStore()) {
  function handle(req) {
    const { method, path, query = {}, userId, body } = req;

    if (!userId) {
      return { status: 401, body: { error: 'unauthenticated' } };
    }

    if (method === 'GET' && path === '/records') {
      const limit = Number(query.limit ?? 10);
      const rows = store.records.filter((r) => r.ownerId === userId).slice(0, limit);
      return { status: 200, body: { data: rows } };
    }

    const match = path.match(/^\/records\/(\d+)$/);
    if (method === 'GET' && match) {
      const record = store.records.find((r) => r.id === Number(match[1]));
      if (!record) {
        return { status: 404, body: { error: 'not_found' } };
      }
      return { status: 200, body: { data: record } };
    }

    if (method === 'POST' && path === '/records') {
      const { title, amount } = body ?? {};
      const record = { id: store.nextId(), ownerId: userId, title, amount };
      store.records.push(record);
      return { status: 201, body: { data: record } };
    }

    return { status: 404, body: { error: 'not_found' } };
  }

  return { handle, store };
}
