# Frontend: Svelte and SvelteKit

Orientation for Svelte apps, mostly SvelteKit. Follow the repository's Svelte generation (stores vs runes) and routing setup.

## Detection
- `package.json`: `svelte`, `@sveltejs/kit`, adapter packages; `svelte.config.js`.
- Routes under `src/routes` with `+page.svelte`, `+page.ts`, `+page.server.ts`, `+layout*`, `+server.ts`; `src/hooks.server.ts`; `$lib` alias.
- Svelte 5 runes (`$state`, `$derived`, `$props`) vs Svelte 4 stores and `export let`.
- Tests: Vitest with Testing Library, Playwright.

## Idioms
- Server-only data and secrets stay in `+page.server.ts`, `+server.ts`, `hooks.server.ts`, and `$lib/server`, never in universal `load` functions or components.
- Use form actions for mutations when the project does, returning field errors with `fail(...)`.
- Authentication and session handling in `hooks.server.ts`; authorization re-checked in server `load` functions and actions.
- Public vs private environment modules (`$env/static/public` vs `private`).
- Sanitize anything rendered with `{@html}`.

## Pitfalls
- Importing a server-only module into code that ships to the browser.
- Using browser-only APIs during server rendering.
- Mixing reactivity models between Svelte 4 and 5 in one component.
- Data loaded in a universal `load` that should be private.
- Assuming a `load` result is fresh after a mutation without invalidating it.
- Disabling the framework's CSRF/origin protections to make a request pass.

## Design quality
For new UI, new screens, copy, states, or accessibility, also follow `../../../references/frontend-design-quality.md`; the repository's existing design system takes precedence.

## Verify
Read `scripts` in `package.json`: typically `npm run check` (svelte-check), lint, unit tests, and `build`; Playwright if configured.

## Version-sensitive
Check installed versions: Svelte 4 vs 5 (runes, event syntax, component API), SvelteKit 1 vs 2 changes, adapter packages, and the Vite major version.
