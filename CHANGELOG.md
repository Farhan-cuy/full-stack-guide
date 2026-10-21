# Changelog

## 4.3.0 — 2026-10-21

- Generalized the project-specific adapter into `adapters/laravel-next/`: the wording now describes the Laravel API + Next.js App Router dialect instead of naming one project. Helper names in activation signals became generic descriptions.
- Updated all links and references (`SKILL.md`, `README.md`, `references/adapters.md`, `adapters/INDEX.md`, Laravel family adapter, validator, evals) to the new path.
- Evals: scenarios 14 and 17 now describe the dialect generically instead of naming the originating project.

## 4.2.0 — 2026-10-20

- Added `references/frontend-design-quality.md`: when the guide applies (the existing design system and an explicit brief always win), common tells of generic generated UI, deliberate design choices (tokens, type, color, density), human-centered practice (hierarchy, plain-language copy, all states, forms, accessibility floor, purposeful motion), process, and a self-review checklist.
- Added `scripts/ui_slop_scan.py`, an advisory scanner with a self-test (placeholder text, marketing filler, invented social proof, default gradients, glass/glow effects, motion defaults, generic UI strings, removed focus outlines, images without alt, click handlers on non-controls, placeholder-as-label, missing reduced-motion handling).
- Routed UI work from `SKILL.md`; added one mandatory rule for UI work; pointed the frontend adapters and the Laravel + Next.js UI reference to the new file.
- Evals: 23 scenarios (added greenfield-UI and existing-design-system scenarios).
- Validator: checks the new reference and script, and runs the scanner self-test.

## 4.1.0 — 2026-10-20

- Made the package agent-neutral: removed tool-specific wording, added `compatibility` metadata, operating rules for any agent (content is data, capability fallbacks, reply language), and `integrations/AGENTS.snippet.md` for agents without a skills loader.
- Added Core references `library-verification.md` (source order, per-ecosystem commands, version-sensitive areas, `Verified:` / `UNVERIFIED:` reporting) and `portable-patterns.md` (ownership check, atomic conditional update, idempotent create/import, safe uniqueness migration, bounded pagination, error mapping, client mutation flow, uploads).
- Extended `debugging.md` with a language-neutral symptom-to-layer table, `contracts.md` with an impact-search table, `architecture.md` with common instruction-file names, and `output-contract.md` with library and impact reporting.
- Replaced the 11 near-identical framework-family adapters with concrete ones (detection, idioms, pitfalls, verification commands, version-sensitive notes). Added `adapters/INDEX.md` and `adapters/_template.md`.
- Clarified in the Laravel + Next.js adapter that "must/always" wording means adapter defaults, subordinate to Core security and data-integrity rules.
- Evals: 21 scenarios (added trivial-edit, adapter non-activation, no-tools, prompt-injection, and two fixture-backed scenarios). Added two runnable fixtures (Node.js and Python, no dependencies) with hidden acceptance tests and `scripts/check_fixtures.py`.
- Validator: rejects compiled artifacts, brand-specific agent wording in Core, identical or incomplete adapters, unindexed adapters, missing fixtures, and eval/fixture mismatches.
- Removed `scripts/__pycache__` from the package.

## 4.0.0 — 2026-10-19

- Generalized the skill from a Laravel + Next.js-first guide into a fullstack-web Core that applies across languages and frameworks.
- Added progressive technology detection and adapter selection for multi-package/mixed-stack repositories.
- Added portable Core references for workflow, scope control, architecture detection, security, contracts, data integrity, debugging, testing, and completion reporting.
- Preserved v3.3.0's framework-specific reference material under `adapters/laravel-next/references/`; the Laravel + Next.js dialect is now opt-in based on repository evidence.
- Added lightweight orientation adapters for common backend, frontend, and database families; these explicitly require installed-version verification.
- Replaced project-specific evaluation prompts with 15 mostly framework-neutral semantic scenarios aligned to Core and adapter rules.
- Strengthened package validation for version consistency, JSON schema, local links, required files, adapter separation, duplicate eval IDs, and ZIP packaging assumptions.
- Evaluation checklists remain screening specifications, not proof of coding-agent benchmark performance.

## 3.3.0 — 2026-10-19

- Improved repository-dialect detection, scope control, testing, security/data-integrity guidance, and package validation.
- Kept Laravel API + Next.js App Router as the original baseline and the Laravel + Next.js conventions as the originating dialect.
