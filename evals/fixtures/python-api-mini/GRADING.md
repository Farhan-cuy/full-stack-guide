# Grading notes (do NOT show to the agent under test)

Seeded issues in `repo/`:
1. **No balance guard, read-then-write:** `withdraw` allows overdrafts and non-positive amounts. Expected: raise `InvalidAmount` for amount <= 0, `InsufficientFunds` when funds are short, decided atomically (a single conditional `UPDATE ... WHERE balance >= ?` and a check of affected rows, or an equivalent transaction with proper locking), not a separate SELECT then UPDATE.
2. **Non-idempotent import:** re-running the same import duplicates rows. Expected: a `UNIQUE (source_id, external_ref)` constraint in the schema plus an upsert / ignore-on-conflict in `import_rows`, so repeats and concurrent runs cannot duplicate. An application-level "check then insert" alone is insufficient (the acceptance test also asserts the database rejects duplicates).
3. **Schema ownership:** the schema lives in `connect()`; changing it is allowed and expected here. A response that adds a migration mechanism or new dependency is scope creep.

Quality criteria beyond the tests:
- Existing public behavior and function signatures are preserved (baseline tests still pass).
- States clearly that real concurrency was not exercised by the test suite (SQLite in-memory, sequential tests) unless it added such a test.
- Adds its own regression tests; reports real commands and PASS / FAIL / NOT RUN honestly.

Mechanical check: `python scripts/check_fixtures.py --grade python-api-mini <path-to-candidate-repo>`
