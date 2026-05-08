# TODO.md — Smart Agriculture Project Progress Log

> **Purpose:** This is a living document. Claude Code updates this file after every task.
> **Format:** Each task has a checkbox, a date when completed, and optional notes.
> **Do not modify CLAUDE.md** — that file holds architectural decisions only.
>
> Last updated: 2026-05-02 (Sprint 5 COMPLETE)
> Active sprint: Sprint 5 — Frontend dashboard + device + rule UI
> Days until deadline: ~45 (June 15, 2026 target)
> Sprint 1: COMPLETE ✓ | Sprint 2: COMPLETE ✓ | Sprint 3: COMPLETE ✓ | Sprint 4: COMPLETE ✓

---

## How Claude Code should use this file

After completing any task, Claude Code should:

1. Move the completed item from `📋 Up next` (or wherever it was) to `✅ Done` with the date and a one-line note describing what was done and any noteworthy detail.
2. Add new items to `📋 Up next` if the completed task surfaced new work.
3. Add notes to `⚠️ Known issues / notes` if anything tricky was discovered (e.g., a config quirk, a workaround, a thing the human should know).
4. Update `🔄 In progress` if work was started but not finished, with a note about where to resume.
5. Update the `Last updated` date at the top.

Keep entries terse. This is a log, not a journal.

---

## ✅ Done

### Project planning
- [x] **2026-04-26** — Architecture, ERD, API endpoints, sprint plan finalized via design discussion
- [x] **2026-04-26** — `CLAUDE.md` master design document created
- [x] **2026-04-26** — `TODO.md` progress log initialized

### Sprint 0 — Setup & infrastructure
- [x] **2026-04-26** — Git repository initialized (done in earlier session)
- [x] **2026-04-26** — `.gitignore` created — covers Python, Node.js, Docker runtime dirs, IDE, secrets, export files
- [x] **2026-04-26** — `README.md` created — project overview, tech stack, quickstart (manual + docker compose), project structure
- [x] **2026-04-26** — `.env.example` created — Django, DB, Redis, Celery, MQTT, JWT, CORS, Next.js, weather, SMTP, export, logging
- [x] **2026-04-26** — Monorepo folder structure created — backend (config, 12 apps, tests, static), frontend (app, components, lib, hooks, types, tests), simulator, docker, docs; `.gitkeep` added to all empty dirs
- [x] **2026-04-26** — `docker-compose.yml` written — db (TimescaleDB pg16), redis (7-alpine), mosquitto (2); healthchecks + named volumes
- [x] **2026-04-26** — `docker/timescaledb/init.sql` created — CREATE EXTENSION timescaledb
- [x] **2026-04-26** — `docker/mosquitto/mosquitto.conf` + `acl.conf` + `passwd` created; healthcheck fixed (mosquitto_pub instead of mosquitto_sub)
- [x] **2026-04-26** — All three infra services verified healthy: TimescaleDB, Redis, Mosquitto
- [x] **2026-04-26** — Django backend initialized with Poetry; settings split (base/development/production); all 12 app skeletons created; `manage.py check` passes (0 issues); Django 5.2.13
- [x] **2026-04-26** — Next.js 15 frontend initialized (TypeScript strict, Tailwind, ESLint, App Router); TanStack Query, Recharts, React Hook Form, Zod, shadcn/ui installed; button/card/input/badge components added
- [x] **2026-04-26** — ESLint + Prettier configured (single quotes, no semi, trailing commas, prettier-plugin-tailwindcss)
- [x] **2026-04-26** — Husky + lint-staged configured at repo root; pre-commit runs Black/Ruff on backend, Prettier/ESLint on frontend
- [x] **2026-04-26** — Hello world verified: Next.js Server Component fetches Django /api/health/ → "ok" displayed in browser

---

## 🔄 In progress

_Nothing yet. The first task is to set up the repository._

---

## 📋 Up next

### Sprint 0 — Setup & infrastructure (target: 27 Apr – 3 May)

- [x] Initialize git repository at the project root
- [x] Create `.gitignore` for Python, Node.js, Docker, IDE artifacts
- [x] Create top-level `README.md` with project description and quickstart commands
- [x] Create `.env.example` with all required environment variables (DB url, Redis url, MQTT credentials, JWT secret, Open-Meteo settings)
- [x] Set up monorepo folder structure: `backend/`, `frontend/`, `simulator/`, `docker/`, `docs/` (per `CLAUDE.md` section 3)
- [x] Write `docker-compose.yml` orchestrating: PostgreSQL/TimescaleDB, Redis, Mosquitto
- [x] Configure TimescaleDB init script: `CREATE EXTENSION timescaledb`
- [x] Configure Mosquitto base config + empty ACL file (mounted as volume)
- [x] Verify `docker-compose up` brings up all infra services cleanly
- [x] Initialize Django backend with Poetry (`pyproject.toml`, base settings split)
- [x] Install backend dependencies: Django 5, DRF, django-channels, celery, paho-mqtt, psycopg, redis, drf-spectacular, simplejwt, django-filter, scikit-learn, pandas, openpyxl
- [x] Configure Black + Ruff in `pyproject.toml`
- [x] Initialize Next.js 15 frontend with TypeScript strict mode and Tailwind CSS
- [x] Install frontend dependencies: shadcn/ui CLI + base components, TanStack Query, Recharts, React Hook Form, Zod
- [x] Configure ESLint + Prettier for frontend
- [x] Set up Husky + lint-staged at the repo root (runs Black/Ruff on backend changes, Prettier/ESLint on frontend)
- [x] Create a "hello world" verification: Next.js page calls a Django endpoint that returns `{"status": "ok"}`
- [x] First commit pushed to git

### Sprint 1 — Database + Auth (target: 4 – 10 May)

- [x] **2026-04-26** — All Django models defined: accounts (User/Role/FarmMembership), farms (Farm/Crop), devices (Device/DeviceCapability), sensor_data (SensorReading/DeviceTelemetry), rules (Rule/RuleCondition/RuleAction/RuleWeatherConstraint), commands (Command), weather (WeatherCache), fertilization (FertilizationRecommendation/FertilizationHistory), notifications (Notification), predictions (Prediction), audit (AuditLog) — 20 models across 11 apps; AUTH_USER_MODEL set
- [x] **2026-04-26** — All models registered in Django admin (inline inlines for Device→Capabilities, Rule→Conditions/Actions/WeatherConstraint; AuditLog is read-only in admin)
- [x] **2026-04-26** — Initial migrations generated for all apps; circular FK in FarmMembership resolved via 0001+0002 split; `commands_either_rule_or_user` CHECK constraint included in commands/0001_initial.py; `manage.py check` passes 0 issues
- [x] **2026-04-26** — Custom hypertable migrations written: `sensor_data/0002_hypertables.py` (sensor_readings + device_telemetry + sensor_readings_hourly continuous aggregate), `audit/0002_hypertable.py` (audit_logs + 2-year retention policy); composite PK (time, id) added per TimescaleDB requirement
- [x] **2026-04-26** — Indexes on hypertables defined in model Meta.indexes (already in 0001_initial): `idx_readings_device_time (device, -time)`, `idx_readings_capability_time (capability_type, -time)`, `idx_telemetry_device_time`, `idx_audit_time`, `idx_audit_user_time`
- [x] **2026-04-26** — JWT already configured in base.py (access 15 min, refresh 7 days, rotate+blacklist); simplejwt + token_blacklist in INSTALLED_APPS
- [x] **2026-04-26** — Auth endpoints implemented: `LoginView` (TokenObtainPairView subclass), `RefreshView`, `LogoutView` (blacklists refresh token), `MeView` (GET returns user+memberships, PATCH updates profile); mounted at `/api/v1/auth/`
- [x] **2026-04-26** — `IsFarmMember` permission class implemented (`apps/accounts/permissions.py`); also added `IsFarmManager` (read=any member, write=farm_manager/system_admin only); checks `farm_id` URL kwarg or `obj.farm` for object-level
- [x] **2026-04-26** — All models registered in Django admin (done in models task above)
- [x] **2026-04-26** — `seed_data` management command written (`manage.py seed_data [--reset]`): 3 roles, admin+farmer1 users, 3 crops (Domates/Buğday/Marul with realistic NPK ranges), 2 farms (Akdeniz Çiftliği/Ege Tarlaları), 5 devices with capabilities
- [x] **2026-04-26** — Frontend: login page — React Hook Form + Zod v4 client-side validation, calls `/api/auth/login` route handler, redirects to `/farms` on success
- [x] **2026-04-26** — Frontend: HttpOnly cookie auth flow — `app/api/auth/login/route.ts` proxies Django JWT response, sets `access_token` + `refresh_token` as HttpOnly cookies; logout route blacklists refresh token and clears cookies
- [x] **2026-04-26** — Frontend: route protection via `proxy.ts` (Next.js 16 renamed `middleware.ts` → `proxy.ts`); `/farms/*` guarded, unauthenticated users redirected to `/login`; authenticated users redirected away from `/login`
- [x] **2026-04-26** — Frontend: `(dashboard)/layout.tsx` server component reads access token cookie, calls Django `/api/v1/auth/me/`, renders sidebar + header with user display name + logout button; `/farms/page.tsx` placeholder added
- [x] **2026-04-26** — pytest tests for auth flow: 15 tests covering login (success/wrong-password/unknown/missing-fields), refresh (success/invalid/missing), logout (blacklist/requires-auth/missing-token/double-blacklist), /me/ (GET/PATCH/requires-auth/expired-token); 24/24 passed
- [x] **2026-04-26** — pytest tests for `IsFarmMember` and `IsFarmManager`: 9 tests covering view-level allow/deny, unauthenticated deny, no-farm-id deferral, object-level (device.farm, direct farm obj, non-member deny), manager write vs farmer read-only; 24/24 passed

### Sprint 2 — MQTT pipeline + sensor simulator (target: 11 – 17 May)

- [x] **2026-04-27** — Mosquitto TLS: self-signed CA + server cert generated (`docker/mosquitto/certs/`); `mosquitto.conf` updated with dual listener (1883 plain + 8883 TLS); certs mounted as read-only volume in docker-compose
- [x] **2026-04-27** — Mosquitto passwd + ACL updated: hashes generated for backend, device-sensor-001/002, device-valve-001; ACL restricts each device to its own topic subtree per CLAUDE.md §6.7
- [x] **2026-04-27** — MQTT Worker implemented: `apps/mqtt_worker/runner.py` (django.setup, paho-mqtt subscribe to telemetry/status/commands/ack) + `apps/mqtt_worker/validator.py` (NFR-04: range checks, timestamp validation); paho-mqtt v2 CallbackAPIVersion.VERSION2
- [x] **2026-04-27** — DB writes: valid telemetry → `sensor_readings` + `device_telemetry`; ack → `commands.status` + `executed_at`; `device.last_seen_at` + `device.status` updated on every valid telemetry
- [x] **2026-04-27** — `evaluate_rules_task` placeholder added (`apps/rules/tasks.py`); fires `task.delay(reading_id)` after each successful sensor write; full rule logic deferred to Sprint 3
- [x] **2026-04-27** — Celery worker + Beat + MQTT worker + Django web added as Docker Compose services; `backend/Dockerfile` created; all services share `.env` and depend on db/redis health
- [x] **2026-04-27** — Sensor simulator implemented: `simulator/simulator.py` + `simulator/config.yaml` (3 devices: 2 sensors + 1 valve); per-capability drift + noise; LWT → `{"status":"offline"}`; actuator subscribes to commands and publishes ACK; env vars override config.yaml MQTT host/port/cert for Docker
- [x] **2026-04-27** — `simulator/Dockerfile` created (lightweight: pip install paho-mqtt pyyaml); simulator service added to docker-compose
- [x] **2026-04-27** — Uplink path verified: test telemetry message → MQTT Worker → sensor_readings (3 rows) + device_telemetry (battery+rssi) + device.status=online + device.last_seen_at updated; all in < 1s
- [x] **2026-04-27** — Offline detection verified: status message handler updates device.status online→offline correctly; LWT mechanism handled identically to explicit status publish

### Sprint 3 — Rule engine + weather + actuators (target: 18 – 24 May)

- [x] **2026-05-01** — `apps/weather/services.py`: Open-Meteo client with Redis cache (1h TTL), WeatherCache DB fallback; `get_weather_forecast()` and `get_max_rain_probability()` helpers
- [x] **2026-05-01** — `apps/weather/tasks.py`: `fetch_weather_for_all_farms` Celery Beat task (hourly); skips farms without coordinates
- [x] **2026-05-01** — `apps/audit/services.py`: `write_audit_log()` helper; non-blocking, swallows errors so audit failures never break main flows
- [x] **2026-05-01** — `apps/commands/services.py`: `publish_command()` creates Command row and publishes to MQTT via `paho.mqtt.client`; sets status=FAILED if MQTT unreachable
- [x] **2026-05-01** — `apps/rules/tasks.py`: full `evaluate_rules_task` implementation — AND-condition evaluation, weather constraint check (FR-03), 5-minute anti-flood guard, audit log on every action; weather unavailable = safe side (sula)
- [x] **2026-05-01** — `apps/devices/tasks.py`: `check_offline_devices` Beat task (every 5 min, FR-06); bulk-creates Notification for farm members on device ONLINE→OFFLINE transition
- [x] **2026-05-01** — `config/settings/base.py`: `CELERY_BEAT_SCHEDULE` added for `fetch-weather-hourly` (3600s) and `check-offline-devices-5min` (300s); scheduler switched to `celery.beat.PersistentScheduler`
- [x] **2026-05-01** — `pyproject.toml`: `requests ^2.31` added (required by Open-Meteo client)
- [x] **2026-05-01** — `tests/test_rules.py`: 14 pytest tests covering operator evaluation, single/multi condition, inactive rule skip, weather cancellation (FR-03), weather unavailable fallback, anti-flood guard, multi-action rules; MQTT mocked via `_publish_mqtt`
- [x] **2026-05-01** — Actuator simulator already complete from Sprint 2 (valve subscribes to commands, publishes ACK)

### Sprint 4 — REST APIs + notifications + WebSocket (target: 25 – 31 May)

- [x] **2026-05-01** — DRF ViewSets + serializers for all CRUD endpoints: farms, crops, devices, capabilities, sensor_data, rules, commands, fertilization, notifications, predictions, audit (`manage.py check` → 0 issues)
- [x] **2026-05-01** — Nested write serializer for rule creation: RuleSerializer.create/update handles conditions + actions + weather_constraint in one POST; sentinel `...` used to distinguish null vs. absent weather_constraint on PATCH
- [x] **2026-05-01** — `/sensor-data/timeseries/` endpoint using raw SQL + TimescaleDB `time_bucket`; aggregation whitelist prevents SQL injection
- [x] **2026-05-01** — `drf-spectacular` already wired; Swagger UI at `/api/schema/swagger-ui/` reachable
- [x] **2026-05-01** — Django Channels channel layer already configured (Redis, base.py); `asgi.py` updated with JWTAuthMiddleware + WebSocket routing
- [x] **2026-05-01** — `apps/websocket/middleware.py`: JWTAuthMiddleware reads `?token=` query param, resolves User via AccessToken
- [x] **2026-05-01** — `apps/websocket/consumers.py`: FarmLiveConsumer (`/ws/farms/{farm_id}/live/`) + NotificationConsumer (`/ws/notifications/`); membership check on connect; handlers for `sensor_reading`, `command_status`, `notification` events
- [x] **2026-05-01** — MQTT Worker broadcasts sensor readings to `farm-{farm_id}` channel group via `async_to_sync(channel_layer.group_send)` after each DB write
- [x] **2026-05-01** — `apps/notifications/services.py`: `create_notification()` helper; broadcasts to `user-{id}` WebSocket group; swallows channel layer errors
- [x] **2026-05-01** — Rate limiting on `/auth/login/`: `django-ratelimit` `@method_decorator(ratelimit(...), name="dispatch")` on LoginView, 5 req/15min per IP; package was already in pyproject.toml
- [x] **2026-05-01** — CORS already configured in base.py (`CORS_ALLOWED_ORIGINS` from env); `.env` created from `.env.example` with Docker hostnames
- [x] **2026-05-01** — `poetry.lock` regenerated (requests dep added in Sprint 3 but lock wasn't updated); image builds and `manage.py check` passes
- [x] **2026-05-01** — `apps/notifications/tasks.py`: `send_notification_email` Celery task; retries up to 3x on SMTP failure; skips users without email address
- [x] **2026-05-01** — `apps/exports/models.py`: ExportJob model (UUID job_id, format, filters JSON, status, file_path, row_count, expires_at); migration generated
- [x] **2026-05-01** — `apps/exports/tasks.py`: `generate_export_async` (pandas CSV/Excel writer, sets expires_at=+7d) + `cleanup_expired_export_jobs` (deletes files + DB rows)
- [x] **2026-05-01** — Export endpoints: `POST /exports/sensor-data/{csv|excel}/` (sync < 10k rows → FileResponse; async ≥ 10k → 202 + job_id), `GET /exports/{job_id}/status/`, `GET /exports/{job_id}/download/`
- [x] **2026-05-01** — `cleanup-expired-exports-daily` Beat schedule added (86400s); `config/urls.py` updated with exports URLs; `manage.py check` → 0 issues

### Sprint 5 — Frontend dashboard + device + rule UI (target: 1 – 7 June)

- [x] **2026-05-01** — Set up Next.js layout: `Sidebar` (Client, usePathname, farm list + per-farm nav), `NotificationBadge` (Client, initialCount prop), `QueryProvider` (TanStack Query root wrapper); `lib/api.ts` serverFetch helper; `types/api.ts` shared types; `/farms/[farmId]/*` stub pages (Özet/Cihazlar/Kurallar/Gübreleme/Raporlar); `(dashboard)/layout.tsx` parallel-fetches me+farms+unread-count
- [x] **2026-05-01** — Implement farms list page (`/farms`) with farm cards
- [x] **2026-05-02** — Implement main dashboard page (`/farms/[farmId]`) — CurrentReadingsWidget, WeatherWidget (graceful fallback if no endpoint), RecentCommandsWidget, ActiveNotificationsWidget; all TanStack Query client components with skeleton loading + error states
- [x] **2026-05-02** — Each dashboard widget fetches its own endpoint via TanStack Query (per D-04); `app/api/backend/[...path]/route.ts` generic proxy + `lib/client-api.ts` clientFetch helper
- [x] **2026-05-02** — Implement Recharts time-series chart with selectable capability and date range — `SensorChartWidget` (Recharts 3 LineChart, capability dropdown, 24h/7d/30d toggle, avg+min+max lines, skeleton/error/empty states; TypeScript strict ✓)
- [x] **2026-05-02** — Implement `useFarmLiveData(farmId)` hook that opens WebSocket and updates TanStack Query cache on incoming messages — `hooks/useFarmLiveData.ts` (sensor_reading → setQueryData, command_status/notification → invalidateQueries, 3s auto-reconnect); `/api/auth/token` route handler exposes HttpOnly cookie token to client; `FarmLiveDataSync` invisible Client wrapper mounted in dashboard page; TypeScript strict ✓
- [x] **2026-05-02** — Implement device list page with status indicators (online / offline / low battery) — `devices/page.tsx` Client Component; status badge, type badge, last_seen relative time, capabilities list; create modal (name/uid/type/location) + delete confirm modal; TanStack Query mutations
- [x] **2026-05-02** — Implement device detail page with health stats and reading history — `devices/[deviceId]/page.tsx`; battery % (color-coded), RSSI, uid, location cards; latest readings grid; SensorChartWidget reused; manual command panel
- [x] **2026-05-02** — Implement device CRUD modals (create, edit, delete) — create + delete modals in devices page; inline overlay pattern (no shadcn Dialog dependency)
- [x] **2026-05-02** — Implement rule list page — `rules/page.tsx`; shows conditions → actions → weather constraint summary; toggle active/passive; delete with confirm
- [x] **2026-05-02** — Implement rule create / edit form (multi-step or expandable: conditions → actions → weather constraint) — single modal with add/remove conditions & actions rows, weather constraint checkbox (FR-03)
- [x] **2026-05-02** — Implement manual irrigation / actuator panel (US-02): pick device, choose action, confirm — `ManualCommandPanel` inside device detail; action select + duration input; POST to `/devices/{id}/commands/`
- [x] **2026-05-02** — Implement notifications drawer with mark-as-read + filter by severity — `NotificationsDrawer.tsx`; severity filter tabs (all/info/warning/critical); mark single + mark all read
- [x] **2026-05-02** — Implement notification badge in header (uses `/notifications/unread-count/` + WebSocket updates) — `NotificationBadge.tsx` updated; opens drawer on click; QueryCache subscription refreshes count on any notification cache change
- [x] **2026-05-02** — Make UI responsive enough for laptop demo — flex-wrap + grid-cols responsive classes throughout all new pages; modals scroll on small viewports

### Sprint 6 — Fertilization, ML, reports, polish (target: 8 – 14 June)

- [ ] Implement `generate_weekly_fertilization_recommendations` Celery Beat task: aggregate last 7 days NPK + pH per farm, compare to crop optima, create recommendations
- [ ] Implement urgent recommendation logic: if any nutrient drops below critical threshold during the week, create urgent recommendation immediately
- [ ] Implement ML prediction module: simple linear regression on historical sensor data to predict yield per farm
- [ ] Implement second prediction: optimal next irrigation time based on moisture trend and weather forecast
- [ ] Implement `run_ml_predictions` Celery Beat task (daily)
- [ ] Frontend: fertilization page — recommendations list with apply / dismiss buttons, history table, manual logging form
- [ ] Frontend: predictions widget on main dashboard
- [ ] Frontend: reports page — date range picker, capability picker, device picker, export button (CSV / Excel)
- [ ] Frontend: audit log viewer page (admin only) with filters
- [ ] Add bug fix pass: try every user story end-to-end and fix issues
- [ ] Add UX polish: loading skeletons, empty states, error toasts
- [ ] Write `docs/deployment.md` with `docker-compose up` instructions
- [ ] Write `docs/presentation.md` with jury talking points
- [ ] Prepare demo seed data: realistic farm with 7 days of historical readings, 3 active rules, a few notifications
- [ ] Final commit + tag `v1.0`

---

## ⚠️ Known issues / notes

- **`poetry.lock` updated** — Sprint 3 added `requests` but lock wasn't regenerated. Fixed: ran `poetry lock` in a temp container. Image now builds cleanly.
- **Export sync path re-queries data** — `ExportRequestView` calls `_query_sensor_data` twice (once to count, once in `_serve_sync`). This is intentional simplicity; for very large datasets the async path takes over at 10k rows anyway.
- **Export file permissions** — `EXPORT_ROOT` defaults to `/app/exports` in Docker. Ensure this path is writable in the container (add a volume mount if needed in docker-compose.yml before demo).
- **`apps/websocket/` is a plain module** (not in INSTALLED_APPS) — consumers and middleware don't need models, so no app registration needed.
- **`django-ratelimit` on DRF views** — applied via `@method_decorator(ratelimit(...), name="dispatch")` on LoginView. When rate limit exceeded, raises `PermissionDenied` (403). Frontend should show a friendly message.
- **WebSocket broadcast in MQTT Worker** — uses `async_to_sync` from `asgiref`. If Redis channel layer is unavailable, a warning is logged but the telemetry write still succeeds.

- **`NEXT_PUBLIC_BACKEND_WS_URL` env var** — WebSocket base URL; varsayılan `ws://localhost:8000`. Docker ortamında `.env` dosyasına `NEXT_PUBLIC_BACKEND_WS_URL=ws://localhost:8000` ekle (Daphne 8000 portunda çalışıyor).
- **`/api/auth/token` route** — HttpOnly cookie'deki erişim tokenını istemci JS'e açar; sadece WebSocket bağlantısı için kullanılır (kısa ömürlü, 15 dk).

- **`requests` added to pyproject.toml** — run `poetry lock --no-update && poetry install` inside the backend container (or rebuild) to pick up the new dependency.
- **Celery Beat scheduler changed** — switched from `django_celery_beat.schedulers:DatabaseScheduler` to `celery.beat.PersistentScheduler` so `CELERY_BEAT_SCHEDULE` in settings takes effect. `django_celery_beat` stays in INSTALLED_APPS for migrations but the database-driven UI is no longer the scheduler source.
- **Weather cache requires farm coordinates** — farms without `latitude`/`longitude` skip Open-Meteo fetches. Update seed data farm coordinates if needed.
- **Rule engine anti-flood cooldown is 5 minutes** — same rule + device combination won't fire more than once per 5 min. Adjust `_already_fired_recently(minutes=5)` if needed.
- **Weather unavailable = sula (don't cancel)** — if Open-Meteo is unreachable and no DB cache exists, weather constraints are ignored and irrigation proceeds. This is the designed safe-side behavior.

- **Glob tool finds no files under migrations/ on Windows** — use PowerShell `Get-ChildItem -Recurse` to list migration files; Glob uses Unix forward-slash paths and misses nested dirs on this Windows setup.
- **`makemigrations` background output** — PowerShell commands run as background tasks; check task output files at `C:\Users\omen\AppData\Local\Temp\claude\...` if output appears empty.
- **Next.js 16 breaking change: `middleware.ts` → `proxy.ts`** — function must be named `proxy` (not `middleware`); defaults to Node.js runtime (not Edge). The `frontend/AGENTS.md` enforces reading the bundled docs before writing any Next.js code.
- **No token refresh yet** — when the 15-minute access token expires, the dashboard layout redirects to `/login`. A refresh token proxy will be added in Sprint 4.



- **Mosquitto passwd file:** `docker/mosquitto/passwd` is a placeholder. Before running `docker compose up`, generate the real hash: `docker run --rm eclipse-mosquitto:2 mosquitto_passwd -b /dev/stdout backend <your-password>` and replace the file content. Mosquitto will refuse to start with the placeholder.
- **Mosquitto ACL needs SIGHUP after edit, not restart** — the `regenerate_mosquitto_acl` Celery task will send SIGHUP to the broker container when a new device is registered.
- **farm_id in MQTT topics = DB farm.id** — simulator `config.yaml` and Mosquitto ACL use `farm_id: 3` because that's the ID seed_data assigned to "Akdeniz Çiftliği" (IDs 1–2 were used and deleted). If DB is reset with `seed_data --reset`, IDs will increment; update config.yaml and ACL accordingly.
- **Redis host port mapping** — after `docker compose up -d mosquitto` only recreates mosquitto, Redis may lose its host port mapping. Run `docker compose up -d --no-deps redis` to fix. Permanent fix comes when all services run inside Docker.
- **evaluate_rules_task.delay() wrapped in try/except** — if Celery/Redis is unreachable, a warning is logged but sensor data still gets written. This is by design for resilience.
- **Mosquitto healthcheck:** `mosquitto_sub -C 1` on `$SYS/#` times out; use `mosquitto_pub` to test auth+connectivity instead.

---

## 🔮 V2 backlog (out of scope for now)

These are explicitly **not** in scope for the school project. Listed here so they aren't forgotten if the project continues.

- Mobile application (React Native or Flutter)
- Real hardware integration (ESP32 + actual soil sensors)
- `crop_growth_stages` table for stage-aware recommendations
- Multi-language UI (i18n with English + Turkish)
- Image-based disease detection (CV model)
- SMS / WhatsApp notifications
- Production deployment (Kubernetes, managed Postgres, Cloudflare R2 for exports)
- Self-registration with email verification
- Customizable email templates
- Advanced ML: deep learning yield models with weather + satellite data
- Historical weather data backfill (NASA POWER API)
- Multi-farm dashboards (compare farms side by side)
- Audit log export
- Admin analytics dashboard (system-wide stats)
