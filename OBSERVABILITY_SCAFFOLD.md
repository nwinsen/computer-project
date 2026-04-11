# Observability Implementation Scaffold

This document lists all the skeleton code that's been created for you to implement. Each file has detailed TODOs explaining what needs to be written.

## Read First
**Start here**: Read `docs/observability.md` to understand what each tool does and how they work together.

## Skeleton Files Created

### Backend
| File | What to Implement |
|------|-------------------|
| `backend/app/core/logging.py` | Centralized JSON logging setup using `python-json-logger`. Configure root logger with stdout + file handlers, rotating file handler at 50MB. |
| `backend/app/api/endpoints/monitoring.py` | Two endpoints: `GET /health` (returns status) and `POST /api/monitoring/frontend-error` (accepts JS errors, logs them). |

### Frontend
| File | What to Implement |
|------|-------------------|
| `frontend/components/ErrorBoundary.tsx` | React class component catching render-phase errors. Exports `shipError()` helper that POSTs errors to backend. |
| `frontend/components/GlobalErrorHandler.tsx` | Client component registering `window.onerror` and `window.onunhandledrejection` handlers. |

### Infrastructure (Config Files - Ready to Use)
| File | Purpose |
|------|---------|
| `infra/docker-compose.yml` | Runs Prometheus, Loki, Grafana, Uptime Kuma on home server. Ready to go (just replace admin password). |
| `infra/prometheus.yml` | Prometheus configuration. TODO: Replace `TAILSCALE_IP` with your app host's Tailscale IP. |
| `infra/loki-config.yml` | Loki configuration. Ready to use. |
| `infra/promtail-config.yml` | Promtail config (runs on app host). TODO: Replace `HOME_SERVER_TAILSCALE_IP` with home server's Tailscale IP. |
| `infra/grafana/provisioning/datasources/datasources.yml` | Auto-provisions Prometheus + Loki in Grafana. Ready to use. |

## What's Already Done
✅ `backend/requirements.txt` — Added `prometheus-fastapi-instrumentator` and `python-json-logger`
✅ Removed print statements from `backend/app/api/endpoints/auth.py` and `riot.py`
✅ Created `backend/app/core/__init__.py` (package marker)
✅ Created `docs/observability.md` (comprehensive guide)

## Implementation Order

### 1. Implement Backend Logging (One file)
**File**: `backend/app/core/logging.py`

Read the TODO comments. The basic structure is:
- Configure Python's root logger with JSON formatter
- Write to stdout + rotating file
- Provide `get_logger(name)` helper

Check the docs for full details.

### 2. Implement Monitoring Endpoints (One file)
**File**: `backend/app/api/endpoints/monitoring.py`

Read the TODO comments. You need:
- Pydantic model for frontend error payload
- `GET /health` endpoint
- `POST /api/monitoring/frontend-error` endpoint that logs errors

### 3. Wire Backend Changes (Two files)
Modify these files to integrate the monitoring code:

**`backend/app/main.py`**
- Import `app.core.logging` at the very top (side-effect: configures logging)
- Add `Instrumentator().instrument(app).expose(app)` before routers
- Mount monitoring router (for `/health` endpoint)

**`backend/app/api/api.py`**
- Include the monitoring router with tag `"Monitoring"`

### 4. Implement Frontend Error Tracking (Two new components)
**Files**: `frontend/components/ErrorBoundary.tsx` and `GlobalErrorHandler.tsx`

Read the TODO comments. Key points:
- ErrorBoundary is a class component (required by React)
- Exports `shipError()` function that POSTs to backend
- GlobalErrorHandler is a client component that uses `useEffect`
- Both use `fetch` (not axios) to avoid circular dependencies

### 5. Wire Frontend Changes (One file)
**`frontend/app/layout.tsx`**
- Import ErrorBoundary and GlobalErrorHandler
- Wrap content with `<ErrorBoundary>`
- Add `<GlobalErrorHandler />`

### 6. Infrastructure Setup (Manual one-time setup)
After implementing code:
1. Fill in Tailscale IPs in `prometheus.yml` and `promtail-config.yml`
2. On home server: `cd infra && docker compose up -d`
3. On app host: Install and configure Promtail as systemd service
4. Create log directory: `sudo mkdir -p /var/log/lolapp`
5. Configure Uptime Kuma monitors via web UI at `http://home-server:3002`

See `docs/observability.md` for detailed setup instructions.

## Testing

After implementing, verify everything works:

```bash
# 1. Backend is running
curl http://localhost:8000/health

# 2. Metrics endpoint exists
curl http://localhost:8000/metrics | head

# 3. Logs are being written
tail -f /var/log/lolapp/app.log

# 4. Home server observability stack is running
docker compose ps  # in infra/ directory

# 5. Grafana is accessible
open http://localhost:3001

# 6. Frontend errors are captured
# In browser console: throw new Error("test")
# Check Grafana Loki for {event="frontend_error"}
```

## Key Learning Points

Implementing this teaches you:
1. **Structured logging** — JSON format for machine readability
2. **Metrics instrumentation** — Automatic request instrumentation in FastAPI
3. **Log shipping** — Promtail pipeline stages and label extraction
4. **Error handling** — Global error boundaries and handlers in React
5. **Docker Compose** — Multi-service orchestration
6. **Observability workflow** — Logs → Loki, Metrics → Prometheus, Dashboard → Grafana
7. **Resume skills** — This demonstrates production-grade ops knowledge

## Questions?

Refer to `docs/observability.md` for detailed explanations of:
- What each tool does (Prometheus, Loki, Grafana, Promtail, Uptime Kuma)
- Full data flow end-to-end
- Common Grafana queries
- Troubleshooting guide
