---
phase: 01-foundation-backend-app-shell
plan: 02
subsystem: backend-api
tags: [fastapi, api-routers, service-layer, sqlalchemy, endpoints]
dependency_graph:
  requires: [01-01]
  provides: [api-lookup, api-evaluate, api-select, api-decisions, api-metrics, api-rules]
  affects: [axiom/api/main.py]
tech_stack:
  added: []
  patterns: [fastapi-apirouter, fastapi-depends, sqlalchemy-session-per-request, pydantic-from-attributes]
key_files:
  created:
    - axiom/services/__init__.py
    - axiom/services/lookup_service.py
    - axiom/services/decision_service.py
    - axiom/services/metrics_service.py
    - axiom/api/routers/__init__.py
    - axiom/api/routers/lookup.py
    - axiom/api/routers/evaluate.py
    - axiom/api/routers/select.py
    - axiom/api/routers/decisions.py
    - axiom/api/routers/metrics.py
    - axiom/api/routers/rules_api.py
  modified:
    - axiom/api/main.py
decisions:
  - Used FastAPI TestClient for endpoint verification instead of live server + curl
  - Route paths stored as /api/lookup (prefix included) - plan's verify script had minor path mismatch, irrelevant to functionality
metrics:
  duration: 7min
  completed: 2026-03-31T03:13:16Z
  tasks_completed: 2
  files_created: 11
  files_modified: 1
---

# Phase 1 Plan 2: Service Layer + API Routers Summary

Six new FastAPI endpoints under /api/ prefix with three service modules, all backed by SQLAlchemy database queries, wired into the existing app while preserving all legacy endpoints.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Create service layer and API routers | 0b11071 | 11 files: 3 services + 6 routers + 2 __init__.py |
| 2 | Wire routers into main app and verify | 51d0349 | axiom/api/main.py |

## What Was Built

### Service Layer (axiom/services/)

- **lookup_service.py**: `lookup_reservation(db, pnr, last_name)` -- queries Reservation by PNR, validates passenger last name match
- **decision_service.py**: `evaluate_reservation(db, reservation)` -- classifies disruption events, evaluates rules against structured reservation data, generates reprotection flight options, creates Decision record
- **metrics_service.py**: `compute_metrics_from_db(db)` -- SQL aggregation for KPIs: total decisions, automation rate, avg processing time, decisions by day/status, top rules

### API Routers (axiom/api/routers/)

| Endpoint | Method | Router File | Purpose |
|----------|--------|-------------|---------|
| /api/lookup | POST | lookup.py | PNR + last name lookup returning structured reservation |
| /api/evaluate | POST | evaluate.py | Rule evaluation producing decision with trace and options |
| /api/select | POST | select.py | Record operator flight selection on an approved decision |
| /api/decisions | GET | decisions.py | Paginated decision history (page, per_page params) |
| /api/metrics | GET | metrics.py | Aggregated KPIs from decision table |
| /api/rules | GET/POST/PUT/DELETE | rules_api.py | Database-backed rules CRUD |

### Main App Integration

- Added `init_db()` call to create tables on startup
- Six `app.include_router()` calls for all new routers
- All existing endpoints unchanged: /health, /process, /rules, /metrics

## Verification Results

All 10 endpoint tests passed via FastAPI TestClient:

1. GET /health -- 200, `{"status": "ok"}`
2. POST /api/lookup (XKJR4T/MARTINEZ) -- 200, 1 passenger, 1 segment
3. POST /api/lookup (invalid) -- 404
4. POST /api/evaluate (XKJR4T) -- 200, status=APPROVED (cancelled flight)
5. POST /api/evaluate (BN7M2P) -- 200, status=ESCALATED (UMNR SSR)
6. GET /api/decisions -- 97 total decisions, pagination working
7. GET /api/metrics -- 97 decisions, automation rate computed
8. GET /api/rules -- 7 active rules from database
9. GET /rules (existing) -- 200, still works
10. GET /metrics (existing) -- 200, still works

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Plan verification script path mismatch**
- **Found during:** Task 1 verification
- **Issue:** Plan's verify script asserted `/lookup` but FastAPI stores routes with prefix as `/api/lookup`
- **Fix:** Used corrected assertion paths in verification
- **Impact:** None -- functional behavior is correct, only the test assertion needed adjustment

**2. [Rule 3 - Blocking] Bash permission restrictions for live server testing**
- **Found during:** Task 2 verification
- **Issue:** Could not start uvicorn background process + curl for live server testing
- **Fix:** Used FastAPI TestClient (synchronous, in-process) for comprehensive endpoint verification
- **Impact:** Same coverage -- TestClient exercises the full ASGI stack including middleware, routing, and response serialization

## Known Stubs

None -- all endpoints return real data from the seeded SQLite database.

## Self-Check: PASSED

- All 11 created files exist (4 services, 7 routers)
- Modified file axiom/api/main.py exists
- Commit 0b11071 exists (Task 1)
- Commit 51d0349 exists (Task 2)
- All 10 endpoint tests passed via TestClient
