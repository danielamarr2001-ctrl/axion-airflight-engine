# Pitfalls Research: AXIOM AirFlight Engine

## Domain-Specific Pitfalls

### 1. Unrealistic Simulated Data
**Risk**: Investors who know airlines will spot fake data instantly.
**Warning signs**: PNR codes that don't follow real formats, impossible routes, non-existent airline codes.
**Prevention**:
- Use real IATA airport codes (BOG, MDE, MIA, MAD, etc.)
- Use realistic airline codes (AV=Avianca, LA=LATAM, IB=Iberia)
- PNR format: 6 alphanumeric chars (like ABC123, XYZWT1)
- Realistic fare classes (Y, B, M, Q, etc.)
- Flight times that make geographic sense
- Seed 10-20 realistic reservations covering different scenarios
**Phase**: Database + Seed Data (Phase 1)

### 2. Oversimplifying Fare Rules
**Risk**: Airline fare rules are extraordinarily complex. Oversimplifying makes the demo look naive.
**Warning signs**: All decisions result in "approved" — no edge cases.
**Prevention**:
- Include at least 3-4 failure scenarios (sensitive SSR, fare class mismatch, different airline)
- Show escalation flow (human review) for ambiguous cases
- Demo should show both "happy path" and "escalation path"
- Don't claim to handle all fare rules — position as "starting with involuntary changes"
**Phase**: Rule Engine enhancement (Phase 2)

### 3. Dashboard Without Meaningful Metrics
**Risk**: Empty charts or zeros everywhere in KPI dashboard.
**Warning signs**: Metrics page shows "0 decisions" on first load.
**Prevention**:
- Pre-seed decision history with 50-100 historical decisions
- Show 14-day trend with realistic volume patterns
- Include both good and bad metrics (some escalations, varying times)
- Ensure first demo experience has meaningful data
**Phase**: KPI Dashboard (Phase 3)

### 4. Ignoring the Operator's Mental Model
**Risk**: Building a developer tool instead of an airline operations tool.
**Warning signs**: Technical jargon in UI, JSON displayed raw, developer-style debugging info.
**Prevention**:
- Use airline terminology: "PNR", "Segment", "Reprotection", "Involuntary Change"
- Decision status should use airline ops language (not HTTP status codes)
- Flight options should look like a booking system, not a JSON response
- Rule trace should be human-readable, not code-level
**Phase**: Frontend development (all phases)

## Technical Pitfalls

### 5. Over-Engineering the Backend
**Risk**: Building production infrastructure for a demo.
**Warning signs**: Setting up Docker, Kubernetes, message queues, microservices.
**Prevention**:
- SQLite is sufficient — no PostgreSQL needed
- Single FastAPI process — no workers or message queues
- No caching layer needed
- No API rate limiting or auth
- Keep it simple: one process, one database file
**Phase**: All phases — constant vigilance

### 6. React/FastAPI CORS & Proxy Issues
**Risk**: Spending hours on CORS configuration instead of features.
**Warning signs**: "Access-Control-Allow-Origin" errors in browser console.
**Prevention**:
- Use Next.js API routes as proxy to FastAPI (eliminates CORS entirely)
- OR configure FastAPI CORS properly once (already has wildcard, but specify Next.js origin)
- Test cross-origin early, don't defer to end
**Phase**: Frontend scaffold (Phase 2)

### 7. Dark Theme Contrast Issues
**Risk**: Text unreadable, charts invisible, brand colors clashing.
**Warning signs**: White text on light gray, teal on dark blue invisible, chart lines disappearing.
**Prevention**:
- Define CSS custom properties for all brand colors upfront
- Test contrast ratios (WCAG AA minimum: 4.5:1 for text)
- Teal (#2ABFBF) works on dark (#0A0A0A to #1A1A1A) — but test lighter teal variants for text
- Charts need explicit dark theme colors (don't rely on defaults)
- shadcn/ui dark mode is built-in — start with it
**Phase**: Frontend scaffold theme setup (Phase 2)

### 8. Slow API Responses Ruining Demo Experience
**Risk**: Investor sees loading spinners for 5+ seconds.
**Warning signs**: SQLite queries without indexes, N+1 queries, synchronous operations.
**Prevention**:
- Add indexes on PNR, last_name, decision timestamps
- Use eager loading for relationships (passengers, segments)
- Processing time should be <200ms for all endpoints
- Pre-compute aggregated metrics, don't calculate on every request
**Phase**: Backend API (Phase 1-2)

### 9. State Management Complexity
**Risk**: React state becomes tangled between lookup, evaluation, selection flows.
**Warning signs**: Prop drilling 5+ levels, stale data after actions, complex useEffect chains.
**Prevention**:
- TanStack Query handles server state (no Redux needed)
- Use URL state for navigation (Next.js router)
- Component-local state for UI-only concerns
- The decision flow is linear — model it as a wizard/stepper
**Phase**: Frontend implementation (Phase 2-3)

### 10. Not Having a Demo Script
**Risk**: Building features but no clear demo narrative for investors.
**Warning signs**: "Let me show you..." followed by confused clicking.
**Prevention**:
- Design seed data around a specific demo scenario:
  1. "Flight AV123 BOG→MDE cancelled"
  2. Operator enters PNR + last name
  3. System shows reservation, evaluates rules, shows APPROVED
  4. Operator selects alternative flight AV125
  5. Decision recorded with full audit trail
  6. KPI dashboard shows this adds to the automation metrics
- Build the demo flow FIRST, then extend for edge cases
**Phase**: Seed data design (Phase 1) + Polish (Phase 4)

## Investor Demo Anti-Patterns

| Anti-Pattern | Better Approach |
|-------------|-----------------|
| "It can do everything" | "It solves THIS specific problem well" |
| Empty state / zero data | Pre-seeded with realistic history |
| Over-technical UI | Operator-friendly, airline terminology |
| Slow/broken features | Fewer features that work flawlessly |
| Generic SaaS look | Branded, professional, domain-specific |
| "Future roadmap" slides | Working demo that speaks for itself |
