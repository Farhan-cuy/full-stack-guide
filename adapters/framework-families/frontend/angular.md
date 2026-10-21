# Frontend: Angular

Orientation for Angular applications. Follow the repository's component model (standalone vs NgModule) and state approach (signals vs RxJS).

## Detection
- `package.json`: `@angular/core`, `@angular/cli`, `rxjs`; `angular.json`; `src/app`.
- Standalone components (`standalone: true` or default in recent versions) vs `NgModule`s; control-flow syntax (`@if`) vs structural directives (`*ngIf`).
- Server rendering: Angular SSR or Universal configuration.
- Tests: Karma/Jasmine, Jest, or Vitest; Playwright or Cypress.

## Idioms
- Services with dependency injection wrap `HttpClient`; interceptors handle authentication headers and error mapping.
- Typed reactive forms; map server validation errors onto form controls.
- Route guards improve UX but are not security; enforce authorization on the server.
- Use the `async` pipe or signals for template data; unsubscribe or use `takeUntilDestroyed`.
- `OnPush` change detection where the project uses it.

## Pitfalls
- Subscription leaks; nested subscribes instead of operators.
- `any` returned from `HttpClient` calls instead of typed models.
- Bypassing the sanitizer (`bypassSecurityTrust*`) or binding untrusted HTML.
- Treating guards or hidden menu items as access control.
- Configuration that ends up in the client bundle (everything in environment files is public).
- Mixing signal-based and RxJS state without a clear boundary.

## Design quality
For new UI, new screens, copy, states, or accessibility, also follow `../../../references/frontend-design-quality.md`; the repository's existing design system takes precedence.

## Verify
Read `scripts` in `package.json`: typically `ng build`, `ng test` (non-watch mode in CI), `ng lint`, and `npx tsc --noEmit`; run end-to-end tests if configured.

## Version-sensitive
Check installed versions: standalone defaults, signals, new control-flow syntax, zoneless change detection, `HttpClient` setup (module vs `provideHttpClient`), and RxJS major version. Use `ng version` and the installed type definitions.
