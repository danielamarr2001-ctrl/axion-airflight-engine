# Stack Research: AXIOM AirFlight Engine

## Current Stack (Existing)
- **Backend**: Python 3.12+ / FastAPI 0.116.1 / Pydantic 2.11.7 / Uvicorn 0.35.0
- **Frontend**: Flutter Web (being replaced)
- **Storage**: JSON file logging, CSV rule storage
- **No database, no auth, no testing framework**

## Recommended Stack (Investor Demo)

### Frontend — React/Next.js

| Technology | Version | Rationale | Confidence |
|-----------|---------|-----------|------------|
| **Next.js** | 15.x (App Router) | Server components, API routes as proxy, optimized builds | HIGH |
| **React** | 19.x | Latest stable with concurrent features | HIGH |
| **TypeScript** | 5.x | Type safety for complex airline data models | HIGH |
| **Tailwind CSS** | 4.x | Rapid dark theme styling, utility-first | HIGH |
| **shadcn/ui** | latest | Dark theme built-in, professional components, customizable | HIGH |
| **Recharts** | 2.x | Best React charting lib for KPI dashboards, composable | HIGH |
| **TanStack Query** | 5.x | Server state management, caching, real-time refetch | HIGH |
| **Lucide React** | latest | Icon set matching professional SaaS aesthetic | MEDIUM |
| **next-themes** | latest | Dark/light mode switching (brand requires dark) | MEDIUM |

**Why shadcn/ui over alternatives:**
- MUI: Too opinionated, heavy bundle, hard to customize dark theme precisely
- Ant Design: Enterprise-focused but Chinese ecosystem, inconsistent dark mode
- Chakra UI: Good but shadcn has better Tailwind integration and is more modern
- shadcn/ui: Copies components into your project (full control), built on Radix UI (accessibility), native Tailwind theming

**Why Recharts over alternatives:**
- Chart.js: Canvas-based, harder to style with React
- D3: Too low-level for dashboard charts
- Nivo: Good but heavier
- Recharts: SVG-based, composable, responsive, easy dark theme

### Backend — FastAPI Extended

| Technology | Version | Rationale | Confidence |
|-----------|---------|-----------|------------|
| **FastAPI** | 0.116.x | Keep existing, extend endpoints | HIGH |
| **SQLAlchemy** | 2.0.x | ORM for structured data, async support | HIGH |
| **SQLite** | built-in | Zero-config local DB for demo, upgradable to PostgreSQL | HIGH |
| **aiosqlite** | 0.20.x | Async SQLite driver for FastAPI | HIGH |
| **Alembic** | 1.x | Database migrations | MEDIUM |
| **Pydantic** | 2.11.x | Keep existing, extend models | HIGH |
| **python-dotenv** | 1.x | Environment configuration | HIGH |
| **httpx** | 0.28.x | Async HTTP client for future GDS integration | MEDIUM |
| **pytest** | 8.x | Testing framework | HIGH |
| **pytest-asyncio** | 0.24.x | Async test support | HIGH |

**Why SQLite over alternatives:**
- PostgreSQL: Overkill for investor demo, requires separate server
- MongoDB: Wrong paradigm for relational PNR/flight data
- SQLite: Zero config, file-based, SQL-compatible, upgradeable to PostgreSQL later
- In-memory dict: Not persistent, hard to query

### Development Tools

| Tool | Purpose | Confidence |
|------|---------|------------|
| **pnpm** | Package manager (faster than npm) | MEDIUM |
| **ESLint + Prettier** | Code quality | HIGH |
| **Ruff** | Python linting (replaces flake8+black+isort) | HIGH |

## What NOT to Use

| Technology | Reason |
|-----------|--------|
| Flutter Web | Being replaced — limited SaaS ecosystem, harder to polish for investor demo |
| MongoDB | Relational data (PNR→segments→passengers) is natural SQL |
| GraphQL | Overkill for this scope, REST is simpler and sufficient |
| Redis | No real-time features needed for demo |
| Docker | Unnecessary complexity for local demo |
| OAuth/Auth0 | No auth needed for investor demo |
| Celery/Background workers | No async processing needed |
| WebSockets | Polling or refetch sufficient for KPI updates |

## Build Order Implications

1. **Database + Models first** — SQLAlchemy models, seed data, migrations
2. **Backend API extension** — New structured endpoints on existing FastAPI
3. **Frontend scaffold** — Next.js + shadcn/ui + Tailwind dark theme
4. **Integration** — Connect frontend to backend APIs
5. **Polish** — KPI charts, animations, brand alignment
