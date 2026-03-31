# Requirements: AXIOM AirFlight Engine

**Defined:** 2026-03-30
**Core Value:** When a flight is cancelled or delayed, the right reprotection decision is made consistently, instantly, and with complete audit trail.

## v1 Requirements

Requirements for investor demo release. Each maps to roadmap phases.

### Data Foundation

- [ ] **DATA-01**: System stores realistic simulated reservations in SQLite database (10-20 PNRs with passengers, segments, fare classes, SSRs)
- [ ] **DATA-02**: System stores realistic simulated available flights for reprotection options
- [ ] **DATA-03**: System stores pre-seeded historical decisions (50-100 records) for KPI dashboard
- [ ] **DATA-04**: All simulated data uses real IATA airport codes, realistic airline codes, and geographic-sense routes
- [ ] **DATA-05**: Database schema supports reservations, passengers, segments, SSR records, flights, rules, and decisions

### PNR Lookup

- [x] **PNR-01**: Operator can enter PNR code and passenger last name in a structured form
- [x] **PNR-02**: System retrieves and displays full reservation after successful lookup
- [x] **PNR-03**: Reservation display shows all passengers with names, ticket numbers, and fare class
- [x] **PNR-04**: Reservation display shows all flight segments with dates, routes, times, and status
- [x] **PNR-05**: System shows clear error state when PNR + last name combination is not found

### Decision Engine

- [ ] **DEC-01**: System evaluates sequential rules against structured reservation data (not text parsing)
- [ ] **DEC-02**: System displays rule evaluation trace showing which rules fired and why
- [ ] **DEC-03**: System generates 2-5 reprotection flight options when decision is APPROVED
- [ ] **DEC-04**: Each flight option shows flight number, time, availability, and fare impact
- [ ] **DEC-05**: Operator can select a reprotection option from the generated list
- [ ] **DEC-06**: System records the decision with selected option, timestamp, justification, and full audit trail
- [ ] **DEC-07**: Decision panel shows real-time status (APPROVED / REJECTED / ESCALATED) with justification

### KPI Dashboard

- [x] **KPI-01**: Dashboard shows automation rate (% decisions auto-approved vs escalated to human review)
- [x] **KPI-02**: Dashboard shows average processing time from PNR input to decision
- [x] **KPI-03**: Dashboard shows decisions-per-day trend chart (last 14 days)
- [x] **KPI-04**: Dashboard shows top triggered rules as bar chart
- [x] **KPI-05**: All KPI metrics update after new decisions are recorded

### Frontend & Brand

- [x] **UI-01**: Application uses Next.js with React and TypeScript
- [x] **UI-02**: Dark theme matching AXIOM brand guidelines (dark background, teal accents ~#2ABFBF)
- [x] **UI-03**: Navigation shell with sidebar or top navigation between Processor, Rules, and Metrics views
- [x] **UI-04**: Loading states with skeleton screens for all API calls
- [x] **UI-05**: Graceful error states for invalid PNR, no results, and API errors
- [x] **UI-06**: Desktop-first responsive layout optimized for large screens
- [x] **UI-07**: Professional investor-demo quality polish matching brand guidelines

### Backend API

- [x] **API-01**: POST /api/lookup endpoint accepts PNR + last name and returns structured reservation
- [x] **API-02**: POST /api/evaluate endpoint runs rule engine against a reservation and returns decision with options
- [x] **API-03**: POST /api/select endpoint records operator's flight selection as a decision
- [x] **API-04**: GET /api/decisions endpoint returns decision history with pagination
- [x] **API-05**: GET /api/metrics endpoint returns aggregated KPI data for dashboard
- [x] **API-06**: Existing /rules CRUD endpoints preserved and enhanced with database storage

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Advanced Intelligence

- **ADV-01**: Decision confidence score with quantified certainty
- **ADV-02**: Escalation prediction flagging cases likely to need human review
- **ADV-03**: Decision replay — re-run past decisions with current rules
- **ADV-04**: Rule impact analysis showing what changes if a rule is modified

### Advanced Visualization

- **VIZ-01**: Real-time decision feed (live ticker)
- **VIZ-02**: Decision flow diagram (visual pipeline)
- **VIZ-03**: Activity heatmap (time-of-day / day-of-week)
- **VIZ-04**: Cost savings calculator

### Integration

- **INT-01**: Real GDS API integration (Amadeus/Sabre/Travelport)
- **INT-02**: Actual ticket reissuance commands
- **INT-03**: Authentication and RBAC

## Out of Scope

| Feature | Reason |
|---------|--------|
| Real GDS integration | Requires commercial agreements and certification |
| Ticket reissuance | Risk of real financial impact, simulated sufficient for demo |
| Authentication/RBAC | Not needed for single-operator investor demo |
| Mobile responsive | Desktop operators only |
| AI/ML predictions | Rule-based is the product differentiator |
| Multi-tenant | Single-tenant demo |
| Email/SMS notifications | Out of scope for decision engine |
| Payment processing | No financial transactions in demo |
| Report export (PDF/Excel) | Nice-to-have, defer to v2 |
| Docker/containerization | Unnecessary for local demo |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| DATA-01 | Phase 1 | Pending |
| DATA-02 | Phase 1 | Pending |
| DATA-03 | Phase 1 | Pending |
| DATA-04 | Phase 1 | Pending |
| DATA-05 | Phase 1 | Pending |
| API-01 | Phase 1 | Complete |
| API-02 | Phase 1 | Complete |
| API-03 | Phase 1 | Complete |
| API-04 | Phase 1 | Complete |
| API-05 | Phase 1 | Complete |
| API-06 | Phase 1 | Complete |
| UI-01 | Phase 1 | Complete |
| UI-02 | Phase 1 | Complete |
| UI-03 | Phase 1 | Complete |
| UI-06 | Phase 1 | Complete |
| PNR-01 | Phase 2 | Complete |
| PNR-02 | Phase 2 | Complete |
| PNR-03 | Phase 2 | Complete |
| PNR-04 | Phase 2 | Complete |
| PNR-05 | Phase 2 | Complete |
| DEC-01 | Phase 2 | Pending |
| DEC-02 | Phase 2 | Pending |
| DEC-03 | Phase 2 | Pending |
| DEC-04 | Phase 2 | Pending |
| DEC-05 | Phase 2 | Pending |
| DEC-06 | Phase 2 | Pending |
| DEC-07 | Phase 2 | Pending |
| UI-04 | Phase 2 | Complete |
| UI-05 | Phase 2 | Complete |
| KPI-01 | Phase 3 | Complete |
| KPI-02 | Phase 3 | Complete |
| KPI-03 | Phase 3 | Complete |
| KPI-04 | Phase 3 | Complete |
| KPI-05 | Phase 3 | Complete |
| UI-07 | Phase 3 | Complete |

**Coverage:**
- v1 requirements: 35 total
- Mapped to phases: 35
- Unmapped: 0

---
*Requirements defined: 2026-03-30*
*Last updated: 2026-03-30 after roadmap creation*
