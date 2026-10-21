# Data integrity and concurrency

For operations that change persistent state, identify the invariant before choosing implementation details. Examples include nonnegative balances, unique business keys, valid state transitions, and ownership consistency.

1. **Trace all writers.** Find every route, job, event handler, scheduled task, import, admin action, and direct persistence path that can change the data.
2. **Define atomicity.** Determine which reads and writes must succeed or fail together. Place the transaction at the use-case boundary that owns those changes, using the project's transaction model.
3. **Handle races at the right layer.** Application checks alone may race. Evaluate database constraints, conditional updates, row/advisory locks, optimistic concurrency, idempotency keys, or serialization according to the database and workload.
4. **Use constraints as defense in depth.** Enforce uniqueness, foreign keys, nullability, and check constraints where supported and appropriate. Plan schema rollout and existing-data cleanup.
5. **Design retries deliberately.** Make retryable jobs and externally retried requests idempotent where required. Define business keys and update-versus-skip behavior.
6. **Consider partial failure.** For batch/import/chunk operations, document whether failure rolls back all work or preserves completed chunks. Avoid claiming all-or-nothing when it is not true.
7. **Test the invariant.** Cover success, rejection, repeated requests, competing writes where feasible, rollback/partial failure, and boundary values. If concurrency cannot be tested in the available environment, state the limitation.

A transaction wrapper alone does not automatically prevent every lost update, duplicate insert, or race condition. The guarantee depends on isolation, query shape, constraints, and all writers.

See `portable-patterns.md` §2 (atomic conditional update), §3 (idempotent create/import), and §4 (safe uniqueness migration).
