# Roadmap: AXIOM AirFlight Engine

## Overview

AXIOM AirFlight Engine goes from existing FastAPI decision engine to investor-demo-ready product in three phases: first build the data foundation, API layer, and branded Next.js shell; then implement the core PNR lookup and decision workflow end-to-end; finally add the KPI dashboard and apply investor-demo polish. Each phase delivers a verifiable, working increment.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Foundation + Backend + App Shell** - Database, seed data, API endpoints, Next.js scaffold with dark theme and navigation
- [ ] **Phase 2: Core Workflow** - PNR lookup, rule evaluation, reprotection options, decision recording with full UI flows
- [ ] **Phase 3: KPI Dashboard + Demo Polish** - Operational metrics dashboard, investor-demo quality brand polish

## Phase Details

### Phase 1: Foundation + Backend + App Shell
**Goal**: A bootable Next.js application with AXIOM dark theme, navigation shell, SQLite database with realistic seed data, and all API endpoints returning structured responses
**Depends on**: Nothing (first phase)
**Requirements**: DATA-01, DATA-02, DATA-03, DATA-04, DATA-05, API-01, API-02, API-03, API-04, API-05, API-06, UI-01, UI-02, UI-03, UI-06
**Success Criteria** (what must be TRUE):
  1. Developer can run the Next.js app and see a dark-themed shell with navigation between Processor, Rules, and Metrics views
  2. SQLite database contains 10-20 realistic PNR reservations with passengers, segments, fare classes, SSRs, and 50-100 historical decisions
  3. POST /api/lookup returns a structured reservation when given a valid PNR + last name from seed data
  4. POST /api/evaluate returns a decision with rule trace and reprotection options for a reservation
  5. GET /api/metrics returns aggregated KPI data computed from pre-seeded historical decisions
**Plans**: 3 plans

Plans:
- [ ] 01-01-PLAN.md — SQLAlchemy database schema, ORM models, Pydantic schemas, and seed data with realistic airline demo data
- [ ] 01-02-PLAN.md — Six new API endpoints (lookup, evaluate, select, decisions, metrics, rules) with service layer
- [ ] 01-03-PLAN.md — Next.js scaffold with AXIOM dark theme, sidebar navigation, and desktop layout
**UI hint**: yes

### Phase 2: Core Workflow
**Goal**: An operator can look up a PNR, view the full reservation, see rules evaluated in real-time, review reprotection options, select a flight, and have the decision recorded with audit trail
**Depends on**: Phase 1
**Requirements**: PNR-01, PNR-02, PNR-03, PNR-04, PNR-05, DEC-01, DEC-02, DEC-03, DEC-04, DEC-05, DEC-06, DEC-07, UI-04, UI-05
**Success Criteria** (what must be TRUE):
  1. Operator can enter a PNR code and last name in a structured form and see the full reservation with passengers, segments, fare class, and status
  2. System shows a clear error message when PNR + last name combination is not found
  3. After lookup, operator sees a rule evaluation trace showing each rule that fired, its result, and the overall decision (APPROVED / REJECTED / ESCALATED)
  4. When decision is APPROVED, operator sees 2-5 reprotection flight options with flight number, time, availability, and fare impact, and can select one
  5. After selection, the decision is recorded and the decision panel shows the complete audit trail with timestamp, justification, and selected option
**Plans**: TBD

Plans:
- [ ] 02-01: PNR lookup flow (form, reservation display, error states)
- [ ] 02-02: Decision engine flow (rule evaluation UI, options, selection, decision panel)
**UI hint**: yes

### Phase 3: KPI Dashboard + Demo Polish
**Goal**: An investor-ready KPI dashboard shows operational metrics computed from decision history, and the entire application meets AXIOM brand guidelines with professional polish
**Depends on**: Phase 2
**Requirements**: KPI-01, KPI-02, KPI-03, KPI-04, KPI-05, UI-07
**Success Criteria** (what must be TRUE):
  1. Dashboard displays automation rate, average processing time, decisions-per-day trend chart, and top triggered rules bar chart
  2. KPI metrics visibly update after a new decision is recorded through the core workflow
  3. Entire application has consistent investor-demo quality polish: smooth transitions, no layout jank, no broken states, brand-aligned typography and spacing
**Plans**: TBD

Plans:
- [ ] 03-01: KPI dashboard with charts and live-updating metrics
- [ ] 03-02: Brand polish pass and demo scenario validation
**UI hint**: yes

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation + Backend + App Shell | 0/3 | Not started | - |
| 2. Core Workflow | 0/2 | Not started | - |
| 3. KPI Dashboard + Demo Polish | 0/2 | Not started | - |
