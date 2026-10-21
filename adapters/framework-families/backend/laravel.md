# Backend: Laravel (PHP)

Orientation for Laravel APIs. If the repository also uses a shared Laravel + Next.js helper layer, load `../../laravel-next/README.md` as well; otherwise follow what the repository already does.

## Detection
- `composer.json` requires `laravel/framework` (note the major version); an `artisan` file at the root.
- Laravel 11+ style bootstrap in `bootstrap/app.php` (routing, middleware, exceptions configured there); older style has `app/Http/Kernel.php` and `app/Exceptions/Handler.php`.
- Routes in `routes/api.php` or `routes/web/**`; controllers in `app/Http/Controllers`; tests in `tests/` (Pest or PHPUnit).
- Auth package in use: Sanctum, Passport, Fortify, or session auth. Permissions: Spatie, policies and gates, or custom.

## Idioms
- Validate in Form Request classes (`rules()`), read data with `validated()`, not `all()`.
- Authorize with policies or gates (`authorize()`, `Gate::allows`, `can:` middleware). Route model binding finds the model; it does not prove the caller owns it.
- Shape output with API Resources instead of returning models directly.
- Mass assignment: explicit `$fillable` (or a deliberate `$guarded`); never pass raw request data to `create`/`update`.
- Put multi-step writes in `DB::transaction(...)`; for contended rows use `lockForUpdate()` or an atomic `update` with a condition.
- Queued jobs: design for retries (idempotent handlers, `ShouldBeUnique`, unique keys); check `tries`, `backoff`, and failure handling.
- Read configuration via `config()`; call `env()` only inside config files (it returns null once config is cached).

## Pitfalls
- `Model::findOrFail($id)` with no ownership or tenant scope exposes other users' rows.
- `DB::table(...)` and raw queries skip global scopes and model events.
- `firstOrCreate` / `updateOrCreate` are not atomic without a unique index; handle duplicate-key errors or use `upsert`.
- N+1 queries from missing `with()`; add `withCount()` for counts.
- Returning validation errors as redirects to API clients when the request does not ask for JSON.
- Exceptions thrown in a controller constructor happen before the action's try/catch and before route middleware has set the user.
- Running with `APP_DEBUG=true` outside local development leaks internals.

## Verify
Check the project's own scripts first (`composer.json` scripts, CI). Typical commands:
- `php artisan route:list` (confirm route, middleware, and names)
- `php artisan test`, or `vendor/bin/pest`, or `vendor/bin/phpunit`
- `vendor/bin/pint --test` or the configured code style tool; `vendor/bin/phpstan analyse` or Larastan if configured
- `php artisan migrate --pretend` to inspect SQL, and run migrations on a scratch database

## Version-sensitive
Check the installed version before using: Laravel 10 vs 11+ skeleton (Kernel/Handler vs `bootstrap/app.php`), where CORS and middleware are configured, default test runner, PHP language features by runtime version, Sanctum/Passport major versions, Spatie permission middleware syntax and guard configuration, `casts()` method vs `$casts` property, and queue driver behavior.
