# Unischedule

Unischedule is a Django 5 + Django REST Framework monolith for managing university schedules and publishing filtered, cacheable feeds for public displays. The project ships with a custom user model tied to institutions, uniform API envelopes, and services that keep display payloads in sync whenever schedules change.

## Overview
- **Institution-scoped authentication:** `accounts.User` extends Django's `AbstractUser` with an `institution` relation so every request can be constrained to a tenant.
- **Consistent models:** `BaseModel` adds timestamps, a soft-delete flag, and paired managers (`objects` vs `objects_with_deleted`) that hide archived rows by default.
- **Shared response contract:** `BaseResponse` provides success/error helpers and paginated responses so all endpoints emit the same envelope and metadata.
- **Schedule lifecycle:** Class sessions enforce conflict checks for professors/classrooms, support cancellations and makeup sessions, and invalidate any display caches that might be affected.
- **Display feeds:** Display screens store filters (day/week rules, building/classroom, course, professor, time range, capacity, etc.) and expose a public `/displays/<slug>/` JSON feed that is cached under `display:<slug>`.

## Application map
| App | Responsibility |
| --- | --- |
| `accounts/` | Token-based login/logout/password change plus the custom `User` model tied to an `Institution`. |
| `institutions/` | CRUD for institutions and logo management. |
| `semesters/` | Manage academic terms and mark the active semester per institution. |
| `professors/`, `courses/` | Faculty and course catalogs used by schedules. |
| `locations/` | Buildings and classrooms referenced by sessions and display filters. |
| `schedules/` | Class sessions with conflict detection, cancellations, and makeup sessions; cache invalidation for impacted displays. |
| `displays/` | Display screen definitions, filtered payload generation, and public, unauthenticated feeds backed by Django's cache. |
| `unischedule/core/` | Cross-cutting concerns: base model, response helpers, logical success/error codes, and shared exceptions. |
| `scripts/` | Utility scripts such as cleaning exported Postman collections. |

## API behavior
- **Routing:** API endpoints live under `/api/...` (e.g., `/api/auth/login/`, `/api/schedules/...`), while public display payloads are served from `/displays/<slug>/`.
- **Authentication:** DRF Token Authentication is enabled by default; unauthenticated access is allowed only for explicit public endpoints (e.g., display feeds). CORS is open to all origins for kiosk/SPA clients.
- **Responses:** All views return the `BaseResponse` envelope with `success`, `code`, `message`, `data`, optional `warnings`, and `meta` for pagination.
- **Pagination:** `BaseResponse.paginate_queryset` wraps DRF's page number pagination with configurable `page_size` and includes totals, current page, navigation links, and timestamps.

## Scheduling and display flow
- **Creating/updating sessions:** Session serializers validate input, enforce an institution context, and reject overlaps for the same professor/classroom/semester/day/time/week type. On save or soft delete, related display caches are invalidated to keep public feeds current.
- **Cancellations & makeups:** `ClassCancellation` records single-day skips; `MakeupClassSession` stores compensatory meetings with their own time/classroom/group code. Both adjustments are merged into display payloads.
- **Display filters:** Each display screen can scope results by semester, course, professor, building/classroom, day of week (including auto-detect), week type, date override, time window, group code, capacity threshold, and activation flags. Titles, layout theme, refresh interval, and per-filter durations are persisted alongside an auto-generated slug and access token.
- **Caching strategy:** Public payloads are cached per screen slug; any changes to sessions, cancellations, makeup sessions, or display settings clear the corresponding cache entries.

## Running locally
1. Create and activate a Python 3.12+ virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Apply migrations against the bundled SQLite database:
   ```bash
   python manage.py migrate
   ```
4. (Optional) Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```
5. Start the development server:
   ```bash
   python manage.py runserver
   ```
6. Authenticate via `/api/auth/login/` to obtain a token and include it in `Authorization: Token <value>` for protected routes. Public display feeds require only the screen slug.

## Utilities
- **Postman collection:** `Unischedule API.postman_collection.json` contains sample requests for the API surface. The `scripts/clean_postman_fragments.py` helper strips `StartFragment`/`EndFragment` artifacts from exported collections:
  ```bash
  python scripts/clean_postman_fragments.py Unischedule\ API.postman_collection.json
  ```

## Configuration & defaults
- Database defaults to SQLite (`db.sqlite3`).
- `DEBUG` is enabled; `ALLOWED_HOSTS` is empty. Adjust before deploying.
- Time zone is set to `Asia/Tehran` with timezone-aware datetimes.
- Static/media paths default to `MEDIA_URL=/media/` and `MEDIA_ROOT=media/` when `DEBUG` is on.
- Django cache settings control display payload storage; the default in-memory backend is sufficient for local testing.

## Notes and limitations
- All domain models use soft deletion; deleted rows remain in the database but are hidden from default querysets.
- Institution context is mandatory for most operations; missing institutions raise structured validation errors.
- The included SQLite database is intended for development only. Configure `DATABASES` for production use.
