# Unischedule

Unischedule is a Django 5 application with Django REST Framework that centralizes university timetables and publishes filtered, cacheable feeds for public displays. It ships with an institution-aware user model, uniform API envelopes, and services that keep display payloads in sync whenever schedules change.

## Project Overview
- **Purpose:** Manage academic schedules per institution, then expose curated, cacheable JSON feeds for kiosks or signage screens.
- **System type:** Backend REST API with a small public feed surface; no front-end assets are included.
- **Core domain:** Institutions own professors, courses, classrooms, semesters, and display screens that consume the schedule data.

## Quickstart
1. Create and activate a Python 3.12+ virtual environment.
2. Install dependencies: `pip install -r requirements.txt`.
3. Apply migrations against the bundled SQLite database: `python manage.py migrate`.
4. (Optional) Create a superuser for the Django admin: `python manage.py createsuperuser`.
5. Run the API locally: `python manage.py runserver 0.0.0.0:8000`.
6. Obtain a token via `POST /api/auth/login/` and send it as `Authorization: Token <value>` for protected routes.
7. Public display feeds are readable without authentication at `/displays/<slug>/`.

## Key Concepts & Capabilities
- **Institution-scoped authentication:** Custom `accounts.User` attaches every user to an `Institution`, enabling tenant-aware queries throughout the API surface.【F:accounts/models.py†L1-L24】
- **Consistent persistence model:** `BaseModel` layers timestamps, soft deletion, and paired managers so default querysets only return active rows.【F:unischedule/core/base_model.py†L1-L58】
- **Uniform response envelope:** `BaseResponse` provides success/error helpers and pagination that wrap all API payloads with `success`, `code`, `message`, `data`, and `meta` fields.【F:unischedule/core/base_response.py†L1-L122】【F:unischedule/core/base_response.py†L124-L195】
- **Schedule conflict checks:** Session creation and updates validate overlaps for professors/classrooms/semesters before saving and invalidate any related display caches afterward.【F:schedules/services/class_session_service.py†L1-L93】【F:schedules/services/class_session_service.py†L95-L167】
- **Display feeds with rich filters:** Display screens persist building/classroom/course/professor/semester filters, automatic day/week detection, time windows, and layout metadata; a slug and access token are generated automatically.【F:displays/models/display_models.py†L1-L136】【F:displays/models/display_models.py†L138-L214】
- **Cached public payloads:** Public endpoints serve paginated session data per display slug and refresh cache entries when display or schedule data changes.【F:displays/views/display_views.py†L1-L128】【F:displays/services/display_service.py†L1-L107】

## Repository Structure
| Path | Responsibility |
| --- | --- |
| `manage.py` | Django entry point for running the server and admin tasks. |
| `unischedule/` | Project settings, URL routing, and shared utilities (base model, response helpers, logical codes). |
| `accounts/` | Custom user model plus login/logout/password change endpoints. |
| `institutions/` | Institution CRUD and logo handling. |
| `semesters/` | Academic term definitions. |
| `professors/`, `courses/` | Faculty and course catalogs referenced by schedules. |
| `locations/` | Buildings and classrooms used when scheduling sessions and displays. |
| `schedules/` | Class sessions, cancellations, makeups, and cache invalidation hooks for displays. |
| `displays/` | Display screen definitions, payload builders, and public/private endpoints. |
| `scripts/` | Utility scripts such as cleaning exported Postman collections. |
| `requirements.txt` | Python dependencies for the project. |

## How It Works
- **API surface:** All application endpoints live under `/api/...` (e.g., `/api/auth/login/`, `/api/schedules/...`); public display feeds are exposed separately under `/displays/<slug>/`. URL routing is centralized in `unischedule/urls.py`.【F:unischedule/urls.py†L17-L48】
- **Authentication and permissions:** DRF token authentication is enabled globally with `IsAuthenticated` as the default permission; only explicit public views (e.g., display feeds) opt into `AllowAny`.【F:unischedule/settings.py†L19-L76】【F:unischedule/settings.py†L84-L110】
- **Domain lifecycle:** Services validate institution context, run serializers, enforce time-conflict rules, and soft-delete instead of hard-deleting records. Related display caches are invalidated on schedule changes to keep kiosk payloads current.【F:schedules/services/class_session_service.py†L19-L135】
- **Display payload generation:** Public display requests fetch the screen by slug, assemble sessions using the screen’s filters (day/week detection, time range, group code, capacity, activation flags), and paginate results while returning screen metadata alongside the session list.【F:displays/views/display_views.py†L89-L128】【F:displays/services/display_service.py†L1-L107】
- **Caching:** Display payloads are cached per slug; updates to screens, sessions, cancellations, or makeups purge the associated cache key (`display:<slug>`) before rebuilding.【F:displays/services/display_service.py†L70-L105】【F:schedules/services/class_session_service.py†L95-L167】

## Usage Examples
- **Authenticate and retrieve a token:**
  ```bash
  curl -X POST http://localhost:8000/api/auth/login/ \
       -H 'Content-Type: application/json' \
       -d '{"username": "admin", "password": "..."}'
  ```
  Responses follow the standard envelope and include `data.token` on success.【F:accounts/views/auth_view.py†L12-L61】

- **Fetch a public display feed (no auth required):**
  ```bash
  curl http://localhost:8000/displays/<slug>/
  ```
  The response is paginated (`meta.total_pages`, `meta.current_page`) and contains `sessions` plus display metadata (title, layout, refresh interval).【F:displays/views/display_views.py†L89-L128】

## Configuration & Defaults
- **Database:** SQLite (`db.sqlite3`) is the default datastore configured in settings; change `DATABASES` for production use.【F:unischedule/settings.py†L58-L76】
- **Debug mode:** `DEBUG=True` with empty `ALLOWED_HOSTS`; tighten these before deployment.【F:unischedule/settings.py†L17-L36】
- **Time zone:** Application uses `Asia/Tehran` and timezone-aware datetimes.【F:unischedule/settings.py†L100-L108】
- **Static/media:** When `DEBUG` is on, media is served from `/media/` with files stored under `media/`.【F:unischedule/settings.py†L92-L99】【F:unischedule/urls.py†L50-L52】
- **CORS:** All origins are allowed to simplify kiosk or SPA access during development.【F:unischedule/settings.py†L112-L123】
- **Authentication/permissions:** Token authentication and `IsAuthenticated` permissions are global defaults; override per view where public access is required.【F:unischedule/settings.py†L112-L123】

## Notes & Limitations
- Models use soft deletion; archived rows remain in the database but are hidden from the default manager unless `objects_with_deleted` is used.【F:unischedule/core/base_model.py†L31-L58】
- Institution context is mandatory for most operations; missing institutions raise structured validation errors surfaced through the API envelope.【F:schedules/services/class_session_service.py†L11-L37】【F:displays/services/display_service.py†L29-L53】
- The included SQLite database and open CORS configuration are development conveniences and should be replaced or hardened for production deployments.【F:unischedule/settings.py†L58-L76】【F:unischedule/settings.py†L112-L123】
