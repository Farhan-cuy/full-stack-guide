# Cross-layer contracts

A contract includes more than an endpoint: request/response shape, types, validation, errors, authentication, pagination, ordering, side effects, and compatibility expectations.

- Establish the source of truth from API schemas, route handlers, DTOs/types, tests, generated clients, and current consumers. Do not assume documentation is current without checking.
- When changing a field or behavior, trace producer → transport → client type → UI/use site and any other consumers (jobs, integrations, mobile clients, scripts).
- Preserve public contracts by default. If a breaking change is required, explain migration/versioning and obtain approval where appropriate.
- Keep validation and error semantics consistent. Distinguish authentication, authorization, validation, conflict, not-found, rate-limit, and server/network failures when the system does.
- Avoid duplicate sources of truth and redundant DTOs/types unless they represent a real boundary or intentionally different view.
- For asynchronous/event-driven systems, document event schema, delivery guarantees, idempotency, ordering assumptions, and retry behavior when relevant.
- Never infer successful behavior from a type definition alone; verify runtime serialization and consumers when feasible.

## Impact search: what to look for when something changes
Search the whole repository (all packages) for consumers before finishing.

| Changed | Look for consumers in |
|---|---|
| Field in a response or serializer | client types, API client functions, UI components, mocks and fixtures, tests, mobile or other clients, exports and reports |
| Request validation rules or messages | client-side validation schemas, form components, tests, API documentation |
| Route path, method, or version | client call sites, tests, gateway/proxy config, docs, scheduled jobs |
| Roles, permissions, or tenant rules | route/middleware guards, client route guards (UX only), seeders and fixtures, tests |
| Error shape or status codes | client error handling, tests, monitoring or alert rules |
| Database column or table | models, serializers, import/export, seeders, factories, reports, raw queries |
| Environment variable or config key | example env files, deployment config, CI, both sides of the stack |
| Shared type or schema | every importer; run the type checker across packages |

A breaking change to something already published needs a new version or a migration plan, not an in-place edit.
