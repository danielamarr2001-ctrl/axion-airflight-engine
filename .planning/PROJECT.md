# AXIOM AirFlight Engine

## What This Is

AXIOM is a rule-based decision engine for automating involuntary flight changes in airline post-sale operations. It takes a PNR + passenger last name, retrieves the reservation, evaluates sequential business rules (cancellation, delay, fare protection, SSR checks), generates reprotection options, and lets the operator select an alternative flight — logging every decision with full traceability. The target audience is small airlines and travel agencies with high-volume post-sale operations.

## Core Value

When a flight is cancelled or delayed, the right reprotection decision is made consistently, instantly, and with complete audit trail — eliminating human error in high-volume involuntary change processing.

## Requirements

### Validated

- ✓ FastAPI backend with decision pipeline (INPUT→VALIDATION→CLASSIFICATION→RULES→OPTIONS→ACTION) — existing
- ✓ Involuntary change rule engine with 5-check validation (cancelled, same airline, same route, no sensitive SSR, same fare class) — existing
- ✓ Table-based rule platform with CSV storage and CRUD API — existing
- ✓ Decision logging with JSON file storage and metrics computation — existing
- ✓ Dual rule engine mode (Python code-based / CSV table-based) — existing

### Active

- [ ] Structured PNR + last name lookup replacing free-text input
- [ ] Full reservation display after PNR retrieval
- [ ] Sequential rule evaluation against structured reservation data
- [ ] Involuntary change options generation with selectable alternatives
- [ ] Flight option selection with decision record creation
- [ ] Decision panel showing justifications and audit trail in real-time
- [ ] KPI dashboard with operational metrics (automation rate, processing time, error reduction)
- [ ] New React/Next.js frontend with AXIOM brand dark theme + teal accents
- [ ] Simulated PNR/flight data store (structured like real GDS data)
- [ ] Investor-demo-quality polished UI matching brand guidelines

### Out of Scope

- Real GDS API integration (Amadeus/Sabre/Travelport) — deferred to pilot phase
- Actual ticket reissuance commands — this phase records decisions only
- Authentication/RBAC — not needed for investor demo
- Real-time GDS data feeds — simulated data sufficient for demo
- Mobile app — web-first
- Multi-tenant architecture — single-tenant demo
- Payment/billing integration — not needed for demo phase

## Context

- **Existing codebase**: Python/FastAPI backend with decision engine + Flutter Web dashboard (being replaced with React/Next.js)
- **Brand**: AXIOM brand guidelines specify dark theme with teal (#2ABFBF-range) accents, hexagonal logo motif, professional B2B SaaS aesthetic
- **Domain**: Airline GDS/legacy systems, PNR processing, involuntary change management (IATA regulations, fare protection rules)
- **Founder**: Daniela Martinez Reyes — deep operational experience in airline post-sale
- **Business model**: B2B SaaS (subscription + usage-based)
- **Target market**: Small airlines and travel agencies with intensive post-sale operations
- **KPIs**: Process time reduction, % automated decisions, error reduction, adoption rate, automated volume, revenue recurrence

## Constraints

- **Data**: Simulated PNR/flight data (structured like real GDS for future integration)
- **Frontend**: React/Next.js with AXIOM brand dark theme (replacing Flutter)
- **Backend**: Python/FastAPI (extend existing, don't rewrite core)
- **Storage**: Local database for demo (SQLite or equivalent)
- **Demo quality**: Investor-ready UI polish following exact brand guidelines
- **No real integrations**: All data simulated, all actions are decision records

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Replace Flutter with React/Next.js | Better ecosystem for polished investor demo, richer component libraries | — Pending |
| Simulated data over GDS integration | Focus on decision logic + UX, defer integration complexity | — Pending |
| Record decisions instead of real issuance | De-risk MVP, prove value of decision automation without GDS coupling | — Pending |
| Extend existing FastAPI backend | Proven decision pipeline, avoid rewrite risk | — Pending |
| Dark theme + teal accents (brand exact) | Match investor pitch deck aesthetic, brand consistency | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd:transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd:complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-03-30 after initialization*
