# node-api-mini

A tiny in-memory records API used as a test fixture. There is no network layer: `createApp()` returns a
`handle(req)` function that takes `{ method, path, query, userId, body }` and returns `{ status, body }`.

- Run tests: `npm test` (Node.js 20+, no dependencies)
- Source: `src/store.js` (in-memory data) and `src/app.js` (routing and handlers)
- Authenticated users are identified by `userId`; records belong to an owner (`ownerId`).
