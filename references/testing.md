# Testing and verification

Test the behavior and risk, not just the implementation shape.

- Start from acceptance criteria and existing test conventions. Inspect test scripts and environment requirements before choosing commands.
- Add unit tests for isolated rules and integration/feature tests for boundaries, persistence, authentication, authorization, and contracts as appropriate.
- Cover happy path, invalid input, missing/unauthorized identity, not-found/conflict cases, boundary values, and failure/rollback behavior relevant to the task.
- For data races, retries, imports, or idempotency, test repeated/concurrent behavior when the test environment can meaningfully support it.
- For frontend behavior, consider loading, error, empty, success, disabled/pending states, accessibility, and cache/state invalidation where relevant.
- Run the narrowest useful test first, then related suite, lint/format, type-check, and build as available. Do not run destructive or production-targeting commands without explicit authorization.
- Report each check as `PASS` (actually executed and passed), `FAIL` (executed and failed), or `NOT RUN` (not executed / unavailable). Include exact command and useful output. A skipped test is not a pass.
- If no automated test exists, provide a concrete manual verification plan and label it as not executed unless it was actually performed.
