# Architecture Research: AXIOM AirFlight Engine

## Current Architecture (As-Is)

```
Text Input → FastAPI /process
                │
                ├─ validators.py (regex PNR/passenger extraction)
                ├─ event_classifier.py (NLP keyword classification)
                ├─ rule_engine.py OR rule_engine_db.py (dual mode)
                ├─ options_generator.py (hardcoded flights)
                └─ → ProcessResponse (JSON) + decision_log.json append
```

**Limitations:**
- Single text-based endpoint
- Regex parsing fragile
- Hardcoded simulated data inline
- JSON file for logging (no query capability)
- No database (CSV for rules, JSON for logs)

## Target Architecture (To-Be)

### Component Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    NEXT.JS FRONTEND                      │
│                                                          │
│  ┌──────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ PNR      │  │ Decision     │  │ KPI Dashboard    │  │
│  │ Lookup   │  │ Panel        │  │ (Recharts)       │  │
│  │ + Reserv │  │ + Audit Trail│  │ + Metrics Cards  │  │
│  └────┬─────┘  └──────┬───────┘  └────────┬─────────┘  │
│       │               │                    │             │
│  ┌────┴───────────────┴────────────────────┴──────────┐ │
│  │              API Client (TanStack Query)            │ │
│  └────────────────────────┬───────────────────────────┘ │
└───────────────────────────┼─────────────────────────────┘
                            │ HTTP/REST
┌───────────────────────────┼─────────────────────────────┐
│                    FASTAPI BACKEND                        │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │                  API Layer                         │   │
│  │  POST /api/lookup    (PNR + last name)           │   │
│  │  POST /api/evaluate  (rule evaluation)            │   │
│  │  POST /api/select    (option selection)           │   │
│  │  GET  /api/decisions (decision history)           │   │
│  │  GET  /api/metrics   (KPI data)                   │   │
│  │  CRUD /api/rules     (existing, enhanced)         │   │
│  └──────────┬───────────────────────────────────────┘   │
│             │                                            │
│  ┌──────────┴───────────────────────────────────────┐   │
│  │              Decision Core (Extended)              │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────────────┐  │   │
│  │  │ PNR      │ │ Rule     │ │ Options          │  │   │
│  │  │ Service  │ │ Engine   │ │ Generator        │  │   │
│  │  └──────────┘ └──────────┘ └──────────────────┘  │   │
│  └──────────┬───────────────────────────────────────┘   │
│             │                                            │
│  ┌──────────┴───────────────────────────────────────┐   │
│  │              Data Layer (SQLAlchemy + SQLite)      │   │
│  │  reservations │ flights │ rules │ decisions │ kpis │   │
│  └──────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────┘
```

### Data Flow

```
1. LOOKUP:    PNR + LastName → Backend → Query DB → Return Reservation
2. EVALUATE:  Reservation → Rule Engine → Sequential Rules → Decision Result
3. OPTIONS:   Decision Result → Options Generator → Query Available Flights → Options List
4. SELECT:    User Selection → Backend → Create Decision Record → Confirmation
5. METRICS:   Dashboard → Query Decision Records → Aggregate KPIs → Charts
```

### API Contracts

#### POST /api/lookup
```json
// Request
{ "pnr": "ABC123", "last_name": "MARTINEZ" }

// Response
{
  "reservation": {
    "pnr": "ABC123",
    "passengers": [{"name": "MARTINEZ/DANIELA", "ticket": "045-1234567890"}],
    "segments": [
      {"flight": "AV123", "origin": "BOG", "destination": "MDE", "date": "2026-04-15", "time": "08:30", "status": "CANCELLED"}
    ],
    "fare_class": "Y",
    "ssr": []
  }
}
```

#### POST /api/evaluate
```json
// Request
{ "pnr": "ABC123", "reservation_id": 1 }

// Response
{
  "decision": {
    "status": "APPROVED",
    "rule_applied": "involuntary_change",
    "justification": "Flight cancelled, same airline, same route, no sensitive SSR, same fare class",
    "trace": [...],
    "options": [
      {"flight": "AV125", "time": "10:30-11:45", "availability": "available", "fare_diff": 0},
      {"flight": "AV127", "time": "14:00-15:15", "availability": "available", "fare_diff": 0}
    ]
  }
}
```

#### POST /api/select
```json
// Request
{ "decision_id": 1, "selected_option": "AV125", "operator_notes": "" }

// Response
{ "confirmation": { "id": 1, "status": "CONFIRMED", "new_flight": "AV125", "timestamp": "..." } }
```

### Database Schema (Simulated Data)

```sql
-- Seed data for demo
reservations (id, pnr, created_at)
passengers (id, reservation_id, last_name, first_name, ticket_number, fare_class)
segments (id, reservation_id, flight_number, airline, origin, destination, departure_date, departure_time, arrival_time, status, cabin_class)
ssr_records (id, passenger_id, ssr_type, ssr_detail)

-- Available alternatives
flights (id, flight_number, airline, origin, destination, departure_time, arrival_time, available_seats, fare_class, status)

-- Rules (replace CSV)
rules (id, field, operator, value, action, priority, active, created_at)

-- Decision records
decisions (id, reservation_id, rule_applied, status, justification, trace, options_generated, selected_option, operator_id, processing_time_ms, created_at)
```

### Build Order (Phase Dependencies)

```
1. Database + Models + Seed Data     (foundation — everything depends on this)
      │
2. Backend API Endpoints             (extend FastAPI with new structured endpoints)
      │
3. Frontend Scaffold + Theme         (Next.js + dark theme + navigation)
      │
4. PNR Lookup + Reservation Display  (first user-facing flow)
      │
5. Rule Evaluation + Decision Panel  (core decision logic with visualization)
      │
6. Options + Selection               (complete the reprotection workflow)
      │
7. KPI Dashboard + Metrics           (operational intelligence)
      │
8. Polish + Brand Alignment          (investor-demo quality finish)
```

### Extending Existing DecisionCore

**Strategy: Adapter pattern** — Don't rewrite `DecisionCore`, wrap it:

1. Keep existing `decision_core.py` for backward compatibility
2. Create new `structured_decision_service.py` that:
   - Accepts structured reservation data (not text)
   - Calls existing rule engine with proper context dict
   - Returns enriched response with DB-backed options
3. New API endpoints use the structured service
4. Old `/process` endpoint remains for legacy/testing

This preserves all existing rule logic while adding structured data flow.
