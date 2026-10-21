# Evidence-led debugging

1. Reproduce or narrow the failure. Capture exact error, affected inputs, environment, and expected versus observed behavior without exposing secrets.
2. Follow the request/data path layer by layer. Check browser/network or client output, server logs, routing/middleware, service logic, database state, queues, and external dependencies as applicable.
3. Form one or more testable hypotheses. Prefer read-only inspection first and change one likely cause at a time.
4. Compare a working sibling path and a failing path. Check installed versions and configuration rather than assuming defaults.
5. Use the smallest safe diagnostic command. Avoid destructive commands, dumping credentials, or changing multiple unrelated configs.
6. Add a regression test or reproducible check for the root cause when feasible.
7. Report root cause with evidence, the fix, commands run, observed result, and remaining uncertainty.

Do not present a plausible cause as confirmed until evidence supports it. If the issue cannot be reproduced, clearly distinguish a suspected fix from a verified fix.

## Narrow the layer first
Cheapest check first, then go deeper:
1. Raw request and response (browser network panel, or a command-line HTTP client): status, headers, body.
2. Route and middleware registration: does the route exist, with the intended auth and role checks?
3. Server logs and error tracking for the exact request.
4. The service or use-case in isolation (a test, a REPL, or a script), skipping HTTP.
5. The database state and the query actually executed.
6. Client state: which cache key or store holds the data, and what it contains.
Change one thing per experiment and re-test; do not patch three places at once.

## Symptom → likely layer
| Symptom | Likely causes | First check |
|---|---|---|
| 401 right after a successful login | credential not sent (header scheme, cookie name or domain), token expired, auth middleware order | request headers/cookies actually sent; server auth log |
| 403 with a "valid" role | role or permission name mismatch, wrong guard or policy, stale permission cache, missing ownership or tenant rule | the exact role/permission names on both sides; policy code path |
| Browser CORS error but an API client works | preflight rejects the origin, method, or a custom header; credentials mode mismatch; an error response without CORS headers hides the real 4xx/5xx | the OPTIONS response and its allow headers; then the real status |
| Validation failure returns HTML or a redirect | client is not asking for JSON, error handler is not API-aware, framework default for non-JSON requests | request `Accept` header; handler configuration |
| 200 response but empty UI | client reads the wrong response path, serializer wraps differently, filter or parameter name mismatch | compare the raw body with the type the client expects |
| UI stale after a mutation | cache key not invalidated, wrong invalidation API for the installed version, optimistic update without rollback | which key the view reads vs which key was invalidated |
| 500 HTML page instead of a JSON error | exception outside the central handler (startup, constructor, middleware), debug mode | stack trace in logs; where the exception was thrown |
| Works locally, fails when deployed | environment variable missing or baked in at build time, base URL, proxy or HTTPS headers, CORS origin, database or engine differences | deployed configuration vs local; build-time vs run-time variables |
| Intermittent duplicates or negative balance | race condition, missing constraint, retry without idempotency | all writers of the data; constraints in the schema |
| Upload fails | content type set by hand on multipart, body size limits (proxy or server), type validation | request content type and size; server and proxy limits |
| Another tenant's or user's data appears | unscoped raw query, client-supplied tenant header trusted, missing ownership check | the query actually executed and where the scope comes from |
| Slow list endpoint | N+1 queries, missing index, unbounded page size | query count and `EXPLAIN` output |
| Build passes, runtime type error | type checking disabled or ignored at build, types written from assumptions | run the type checker explicitly; compare types with real responses |

If the symptom is not in the table, return to "Narrow the layer first"; do not pick the closest-looking row.
