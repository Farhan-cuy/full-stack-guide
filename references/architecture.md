# Architecture and technology detection

## Detect before prescribing
1. Read repository-level instructions and workspace/monorepo layout. Common instruction files include `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.cursor/rules/`, `.cursorrules`, `.github/copilot-instructions.md`, `.windsurfrules`, `CONTRIBUTING.md`, the README, and `docs/`. Whichever your environment does not load automatically, read if present. Where they conflict with each other, follow the most specific and most recent, and report the conflict.
2. Inspect manifests and lockfiles to identify languages, frameworks, versions, package managers, and test tools. Examples: `package.json` and lockfiles; `pyproject.toml`/lockfiles; `go.mod`; `Cargo.toml`; `composer.json`; build files for Java/.NET; infrastructure manifests.
3. Identify frontend, backend, API, persistence, jobs, and deployment boundaries only where relevant. A repository may use several languages or frameworks.
4. Confirm actual usage from source imports, entry points, routes, build scripts, tests, and CI. A dependency being installed does not prove it is the right pattern for the touched code.
5. Select a matching adapter only when both technology and version/context match. Load only the references needed for the task.

## When no adapter matches
Use Core principles, copy the closest maintained sibling pattern, consult official documentation for the installed version, and implement the smallest conventional solution. State uncertainty when evidence is insufficient. Never fabricate framework APIs or assume an adapter exists.

## Architecture decisions
Choose boundaries based on domain complexity, ownership, side effects, deployment, and testability—not file count or fashion. Keep UI, transport, domain/use-case logic, and persistence responsibilities clear where the project already separates them. Do not force a layered architecture onto a small project without need.

## Monorepos and mixed stacks
Treat each package/service as its own context while preserving cross-package contracts. Check workspace commands and shared types. Do not apply one framework's conventions to another package merely because they live in the same repository.
