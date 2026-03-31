# Phase 1: Foundation + Backend + App Shell - Research

**Researched:** 2026-03-30
**Domain:** SQLAlchemy/SQLite database layer, FastAPI endpoint extension, Next.js 15 scaffold with shadcn/ui dark theme
**Confidence:** HIGH

## Summary

Phase 1 establishes three foundations simultaneously: (1) a SQLite database with SQLAlchemy ORM replacing the current JSON/CSV file storage, seeded with realistic airline data; (2) six new FastAPI endpoints for structured PNR lookup, rule evaluation, option selection, decision history, metrics, and enhanced rules CRUD; (3) a Next.js 15 App Router scaffold with AXIOM dark theme, sidebar navigation, and desktop layout.

The existing FastAPI app at `axiom/api/main.py` uses synchronous route handlers (no async/await). The simplest integration path is **synchronous SQLAlchemy** with `create_engine` and `SessionLocal`, matching the existing codebase pattern. FastAPI automatically runs sync handlers in a threadpool, so there is no performance concern for a single-user demo. This avoids the complexity of async engine setup, aiosqlite driver, and async session management.

**Primary recommendation:** Use synchronous SQLAlchemy 2.0 with SQLite, FastAPI APIRouter for new endpoints, and Next.js 15 with shadcn/ui dark theme using CSS variables mapped to AXIOM brand teal (#2ABFBF).

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| DATA-01 | Store realistic simulated reservations in SQLite (10-20 PNRs with passengers, segments, fare classes, SSRs) | SQLAlchemy models for reservations, passengers, segments, ssr_records tables; seed script with IATA-compliant data |
| DATA-02 | Store realistic simulated available flights for reprotection options | flights table with real IATA routes, multiple departure times per route |
| DATA-03 | Store pre-seeded historical decisions (50-100 records) for KPI dashboard | decisions table with 100 records spread across 14-30 days, realistic processing times and rule triggers |
| DATA-04 | All simulated data uses real IATA airport codes, airline codes, geographic-sense routes | Research provides IATA codes (BOG, MDE, MIA, MAD, CLO, CTG, SCL, LIM, PTY, GRU), airline codes (AV, LA, IB, AA, CM), SSR types, fare classes |
| DATA-05 | Database schema supports reservations, passengers, segments, SSR records, flights, rules, decisions | Normalized schema with 7 tables, SQLAlchemy 2.0 Mapped column types, proper foreign keys |
| API-01 | POST /api/lookup - accepts PNR + last name, returns structured reservation | New endpoint using SQLAlchemy session query, Pydantic response models |
| API-02 | POST /api/evaluate - runs rule engine against reservation, returns decision with options | Adapter service wrapping existing DecisionCore with structured input |
| API-03 | POST /api/select - records operator flight selection as decision | Insert into decisions table with selected option |
| API-04 | GET /api/decisions - returns decision history with pagination | SQLAlchemy query with limit/offset pagination |
| API-05 | GET /api/metrics - returns aggregated KPI data | SQL aggregation queries replacing JSON file reads |
| API-06 | Existing /rules CRUD preserved and enhanced with database storage | Migrate RuleRepository from CSV to SQLAlchemy; keep same API contract |
| UI-01 | Application uses Next.js with React and TypeScript | Next.js 15.x App Router with TypeScript, create-next-app scaffold |
| UI-02 | Dark theme matching AXIOM brand (dark background, teal accents ~#2ABFBF) | shadcn/ui CSS variables mapped to AXIOM palette, OKLCH/HSL tokens |
| UI-03 | Navigation shell with sidebar between Processor, Rules, and Metrics views | shadcn/ui sidebar component with lucide-react icons |
| UI-06 | Desktop-first responsive layout optimized for large screens | Min-width 1280px design target, no mobile breakpoints needed |
</phase_requirements>

## Project Constraints (from CLAUDE.md)

- **Backend**: Python/FastAPI -- extend existing, do not rewrite core
- **Frontend**: React/Next.js with AXIOM brand dark theme (replacing Flutter)
- **Storage**: Local database for demo (SQLite)
- **Demo quality**: Investor-ready UI polish following exact brand guidelines
- **No real integrations**: All data simulated, all actions are decision records
- **NEVER use Bash heredocs** for file creation -- always use Write tool
- **NEVER embed secrets** in Bash commands
- **GSD workflow enforcement**: Use GSD commands for planned work

## Standard Stack

### Core - Backend (Python)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| SQLAlchemy | 2.0.48 | ORM for structured data, model definitions, queries | Standard Python ORM, 2.0 style with Mapped types, sync works with existing FastAPI sync handlers |
| SQLite | built-in | Zero-config local database | Python stdlib, no server process, single file, sufficient for demo |
| Alembic | 1.18.4 | Database schema migrations | Standard companion to SQLAlchemy, autogenerate from models |
| python-dotenv | 1.2.2 | Environment configuration from .env files | Already installed on system, standard for FastAPI projects |
| FastAPI | 0.116.1 | HTTP API (existing) | Already in use, extend with APIRouter |
| Pydantic | 2.11.7 | Data validation (existing) | Already in use, extend with new response models |
| Uvicorn | 0.35.0 | ASGI server (existing) | Already in use |

**Important decision: Synchronous SQLAlchemy, NOT async.** The existing codebase has zero async code. All route handlers in `main.py` are synchronous functions. FastAPI runs sync handlers in a threadpool automatically. Using async SQLAlchemy would require: (1) aiosqlite driver, (2) async engine, (3) async sessions, (4) converting all handlers to async, (5) async Alembic env.py. For a single-user demo with SQLite, this complexity provides no benefit.

### Core - Frontend (JavaScript/TypeScript)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Next.js | 15.x (latest 15.2.1+) | React framework with App Router | Standard for new React projects, static export capable |
| React | 19.x (latest 19.2.4) | UI library | Required by Next.js 15 |
| TypeScript | 5.x+ (latest 6.0.2 available but 5.x is safer with Next.js 15) | Type safety | Required for airline data model complexity |
| Tailwind CSS | 4.x (latest 4.2.2) | Utility-first CSS | Built into Next.js, shadcn/ui requires it |
| shadcn/ui | latest | Component library (copies into project) | Dark theme built-in, Radix UI accessibility, full customization |
| TanStack Query | 5.x (latest 5.95.2) | Server state management | Caching, auto-refetch, loading/error states for API calls |
| Recharts | 2.x (latest 3.8.1 available -- use 2.x for stability) | Charting for KPI dashboard | SVG-based, composable, React-native, dark theme friendly |
| Lucide React | latest (1.7.0) | Icon set | Clean, consistent, used by shadcn/ui sidebar |
| next-themes | latest (0.4.6) | Theme management | Dark mode persistence and switching |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| class-variance-authority | 0.7.1 | Component variant management | Required by shadcn/ui components |
| clsx | 2.1.1 | Conditional class names | Required by shadcn/ui cn() utility |
| tailwind-merge | 3.5.0 | Tailwind class deduplication | Required by shadcn/ui cn() utility |
| @radix-ui/react-slot | 1.2.4 | Polymorphic component support | Required by shadcn/ui Button, etc. |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Sync SQLAlchemy | Async SQLAlchemy + aiosqlite | Adds complexity (async engine, sessions, handlers) for zero demo benefit |
| SQLAlchemy | SQLModel | SQLModel is simpler but less mature, fewer patterns documented |
| shadcn/ui | MUI, Chakra UI | MUI/Chakra have opinionated dark themes that fight custom brand colors |
| Recharts 2.x | Recharts 3.x | v3 is newer but less documented; v2 is battle-tested for dashboards |
| pnpm | npm | pnpm is faster, already available on dev machine (v10.26.0) |

**Backend installation:**
```bash
pip install sqlalchemy==2.0.48 alembic==1.18.4 python-dotenv==1.2.2
```

**Frontend scaffold:**
```bash
pnpm create next-app@latest axiom-ui --typescript --tailwind --eslint --app --src-dir --import-alias "@/*"
cd axiom-ui
pnpm dlx shadcn@latest init
pnpm add @tanstack/react-query recharts lucide-react next-themes
```

## Architecture Patterns

### Recommended Project Structure

```
axiom/                          # Existing Python backend
  api/
    main.py                     # Existing app + include new routers
    routers/                    # NEW: API route modules
      lookup.py                 # POST /api/lookup
      evaluate.py               # POST /api/evaluate
      select.py                 # POST /api/select
      decisions.py              # GET /api/decisions
      metrics.py                # GET /api/metrics
      rules.py                  # Enhanced CRUD /api/rules
  db/                           # NEW: Database layer
    engine.py                   # SQLAlchemy engine + SessionLocal
    models.py                   # ORM model definitions
    seed.py                     # Seed data script
  services/                     # NEW: Business logic layer
    lookup_service.py           # PNR lookup queries
    decision_service.py         # Adapter wrapping DecisionCore
    metrics_service.py          # KPI aggregation queries
  models/                       # Existing Pydantic models
    request.py                  # Existing
    response.py                 # Existing
    schemas.py                  # NEW: API request/response schemas for new endpoints
  decision_engine/              # Existing (DO NOT MODIFY)
  rule_platform/                # Existing (keep, but rules CRUD migrates to DB)
  rules/                        # Existing (keep)
  config.py                     # Existing (extend with DB_URL)

axiom-ui/                       # NEW: Next.js frontend
  src/
    app/
      layout.tsx                # Root layout with providers + theme
      page.tsx                  # Redirect to /processor
      processor/
        page.tsx                # PNR Lookup / Decision panel (Phase 2 content)
      rules/
        page.tsx                # Rules management
      metrics/
        page.tsx                # KPI dashboard
    components/
      app-sidebar.tsx           # Navigation sidebar
      theme-provider.tsx        # next-themes provider
      query-provider.tsx        # TanStack Query provider
    lib/
      api.ts                    # API client base URL + fetch helpers
      utils.ts                  # cn() utility from shadcn
    styles/
      globals.css               # AXIOM dark theme CSS variables
  next.config.ts                # API proxy rewrites to FastAPI
  components.json               # shadcn/ui configuration
  tailwind.config.ts            # Tailwind theme extensions
```

### Pattern 1: FastAPI APIRouter for New Endpoints

**What:** Use FastAPI's APIRouter to organize new endpoints in separate files, then include them in the main app.
**When to use:** Always when adding new endpoint groups to an existing FastAPI app.

```python
# axiom/api/routers/lookup.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from axiom.db.engine import get_db
from axiom.models.schemas import LookupRequest, ReservationResponse

router = APIRouter(prefix="/api", tags=["lookup"])

@router.post("/lookup", response_model=ReservationResponse)
def lookup_reservation(request: LookupRequest, db: Session = Depends(get_db)):
    reservation = db.query(Reservation).filter(
        Reservation.pnr == request.pnr
    ).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    # Check passenger last name matches
    passenger_match = any(
        p.last_name.upper() == request.last_name.upper()
        for p in reservation.passengers
    )
    if not passenger_match:
        raise HTTPException(status_code=404, detail="PNR and last name do not match")
    return reservation

# axiom/api/main.py (modification)
from axiom.api.routers import lookup, evaluate, select, decisions, metrics, rules
app.include_router(lookup.router)
app.include_router(evaluate.router)
# ... etc
```

### Pattern 2: SQLAlchemy Synchronous Engine with FastAPI Dependency

**What:** Create engine once at module level, yield sessions through dependency injection.
**When to use:** For all database access in route handlers.

```python
# axiom/db/engine.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from axiom.config import DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # Required for SQLite
    echo=False,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### Pattern 3: SQLAlchemy 2.0 Mapped Models

**What:** Use the modern `Mapped` annotation style for model definitions.
**When to use:** All ORM model definitions.

```python
# axiom/db/models.py
from datetime import datetime, date
from typing import List, Optional
from sqlalchemy import String, Integer, ForeignKey, DateTime, Text, Date, Time, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from axiom.db.engine import Base

class Reservation(Base):
    __tablename__ = "reservations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    pnr: Mapped[str] = mapped_column(String(6), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    passengers: Mapped[List["Passenger"]] = relationship(back_populates="reservation", cascade="all, delete-orphan")
    segments: Mapped[List["Segment"]] = relationship(back_populates="reservation", cascade="all, delete-orphan")

class Passenger(Base):
    __tablename__ = "passengers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    reservation_id: Mapped[int] = mapped_column(ForeignKey("reservations.id"))
    last_name: Mapped[str] = mapped_column(String(50))
    first_name: Mapped[str] = mapped_column(String(50))
    ticket_number: Mapped[str] = mapped_column(String(13))  # e.g., 045-1234567890
    fare_class: Mapped[str] = mapped_column(String(1))      # Y, B, M, H, Q, etc.

    reservation: Mapped["Reservation"] = relationship(back_populates="passengers")
    ssr_records: Mapped[List["SSRRecord"]] = relationship(back_populates="passenger", cascade="all, delete-orphan")
```

### Pattern 4: Next.js API Proxy via Rewrites

**What:** Proxy all `/api/*` requests from Next.js to FastAPI backend, eliminating CORS issues.
**When to use:** During development and demo deployment.

```typescript
// next.config.ts
import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://127.0.0.1:8000/api/:path*',
      },
    ];
  },
};

export default nextConfig;
```

### Pattern 5: TanStack Query Provider in App Router

**What:** Client-side QueryClientProvider wrapping the app layout.
**When to use:** Required for all TanStack Query hooks to work.

```typescript
// src/components/query-provider.tsx
"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState } from "react";

export function QueryProvider({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 5 * 60 * 1000,  // 5 minutes
        retry: 1,
      },
    },
  }));

  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
}

// src/app/layout.tsx
import { QueryProvider } from "@/components/query-provider";
import { ThemeProvider } from "@/components/theme-provider";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <ThemeProvider attribute="class" defaultTheme="dark" enableSystem={false}>
          <QueryProvider>
            {children}
          </QueryProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
```

### Pattern 6: AXIOM Dark Theme CSS Variables

**What:** Map AXIOM brand colors to shadcn/ui CSS variable system.
**When to use:** Set up once in globals.css, all components inherit.

```css
/* src/styles/globals.css */
@import "tailwindcss";

:root {
  --background: oklch(0.145 0.02 260);      /* Very dark blue-gray */
  --foreground: oklch(0.95 0.01 260);        /* Near-white */
  --card: oklch(0.18 0.02 260);              /* Slightly lighter surface */
  --card-foreground: oklch(0.95 0.01 260);
  --primary: oklch(0.72 0.15 185);           /* AXIOM Teal ~#2ABFBF */
  --primary-foreground: oklch(0.15 0.02 185);/* Dark text on teal */
  --secondary: oklch(0.22 0.02 260);
  --secondary-foreground: oklch(0.9 0.01 260);
  --muted: oklch(0.2 0.02 260);
  --muted-foreground: oklch(0.6 0.01 260);
  --accent: oklch(0.72 0.15 185);            /* Teal accent */
  --accent-foreground: oklch(0.15 0.02 185);
  --destructive: oklch(0.55 0.2 25);         /* Error red */
  --border: oklch(0.28 0.02 260);
  --input: oklch(0.28 0.02 260);
  --ring: oklch(0.72 0.15 185);              /* Teal focus ring */
  --radius: 0.5rem;

  /* Chart palette */
  --chart-1: oklch(0.72 0.15 185);           /* Teal */
  --chart-2: oklch(0.65 0.15 250);           /* Blue */
  --chart-3: oklch(0.7 0.15 145);            /* Green */
  --chart-4: oklch(0.7 0.15 55);             /* Yellow */
  --chart-5: oklch(0.65 0.15 310);           /* Purple */

  /* Sidebar */
  --sidebar: oklch(0.12 0.02 260);
  --sidebar-foreground: oklch(0.85 0.01 260);
  --sidebar-primary: oklch(0.72 0.15 185);
  --sidebar-primary-foreground: oklch(0.15 0.02 185);
  --sidebar-accent: oklch(0.2 0.02 260);
  --sidebar-accent-foreground: oklch(0.9 0.01 260);
  --sidebar-border: oklch(0.25 0.02 260);
  --sidebar-ring: oklch(0.72 0.15 185);
}

/* Force dark theme only -- no .dark class needed since defaultTheme="dark" */
.dark {
  /* Same as :root since app is dark-only */
}
```

**Note:** The exact OKLCH values need visual testing. The key principle is: `--primary` and `--accent` both map to the AXIOM teal (#2ABFBF approximated in OKLCH), and all background surfaces use very dark blue-gray tones.

### Anti-Patterns to Avoid

- **Mixing sync and async handlers in the same app without understanding:** Existing handlers are sync. New handlers should also be sync for consistency. Do NOT convert existing handlers to async.
- **Putting all new endpoints in main.py:** Use APIRouter to keep main.py clean. Include routers at the end of main.py.
- **Hardcoding colors in components:** All colors must come from CSS variables. No `text-[#2ABFBF]` in component code.
- **Using Pages Router patterns in App Router:** No `getServerSideProps`, no `_app.tsx`. Use server components and client components with `"use client"` directive.
- **Importing server-only code in client components:** Keep TanStack Query hooks in client components, data fetching helpers separate.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Database ORM | Custom SQL query builder | SQLAlchemy 2.0 Mapped models | Relationships, migrations, type safety |
| DB migrations | Manual CREATE TABLE scripts | Alembic with autogenerate | Schema evolution, rollback capability |
| API data fetching in React | Custom fetch + useState | TanStack Query | Caching, deduplication, loading/error states, refetch |
| Dark theme system | Custom CSS class toggling | next-themes + shadcn CSS variables | Persistence, SSR flash prevention, variable inheritance |
| UI components | Custom buttons, dialogs, dropdowns | shadcn/ui components | Accessibility (Radix), keyboard navigation, dark theme |
| Form validation (frontend) | Custom validation logic | Pydantic on backend, form libs later | Backend validation is the authority; frontend validation is Phase 2+ |
| Data seeding | Manual INSERT statements | Python seed script with Faker-like patterns | Repeatable, consistent, can be reset |
| CORS handling | Custom middleware | Next.js rewrites proxy | Eliminates CORS entirely for the client |

**Key insight:** This is a demo, not a production system. Every hand-rolled solution is time taken away from making the demo visually impressive. Use standard tools.

## Common Pitfalls

### Pitfall 1: SQLite `check_same_thread` Error

**What goes wrong:** SQLite objects created in one thread cannot be used in another. FastAPI runs sync handlers in a threadpool, creating cross-thread access.
**Why it happens:** SQLite's default safety check.
**How to avoid:** Pass `connect_args={"check_same_thread": False}` to `create_engine()`. This is safe for a single-user demo.
**Warning signs:** `ProgrammingError: SQLite objects created in a thread can only be used in that same thread`

### Pitfall 2: Alembic SQLite ALTER TABLE Limitations

**What goes wrong:** SQLite does not support most ALTER TABLE operations (drop column, rename column, change type). Alembic migrations fail.
**Why it happens:** SQLite's limited DDL support.
**How to avoid:** Configure Alembic with `render_as_batch=True` in `env.py`. This recreates the table on schema changes instead of altering it.
**Warning signs:** `OperationalError: near "ALTER": syntax error`

```python
# alembic/env.py
context.configure(
    connection=connection,
    target_metadata=target_metadata,
    render_as_batch=True,  # CRITICAL for SQLite
)
```

### Pitfall 3: Breaking Existing `/process` and `/rules` Endpoints

**What goes wrong:** New database-backed endpoints break backward compatibility with the existing text-based pipeline.
**Why it happens:** Refactoring the existing code instead of extending it.
**How to avoid:** Keep ALL existing endpoints untouched. Add new endpoints under `/api/` prefix. The existing `/process`, `/rules`, `/metrics`, and `/health` remain exactly as they are. New frontend uses only `/api/*` endpoints.
**Warning signs:** Existing Flutter dashboard (if tested) stops working.

### Pitfall 4: Simulated Data Missing Critical Fields

**What goes wrong:** Seed data has PNR and passenger name but omits fare class, ticket number, SSR records, segment times, cabin class. Phase 2 UI needs these fields and the seed must be re-done.
**Why it happens:** Building minimal schema for the API without thinking about what the UI will display.
**How to avoid:** Define the FULL seed data schema now, including every field the UI will display in Phases 2-3. Include: fare basis codes (YOWCO, HLXP3M), booking class letters (Y, B, M, H, Q), ticket numbers (045-1234567890), SSR types (WCHR, PETC, UMNR, MEDA), segment status (HK/confirmed, XX/cancelled, TK/schedule change).
**Warning signs:** Any NULL or "unknown" field in the seed data that the UI will need to display.

### Pitfall 5: Next.js Dark Theme Flash of White

**What goes wrong:** On first load, the page briefly shows white background before dark theme applies.
**Why it happens:** Theme class not applied during SSR, hydration mismatch.
**How to avoid:** Use `next-themes` with `attribute="class"`, `defaultTheme="dark"`, `enableSystem={false}`. Add `suppressHydrationWarning` to `<html>` tag. Since this app is dark-only, set the `.dark` class directly and configure shadcn with dark as default.
**Warning signs:** Brief white flash on page load.

### Pitfall 6: shadcn/ui Init Choosing Wrong Settings

**What goes wrong:** Running `shadcn init` with wrong options creates CSS variable format mismatches or wrong base color.
**Why it happens:** Defaults may not match AXIOM requirements.
**How to avoid:** When running `pnpm dlx shadcn@latest init`, select: style = default, base color = slate or neutral (closest to dark blue-gray), CSS variables = yes. Then customize the CSS variables after init to match AXIOM palette.
**Warning signs:** Components render with unexpected colors.

### Pitfall 7: Forgetting the API Prefix Collision

**What goes wrong:** New `/api/rules` endpoint collides with existing `/rules` endpoint. Or Next.js API routes at `/api/*` conflict with the proxy rewrite.
**Why it happens:** Namespace overlap between old and new endpoints.
**How to avoid:** All new endpoints use `/api/` prefix. Old endpoints remain at root (`/rules`, `/process`, `/metrics`). Next.js rewrites forward `/api/*` to FastAPI. Next.js should NOT have its own API routes -- all API calls go through the proxy to FastAPI.
**Warning signs:** 404 errors on API calls, or responses from wrong handler.

## Code Examples

### Complete Database Engine Setup

```python
# axiom/db/engine.py
import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Database file lives next to the axiom package
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/axiom_demo.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    """FastAPI dependency that provides a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### Complete Alembic Setup for SQLite

```python
# alembic/env.py (key parts)
from axiom.db.engine import Base, DATABASE_URL
from axiom.db import models  # Import all models so metadata is populated

target_metadata = Base.metadata

def run_migrations_offline():
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        render_as_batch=True,  # CRITICAL for SQLite
        literal_binds=True,
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,  # CRITICAL for SQLite
        )
        with context.begin_transaction():
            context.run_migrations()
```

### Seed Data Structure -- Airline Domain Reference

```python
# Realistic IATA codes for LATAM-focused demo
AIRPORTS = {
    "BOG": "El Dorado, Bogota",
    "MDE": "Jose Maria Cordova, Medellin",
    "CLO": "Alfonso Bonilla Aragon, Cali",
    "CTG": "Rafael Nunez, Cartagena",
    "MIA": "Miami International",
    "MAD": "Adolfo Suarez Madrid-Barajas",
    "GRU": "Guarulhos, Sao Paulo",
    "SCL": "Arturo Merino Benitez, Santiago",
    "LIM": "Jorge Chavez, Lima",
    "PTY": "Tocumen, Panama City",
    "JFK": "John F. Kennedy, New York",
    "FLL": "Fort Lauderdale-Hollywood",
    "CUN": "Cancun International",
    "MEX": "Benito Juarez, Mexico City",
    "EZE": "Ministro Pistarini, Buenos Aires",
}

AIRLINES = {
    "AV": "Avianca",
    "LA": "LATAM Airlines",
    "IB": "Iberia",
    "AA": "American Airlines",
    "CM": "Copa Airlines",
    "B6": "JetBlue",
    "DL": "Delta Air Lines",
}

# Realistic routes (airlines actually fly these)
ROUTES = [
    ("AV", "BOG", "MDE"),  # Avianca domestic Colombia
    ("AV", "BOG", "CTG"),
    ("AV", "BOG", "MIA"),  # Avianca to US
    ("AV", "BOG", "MAD"),  # Avianca to Europe
    ("LA", "BOG", "LIM"),  # LATAM hub connections
    ("LA", "SCL", "GRU"),
    ("LA", "LIM", "MIA"),
    ("IB", "MAD", "BOG"),  # Iberia transatlantic
    ("IB", "MAD", "MIA"),
    ("CM", "PTY", "BOG"),  # Copa hub connections
    ("CM", "PTY", "MDE"),
    ("AA", "MIA", "BOG"),  # American Airlines
    ("AA", "JFK", "BOG"),
]

# Fare classes by cabin
FARE_CLASSES = {
    "economy_full": ["Y", "B"],
    "economy_discount": ["M", "H", "Q", "V", "W", "S", "T", "L", "K"],
    "business": ["J", "C", "D"],
    "first": ["F", "A"],
}

# SSR types that affect reprotection decisions
SSR_TYPES = {
    "WCHR": "Wheelchair - ramp",
    "WCHS": "Wheelchair - steps",
    "WCHC": "Wheelchair - cabin seat",
    "UMNR": "Unaccompanied minor",
    "MEDA": "Medical assistance",
    "PETC": "Pet in cabin",
    "BLND": "Blind passenger",
    "DEAF": "Deaf passenger",
    "MAAS": "Meet and assist",
}

# Segment statuses
SEGMENT_STATUSES = {
    "HK": "Confirmed",
    "XX": "Cancelled",
    "TK": "Schedule change",
    "UN": "Unable - waitlisted",
}

# PNR format: 6 alphanumeric characters, uppercase
# Examples: XKJR4T, BN7M2P, FW3KLC, HT9QRS
# Ticket number format: 3-digit airline code + 10 digits
# Examples: 045-1234567890 (Avianca), 045-9876543210
```

### FastAPI Router with Database Dependency

```python
# axiom/api/routers/decisions.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from axiom.db.engine import get_db
from axiom.db.models import Decision
from axiom.models.schemas import DecisionListResponse, PaginatedResponse

router = APIRouter(prefix="/api", tags=["decisions"])

@router.get("/decisions", response_model=PaginatedResponse)
def list_decisions(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    total = db.query(Decision).count()
    decisions = (
        db.query(Decision)
        .order_by(Decision.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )
    return {
        "items": decisions,
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page,
    }
```

### Next.js Sidebar Navigation Component

```typescript
// src/components/app-sidebar.tsx
"use client";

import { usePathname } from "next/navigation";
import Link from "next/link";
import { Search, BookOpen, BarChart3 } from "lucide-react";
import { cn } from "@/lib/utils";

const navigation = [
  { name: "Processor", href: "/processor", icon: Search },
  { name: "Rules", href: "/rules", icon: BookOpen },
  { name: "Metrics", href: "/metrics", icon: BarChart3 },
];

export function AppSidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex h-screen w-64 flex-col border-r border-sidebar-border bg-sidebar">
      <div className="flex h-16 items-center px-6">
        <span className="text-xl font-bold text-sidebar-primary">AXIOM</span>
      </div>
      <nav className="flex-1 space-y-1 px-3 py-4">
        {navigation.map((item) => (
          <Link
            key={item.name}
            href={item.href}
            className={cn(
              "flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors",
              pathname === item.href
                ? "bg-sidebar-accent text-sidebar-primary"
                : "text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
            )}
          >
            <item.icon className="h-4 w-4" />
            {item.name}
          </Link>
        ))}
      </nav>
    </aside>
  );
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| SQLAlchemy 1.x `declarative_base()` | SQLAlchemy 2.0 `DeclarativeBase` class + `Mapped` types | 2023 (SQLAlchemy 2.0 release) | Type-safe columns, better IDE support |
| Next.js Pages Router `getServerSideProps` | Next.js App Router server components + `"use client"` | 2023 (Next.js 13.4 stable) | Simpler data flow, smaller bundles |
| Tailwind CSS v3 `tailwind.config.js` | Tailwind CSS v4 CSS-first config with `@theme` | 2025 (Tailwind v4) | No JS config file, CSS variables native |
| shadcn/ui HSL color format | shadcn/ui OKLCH color format | 2025 (with Tailwind v4 migration) | Better perceptual uniformity |
| React Query v3 context | TanStack Query v5 with `useState` QueryClient | 2023 (TanStack rebrand) | Framework-agnostic, better SSR support |
| `hsl(var(--chart-1))` in Recharts | `var(--chart-1)` directly | 2025 (Tailwind v4 wraps at declaration) | Simpler chart config |

**Deprecated/outdated:**
- SQLAlchemy `Column(Integer)` style: Replaced by `Mapped[int] = mapped_column()`
- `declarative_base()` function: Replaced by `class Base(DeclarativeBase):`
- Next.js `_app.tsx` / `_document.tsx`: Replaced by `app/layout.tsx`
- Tailwind `tailwind.config.js` with theme.extend: Tailwind v4 uses CSS `@theme` directive
- `hsl(var(--color))` pattern: Tailwind v4 wraps at declaration time, use `var(--color)` directly

## Open Questions

1. **Recharts 2.x vs 3.x?**
   - What we know: Recharts 3.8.1 is latest. v3 is a major rewrite.
   - What's unclear: Whether v3 has stable dark theme support and sufficient documentation.
   - Recommendation: Start with latest (v3) if documentation exists; fall back to v2 if issues arise. The planner should specify one version.

2. **OKLCH exact values for AXIOM teal?**
   - What we know: #2ABFBF in HSL is approximately hsl(180, 66%, 46%). In OKLCH this is roughly oklch(0.72 0.12 185).
   - What's unclear: The exact OKLCH values that match the brand guidelines after rendering.
   - Recommendation: Start with the OKLCH approximation, then visually verify against the brand PDF and adjust. This is a 5-minute task.

3. **Alembic vs direct `Base.metadata.create_all()`?**
   - What we know: For a demo, `create_all()` is simpler. Alembic adds migration capability.
   - What's unclear: Whether migrations are needed if the DB can be recreated from seed at any time.
   - Recommendation: Use `create_all()` for Phase 1 simplicity. Add Alembic only if schema evolves in later phases. The seed script can drop-and-recreate.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.14 | Backend | Yes | 3.14.3 | -- |
| Node.js | Frontend | Yes | 25.2.1 | -- |
| pnpm | Package management | Yes | 10.26.0 | npm (built into Node) |
| pip | Python packages | Yes | via pyenv | -- |
| SQLite | Database | Yes | built into Python | -- |

**Missing dependencies with no fallback:** None -- all required tools are available.

**Missing dependencies with fallback:** None.

**Note:** Python environment is externally managed (pyenv). Backend dependencies must be installed in a virtual environment:
```bash
cd /Users/fbetncourtc/Documents/finops/axion-airflight-engine
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install sqlalchemy==2.0.48 alembic==1.18.4 python-dotenv==1.2.2
```

## Database Schema Reference

The following normalized schema supports all Phase 1 requirements:

```sql
-- Reservations (DATA-01, DATA-05)
CREATE TABLE reservations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pnr VARCHAR(6) UNIQUE NOT NULL,         -- e.g., "XKJR4T"
    booking_reference VARCHAR(20),           -- External reference
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Passengers (DATA-01, DATA-05)
CREATE TABLE passengers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reservation_id INTEGER NOT NULL REFERENCES reservations(id),
    last_name VARCHAR(50) NOT NULL,          -- e.g., "MARTINEZ"
    first_name VARCHAR(50) NOT NULL,         -- e.g., "DANIELA"
    ticket_number VARCHAR(15),               -- e.g., "045-1234567890"
    fare_class VARCHAR(1) NOT NULL,          -- e.g., "Y"
    fare_basis VARCHAR(10),                  -- e.g., "YOWCO"
    passenger_type VARCHAR(3) DEFAULT 'ADT'  -- ADT, CHD, INF
);

-- Segments (DATA-01, DATA-05)
CREATE TABLE segments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reservation_id INTEGER NOT NULL REFERENCES reservations(id),
    flight_number VARCHAR(7) NOT NULL,       -- e.g., "AV123"
    airline VARCHAR(2) NOT NULL,             -- e.g., "AV"
    origin VARCHAR(3) NOT NULL,              -- IATA code "BOG"
    destination VARCHAR(3) NOT NULL,         -- IATA code "MDE"
    departure_date DATE NOT NULL,
    departure_time VARCHAR(5) NOT NULL,      -- "08:30"
    arrival_time VARCHAR(5) NOT NULL,        -- "09:45"
    status VARCHAR(2) NOT NULL DEFAULT 'HK', -- HK, XX, TK, UN
    cabin_class VARCHAR(1) DEFAULT 'Y',      -- Y=economy, C=business, F=first
    aircraft_type VARCHAR(4)                 -- e.g., "A320"
);

-- SSR Records (DATA-01, DATA-05)
CREATE TABLE ssr_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    passenger_id INTEGER NOT NULL REFERENCES passengers(id),
    ssr_type VARCHAR(4) NOT NULL,            -- e.g., "WCHR"
    ssr_detail VARCHAR(100)                  -- Free-text detail
);

-- Available Flights for reprotection (DATA-02)
CREATE TABLE flights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    flight_number VARCHAR(7) NOT NULL,
    airline VARCHAR(2) NOT NULL,
    origin VARCHAR(3) NOT NULL,
    destination VARCHAR(3) NOT NULL,
    departure_date DATE NOT NULL,
    departure_time VARCHAR(5) NOT NULL,
    arrival_time VARCHAR(5) NOT NULL,
    available_seats INTEGER DEFAULT 0,
    fare_class VARCHAR(1) DEFAULT 'Y',
    aircraft_type VARCHAR(4),
    status VARCHAR(10) DEFAULT 'SCHEDULED'   -- SCHEDULED, DELAYED, CANCELLED
);

-- Rules (API-06 -- migrated from CSV)
CREATE TABLE rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    field VARCHAR(50) NOT NULL,
    operator VARCHAR(10) NOT NULL,
    value VARCHAR(100) DEFAULT '',
    action VARCHAR(100) NOT NULL,
    priority INTEGER DEFAULT 1,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Decision Records (DATA-03, API-03, API-04)
CREATE TABLE decisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reservation_id INTEGER REFERENCES reservations(id),
    pnr VARCHAR(6),
    rule_applied VARCHAR(100),
    status VARCHAR(20) NOT NULL,             -- APPROVED, REJECTED, ESCALATED
    justification TEXT,
    trace TEXT,                              -- JSON array of trace strings
    options_generated TEXT,                  -- JSON array of option objects
    selected_option VARCHAR(10),             -- Selected flight number
    operator_notes TEXT,
    processing_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Seed Data Strategy

**Target quantities (from requirements):**
- 15-20 reservations with full passenger, segment, SSR data (DATA-01)
- 30-50 available flights across the main routes (DATA-02)
- 50-100 historical decision records spread across 14-30 days (DATA-03)
- 4-8 business rules migrated from existing CSV + new ones (API-06)

**Seed data must include specific demo scenarios:**
1. **Golden path scenario:** PNR with cancelled flight, same airline has alternatives, no sensitive SSR, same fare class = APPROVED
2. **Escalation scenario:** PNR with UMNR or MEDA SSR = ESCALATED (demonstrates edge case handling)
3. **Multi-segment scenario:** PNR with connecting flights where first segment is cancelled
4. **Multi-passenger scenario:** Family booking with 3+ passengers

**Historical decisions should show patterns:**
- 85-92% automation rate (APPROVED decisions)
- 5-10% escalated (SSR triggers)
- 3-5% rejected (fare class mismatch)
- Processing times: 8-120ms with realistic distribution
- Spread across 14 days with weekday peaks
- Top triggered rules: involuntary_change (most common), fare_protection, ssr_check

## Sources

### Primary (HIGH confidence)
- [shadcn/ui theming docs](https://ui.shadcn.com/docs/theming) - CSS variable system, OKLCH format
- [shadcn/ui Tailwind v4 docs](https://ui.shadcn.com/docs/tailwind-v4) - @theme configuration
- [shadcn/ui Next.js install](https://ui.shadcn.com/docs/installation/next) - Installation steps
- [Next.js rewrites docs](https://nextjs.org/docs/app/api-reference/config/next-config-js/rewrites) - API proxy pattern
- npm registry -- verified package versions (Next.js 16.2.1, React 19.2.4, TanStack Query 5.95.2, etc.)
- pip registry -- verified package versions (SQLAlchemy 2.0.48, Alembic 1.18.4, aiosqlite 0.22.1)

### Secondary (MEDIUM confidence)
- [FastAPI + Async SQLAlchemy 2.0 guide](https://medium.com/@tclaitken/setting-up-a-fastapi-app-with-async-sqlalchemy-2-0-pydantic-v2-e6c540be4308) - Session management patterns (adapted to sync)
- [Alembic async migrations](https://oboe.com/learn/async-sqlalchemy-and-fastapi-integration-wiocrt/async-alembic-migrations-1ixd0xz) - render_as_batch for SQLite
- [TanStack Query Next.js guide](https://ihsaninh.com/blog/the-complete-guide-to-tanstack-query-next.js-app-router) - Provider setup pattern
- [PNR structure explained](https://www.altexsoft.com/blog/pnr-explained/) - 6-character format, reservation structure
- [SSR codes reference](https://wheelchairtravel.org/air-travel-special-service-request-codes/) - WCHR, MEDA, UMNR, PETC codes
- [Fare basis codes](https://www.alternativeairlines.com/fare-basis-codes-explained) - Y, B, M, H, Q class letters

### Tertiary (LOW confidence)
- OKLCH color values for AXIOM teal -- approximated from #2ABFBF, needs visual verification

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All packages verified against registry, versions confirmed current
- Architecture: HIGH - Patterns based on official docs + existing codebase analysis
- Pitfalls: HIGH - Based on direct codebase inspection + domain knowledge verified through research
- Seed data domain accuracy: MEDIUM - IATA codes and airline routes verified through web search, but fare basis code format needs domain expert review
- OKLCH color values: LOW - Approximated, needs visual testing

**Research date:** 2026-03-30
**Valid until:** 2026-04-30 (stable domain, 30-day validity)
