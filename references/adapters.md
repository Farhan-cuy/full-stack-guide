# Adapter selection and progressive loading

Adapters contain technology-specific guidance; Core contains portable rules. Load the minimum adapter set needed for the requested change.

Start at `../adapters/INDEX.md`, which maps detection signals to adapter files. To add support for another technology, copy `../adapters/_template.md`.

## Selection protocol
1. Detect language/framework/database and installed versions from manifests, lockfiles, imports, runtime, and CI.
2. Confirm the adapter matches the actual code path. In a monorepo, choose per package/service.
3. Read only the relevant adapter references. A frontend-only change does not require backend details unless the contract crosses that boundary.
4. Treat examples as version-bound guidance, not commands to copy blindly. Verify against local conventions and official docs.
5. If a helper or pattern described by an adapter is absent, do not introduce it just to conform. Follow the closest maintained sibling or the simplest idiomatic pattern.
6. When no adapter exists, Core + repo evidence + official docs remain sufficient for a careful implementation. Do not claim comprehensive coverage of an unsupported technology.

## Included adapter packs
- `../adapters/laravel-next/`: specific Laravel API + Next.js App Router conventions retained from v3.3.0.
- `../adapters/framework-families/`: progressive orientation guides for common backend, frontend, and database families. These guide detection and decision-making; exact APIs must be verified for the installed version.

The existence of an adapter never overrides explicit user instructions, security, data integrity, or established public contracts.
