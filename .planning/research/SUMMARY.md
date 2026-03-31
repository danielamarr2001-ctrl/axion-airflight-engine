# Research Summary: AXIOM AirFlight Engine

## Key Findings

### Stack
- **Frontend**: Next.js 15 + React 19 + TypeScript + Tailwind CSS 4 + shadcn/ui + Recharts
- **Backend**: Extend existing FastAPI + SQLAlchemy 2.0 + SQLite + Pydantic 2.x
- **Why shadcn/ui**: Native dark theme, Tailwind integration, professional aesthetic, full control
- **Why SQLite**: Zero-config for demo, SQL-compatible, upgradeable to PostgreSQL later

### Table Stakes (Must Have)
- Structured PNR + last name lookup (replace text input)
- Full reservation display (passengers, segments, fare class, SSR)
- Rule evaluation with visual trace
- Reprotection options with selection flow
- Decision recording with audit trail
- KPI dashboard (automation rate, processing time, volume trends)
- Dark theme matching AXIOM brand guidelines

### Architecture
- Adapter pattern: Wrap existing DecisionCore, don't rewrite
- New structured endpoints alongside existing `/process`
- SQLite database for reservations, flights, rules, decisions
- Pre-seeded demo data (10-20 reservations, 50-100 historical decisions)
- Next.js API routes as proxy to FastAPI (eliminates CORS issues)

### Critical Pitfalls
1. **Unrealistic simulated data** → Use real IATA codes, realistic PNR formats, geographic-sense routes
2. **Empty dashboard on first load** → Pre-seed 50-100 historical decisions
3. **Over-engineering** → SQLite, single process, no Docker/k8s/queues
4. **Dark theme contrast** → Define CSS custom properties upfront, test WCAG AA
5. **No demo script** → Design seed data around a specific investor demo scenario

## Build Order (Suggested Phases)

1. **Foundation**: Database schema + models + seed data + .gitignore + project cleanup
2. **Backend API**: New structured endpoints (lookup, evaluate, select, decisions, metrics)
3. **Frontend Core**: Next.js scaffold + dark theme + PNR lookup + reservation display
4. **Decision Flow**: Rule evaluation UI + options + selection + decision panel
5. **Polish**: KPI dashboard + brand alignment + demo scenario validation

## Roadmap Implications

- **Coarse granularity** (3-5 phases) works well — natural breakpoints at: Foundation, Backend, Frontend+Integration, Polish
- **Database + seed data must come first** — everything depends on structured data
- **Frontend and backend can partially parallel** after API contracts defined
- **Polish phase is critical** for investor demo — allocate real time for it
- **Keep existing code working** throughout (adapter pattern, not rewrite)
