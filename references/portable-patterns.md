# Portable patterns (language-neutral)

Short, framework-free sketches of patterns that Core rules refer to. They are illustrations in pseudo-code and SQL, not code to paste: adapt to the project's language, ORM, and conventions, and check dialect differences for the installed database.

## 1. Object-level authorization (ownership)

Authentication tells you who the caller is. Authorization must also check that the caller may touch this object.

```
# Unsafe: any authenticated user can read any id
record = repo.find(id)

# Safe: scope the lookup by the trusted identity (or tenant) from the server-side session
record = repo.find(id, owner = current_identity.id)
if record is none: respond not_found        # or forbidden, matching the project's existing choice
```

- The identity comes from the server-side session or token, never from a client-supplied body, query, or header field.
- Apply the same scoping to list, update, delete, export, and download paths, and to every relation the request references.
- Choose 404 vs 403 for foreign objects consistently with the project; 404 avoids confirming that the object exists.

## 2. Invariant enforced by one atomic statement

Read-then-write checks race. Let the database make the decision in one statement.

```sql
UPDATE accounts
   SET balance = balance - :amount
 WHERE id = :id AND balance >= :amount;
-- affected rows = 0  →  reject (insufficient funds or unknown account)
```

- Also validate input before the statement (amount > 0, correct type and precision).
- Where several rows or tables must change together, wrap them in one transaction at the use-case boundary and keep the lock order consistent.
- Where a constraint can express the rule (`CHECK (balance >= 0)`), add it as defense in depth.
- Store money as integer minor units or an exact decimal type, never a binary float.

## 3. Idempotent create, import, or retried job

```sql
-- Business key protected by the database
ALTER TABLE records ADD CONSTRAINT uq_records_source_ref UNIQUE (source_id, external_ref);

-- Dialect-specific upsert (check the installed engine):
--   PostgreSQL / SQLite:  INSERT ... ON CONFLICT (source_id, external_ref) DO NOTHING | DO UPDATE ...
--   MySQL / MariaDB:      INSERT ... ON DUPLICATE KEY UPDATE ...
```

- Decide explicitly: on a repeat, skip, update, or fail?
- A "find or create" in application code is not safe under concurrency without the unique constraint.
- For retried requests and webhooks, accept a client key or external event id, store the processing status, and return the earlier result on repeat.
- For side effects such as email or payment, record intent in the same transaction and send after commit (outbox), with a deduplication key on the receiver side when possible.

## 4. Safe uniqueness migration on existing data

1. Detect existing violations: `SELECT col, COUNT(*) FROM t GROUP BY col HAVING COUNT(*) > 1;`
2. Decide the cleanup rule (keep oldest, merge, or manual review) and back up or snapshot first.
3. Make application writes safe (so no new duplicates appear), then clean up, then add the constraint using the engine's online or concurrent option if one exists.
4. Order the rollout for rolling deploys: old and new code may run together. Avoid a step that breaks the old version.
5. State the rollback limits; dropping a constraint is easy, restoring deleted duplicates is not.

## 5. Bounded, stable pagination

```
limit  = clamp(requested_limit or default, 1, MAX_LIMIT)
order  = (sort_column, unique_tiebreaker)        # stable ordering, otherwise pages overlap
```

- Reject or clamp out-of-range values; never trust `limit`, `page`, or `size` from the client.
- For large tables prefer keyset (cursor) pagination over deep offsets.
- Return pagination metadata in the shape existing consumers already expect.

## 6. Error mapping at the boundary

```
validation failure            → 4xx with field-level messages (the project's existing shape)
domain rule violated          → 4xx with a safe, user-facing message; no stack trace
unauthenticated / unauthorized → 401 / 403 as the project already distinguishes
not found                     → 404
unexpected exception          → 5xx generic message; log details server-side with secrets redacted
```

- One central place maps errors to responses; handlers do not hand-build error bodies.
- Anything thrown outside the central handler (startup, constructors, middleware) must still produce a safe response, so test those paths.

## 7. Client mutation flow

```
submit → disable the control, show pending
  success → close or navigate, show confirmation, invalidate or refresh affected cached data
  field validation error → keep the form open, show errors on their fields, keep user input
  other failure → show a safe message, keep the form open, allow retry
```

- Treat "request resolved" and "operation succeeded" as different things: check the status and body, not only that a promise resolved.
- Invalidate every cached view that the change affects (lists, counts, detail pages), using the data library's documented mechanism for the installed version.

## 8. Upload and download

```
upload:   enforce max size and allowed types server-side; sniff content, do not trust the client MIME type;
          store under a generated name outside the web root or in private storage
download: authorize per object (pattern 1), set a safe content type and disposition, never build paths from user input
```
