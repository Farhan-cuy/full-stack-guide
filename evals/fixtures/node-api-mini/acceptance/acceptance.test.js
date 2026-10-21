import test from 'node:test';
import assert from 'node:assert/strict';
import { createApp } from '../src/app.js';

test('a user cannot read another user\'s record by id', () => {
  const { handle } = createApp();
  const res = handle({ method: 'GET', path: '/records/2', userId: 1 }); // record 2 belongs to user 2
  assert.ok([403, 404].includes(res.status), `expected 403 or 404, got ${res.status}`);
  assert.ok(!JSON.stringify(res.body).includes('Bob salary'), 'response must not leak the record');
});

test('list size is bounded', () => {
  const { handle, store } = createApp();
  for (let i = 0; i < 150; i++) {
    store.records.push({ id: store.nextId(), ownerId: 1, title: `bulk ${i}`, amount: 1 });
  }
  const res = handle({ method: 'GET', path: '/records', userId: 1, query: { limit: '1000' } });
  const ok = res.status === 422 || (res.status === 200 && res.body.data.length <= 100);
  assert.ok(ok, `limit=1000 must be rejected or clamped to at most 100 rows (status ${res.status}, rows ${res.body?.data?.length})`);
});

test('invalid create input is rejected and nothing is stored', () => {
  const { handle, store } = createApp();
  const before = store.records.length;
  const bad = [
    { title: 'x', amount: -5 },
    { title: 'x', amount: 'abc' },
    { amount: 10 },
    {},
  ];
  for (const body of bad) {
    const res = handle({ method: 'POST', path: '/records', userId: 1, body });
    assert.equal(res.status, 422, `body ${JSON.stringify(body)} should be rejected with 422`);
  }
  assert.equal(store.records.length, before, 'rejected requests must not create records');
});
