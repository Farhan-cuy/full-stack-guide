# Scope control

Before changing code, identify the user-visible behavior and acceptance criteria. Trace only the code paths necessary to deliver it.

## Do
- Fix the smallest complete path that solves the problem, including tests where appropriate.
- Search for consumers of renamed/removed fields, routes, events, shared types, and configuration.
- Reuse a maintained sibling pattern when it fits the requirement.
- State assumptions that materially affect the design.
- Separate required work from optional improvements.

## Avoid unless required or explicitly approved
- Broad refactors unrelated to the requested outcome.
- New dependencies, framework migrations, public API changes, schema changes, or destructive operations.
- Creating every CRUD operation when only one action is requested.
- Adding abstractions for hypothetical future needs.
- Reformatting unrelated files or replacing established UI design.

If a security defect or data corruption risk is discovered outside the immediate scope, explain its impact and propose a bounded fix; do not silently expand a risky migration or public contract change.
