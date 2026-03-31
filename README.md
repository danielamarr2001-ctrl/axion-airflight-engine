# AXIOM AirFlight Engine

Rule-based decision engine for automating involuntary flight changes in airline post-sale operations.

AXIOM takes a PNR + passenger last name, retrieves the reservation, evaluates sequential business rules, generates reprotection options, and lets the operator select an alternative flight — logging every decision with full traceability.

## Architecture

```
┌─────────────────────────────┐     ┌──────────────────────────────┐
│     axiom-ui (Next.js)      │────▶│     axiom (FastAPI)          │
│  React 19 + shadcn/ui       │     │  Decision Engine + Rules     │
│  Tailwind + Recharts        │     │  SQLAlchemy + SQLite         │
└─────────────────────────────┘     └──────────────────────────────┘
```

**Decision Flow:**

```
PNR + Last Name → Lookup Reservation → Evaluate Rules → Generate Options → Select Flight → Record Decision
```

## Project Structure

```
axiom-airflight-engine/
├── axiom/                    # Python backend
│   ├── api/                  # FastAPI endpoints
│   │   ├── main.py           # App entry + router wiring
│   │   └── routers/          # API route handlers
│   ├── db/                   # Database layer
│   │   ├── engine.py         # SQLAlchemy engine + session
│   │   ├── models.py         # 7 ORM models
│   │   └── seed.py           # Demo data generation
│   ├── decision_engine/      # Core decision pipeline
│   │   ├── decision_core.py  # Orchestrator
│   │   ├── validators.py     # PNR/passenger validation
│   │   ├── event_classifier.py
│   │   ├── rule_engine.py    # Python rule engine
│   │   └── options_generator.py
│   ├── models/               # Pydantic schemas
│   ├── rules/                # Business rules
│   ├── rule_platform/        # Table-based rule subsystem
│   └── services/             # Service layer
│       ├── lookup_service.py
│       ├── decision_service.py
│       └── metrics_service.py
├── axiom-ui/                 # React frontend
│   ├── src/
│   │   ├── app/              # Next.js App Router pages
│   │   │   ├── processor/    # PNR lookup + decision workflow
│   │   │   ├── metrics/      # KPI dashboard
│   │   │   └── rules/        # Rules management
│   │   ├── components/       # React components
│   │   │   ├── processor/    # Decision flow components
│   │   │   ├── metrics/      # Chart components
│   │   │   └── ui/           # shadcn/ui primitives
│   │   └── lib/              # Types, API client, translations
│   └── next.config.ts        # API proxy to FastAPI
├── axiom_dashboard/          # [DEPRECATED] Old Flutter dashboard
├── docs/                     # Documentation + brand assets
├── .planning/                # GSD planning artifacts
├── requirements.txt          # Python dependencies
└── CLAUDE.md                 # AI development guide
```

## Quick Start

### Backend

```bash
pip install -r requirements.txt
python -m axiom.db.seed          # Seed demo data
uvicorn axiom.api.main:app --port 8000
```

### Frontend

```bash
cd axiom-ui
pnpm install
pnpm dev                         # Starts on port 3000
```

Open http://localhost:3000

### Demo PNRs

| PNR | Last Name | Scenario |
|-----|-----------|----------|
| `XKJR4T` | `MARTINEZ` | Golden path — cancelled flight, reprotection approved |
| `BN7M2P` | `TORRES` | Escalation — sensitive SSR, manual review |
| `FW3KLC` | `RODRIGUEZ` | Multi-segment itinerary |
| `HT9QRS` | `GARCIA` | Standard case |

## API Endpoints

### New Structured API (`/api/`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/lookup` | PNR + last name lookup |
| POST | `/api/evaluate` | Rule evaluation for reservation |
| POST | `/api/select` | Record flight selection |
| GET | `/api/decisions` | Decision history |
| GET | `/api/metrics` | KPI dashboard data |
| GET/POST/PUT/DELETE | `/api/rules` | Rules CRUD |

### Legacy API

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/process` | Text-based decision processing |
| GET | `/health` | Health check |

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 15, React 19, TypeScript, Tailwind CSS, shadcn/ui, Recharts |
| Backend | Python 3.12, FastAPI, Pydantic 2, SQLAlchemy 2.0 |
| Database | SQLite (upgradeable to PostgreSQL) |
| State | TanStack Query (frontend), useReducer state machine |

## Brand

AXIOM uses a dark theme with teal (#2ABFBF) accents. See `docs/AXIOM BRAND GUIDELINES.pdf` for full brand specifications.

## License

Proprietary. All rights reserved.
