# Backend: Go HTTP services

Orientation for Go services. Go projects vary widely in structure; follow the repository's own layout.

## Detection
- `go.mod` (module path and `go` directive), `go.sum`; entry in `main.go` or `cmd/<name>/`.
- Router in use: standard library `net/http` (Go 1.22+ method and wildcard patterns), `chi`, `gin`, `echo`, or `fiber`.
- Data access: `database/sql` with a driver, `pgx`, `sqlc` output, `gorm`, or `ent`. Migrations: `golang-migrate`, `goose`, `atlas`, or SQL files.
- Build and task entry points: `Makefile`, `Taskfile`, CI workflow.

## Idioms
- Keep handlers thin: decode and validate, call a use-case or service, map errors to responses.
- Pass `context.Context` from the request into every database and outbound call; honor cancellation and timeouts.
- Return errors; wrap with `%w`; use sentinel or typed errors and map them to status codes in one place.
- Decode JSON defensively: `http.MaxBytesReader`, `DisallowUnknownFields` where the contract is strict, and validate the decoded struct.
- Transactions: begin, `defer tx.Rollback()`, commit at the end; pass the transaction handle explicitly to the functions that must share it.
- Authentication in middleware, putting identity into the context; authorization checked in the use-case with that identity and the object being accessed.
- Table-driven tests with the standard `testing` package; `net/http/httptest` for handlers.

## Pitfalls
- Ignored errors (`_ = ...`) and missing `rows.Err()` / `rows.Close()`.
- Goroutines that outlive the request, or that ignore context cancellation.
- Shared mutable state without synchronization (maps are not safe for concurrent writes).
- A nil slice encodes as JSON `null`, an empty slice as `[]`; clients often treat these differently.
- Money in `float64`; use integer minor units or a decimal library.
- Returning early inside a transaction without rolling back, or holding a transaction open across slow external calls.
- Loop-variable capture in closures and goroutines before Go 1.22 semantics.
- Building SQL by string concatenation; use placeholders.

## Verify
- `go build ./...`, `go vet ./...`, `gofmt -l .`
- `go test ./...` (add `-race` where the platform supports it for concurrency-related changes)
- The repository's linter if configured (for example `golangci-lint run`)
- Run database-backed tests against the same engine as production when the change touches queries or locking

## Version-sensitive
Check `go.mod` and `go version`: loop-variable semantics and `ServeMux` patterns changed in Go 1.22, generics availability, standard-library additions, and each third-party router or ORM major version. Use `go list -m <module>` and `go doc` for the installed API.
