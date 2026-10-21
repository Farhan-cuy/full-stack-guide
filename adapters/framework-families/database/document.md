# Database: document, key-value, and wide-column stores (MongoDB, Redis, DynamoDB, and similar)

Orientation for non-relational stores. Do not assume relational guarantees (foreign keys, multi-row transactions) exist.

## Detection
- Store and version: connection config, `docker-compose`, cloud service, client library and version.
- Schema discipline: schema validation or an ODM (Mongoose, and so on), index definitions, TTL settings.
- Deployment topology: replica set or cluster, consistency level defaults, regions.

## Idioms
- Define explicitly what each document or key owns, and which fields are the unique business key; enforce uniqueness with a unique index or conditional write.
- Use atomic operations rather than read-modify-write: increment operators, conditional updates with a filter, compare-and-set, `SET ... NX`.
- Multi-document transactions are conditional on topology and version; verify availability before relying on them.
- Design for duplicate delivery and retries: idempotency keys, deduplication ids, upserts.
- Bound document size, array growth, and query cost; always paginate.
- Redis used as a cache is not a source of truth unless the system was designed that way; set TTLs deliberately and plan for eviction.

## Pitfalls
- Query-operator injection when user JSON is passed straight into a query (for example, objects instead of strings); validate types and reject operators.
- Unbounded arrays inside documents; missing indexes leading to full scans.
- Reading from replicas or with weak consistency and then making decisions on stale data.
- Hot keys or partitions; large scans in request paths.
- Assuming schemaless means no contract: other services and the UI still depend on the shape.
- Cache invalidation and stampedes when many clients refill the same expired key.

## Verify
- Test against the same engine and major version as production (not an in-memory substitute) for query, index, and atomicity behavior.
- Check index usage with the engine's explain tooling.
- Test duplicate and concurrent writes where the environment supports it; otherwise state the limitation.

## Version-sensitive
Check store and client versions: transaction support, consistency defaults, operator behavior, TTL and eviction semantics, driver API changes, and managed-service limits.
