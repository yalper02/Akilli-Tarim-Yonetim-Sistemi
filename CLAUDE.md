# CLAUDE.md — Smart Agriculture Management System

> **Purpose of this file:** This is the master design document for the project. Claude Code reads this at the start of every session to understand the architecture, technology choices, and design decisions. **Do not modify this file unless an architectural decision changes.** For day-to-day progress tracking, use `TODO.md`.

---

## 1. Project Overview

### 1.1 What we are building

A **Smart Agriculture Management System** that uses IoT sensors to optimize irrigation and fertilization decisions on farms. The system collects soil moisture, temperature, pH, and NPK (nitrogen, phosphorus, potassium) readings, evaluates them against rules and weather forecasts, and either acts automatically (irrigation, fertigation pumps) or recommends actions to the farmer.

### 1.2 Target users

- **Farmer (`Çiftçi`):** Day-to-day operator, monitors dashboards, manually triggers irrigation
- **Farm manager (`Tarım yöneticisi`):** Sets rules, reviews recommendations, plans operations
- **System administrator (`Sistem yöneticisi`):** Manages devices, troubleshoots hardware

A single farm can have multiple managers. A user can have different roles on different farms.

### 1.3 Constraints

- **Deadline:** June 2026 (school project)
- **Scope:** No mobile app (deferred). No real hardware — sensor simulator only.
- **Deployment:** Local Docker Compose for demo/jury presentation. No production hosting.

**Language conventions:**

- **Conversation with the user (Muhammed):** Turkish. All chat replies, explanations, suggestions, and questions must be in Turkish.
- **Code comments and docstrings:** Turkish. Inline comments, function/class docstrings, and any explanatory notes inside source files must be in Turkish.
- **TODO.md updates:** English. Progress entries, task descriptions, and notes added to TODO.md remain in English.
- **CLAUDE.md (this file):** English. The architectural reference stays in English.
- **Variable, function, class, and module names:** English. Always. (e.g., `evaluate_rules_task`, `SensorReading`, `farm_memberships`)
- **File and directory names:** English. (e.g., `apps/rules/engine.py`, not `apps/kurallar/motor.py`)
- **Database table and column names:** English. (e.g., `sensor_readings.battery_level`, not `sensor_kayitlari.pil_seviyesi`)
- **API endpoint paths:** English. (e.g., `/api/v1/farms/`, not `/api/v1/tarlalar/`)
- **Git commit messages:** English (Conventional Commits). (e.g., `feat: add rule engine`, not `feat: kural motoru ekle`)
- **UI text shown to end users:** Turkish. (e.g., button labels, headings, messages, validation errors)
- **Log messages:** English. (Easier to search and share with English-speaking communities when troubleshooting.)

**Rationale:** Code stays internationally readable and grep-friendly. Comments and conversation stay accessible to the developer. UI stays accessible to the end user.

---

## 2. Technology Stack

### 2.1 Backend

| Component | Choice | Rationale |
|---|---|---|
| Language | Python 3.11+ | Domain ecosystem (Django, paho-mqtt, scikit-learn) |
| Web framework | Django 5.x | Built-in auth, ORM, admin, mature ecosystem |
| API framework | Django REST Framework (DRF) | Industry standard for Django APIs |
| WebSocket | Django Channels | Native ASGI integration with Django |
| Async tasks | Celery + Celery Beat | Periodic jobs, long-running tasks |
| Message queue | Redis | Celery broker + cache layer |
| MQTT client | paho-mqtt | Standalone worker process |
| MQTT broker | Mosquitto | Lightweight, mature, Docker-ready |
| Database | TimescaleDB (PostgreSQL extension) | Native time-series support, PG compatibility |
| Authentication | djangorestframework-simplejwt | JWT access + refresh tokens |
| API docs | drf-spectacular | OpenAPI 3 / Swagger UI auto-generation |
| ML | scikit-learn | Simple yield/irrigation prediction models |
| Package manager | Poetry | Lock file for reproducible builds |
| Formatter | Black | "No arguments" Python formatter |
| Linter | Ruff | Fast, all-in-one linter + import sorter |

### 2.2 Frontend

| Component | Choice | Rationale |
|---|---|---|
| Framework | Next.js 15 (App Router) | Modern React, SSR, file-based routing |
| Language | TypeScript (strict mode ON) | Type safety, better Claude Code output |
| Styling | Tailwind CSS | Utility-first, fast iteration |
| Components | shadcn/ui | Accessible, composable, Tailwind-native |
| Server state | TanStack Query (React Query) | Caching, refetch, optimistic updates |
| Charts | Recharts | React-native charting library |
| Forms | React Hook Form + Zod | Type-safe form validation |
| Package manager | npm | Standard, well-supported |
| Formatter | Prettier | Industry standard |
| Linter | ESLint (Next.js config) | Default + minor customization |

### 2.3 Infrastructure

| Component | Choice |
|---|---|
| Container orchestration | Docker Compose |
| Pre-commit hooks | Husky + lint-staged |
| Weather API | Open-Meteo (free, no API key) |
| Repo structure | Monorepo |

---

## 3. Repository Structure

```
akilli-tarim/
├── CLAUDE.md                  # This file (architecture reference)
├── TODO.md                    # Living progress log (Claude updates this)
├── README.md                  # Setup instructions for humans
├── docker-compose.yml         # Full stack orchestration
├── .env.example               # Environment variable template
├── .gitignore
│
├── backend/                   # Django + DRF + Channels
│   ├── pyproject.toml         # Poetry config
│   ├── poetry.lock
│   ├── manage.py
│   ├── config/                # Django project settings
│   │   ├── settings/
│   │   │   ├── base.py
│   │   │   ├── development.py
│   │   │   └── production.py
│   │   ├── urls.py
│   │   ├── asgi.py
│   │   ├── wsgi.py
│   │   └── celery.py
│   ├── apps/
│   │   ├── accounts/          # users, roles, memberships
│   │   ├── farms/             # farms, crops
│   │   ├── devices/           # devices, capabilities, telemetry
│   │   ├── sensor_data/       # readings (TimescaleDB hypertables)
│   │   ├── rules/             # rule engine + Celery task
│   │   ├── commands/          # MQTT commands history
│   │   ├── weather/           # Open-Meteo integration + cache
│   │   ├── notifications/     # in-app + email notifications
│   │   ├── fertilization/     # recommendations + history
│   │   ├── predictions/       # ML predictions
│   │   ├── audit/             # audit logs (TimescaleDB)
│   │   └── exports/           # CSV/Excel export
│   ├── tests/                 # pytest tests (critical paths)
│   └── static/
│
├── frontend/                  # Next.js 15 App Router
│   ├── package.json
│   ├── tsconfig.json
│   ├── next.config.ts
│   ├── tailwind.config.ts
│   ├── app/
│   │   ├── (auth)/
│   │   │   └── login/
│   │   ├── (dashboard)/
│   │   │   ├── farms/[farmId]/
│   │   │   │   ├── page.tsx           # main dashboard
│   │   │   │   ├── devices/
│   │   │   │   ├── rules/
│   │   │   │   ├── fertilization/
│   │   │   │   └── reports/
│   │   ├── api/                       # Next.js route handlers (proxy/edge if needed)
│   │   ├── layout.tsx
│   │   └── globals.css
│   ├── components/
│   │   ├── ui/                # shadcn/ui components
│   │   ├── charts/
│   │   ├── dashboard/
│   │   └── forms/
│   ├── lib/
│   │   ├── api.ts             # API client (fetch wrappers)
│   │   ├── auth.ts            # JWT handling
│   │   ├── ws.ts              # WebSocket client
│   │   └── utils.ts
│   ├── hooks/                 # custom React hooks (useFarmDashboard, etc.)
│   ├── types/                 # shared TypeScript types
│   └── tests/                 # Vitest tests
│
├── simulator/                 # Python sensor simulator
│   ├── pyproject.toml
│   ├── simulator.py
│   ├── config.yaml            # device list, capabilities, intervals
│   └── README.md
│
├── docker/
│   ├── mosquitto/
│   │   ├── mosquitto.conf
│   │   └── acl.conf           # per-device ACL rules
│   ├── timescaledb/
│   │   └── init.sql           # CREATE EXTENSION timescaledb
│   └── nginx/                 # reverse proxy (optional, for demo)
│
└── docs/
    ├── api.md                 # API endpoint reference
    ├── mqtt.md                # MQTT topic structure
    ├── deployment.md          # how to run the project
    └── presentation.md        # jury presentation talking points
```

---

## 4. System Architecture

### 4.1 Component overview

The system has six logical layers:

1. **IoT layer** — Sensor simulator (Python script), valve/pump simulators, third-party weather API
2. **Messaging layer** — Mosquitto MQTT broker (TLS-encrypted, per-device ACL)
3. **Backend services** — MQTT Worker (paho-mqtt), Django + DRF + Channels, Celery + Beat, rule engine (Celery task), ML module
4. **Data layer** — TimescaleDB (hypertables + relational), Redis (cache + Celery broker)
5. **Presentation layer** — Next.js 15 frontend (App Router, TanStack Query, Recharts)
6. **Users** — Farmer, farm manager, system administrator

### 4.2 Data flow: Automated irrigation (FR-01 → FR-03)

```
Sensor (simulator) → MQTT publish → Mosquitto broker
                                          ↓
                        MQTT Worker (paho-mqtt subscriber)
                                          ↓
                            Validate (NFR-04: reject -200°C, future timestamps, etc.)
                                          ↓
                            Write to sensor_readings (TimescaleDB hypertable)
                                          ↓
                            evaluate_rules_task.delay(reading_id)  ← Celery task
                                          ↓
                            (Celery worker picks up task)
                                          ↓
                            Load rule_conditions for this device
                                          ↓
                            Threshold check (e.g., soil_moisture < 30)
                                          ↓
                            If condition met → check rule_weather_constraints
                                          ↓
                            Read weather forecast from Redis cache
                                          ↓
                            If rain probability > threshold → cancel + log
                            Else → publish "open valve" command to MQTT
                                          ↓
                            Write commands record + audit_logs entry
                                          ↓
                            Valve simulator subscribes → executes → publishes ack
                                          ↓
                            MQTT Worker receives ack → updates command.status
                                          ↓
                            Channels broadcast → frontend updates live
```

### 4.3 Data flow: Manual irrigation (US-02)

```
Farmer clicks "Start irrigation" in Next.js dashboard
              ↓
POST /api/v1/devices/{id}/commands/  with body { action_type, parameters }
              ↓
Django view: check IsFarmMember permission
              ↓
Create commands record with triggered_by="manual", user_id=current_user
              ↓
Write audit_logs entry (user_id, ip_address, action_type)
              ↓
Publish MQTT command to broker
              ↓
(Same ack flow as automated path)
```

### 4.4 Data flow: Fertilization recommendation (weekly)

```
Celery Beat (every Monday 06:00)
              ↓
For each active farm:
              ↓
Read last 7 days of NPK + pH readings from sensor_readings
              ↓
Aggregate (avg, min, max) using TimescaleDB time_bucket
              ↓
Compare against farm.crop.optimal_* fields
              ↓
For each deficient nutrient:
    Create fertilization_recommendation
    (urgency=scheduled, status=pending, reasoning=auto-generated)
              ↓
If any nutrient is critically low → also create urgent notification
```

### 4.5 Rule engine architecture (key decision)

The rule engine is **not** an inline function in the MQTT Worker. It is a **Celery task** (`evaluate_rules_task`) that lives in `apps/rules/tasks.py`. This decision was made because:

1. **Two trigger paths converge:** Automatic (from MQTT Worker after writing reading) and manual (from Django view for ad-hoc commands). Both call the same Celery task.
2. **Worker stays fast:** Worker writes to DB, fires task into queue, immediately returns to listening. Heavy logic (weather lookup, ML calls) doesn't block MQTT consumption.
3. **Free retry mechanism:** Celery's `bind=True, max_retries=3` handles transient failures.
4. **Testable:** Task can be invoked directly in tests without spinning up the MQTT pipeline.

---

## 5. Database Schema

### 5.1 Tables overview

**Total: 18 tables (15 relational + 3 TimescaleDB hypertables)**

#### Identity & access
- `users` (Django built-in `auth_user`, extended)
- `roles`
- `farm_memberships` (M:N junction with role)

#### Domain
- `farms`
- `crops` (reference table with optimal moisture, temperature, pH, NPK ranges)
- `devices`
- `device_capabilities`

#### Time-series (HYPERTABLES)
- `sensor_readings` — all environmental measurements
- `device_telemetry` — battery + RSSI (FR-08)
- `audit_logs` — who did what when (FR-09)

#### Rule engine
- `rules`
- `rule_conditions`
- `rule_actions`
- `rule_weather_constraints` (1:0..1 with rules)

#### Operations
- `commands` (both rule-triggered and manual; CHECK constraint enforces XOR of `rule_id` and `user_id`)
- `weather_cache`

#### Decisions & feedback
- `fertilization_recommendations`
- `fertilization_history`
- `notifications`
- `predictions` (ML output)

### 5.2 Key schema decisions

#### `sensor_readings` is one wide table, not split per capability type

```
sensor_readings (HYPERTABLE)
├── time TIMESTAMPTZ NOT NULL  (partition key)
├── id BIGSERIAL
├── device_id INT FK
├── capability_type VARCHAR  (soil_moisture | temperature | humidity | ph_level | nitrogen_level | phosphorus_level | potassium_level)
├── value DOUBLE PRECISION
└── PRIMARY KEY (time, id)
```

Indexes:
- `(device_id, time DESC)` — for "latest reading per device"
- `(capability_type, time DESC)` — for capability-filtered queries

Splitting by capability type would create many tables with similar structure; TimescaleDB's automatic chunking on `time` already gives us the partitioning benefit.

#### `commands` uses a single table with CHECK constraint

```sql
CONSTRAINT commands_either_rule_or_user CHECK (
    (rule_id IS NOT NULL AND user_id IS NULL) OR
    (rule_id IS NULL AND user_id IS NOT NULL)
)
```

Allows simple "show last 10 commands for this device" queries without UNION across two tables.

#### `audit_logs` is a hypertable

Because audit entries are immutable, append-only, and queried by time range. TimescaleDB retention policy can drop old chunks automatically:

```sql
SELECT add_retention_policy('audit_logs', INTERVAL '2 years');
```

#### `crops` is a reference table with NPK and pH ranges

```
crops
├── id, name, scientific_name
├── optimal_soil_moisture_min, optimal_soil_moisture_max
├── optimal_temperature_min, optimal_temperature_max
├── irrigation_water_need_mm_per_day
├── optimal_ph_min, optimal_ph_max
├── nitrogen_need_ppm, phosphorus_need_ppm, potassium_need_ppm
└── frost_sensitivity (low | medium | high)
```

This lets the rule engine and ML module derive crop-specific thresholds automatically rather than requiring users to enter every threshold by hand.

### 5.3 TimescaleDB setup

```sql
-- Run once after migrations
CREATE EXTENSION IF NOT EXISTS timescaledb;

SELECT create_hypertable('sensor_readings', 'time');
SELECT create_hypertable('device_telemetry', 'time');
SELECT create_hypertable('audit_logs', 'time');

-- Continuous aggregates for fast dashboard queries
CREATE MATERIALIZED VIEW sensor_readings_hourly
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', time) AS bucket,
    device_id,
    capability_type,
    AVG(value) AS avg_value,
    MIN(value) AS min_value,
    MAX(value) AS max_value
FROM sensor_readings
GROUP BY bucket, device_id, capability_type;
```

---

## 6. MQTT Topic Structure

### 6.1 Topic hierarchy

```
farms/{farm_id}/devices/{device_id}/telemetry        (uplink, sensor → broker)
farms/{farm_id}/devices/{device_id}/status           (uplink, retained, LWT)
farms/{farm_id}/devices/{device_id}/commands         (downlink, broker → actuator)
farms/{farm_id}/devices/{device_id}/commands/ack     (uplink, actuator → broker)
```

The `farms/{farm_id}/...` prefix enables multi-tenancy via Mosquitto ACL.

### 6.2 Telemetry message format (JSON)

```json
{
  "timestamp": "2026-04-26T14:30:00Z",
  "device_id": "sensor-042",
  "readings": {
    "soil_moisture": 28.5,
    "temperature": 22.3,
    "humidity": 65.0,
    "ph_level": 6.5,
    "nitrogen_level": 145.0,
    "phosphorus_level": 32.0,
    "potassium_level": 210.0
  },
  "telemetry": {
    "battery_level": 87,
    "rssi": -68
  }
}
```

The MQTT Worker validates `timestamp` (rejects future timestamps and timestamps older than 24 hours), validates each reading against sane physical ranges (e.g., soil_moisture must be 0–100, temperature must be -50 to 80), and writes valid readings to `sensor_readings` and telemetry to `device_telemetry`.

### 6.3 Command message format

```json
{
  "command_id": "cmd-abc123",
  "action": "open_valve",
  "duration_seconds": 1800,
  "issued_by": "user-15",
  "issued_at": "2026-04-26T14:31:00Z"
}
```

Action types: `open_valve`, `close_valve`, `dispense_fertilizer` (with `nutrient_type` and `volume_ml` in parameters).

### 6.4 Ack message format

```json
{
  "command_id": "cmd-abc123",
  "status": "executed",
  "executed_at": "2026-04-26T14:31:02Z"
}
```

Status values: `received`, `executed`, `failed`.

### 6.5 QoS levels

| Topic | QoS | Retain |
|---|---|---|
| `.../telemetry` | 1 | no |
| `.../status` | 1 | yes |
| `.../commands` | 2 | no |
| `.../commands/ack` | 2 | no |

QoS 2 for commands because actuating a valve twice is unacceptable. QoS 1 for telemetry because Worker is idempotent (timestamp + device_id unique constraint).

### 6.6 Last Will and Testament

Each device connects with an LWT message that publishes `{"status": "offline"}` to `.../status` if the connection drops. This satisfies FR-06 (alert when sensor data hasn't been received for 1 hour) without polling.

### 6.7 Mosquitto ACL

Each device gets its own MQTT username and password. ACL rules restrict each device to its own topics:

```
user backend
topic readwrite farms/#

user device-sensor-042
topic write farms/1/devices/sensor-042/telemetry
topic write farms/1/devices/sensor-042/status
topic read  farms/1/devices/sensor-042/commands

user device-valve-007
topic read  farms/1/devices/valve-007/commands
topic write farms/1/devices/valve-007/commands/ack
topic write farms/1/devices/valve-007/status
```

When a new device is registered via the Django admin or API, a Celery task generates credentials and updates the Mosquitto ACL config (mounted as a Docker volume), then triggers a SIGHUP reload of the broker.

---

## 7. API Endpoints

All endpoints are prefixed with `/api/v1/`. JWT auth via `Authorization: Bearer <token>` header.

### 7.1 Authentication

| Method | Path | Purpose |
|---|---|---|
| POST | `/auth/login/` | username + password → access + refresh token |
| POST | `/auth/refresh/` | refresh token → new access token |
| POST | `/auth/logout/` | blacklist refresh token |
| GET | `/auth/me/` | current user + memberships + roles |

### 7.2 Users & memberships

| Method | Path | Purpose |
|---|---|---|
| GET | `/users/` | list (admin only) |
| GET | `/users/{id}/` | detail |
| PATCH | `/users/{id}/` | update profile (self only) |
| GET | `/farms/{farm_id}/memberships/` | list memberships of a farm |
| POST | `/farms/{farm_id}/memberships/` | add member (farm manager only) |
| DELETE | `/farms/{farm_id}/memberships/{id}/` | remove member |

### 7.3 Farms & crops

| Method | Path | Purpose |
|---|---|---|
| GET | `/farms/` | user's farms |
| POST | `/farms/` | create farm |
| GET | `/farms/{id}/` | farm detail |
| PATCH | `/farms/{id}/` | update farm |
| DELETE | `/farms/{id}/` | delete farm |
| GET | `/crops/` | crop catalog |
| GET | `/crops/{id}/` | crop detail with optimal ranges |

### 7.4 Devices & capabilities

| Method | Path | Purpose |
|---|---|---|
| GET | `/farms/{farm_id}/devices/` | list devices in farm |
| POST | `/farms/{farm_id}/devices/` | register device (also generates MQTT credentials) |
| GET | `/devices/{id}/` | device detail |
| PATCH | `/devices/{id}/` | update device |
| DELETE | `/devices/{id}/` | delete device |
| GET | `/devices/{id}/health/` | latest battery + RSSI + uptime |
| GET | `/devices/{id}/capabilities/` | list capabilities |
| POST | `/devices/{id}/capabilities/` | add capability |

### 7.5 Sensor data

| Method | Path | Purpose |
|---|---|---|
| GET | `/sensor-data/` | filtered query (`?device_id=X&capability=...&start=...&end=...&aggregation=hour`) |
| GET | `/sensor-data/latest/` | latest reading per (device, capability) |
| GET | `/sensor-data/timeseries/` | bucketed time series (uses continuous aggregates) |

`aggregation` values: `raw`, `minute`, `hour`, `day`, `week`.

### 7.6 Rules

| Method | Path | Purpose |
|---|---|---|
| GET | `/farms/{farm_id}/rules/` | list rules |
| POST | `/farms/{farm_id}/rules/` | create rule (nested write: conditions + actions + weather constraint) |
| GET | `/rules/{id}/` | rule detail |
| PATCH | `/rules/{id}/` | update rule |
| DELETE | `/rules/{id}/` | delete rule |
| POST | `/rules/{id}/toggle/` | activate / deactivate |
| POST | `/rules/{id}/test/` | dry-run (returns "would have triggered" without acting) |

### 7.7 Commands

| Method | Path | Purpose |
|---|---|---|
| GET | `/farms/{farm_id}/commands/` | command history |
| GET | `/commands/{id}/` | command detail + ack status |
| POST | `/devices/{id}/commands/` | manual command (US-02) |

### 7.8 Fertilization

| Method | Path | Purpose |
|---|---|---|
| GET | `/farms/{farm_id}/fertilization/recommendations/` | active recommendations |
| GET | `/fertilization/recommendations/{id}/` | detail with reasoning |
| POST | `/fertilization/recommendations/{id}/apply/` | mark as applied (creates history entry) |
| POST | `/fertilization/recommendations/{id}/dismiss/` | reject |
| GET | `/farms/{farm_id}/fertilization/history/` | history |
| POST | `/farms/{farm_id}/fertilization/history/` | log manual fertilization (no recommendation) |

### 7.9 Notifications

| Method | Path | Purpose |
|---|---|---|
| GET | `/notifications/` | user's notifications (filterable) |
| GET | `/notifications/unread-count/` | for header badge |
| POST | `/notifications/{id}/mark-read/` | mark single |
| POST | `/notifications/mark-all-read/` | mark all |

### 7.10 Audit logs

| Method | Path | Purpose |
|---|---|---|
| GET | `/audit-logs/` | filtered query (read-only) |

### 7.11 Predictions

| Method | Path | Purpose |
|---|---|---|
| GET | `/farms/{farm_id}/predictions/` | active predictions |
| GET | `/predictions/{id}/` | detail with confidence |
| POST | `/farms/{farm_id}/predictions/run/` | manually trigger ML model (admin) |

### 7.12 Exports (hybrid sync/async)

| Method | Path | Purpose |
|---|---|---|
| POST | `/exports/sensor-data/csv/` | request CSV export |
| POST | `/exports/sensor-data/excel/` | request Excel export |
| GET | `/exports/{job_id}/status/` | check async job status |
| GET | `/exports/{job_id}/download/` | download finished file |

If the predicted result set is **less than 10,000 rows**, the endpoint responds with the file directly (sync). If larger, it returns a `job_id` and processing happens in Celery; the frontend polls `/status/` until ready.

### 7.13 WebSocket endpoints

| Path | Purpose |
|---|---|
| `/ws/farms/{farm_id}/live/` | live sensor readings + command status for one farm |
| `/ws/notifications/` | global notifications stream for the current user |

JWT auth via query string token: `?token=<access_token>`.

---

## 8. Frontend Architecture

### 8.1 Routing strategy (App Router)

```
app/
├── (auth)/login/page.tsx            # public
├── (dashboard)/                      # protected (auth wrapper)
│   ├── layout.tsx                    # sidebar + header
│   ├── farms/page.tsx                # farm picker
│   └── farms/[farmId]/
│       ├── page.tsx                  # main dashboard
│       ├── devices/page.tsx
│       ├── devices/[deviceId]/page.tsx
│       ├── rules/page.tsx
│       ├── rules/new/page.tsx
│       ├── rules/[ruleId]/edit/page.tsx
│       ├── fertilization/page.tsx
│       ├── reports/page.tsx
│       └── audit-logs/page.tsx
└── layout.tsx                        # root + theme provider
```

### 8.2 Data fetching strategy

The dashboard uses **separate endpoints with TanStack Query**, not a single aggregate endpoint. Reasons:
- Per-widget loading states (better UX)
- Independent cache invalidation
- Works seamlessly with Next.js parallel server components

After initial load, **WebSocket takes over** for live updates. No polling.

### 8.3 Authentication

JWT tokens stored in **HttpOnly cookies** (set by Next.js route handler that proxies the login response). Frontend never touches the token directly. This prevents XSS-based token theft.

The auth wrapper is a server component that checks the cookie, calls `/auth/me/`, and either renders the dashboard or redirects to `/login`.

### 8.4 WebSocket integration

A custom `useFarmLiveData(farmId)` hook opens the WebSocket on mount, receives sensor readings and notifications, and merges them into TanStack Query cache via `queryClient.setQueryData(...)`. On unmount, it closes the connection.

---

## 9. Background Jobs (Celery)

### 9.1 Periodic tasks (Celery Beat)

| Task | Schedule | Purpose |
|---|---|---|
| `fetch_weather_for_all_farms` | hourly | refresh Open-Meteo cache (NFR-05) |
| `check_offline_devices` | every 5 min | detect devices with no telemetry in last hour (FR-06) |
| `generate_weekly_fertilization_recommendations` | Mondays 06:00 | analyze NPK + pH → create recommendations |
| `run_ml_predictions` | daily 02:00 | yield + irrigation predictions per farm |
| `cleanup_expired_export_jobs` | daily 03:00 | delete export files older than 7 days |

### 9.2 On-demand tasks

| Task | Trigger | Purpose |
|---|---|---|
| `evaluate_rules_task(reading_id)` | MQTT Worker after each reading | the rule engine |
| `evaluate_rules_task(manual_command=...)` | Django view after manual command | manual irrigation |
| `generate_export_async(filters, format)` | Export endpoint (large jobs) | CSV/Excel generation |
| `send_notification_email(notification_id)` | Notification service | email delivery |
| `regenerate_mosquitto_acl()` | After device CRUD | update ACL config |

---

## 10. Security

### 10.1 Authentication

- JWT access token: 15 minute lifetime
- JWT refresh token: 7 day lifetime, blacklisted on logout
- Tokens stored in HttpOnly cookies on frontend
- Login rate limited (5 attempts per IP per 15 min)

### 10.2 Authorization

- Custom `IsFarmMember` permission class checks `farm_memberships` for any endpoint scoped to a farm
- Role-based action gating (e.g., only farm managers can delete rules)
- WebSocket connections authenticated via token in query string + middleware

### 10.3 MQTT security

- TLS encryption between devices and broker (NFR-03)
- Per-device username and password
- ACL restricts each device to its own topic subtree
- Backend service has separate credentials with farm-wide access

### 10.4 Secrets management

- `.env` file (gitignored) holds API keys, DB passwords, JWT secret
- `.env.example` documents required variables
- No secrets in code (NFR-03)

### 10.5 Input validation

- All sensor readings validated against physical ranges (NFR-04)
- DRF serializers enforce schema on every endpoint
- TypeScript + Zod validates on frontend before submission

---

## 11. Testing Strategy

### 11.1 Critical paths to test

**Backend (pytest):**
- `evaluate_rules_task` with various conditions, including weather constraint cancellation
- MQTT Worker message validation (reject invalid data)
- JWT auth flow (login, refresh, expiry)
- `IsFarmMember` permission (negative cases)
- Manual command endpoint (audit log creation)
- Fertilization recommendation generation logic
- Export sync vs async threshold

**Frontend (Vitest + React Testing Library):**
- Auth flow component (login, logout, redirect)
- Dashboard data fetching hook (TanStack Query mocking)
- Form validation (rule creation form)
- WebSocket reconnection logic

### 11.2 Out of scope

- Visual regression tests
- E2E tests (Playwright) — too much setup for school project
- Load tests
- Mutation testing

---

## 12. Conventions

### 12.1 Language conventions (recap from section 1.3)

- **Conversation with Muhammed:** Turkish
- **Code comments and docstrings:** Turkish
- **TODO.md updates:** English
- **Identifiers (variables, functions, classes, files, tables, columns, endpoints):** English
- **UI text shown to users:** Turkish
- **Log messages and git commits:** English

**Examples:**

```python
# Türkçe yorum: Sensörden gelen veriyi doğrula ve veritabanına yaz
def process_sensor_reading(reading: SensorReading) -> None:
    """Gelen sensör ölçümünü işler ve hypertable'a kaydeder.

    NFR-04 gereği fiziksel olarak imkansız değerler reddedilir
    (örn: -200°C sıcaklık veya %150 nem).
    """
    if not is_valid_reading(reading):
        logger.warning("Rejected invalid reading from device %s", reading.device_id)
        return

    # Geçerli okuma → hypertable'a yaz, kural motorunu tetikle
    reading.save()
    evaluate_rules_task.delay(reading.id)
```

```typescript
// Türkçe yorum: Çiftliğe ait canlı sensör verisini WebSocket'ten dinle
export function useFarmLiveData(farmId: number) {
  // TanStack Query cache'ini WebSocket mesajlarıyla güncelle
  const queryClient = useQueryClient()

  useEffect(() => {
    const socket = new WebSocket(`/ws/farms/${farmId}/live/?token=${token}`)
    // ...
  }, [farmId])
}
```

### 12.2 Naming

- **Database:** snake_case for tables and columns (English)
- **Python:** snake_case for variables and functions, PascalCase for classes (English)
- **TypeScript:** camelCase for variables and functions, PascalCase for components and types (English)
- **Files:** kebab-case for non-component files (`api-client.ts`), PascalCase for React components (`FarmDashboard.tsx`)
- **Branches:** `feature/...`, `fix/...`, `chore/...`
- **Commits:** Conventional Commits in English (`feat: add rule engine`, `fix: validate sensor timestamp`)

### 12.3 Code style

- **Python:** Black default + Ruff defaults. Line length 100.
- **TypeScript:** Prettier defaults, single quotes, no semicolons (Next.js default), trailing commas.
- **Tailwind:** Use `clsx` for conditional classes. Avoid arbitrary values when a token exists.

### 12.4 API conventions

- RESTful where natural; nested resources for ownership (`/farms/{id}/devices/`)
- Pagination via `?page=N&page_size=20` (DRF default)
- Filtering via `django-filter` (`?device_id=5&start=...`)
- Errors return `{"detail": "...", "code": "..."}` with appropriate HTTP status — `detail` field shown to UI is in Turkish, `code` is a stable English machine identifier
- Timestamps always ISO 8601 with timezone (`2026-04-26T14:30:00Z`)

---

## 13. Out-of-scope (deferred to v2)

- Mobile application
- Real hardware integration (currently sensor simulator only)
- Crop growth stage tracking (`crop_growth_stages` table)
- Multi-language UI (Turkish only)
- Production deployment (Kubernetes, managed Postgres)
- Advanced ML (deep learning, image-based disease detection)
- Self-registration for users
- Email templates customization
- SMS notifications
- Historical weather backfill

---

## 14. Decision log

Major architectural decisions and rationale.

### D-01: TimescaleDB over plain PostgreSQL with manual partitioning
TimescaleDB's hypertable abstraction eliminates manual partition management and enables continuous aggregates for fast dashboard queries. Still PostgreSQL-compatible — Django ORM works unchanged.

### D-02: Rule engine as Celery task, not inline in MQTT Worker
Two trigger paths (automatic + manual) share the same logic. Worker stays fast and focused. Celery provides free retry mechanism.

### D-03: Next.js + Vite-style separation rejected in favor of pure Next.js
Next.js 15 chosen for portfolio value and modern App Router experience. Authenticated dashboard doesn't need SSR for SEO, but Server Components still offer parallel data fetching benefits.

### D-04: Dashboard uses per-widget endpoints, not a single aggregate
Better UX (independent loading states), better cache invalidation, works with Server Components. WebSocket replaces polling after initial load.

### D-05: Export endpoint is hybrid sync/async with 10k row threshold
Small exports return file directly (good UX). Large exports go through Celery (avoids 30s gateway timeouts). Threshold-based dispatch is transparent to the frontend.

### D-06: Per-device MQTT credentials with ACL, not shared credential
Stronger security posture. New device registration triggers Celery task to regenerate ACL config and reload broker.

### D-07: `crops` is a reference table with optimal ranges, not just a string field
Enables crop-specific rule defaults, ML feature engineering, and frost risk warnings (US-06) without per-farm threshold configuration.

### D-08: `commands` is one table with CHECK constraint, not split
Single table simplifies "last N commands" queries. CHECK constraint enforces XOR of `rule_id` and `user_id`. Manual command audit details (IP, user agent) live in `audit_logs` instead.

### D-09: `audit_logs` is a TimescaleDB hypertable
Append-only, time-queried, immutable. Retention policy can drop old chunks. Consistent with other time-series tables.

### D-10: npm over pnpm
Better Claude Code compatibility (less risk of mixed package manager commands), simpler defaults, well-supported ecosystem. pnpm's disk efficiency advantage isn't material for a single-developer project.

### D-11: Hybrid linting (Black + Ruff + Prettier + ESLint + TypeScript strict, no mypy)
Catches formatting and basic mistakes without slowing Claude Code with mypy false positives. TypeScript strict mode provides strong frontend type safety. Pre-commit hooks via Husky + lint-staged enforce on commit.

### D-12: Mixed-language convention (Turkish for human-facing, English for code)
Conversation with the developer and code comments are in Turkish so explanations stay accessible. Identifiers, file paths, and structural artifacts (DB names, endpoints, commits) stay in English so the codebase remains internationally readable, grep-friendly, and consistent with mainstream open-source conventions. End-user UI is Turkish because users are Turkish farmers. TODO.md stays English so it remains a stable progress log readable by any future collaborator.

---

## 15. Glossary

| Term | Meaning |
|---|---|
| **Capability** | A specific measurement or actuation a device supports (e.g., `soil_moisture`, `valve_control`) |
| **Fertigation** | Delivering liquid fertilizer through the irrigation system |
| **Hypertable** | TimescaleDB's term for a partitioned time-series table that looks like a normal table |
| **LWT** | Last Will and Testament — MQTT broker auto-publishes a message if a client disconnects unexpectedly |
| **NPK** | Nitrogen, Phosphorus, Potassium — the three macro-nutrients |
| **RSSI** | Received Signal Strength Indicator — wireless signal quality, in dBm |
| **Hypertable chunk** | TimescaleDB's automatic time-based partition (typically 1 day or 1 week wide) |
| **Continuous aggregate** | Materialized view auto-refreshed by TimescaleDB for fast aggregated queries |

---

## 16. References

- Requirement document: `gereksinim_analizi.md` (uploaded by Muhammed)
- TimescaleDB docs: https://docs.timescale.com/
- Django Channels: https://channels.readthedocs.io/
- Open-Meteo API: https://open-meteo.com/en/docs
- Mosquitto ACL: https://mosquitto.org/man/mosquitto-conf-5.html
- Next.js App Router: https://nextjs.org/docs/app
