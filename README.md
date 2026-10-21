# Fullstack Engineering Guide v4.3.0

Framework-agnostic, agent-agnostic guidance for fullstack web engineering. A portable Core (workflow, scope control, security, contracts, data integrity, debugging, testing, reporting, library verification) plus optional technology adapters that are loaded only when repository evidence matches.

It follows the open Agent Skills layout (`SKILL.md` with `name` and `description`, plus supporting files), so it works with any coding agent that supports skills, and with any other agent through a short pointer in the repository's instruction file.

## Package layout
- `SKILL.md`: router, priorities, operating rules for any agent, mandatory rules.
- `references/`: portable Core, including `library-verification.md`, `portable-patterns.md`, and `frontend-design-quality.md` (avoiding generic UI, human-centered design).
- `adapters/INDEX.md`: detection signal to adapter map. `adapters/_template.md`: how to add one.
- `adapters/framework-families/`: orientation for Laravel, Go, Node (Express/Nest), Python (Django/FastAPI), Java/.NET, React/Next.js, Vue/Nuxt, Svelte/SvelteKit, Angular, relational and document databases. Each has detection signals, idioms, pitfalls, verification commands, and version-sensitive notes.
- `adapters/laravel-next/`: opt-in Laravel API + Next.js App Router conventions (Indonesian), used only for repositories that really follow them.
- `integrations/AGENTS.snippet.md`: copy-paste block for agents without a skills loader.
- `evals/`: 23 scenarios and two runnable fixtures with hidden acceptance tests.
- `scripts/validate_package.py`, `scripts/check_fixtures.py`, `scripts/ui_slop_scan.py`: standard-library checks. The UI scanner is advisory: it flags placeholder text, marketing filler, default gradients, motion defaults, and common accessibility slips, and cannot judge design quality.

## Install
Keep the whole folder together. Put it where your agent loads skills from; the cross-agent convention is `.agents/skills/fullstack-engineering-guide/` at the repository root, and several agents also read their own directories (for example `.claude/skills/` or `.github/skills/`). These locations are still evolving, so confirm the current path in your agent's documentation.

If your agent has no skills loader (or you want reliable activation), copy `integrations/AGENTS.snippet.md` into the repository's instruction file (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.github/copilot-instructions.md`, `.cursor/rules/`, and so on) and point `<path>` at this folder.

Then validate:
```
python scripts/validate_package.py
python scripts/check_fixtures.py
```

## Design principles
Core rules are portable and tool-neutral: the guide never requires a particular tool, and it tells the agent what to do when it cannot run commands or reach documentation (`NOT RUN` / `UNVERIFIED`). Repository evidence, actual contracts, and official documentation for the installed versions outrank generic examples. Adapters are optional and version-sensitive. Unsupported stacks still use Core and the nearest sibling.

## Limits
Validation checks structure, metadata, links, adapter separation, and fixture behavior. It does not prove that an agent writes correct code. The scenarios are screening specifications; only the two fixture scenarios have mechanical grading, and they exercise a small slice of the guide.
