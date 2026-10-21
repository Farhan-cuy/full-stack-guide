# Security baseline

Security is a Core requirement across frameworks and languages. Use the framework-specific adapter for exact APIs, but do not relax these principles.

- **Authentication is not authorization.** Enforce authorization on trusted server/service boundaries for every sensitive read and write. Check object ownership, tenant boundaries, and role/capability rules server-side.
- **Treat all external input as untrusted:** request bodies, query/path parameters, headers, cookies, uploaded files, webhooks, messages, environment/config values, and imported data. Validate shape, bounds, encoding, and business rules.
- **Prevent injection:** use parameterized queries and safe APIs; avoid shell/string evaluation and unsafe dynamic query construction. Escape output in the correct context.
- **Protect secrets:** never commit, log, return, or expose credentials/private keys/session tokens. Keep privileged secrets server-side; redact sensitive data from logs and error responses.
- **Session and token safety:** follow the actual auth architecture, secure cookie/CSRF settings where applicable, expiration/rotation/revocation requirements, and least privilege. Do not move tokens to weaker storage as a quick fix.
- **Uploads and downloads:** validate size and content, generate safe storage names, use private storage for sensitive files, and authorize each download. Never trust a client-provided path or MIME value alone.
- **Web boundaries:** configure CORS narrowly; use CSRF defenses when relevant; validate webhook signatures and replay protections where applicable. CORS is not authorization.
- **Abuse resistance:** rate-limit sensitive operations; bound pagination, file sizes, query complexity, retries, and resource consumption.
- **Errors:** return safe, consistent errors without stack traces, SQL, internal paths, secrets, or unnecessary existence leaks.
- **Dependencies and configuration:** avoid unnecessary packages; review permissions and production debug settings. Do not disable security controls to make a failing request work.

Add negative tests for unauthorized access, invalid input, and boundary conditions appropriate to the risk.

See `portable-patterns.md` §1 (ownership), §6 (error mapping), and §8 (uploads) for neutral sketches.
