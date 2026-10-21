# Frontend: React and Next.js

Orientation for React applications, with and without Next.js. Follow the repository's router, data layer, and component conventions.

## Detection
- `package.json`: `react`, `next` (App Router uses `app/`; Pages Router uses `pages/`), or a Vite/CRA setup.
- Data layer: SWR, TanStack Query, RTK Query, Apollo, or plain `fetch`; forms: React Hook Form, Formik; validation: zod, yup.
- Component library and styling: shadcn/Radix, MUI, Tailwind, CSS modules.
- Tests: Vitest or Jest with Testing Library; Playwright or Cypress for end to end.

## Idioms
- Route all server calls through the project's existing API client; do not scatter `fetch` calls with duplicated headers and URLs.
- Next.js App Router: decide per component whether it is a server or client component (data sensitivity, interactivity, freshness); keep server-only values out of client code.
- Cache invalidation follows the data library's documented API for the installed version; the cache key must include every parameter that changes the result.
- Model loading, empty, error, success, pending, and disabled states; keep user input when a submit fails; show field-level server validation errors.
- Preserve existing design tokens, components, and accessibility patterns.

## Pitfalls
- Environment variables that are exposed to the browser (for example those with a public prefix) used for secrets; such values are fixed at build or start time.
- Browser-only APIs (`window`, `localStorage`) used during server rendering, causing hydration mismatches.
- Hooks reading search parameters may need a Suspense boundary during static rendering in some versions.
- Stale closures in effects; missing dependency arrays; effects that fetch without cancellation.
- Treating "promise resolved" as "operation succeeded" when the client helper does not throw on error statuses.
- Closing a dialog before knowing the submit succeeded; double submits.
- Relying on client-side route guards for security; the server must enforce access.
- Rendering untrusted HTML without sanitizing.

## Design quality
For new UI, new screens, copy, states, or accessibility, also follow `../../../references/frontend-design-quality.md`; the repository's existing design system takes precedence.

## Verify
Read `scripts` in `package.json`, then typically: the lint script, `npx tsc --noEmit` (needed when the build ignores type errors), the unit/component tests, and the production build. Run end-to-end tests if present and the environment supports them.

## Version-sensitive
Check installed versions before relying on: Next.js 13/14/15 differences (async request APIs such as `params`, `cookies()`, `headers()`, and fetch caching defaults), React 18 vs 19, TanStack Query v4 vs v5 names, SWR 1 vs 2 mutation APIs, zod 3 vs 4 schema options, and the notification or toast library's promise API.
