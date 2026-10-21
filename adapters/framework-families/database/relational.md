# Database: relational systems (PostgreSQL, MySQL/MariaDB, SQLite, SQL Server)

Orientation for schema, query, and migration decisions. Behavior differs by engine and version; confirm which one the project actually uses.

## Detection
- Engine and version: `docker-compose` image tags, connection URL scheme, ORM configuration, CI service containers, deployment docs.
- Migration tool and directory (framework migrations, Flyway, Liquibase, Alembic, Prisma Migrate, goose, and so on) and how it runs in deployment.
- ORM or query layer and whether raw SQL is used.
- Whether tests run on the same engine as production (SQLite in tests does not reproduce locking or collation behavior).

## Idioms
- Put invariants the database can enforce into the schema: primary and foreign keys, `NOT NULL`, `UNIQUE`, `CHECK`.
- Use parameterized queries only. Escape `LIKE` wildcards in user input when matching literally.
- Atomic conditional updates and upserts instead of read-then-write (see `../../../references/portable-patterns.md`).
- Pick the right locking tool for the engine: row locks (`SELECT ... FOR UPDATE`), `SKIP LOCKED` for work queues, optimistic version columns.
- Index the columns used to filter, join, and sort; check plans with `EXPLAIN` for new or heavy queries.
- Store timestamps in UTC; money as integer minor units or exact decimals.
- Migrations: expand, backfill, then contract; avoid long table locks; make them safe for rolling deploys.

## Pitfalls
- Default isolation differs: PostgreSQL defaults to READ COMMITTED, MySQL InnoDB to REPEATABLE READ; a race that appears in one may not appear in the other.
- `UNIQUE` over nullable columns: engines differ on how many `NULL`s are allowed (SQL Server allows one; PostgreSQL and MySQL allow many).
- Upsert syntax differs (`ON CONFLICT` vs `ON DUPLICATE KEY UPDATE` vs `MERGE`).
- Collation and case sensitivity change `UNIQUE` and `LIKE` results.
- Soft-delete columns interacting with unique constraints.
- Deep offset pagination on large tables; very large `IN (...)` lists; N+1 queries from ORMs.
- Lock ordering that causes deadlocks; transactions held open across network calls.

## Verify
- Run migrations up (and down if supported) on a scratch database, including against data resembling production.
- Run the tests against the production engine; add tests for uniqueness, foreign keys, rollback, and races where feasible.
- `EXPLAIN` the new or changed queries.
- State plainly what was not tested (for example, real concurrency or production data volume).

## Version-sensitive
Check the engine version: features such as online DDL, `CHECK` enforcement, generated columns, `JSON` operators, `SKIP LOCKED`, and default isolation change between releases and between engines. Check the ORM and migration-tool versions too.
