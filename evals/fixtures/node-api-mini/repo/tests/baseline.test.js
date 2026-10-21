import test from 'node:test';
import assert from 'node:assert/strict';
import { createApp } from '../src/app.js';

test('rejects unauthenticated requests', () => {
  const { handle } = createApp();
  assert.equal(handle({ method: 'GET', path: '/records' }).status, 401);
});

test('lists only the caller\'s own records', () => {
  const { handle } = createApp();
  const res = handle({ method: 'GET', path: '/records', userId: 1 });
  assert.equal(res.status, 200);
  assert.deepEqual(res.body.data.map((r) => r.id), [1, 3]);
});

test('returns the caller\'s own record by id', () => {
  const { handle } = createApp();
  const res = handle({ method: 'GET', path: '/records/1', userId: 1 });
  assert.equal(res.status, 200);
  assert.equal(res.body.data.title, 'Alice rent');
});

test('returns 404 for an unknown record', () => {
  const { handle } = createApp();
  assert.equal(handle({ method: 'GET', path: '/records/999', userId: 1 }).status, 404);
});

test('creates a record owned by the caller', () => {
  const { handle } = createApp();
  const res = handle({ method: 'POST', path: '/records', userId: 2, body: { title: 'Gift', amount: 25 } });
  assert.equal(res.status, 201);
  assert.equal(res.body.data.ownerId, 2);
});
