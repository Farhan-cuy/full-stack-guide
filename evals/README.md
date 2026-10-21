# Evaluation scenarios

`evals.json` holds 23 semantic screening scenarios. They are framework-neutral except for the scenarios that name a technology or adapter explicitly. Scenarios 22-23 cover frontend design quality (greenfield UI without generic output, and deferring to an existing design system). Scenarios 16-19 test *behavior around the skill* (staying light on trivial edits, not applying an opt-in adapter without evidence, degrading honestly without tools, resisting prompt injection). Scenarios 20-21 are backed by runnable fixtures.

## Two kinds of checks
1. **Mechanical (fixtures 20-21).** `evals/fixtures/<name>/repo` is a small project with seeded defects and its own passing baseline tests. Hidden acceptance tests (in `acceptance/`, never shown to the agent) must fail on the untouched repo and pass after a correct fix.
   - Validate the fixtures themselves: `python scripts/check_fixtures.py`
   - Grade an agent's result: `python scripts/check_fixtures.py --grade <fixture> <candidate_repo_dir>`
   - Both fixtures use only Node.js (20+) or Python (3.9+) and no installed dependencies. A missing runtime is reported as `NOT RUN`.
2. **Semantic (all scenarios).** Compare the agent's diff and report with `must_include` / `must_not_include`. Judge meaning, not literal phrases. Framework-specific helper names count only if the fixture confirms them.

## Run a meaningful evaluation
1. Give the agent only `repo/` (never `GRADING.md` or `acceptance/`). For other scenarios, prepare a fixture with an explicit stack, versions, auth model, persistence engine, tests, and commands.
2. Run each prompt with the skill active and, for comparison, without it. Keep the model, tools, fixture, and prompt identical.
3. Inspect the real diff; run the applicable tests, lint, type-check, and build.
4. Mark each criterion PASS, FAIL, or NOT RUN from evidence.

Suggested dimensions (0-4 each; N/A excluded): acceptance correctness, security/authorization, data integrity, contract compatibility, scope control, maintainability, truthful verification. A critical security or data-integrity failure blocks a release regardless of the total.

The scenarios are screening specifications, not a proof that any agent performs correctly.
