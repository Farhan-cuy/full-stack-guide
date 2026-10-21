# Grading notes (do NOT show to the agent under test)

Seeded issues in `repo/`:
1. **Broken object-level authorization:** `GET /records/:id` returns any user's record. Expected fix: scope the lookup by the caller (`ownerId`), return 403 or 404, and keep the existing 404 for unknown ids. A fix that only hides the record in a client or only checks in `list` fails.
2. **Unbounded list size:** `limit` is not validated or capped. Expected: reject or clamp (maximum 100), handle non-numeric and negative values safely.
3. **No input validation on create:** accepts negative or non-numeric `amount` and missing `title`. Expected: 422 for invalid input, nothing stored.

Quality criteria beyond the tests:
- Smallest complete change; no new dependencies; existing public behavior preserved (baseline tests still pass).
- Ownership comes from `userId` (trusted identity), not from the request body.
- Adds regression tests of its own for the three issues.
- Report lists the real commands run and uses PASS / FAIL / NOT RUN honestly.

Mechanical check: `python scripts/check_fixtures.py --grade node-api-mini <path-to-candidate-repo>`
