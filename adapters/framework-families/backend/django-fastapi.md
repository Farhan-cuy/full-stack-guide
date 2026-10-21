# Backend: Python (Django, Django REST Framework, FastAPI)

Orientation for Python web backends. Django is batteries-included; FastAPI is a typed, dependency-injected ASGI framework. Follow the one in the repository.

## Detection
- Dependencies in `pyproject.toml`, `requirements*.txt`, or lockfiles (`poetry.lock`, `uv.lock`, `Pipfile.lock`).
- Django: `manage.py`, `settings.py`, `urls.py`, `models.py`, `migrations/`; DRF if `rest_framework` is installed.
- FastAPI: `FastAPI(` application object, `APIRouter`, `Depends(...)`; Pydantic models; SQLAlchemy/SQLModel; Alembic migrations.
- Tests: `pytest`, Django's test runner, `httpx`/`TestClient`.

## Idioms
- Django/DRF: validation in serializers or forms; permissions in permission classes; `get_queryset()` scoped to the requesting user or tenant; `transaction.atomic`, `select_for_update`, and `F()` expressions for atomic updates; `select_related`/`prefetch_related` against N+1.
- FastAPI: request and response Pydantic models; `response_model` to control what leaves the API; `Depends` for authentication, authorization, and the database session; one session per request.
- Business rules in a service or use-case module that both the transport layer and tests can call.
- Migrations reviewed as code; data migrations kept separate from schema changes.

## Pitfalls
- `get_object_or_404(Model, pk=pk)` or `Model.objects.all()` in a view without an ownership or tenant filter.
- Returning a model or ORM object without a serializer or `response_model`, leaking fields.
- Blocking calls (database, HTTP, file) inside `async def` endpoints; or mixing sync and async sessions incorrectly.
- Naive vs timezone-aware datetimes; mutable default arguments; `Decimal` vs `float` for money.
- Pydantic v1 vs v2 API differences; SQLAlchemy 1.x vs 2.0 query style.
- Relying on `DEBUG=True` behavior, or hard-coded `ALLOWED_HOSTS` / CORS settings that differ between environments.

## Verify
Check the project's task runner, `pyproject.toml`, or CI first. Typical:
- `pytest` (or `python manage.py test`)
- Django: `python manage.py check`, `python manage.py makemigrations --check --dry-run`
- `ruff check` / `flake8`, `mypy` or `pyright` if configured
- Alembic: apply migrations on a scratch database

## Version-sensitive
Check installed versions: Django LTS vs latest, DRF version, FastAPI/Starlette (lifespan handling), Pydantic v1 vs v2, SQLAlchemy 1.4 vs 2.0, Python version features. Use `pip show <pkg>` and read the installed source.
