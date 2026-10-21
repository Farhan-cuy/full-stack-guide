# Backend: Node.js (Express, Fastify, Koa, NestJS)

Orientation for Node HTTP backends. Express is minimal and unopinionated; NestJS imposes modules, providers, and decorators. Follow the one in the repository.

## Detection
- `package.json` dependencies: `express`, `fastify`, `koa`, or `@nestjs/*`; package manager from the lockfile (`package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`, `bun.lockb`).
- Entry points: `src/main.ts` (Nest), `app.js` / `server.js` / `src/index.ts`. Language: TypeScript (`tsconfig.json`) or JavaScript; module system ESM vs CommonJS (`"type"` in `package.json`).
- Data layer: Prisma, TypeORM, Sequelize, Drizzle, Knex, Mongoose, or raw drivers.
- Test runner: Jest, Vitest, Mocha, or `node --test`.

## Idioms
- Validate at the boundary with the project's tool (zod, joi, class-validator with Nest pipes); do not trust `req.body` types.
- One central error-handling middleware (Express) or exception filter (Nest); handlers throw typed errors rather than building responses.
- Authentication in middleware or a guard; authorization checks ownership or tenant per object in the service.
- Nest: controllers for transport, providers for use-cases, guards for access, pipes for validation, DTOs for shapes.
- Transactions through the ORM's API (for example Prisma's `$transaction`); keep external calls out of the transaction.
- Test HTTP behavior with the project's request-testing helper against the app instance, not only unit tests of services.

## Pitfalls
- A missing `await`, or an unhandled promise rejection, that turns into a hung request or a crash. In Express 4, errors thrown in async handlers are not forwarded to error middleware unless wrapped; Express 5 changes this.
- Middleware order mistakes (CORS, body parsing, auth, error handler placement).
- Spreading `req.body` into ORM calls (mass assignment) or into NoSQL queries.
- Sharing mutable module-level state across requests.
- Large integers and decimals handled as JavaScript numbers.
- CommonJS/ESM import mismatches that only appear at runtime or in the production build.
- Secrets or server-only values reaching a client bundle in a monorepo that shares config.

## Verify
Read the `scripts` in `package.json`, then typically:
- `npm test` (or the pnpm/yarn equivalent)
- `npm run lint`, `npx tsc --noEmit`, `npm run build`
- Run database-backed tests against a real engine matching production for query or transaction changes

## Version-sensitive
Check installed versions: Express 4 vs 5 behavior, Fastify and Koa majors, NestJS majors and decorators, Prisma/TypeORM/Sequelize major changes, Node.js LTS features, and ESM/CommonJS configuration. Read `node_modules/<pkg>/package.json` and its type definitions.
