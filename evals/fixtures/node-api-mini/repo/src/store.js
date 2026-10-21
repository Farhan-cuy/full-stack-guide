// In-memory data store. A fresh store is created per app instance so tests stay isolated.
export function createStore() {
  const store = {
    users: [
      { id: 1, name: 'alice' },
      { id: 2, name: 'bob' },
    ],
    records: [
      { id: 1, ownerId: 1, title: 'Alice rent', amount: 1200 },
      { id: 2, ownerId: 2, title: 'Bob salary', amount: 5000 },
      { id: 3, ownerId: 1, title: 'Alice groceries', amount: 90 },
    ],
    _nextId: 4,
    nextId() {
      return store._nextId++;
    },
  };
  return store;
}
