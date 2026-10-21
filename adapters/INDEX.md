# Adapter index

Pick adapters from detection evidence, never from a guess. Load the smallest set that covers the task; in a monorepo choose per package. If nothing matches, use Core plus the nearest maintained sibling (see `../references/adapters.md`).

| Detection signal (confirm in source, not only in a manifest) | Adapter |
|---|---|
| `composer.json` requires `laravel/framework`; `artisan` file | `framework-families/backend/laravel.md` |
| ...and the repository also has shared API helpers (Form Request base class, response helper, typed fetch client, tenant global scope) | also `laravel-next/README.md` |
| `go.mod`; HTTP handlers in Go | `framework-families/backend/go.md` |
| `package.json` with `express`, `fastify`, `koa`, or `@nestjs/*` | `framework-families/backend/express-nest.md` |
| `manage.py` or `django` dependency; `FastAPI(` in source | `framework-families/backend/django-fastapi.md` |
| `pom.xml` / `build.gradle*` with Spring; `*.csproj` / `*.sln` with ASP.NET | `framework-families/backend/java-dotnet.md` |
| `react` / `next` dependencies; `app/` or `pages/` routes | `framework-families/frontend/react-next.md` |
| `vue` / `nuxt` dependencies; `.vue` files | `framework-families/frontend/vue.md` |
| `svelte` / `@sveltejs/kit`; `+page.svelte` files | `framework-families/frontend/svelte.md` |
| `@angular/core`; `angular.json` | `framework-families/frontend/angular.md` |
| SQL engine (PostgreSQL, MySQL/MariaDB, SQLite, SQL Server); migrations directory | `framework-families/database/relational.md` |
| MongoDB, Redis, DynamoDB, or similar stores | `framework-families/database/document.md` |
| None of the above | Core only; follow the nearest sibling and official docs |

Adapters never override explicit user instructions, security, data integrity, or established public contracts.
