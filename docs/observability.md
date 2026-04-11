# Observability Stack Guide

This document explains the logging, metrics, and monitoring infrastructure for this project.

## Overview

The observability stack comprises four tools running on your home server, connected to the application via Tailscale. Together, they enable you to:

- **See what's happening** (logs)
- **Measure performance** (metrics)
- **Know when things break** (uptime monitoring)
- **Catch errors users experience** (frontend error tracking)

This is production-grade observability suitable for demonstrating DevOps/SRE skills in interviews.

---

## The Tools

### 1. Prometheus

**What it is**: Time-series database for metrics. It scrapes endpoints (pulls data) and stores timestamped readings.

**Why it's here**: Records request counts, latency, error rates, system resource usage;anything quantifiable. You can query "What was the 95th percentile latency last hour?" or "How many 500 errors per minute?"

**Your app exposes**: FastAPI generates a `/metrics` endpoint automatically via `prometheus-fastapi-instrumentator`. It outputs metrics in Prometheus text format like:

```
http_requests_total{method="GET", status="200", path="/api/riot/champions"} 42
http_request_duration_seconds{method="GET", path="/api/riot/champions"} 0.145
```

**Port on home server**: `9090` (access at `http://home-server:9090`)

---

### 2. Loki

**What it is**: Log aggregation system. It stores unstructured text (or structured JSON) and makes it queryable.

**Why it's here**: Logs are different from metrics. A log is a discrete event: "User logged in," "Database query failed," "Frontend error occurred." Prometheus is for trends; Loki is for debugging specific incidents.

**Your app sends**: FastAPI writes JSON-structured logs to `/var/log/lolapp/app.log`. Each line is a complete JSON object:

```json
{"asctime": "2026-03-26 14:30:45", "name": "app.api.endpoints.riot", "levelname": "INFO", "message": "match_cache_miss", "match_id": "NA1_1234567"}
{"asctime": "2026-03-26 14:30:46", "name": "app.api.endpoints.auth", "levelname": "ERROR", "message": "authentication_failed", "user_email": "user@example.com", "reason": "wrong_password"}
```

**Promtail ships it**: Promtail (running on your app host) tails this file and pushes it to Loki on the home server. Loki extracts fields like `levelname` and `name` and makes them filterable labels.

**Port on home server**: `3100` (usually not accessed directly; use Grafana UI instead)

---

### 3. Grafana

**What it is**: Dashboard and visualization platform. It connects to Prometheus and Loki as data sources and displays charts, tables, and logs.

**Why it's here**: Prometheus and Loki have query languages, but humans don't read JSON/Prometheus text. Grafana lets you create dashboards showing:

- Request latency over time (line chart)
- Error rate spiking (alert)
- Recent error logs from users (log viewer)
- Uptime status (status page)

**Your setup**: Grafana auto-configures Prometheus + Loki as data sources on first boot (via `provisioning/datasources/datasources.yml`). You don't need to click through the UI.

**Port on home server**: `3001` (access at `http://home-server:3001`)

**Login**: Default user is `admin`, password is set via `GRAFANA_ADMIN_PASSWORD` env var (default: `changeme`)

---

### 4. Promtail

**What it is**: Log shipper. A lightweight agent that follows files and ships their contents to Loki.

**Why it's here**: Loki doesn't read files directly. Promtail sits on the app host and watches `/var/log/lolapp/app.log`, immediately pushing new lines to Loki on the home server.

**Your setup**: Runs as a systemd service on the app host. Reads its config from `/etc/promtail/config.yml` (or wherever you place it).

**Port on app host**: `9080` (mainly internal; used for Promtail's own metrics, not usually accessed)

---

### 5. Uptime Kuma

**What it is**: Simple, web-based uptime monitoring. Periodically pings endpoints and alerts if they go down.

**Why it's here**: While Prometheus and Loki are for detailed metrics/logs, Uptime Kuma is for "is my app working right now?" and automated alerting.

**Your setup**: Configure monitors via its web UI to ping:

- `/health` (returns 200 if app is up)
- `/metrics` (confirms Prometheus scrape is working)
- Your Next.js frontend URL (confirms frontend is reachable)

If any monitor fails, Uptime Kuma can send alerts to Discord, email, Telegram, etc.

**Port on home server**: `3002` (access at `http://home-server:3002`)

---

## Data Flow (End-to-End)

### Metrics Flow

```
[FastAPI app]
    ↓ (exposes /metrics every request)
[Prometheus on home server]
    ↓ (scrapes /metrics every 15 seconds over Tailscale)
[Prometheus time-series database]
    ↓ (stores request counts, latencies, error rates)
[Grafana dashboards]
    ↓ (queries Prometheus, displays charts)
[You]
    ↓ (opens http://home-server:3001 and sees graphs)
```

### Logs Flow

```
[FastAPI app]
    ↓ (writes JSON to /var/log/lolapp/app.log)
[Promtail on app host]
    ↓ (tails the file, ships new lines over Tailscale)
[Loki on home server]
    ↓ (receives lines, indexes by labels like job, level, logger name)
[Grafana Loki data source]
    ↓ (queries Loki)
[You]
    ↓ (opens Grafana Explore tab, sees log lines)
```

### Frontend Errors Flow

```
[Next.js app]
    ↓ (user gets JavaScript error, window.onerror fires)
[ErrorBoundary + GlobalErrorHandler]
    ↓ (catches error, calls shipError())
[shipError() helper]
    ↓ (POSTs to /api/monitoring/frontend-error)
[Backend /api/monitoring/frontend-error endpoint]
    ↓ (receives payload, logs as JSON to app.log)
[Same as logs flow above]
    ↓ (Promtail → Loki → Grafana)
[You]
    ↓ (sees user JavaScript errors in Loki: {event="frontend_error"})
```

### Uptime Flow

```
[Uptime Kuma on home server]
    ↓ (every 60 seconds, HTTP GET to /health over Tailscale)
[FastAPI /health endpoint]
    ↓ (returns 200 OK)
[Uptime Kuma dashboard]
    ↓ (records success, increments uptime percentage)
[You]
    ↓ (opens http://home-server:3002, sees green "online" status)
```

---

## Networking

All communication between the app and home server happens over **Tailscale VPN**. This means:

- **Tailscale IP of app host**: Find with `tailscale ip -4` on the app machine. Example: `100.123.45.67`
- **Tailscale IP of home server**: Find with `tailscale ip -4` on the home server. Example: `100.87.65.43`

You must fill in these IPs in:

- `infra/prometheus.yml` — `targets: ["100.123.45.67:8000"]`
- `infra/promtail-config.yml` — `url: http://100.87.65.43:3100/loki/api/v1/push`

(In the future, if you switch to Cloudflare Tunnel, the IPs will be replaced with DNS names or public URLs, but the architecture stays the same.)

---

## Setup Instructions

### Prerequisites

- Home server with Docker and Docker Compose installed
- Both machines on Tailscale (or another private VPN)
- Know the Tailscale IP of both machines (run `tailscale ip -4`)

### Step 1: Home Server — Start Observability Stack

```bash
cd infra

# Edit prometheus.yml and promtail-config.yml to fill in real Tailscale IPs
# Example:
# - targets: ["100.123.45.67:8000"]  # app host IP
# - url: http://100.87.65.43:3100/loki/api/v1/push  # home server IP

# Set Grafana admin password
export GRAFANA_ADMIN_PASSWORD="your-secure-password"

# Start all services
docker compose up -d

# Verify they're running
docker compose ps
docker compose logs -f grafana  # Watch Grafana startup logs
```

Access the services:

- **Grafana**: `http://localhost:3001` (login with admin/your-secure-password)
- **Prometheus**: `http://localhost:9090` (check targets at `/targets`)
- **Uptime Kuma**: `http://localhost:3002`

### Step 2: App Host — Set Up Logging

```bash
# Create log directory
sudo mkdir -p /var/log/lolapp
sudo chown $USER:$USER /var/log/lolapp

# Add to backend .env
echo "LOG_FILE_PATH=/var/log/lolapp/app.log" >> backend/.env
echo "LOG_LEVEL=INFO" >> backend/.env

# Install Python packages
cd backend
pip install -r requirements.txt  # Now includes prometheus-fastapi-instrumentator and python-json-logger
```

### Step 3: App Host — Install Promtail

```bash
# Download Promtail (match your home server's Loki version, e.g., 3.0.0)
PROMTAIL_VERSION="3.0.0"
curl -O -L "https://github.com/grafana/loki/releases/download/v${PROMTAIL_VERSION}/promtail-linux-amd64.zip"
unzip promtail-linux-amd64.zip
chmod +x promtail-linux-amd64
sudo mv promtail-linux-amd64 /usr/local/bin/promtail

# Copy config and edit to fill in home server Tailscale IP
sudo mkdir -p /etc/promtail
sudo cp infra/promtail-config.yml /etc/promtail/config.yml
sudo nano /etc/promtail/config.yml  # Fill in http://100.87.65.43:3100/loki/api/v1/push

# Create systemd service
sudo tee /etc/systemd/system/promtail.service > /dev/null <<'EOF'
[Unit]
Description=Promtail log shipper for lolapp
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/promtail -config.file=/etc/promtail/config.yml
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable promtail
sudo systemctl start promtail
sudo systemctl status promtail
```

### Step 4: Verify Everything Works

```bash
# 1. Metrics endpoint
curl http://localhost:8000/metrics | head -20
# Expect: text in Prometheus exposition format

# 2. Health endpoint
curl http://localhost:8000/health
# Expect: {"status": "ok", "service": "lolapp-backend"}

# 3. Logs are being written
tail -f /var/log/lolapp/app.log
# Expect: JSON lines on each request

# 4. Promtail is running
sudo systemctl status promtail
# Expect: active (running)

# 5. On home server: Prometheus sees the app
# Open http://home-server:9090/targets
# Expect: lolapp-backend target with State=UP

# 6. On home server: Grafana sees data
# Open http://home-server:3001
# Go to Explore > select Loki data source
# Query: {job="lolapp-backend"}
# Expect: Log lines appear

# 7. Frontend errors
# Open frontend in browser, console:
# throw new Error("test observability")
# Check Grafana Loki: {event="frontend_error"}
# Expect: error logged with stack trace and URL
```

### Step 5: Configure Uptime Kuma

1. Open `http://home-server:3002`
2. Go to "Add Monitor"
3. Create these monitors:

| Name            | Type    | URL                                 | Interval |
| --------------- | ------- | ----------------------------------- | -------- |
| lolapp-health   | HTTP(s) | `http://100.123.45.67:8000/health`  | 60s      |
| lolapp-metrics  | HTTP(s) | `http://100.123.45.67:8000/metrics` | 300s     |
| lolapp-frontend | HTTP(s) | your Next.js URL                    | 60s      |

4. Configure notification channels (Discord, email, Telegram, Slack, etc.)
5. Create status page to publicly show uptime (optional but looks professional)

---

## Common Queries in Grafana

### Prometheus (Metrics)

**Request rate (requests per second)**

```
rate(http_requests_total[5m])
```

**95th percentile latency**

```
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

**Error rate**

```
rate(http_requests_total{status=~"5.."}[5m])
```

### Loki (Logs)

**All logs from backend**

```
{job="lolapp-backend"}
```

**Only errors**

```
{job="lolapp-backend"} | json | level="ERROR"
```

**Frontend errors**

```
{job="lolapp-backend"} | json | event="frontend_error"
```

**Logs from specific logger**

```
{job="lolapp-backend"} | json | logger="app.api.endpoints.riot"
```

---

## Troubleshooting

### Prometheus target shows DOWN

**Symptom**: `http://home-server:9090/targets` shows lolapp-backend as RED
**Causes**:

- FastAPI not running (`python -m uvicorn app.main:app --reload`)
- Tailscale IP is wrong in `prometheus.yml`
- Firewall blocking port 8000

**Fix**:

- Verify Tailscale IPs match: `tailscale ip -4` on both machines
- Test manually: `curl http://100.x.x.x:8000/health` from home server
- Check logs: `docker compose logs prometheus`

### Loki has no logs

**Symptom**: `{job="lolapp-backend"}` returns no results in Grafana
**Causes**:

- Promtail not running
- Log file doesn't exist or wrong path
- Promtail config has wrong Loki IP

**Fix**:

- Check Promtail: `sudo systemctl status promtail`
- Check log file: `ls -la /var/log/lolapp/app.log`
- Check Promtail logs: `sudo journalctl -u promtail -f`
- Test Loki directly: `curl -G -s "http://home-server:3100/loki/api/v1/query" --data-urlencode 'query={job="lolapp-backend"}' | jq .`

### No frontend errors appearing

**Symptom**: Throwing errors in the browser console doesn't create log entries
**Causes**:

- ErrorBoundary not mounted in layout.tsx
- GlobalErrorHandler not mounted
- Axios base URL wrong in frontend config
- Backend `/api/monitoring/frontend-error` endpoint not created

**Fix**:

- Check browser console for errors when fetching `/api/monitoring/frontend-error`
- Verify layout.tsx has `<ErrorBoundary>` and `<GlobalErrorHandler />`
- Test manually: `curl -X POST http://localhost:8000/api/monitoring/frontend-error -H "Content-Type: application/json" -d '{"message": "test"}'`

---

## What to Show Interviewers

When discussing this on interviews, highlight:

1. **Architecture reasoning**: "I chose Prometheus for metrics because it's pull-based (no need to send data), Loki for logs because it's simpler than ELK Stack, and Grafana as the unified dashboard."

2. **Operational knowledge**: "The app ships metrics to `/metrics`, Prometheus scrapes it every 15 seconds, and I can query any time-series (latency, error rate, request count) from the last 30 days."

3. **Observability culture**: "I instrumented the whole app including frontend error tracking, so I get alerts when things break, not when users complain."

4. **Practical skills**: "I'm comfortable with Docker Compose, systemd services, VPN networking (Tailscale), and structured logging in JSON format."

5. **Learning mindset**: "This is my first time implementing a full observability stack. I researched each tool's purpose and built it from scratch to understand how the pieces fit together."

---

## Further Reading

- **Prometheus**: https://prometheus.io/docs/introduction/overview/
- **Loki**: https://grafana.com/docs/loki/latest/
- **Grafana**: https://grafana.com/docs/grafana/latest/
- **Promtail**: https://grafana.com/docs/loki/latest/clients/promtail/
- **Observability (general)**: https://opentelemetry.io/docs/concepts/ (the three pillars: metrics, logs, traces)
