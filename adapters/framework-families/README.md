# Framework-family adapters

Each file is an orientation guide for one technology family: how to detect it, what idiomatic code looks like, common pitfalls, how to verify, and what changes between versions. They are not API manuals. Select one only after detection (see `../INDEX.md`), and verify version-sensitive APIs against the installed package and official documentation (`../../references/library-verification.md`).

- `backend/`: Laravel, Go, Node (Express/Fastify/Koa/NestJS), Python (Django/DRF/FastAPI), Java/.NET
- `frontend/`: React/Next.js, Vue/Nuxt, Svelte/SvelteKit, Angular
- `database/`: relational, document and key-value stores

Do not mix patterns across frameworks. If the project uses something not listed, apply Core and inspect the nearest maintained sibling. To add an adapter, copy `../_template.md`.
