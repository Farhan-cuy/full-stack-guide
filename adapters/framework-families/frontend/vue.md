# Frontend: Vue and Nuxt

Orientation for Vue 3 applications (plain Vue with Vite, or Nuxt). Follow the API style already used in the repository.

## Detection
- `package.json`: `vue`, `nuxt`, `vue-router`, `pinia` (or `vuex` in older projects), `vite`; single-file components (`*.vue`).
- API style per file: Composition API with `<script setup>` or Options API; do not mix styles in one component.
- Nuxt: `nuxt.config.*`, `pages/`, `server/`, composables such as `useFetch` / `useAsyncData`.
- Tests: Vitest with Vue Test Utils, Playwright, or Cypress.

## Idioms
- Props down, events up; keep stores (Pinia) for state that is truly shared.
- Put data fetching in composables or the project's API layer; reuse existing ones.
- Nuxt: use the framework's data-fetching helpers with stable keys so server-rendered data hydrates correctly; separate private and public runtime config.
- Validate forms with the project's library and mirror server validation; surface server field errors.
- Sanitize anything rendered with `v-html`.

## Pitfalls
- Losing reactivity by destructuring reactive objects or props (use `toRefs` / `storeToRefs` or access through the object).
- Mutating props; missing or unstable `v-for` keys.
- Watchers and async calls without cleanup or cancellation.
- Browser-only code running during server rendering; hydration mismatches.
- Client-exposed environment prefixes (`VITE_`, public runtime config) used for secrets.
- Router guards used as the only access control.

## Design quality
For new UI, new screens, copy, states, or accessibility, also follow `../../../references/frontend-design-quality.md`; the repository's existing design system takes precedence.

## Verify
Read `scripts` in `package.json`: lint, `vue-tsc --noEmit` (or `nuxi typecheck`), unit tests, build. Run end-to-end tests when available.

## Version-sensitive
Check installed versions: Vue 2 vs 3 (Options vs Composition, Vuex vs Pinia, `v-model` changes), Nuxt 2/3/4 conventions, Vue Router majors, Pinia API differences, and Vite major versions.
