# Unischedule

Unischedule is a Django 5 + Django REST Framework monolith for managing academic schedules and publishing curated views to public display screens.

## Project Overview
- Custom user model ties each account to an `Institution`, providing a simple multi-tenant boundary for all domain objects.
- Domain models such as courses, professors, classrooms, semesters, sessions, cancellations, makeups, and display screens inherit shared conventions for timestamps and soft deletion.
- API responses are normalized through a single helper to keep success and error payloads consistent across apps.
- Display payloads are cached per screen slug so kiosks can poll lightweight JSON feeds without recomputing filters on each request.

## Key Features
- **Institution-scoped authentication:** `accounts.User` extends Django's `AbstractUser` with a foreign key to `Institution`, ensuring every request can be constrained to the caller's institution.
- **Soft deletion with audit fields:** `BaseModel` and `ActiveManager` add `created_at`/`updated_at` timestamps, an `is_deleted` flag, and a manager that hides deleted rows while still allowing access via `objects_with_deleted`.
- **Uniform API envelopes:** `BaseResponse` centralizes success/error helpers and pagination so view functions only provide payload data and codes.
- **Schedule conflict detection:** `schedules` services validate that class sessions do not overlap for the same professor or classroom before persisting changes, and invalidate display caches after modifications.
- **Cancellations and makeups:** Dedicated models capture single-day cancellations and compensatory sessions so displays can merge base schedules with adjustments.
- **Display filtering and caching:** Display screens store filter rules (day-of-week, week type, building, course, professor, time ranges, etc.). Public payloads are cached under `display:<slug>` for the configured `refresh_interval`.
- **Postman cleaner utility:** `scripts/clean_postman_fragments.py` removes `StartFragment`/`EndFragment` markers from exported Postman collections for cleaner documentation.

## Architecture / Structure
- Each app follows a consistent layout: `models` define data structures, `repositories` encapsulate queryset logic, `serializers` validate and shape payloads, `services` host business rules, and `views` expose DRF endpoints.
- The core layer (`unischedule/core`) provides shared building blocks such as the base model, response helpers, and domain-specific success/error codes.
- URL routing under `unischedule/urls.py` mounts each app under `/api/...`, plus a public `/displays/<slug>/` namespace for anonymous display feeds.

## How It Works
- **Authentication:** DRF Token Authentication is enabled by default. Authenticated endpoints use the token to resolve the associated institution and enforce scope. CORS is open for all origins to support kiosk or SPA clients.
- **Request flow:** Views are intentionally thin; they validate authentication, delegate to services, and wrap results with `BaseResponse`. Services perform validation, conflict checks, cache invalidation, and call repositories for database access.
- **Display payloads:** Public display requests resolve the target screen by slug, compute day/week filters (or override by date), merge base sessions with cancellations and makeups, sort results, and cache the serialized payload for reuse.

## Requirements & Dependencies
- Python environment with the packages listed in `requirements.txt`, including Django 5.2.4, Django REST Framework 3.16.0, `django-cors-headers`, and `rest_framework.authtoken`.

## Configuration
- Default database is SQLite (`db.sqlite3`); change `DATABASES` in `unischedule/settings.py` for other backends.
- `DEBUG` is enabled and `ALLOWED_HOSTS` is empty by default; adjust for production deployments.
- Time zone defaults to `Asia/Tehran` with timezone-aware datetimes enabled.
- `AUTH_USER_MODEL` is set to `accounts.User`.
- Static/media handling uses `MEDIA_URL` and `MEDIA_ROOT = BASE_DIR / 'media'` when `DEBUG` is on.

## How to Run / Use
1. Create and activate a virtual environment.
2. Install dependencies: `pip install -r requirements.txt`.
3. Apply migrations: `python manage.py migrate`.
4. Create an admin user (optional): `python manage.py createsuperuser`.
5. Start the development server: `python manage.py runserver`.
6. Authenticate via `/api/auth/login/` to obtain a token, then pass `Authorization: Token <value>` to access protected endpoints.
7. Public display payloads are available without authentication at `/displays/<slug>/`.

## Notes & Limitations
- Cache invalidation for display screens relies on Django's configured cache backend; the default in settings will store entries in process memory.
- Schedule and display services assume each request provides an institution context; attempts without it raise structured validation errors.
- The provided `db.sqlite3` is suitable for local development only.
