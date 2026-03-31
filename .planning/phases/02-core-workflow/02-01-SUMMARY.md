---
phase: 02-core-workflow
plan: 01
subsystem: ui
tags: [react, typescript, shadcn-ui, useReducer, state-machine, tailwind, radix-ui]

requires:
  - phase: 01-foundation
    provides: "Next.js app shell, FastAPI backend with /api/lookup and /api/evaluate endpoints, dark theme, sidebar navigation"
provides:
  - "TypeScript interfaces matching all Pydantic schemas (Reservation, Passenger, Segment, EvaluateResponse, etc.)"
  - "Discriminated union state machine (ProcessorState with 13 states, ProcessorAction with 12 actions)"
  - "GDS status code translation layer (HK->SCHEDULED, XX->CANCELLED, etc.)"
  - "6 semantic badge variants (approved, rejected, escalated, scheduled, cancelled, confirmed)"
  - "PNR lookup form with validation, loading states, and auto-uppercase"
  - "Reservation panel with passengers table and segments table"
  - "Skeleton loading screens for reservation, rule trace, and decision panels"
  - "Error states for PNR not found and evaluation failure"
  - "Processor page wired with useReducer + useMutation chain (lookup -> evaluate)"
  - "Backend English-only justification strings (Spanish removed from airline_rules.py and decision_service.py)"
affects: [02-core-workflow-plan-02, 03-kpi-polish]

tech-stack:
  added: ["@radix-ui/react-dialog", "@radix-ui/react-label", "@radix-ui/react-separator", "@radix-ui/react-tooltip"]
  patterns: ["useReducer with discriminated union types", "useMutation chaining (lookup -> evaluate)", "GDS code translation layer", "semantic badge variants via cva"]

key-files:
  created:
    - axiom-ui/src/lib/types.ts
    - axiom-ui/src/lib/translations.ts
    - axiom-ui/src/app/processor/reducer.ts
    - axiom-ui/src/components/processor/pnr-lookup-form.tsx
    - axiom-ui/src/components/processor/passengers-table.tsx
    - axiom-ui/src/components/processor/segments-table.tsx
    - axiom-ui/src/components/processor/reservation-panel.tsx
    - axiom-ui/src/components/processor/reservation-skeleton.tsx
    - axiom-ui/src/components/processor/rule-trace-skeleton.tsx
    - axiom-ui/src/components/processor/decision-skeleton.tsx
    - axiom-ui/src/components/ui/ (11 shadcn components)
  modified:
    - axiom-ui/src/lib/api.ts
    - axiom-ui/src/components/ui/badge.tsx
    - axiom-ui/src/app/processor/page.tsx
    - axiom/rules/airline_rules.py
    - axiom/services/decision_service.py

key-decisions:
  - "Used discriminated union types for state machine instead of flat state object -- makes invalid states unrepresentable at compile time"
  - "Translation layer in lib/translations.ts maps GDS codes to display strings rather than transforming in backend -- keeps backend codes stable for future GDS integration"
  - "Badge variants use oklch color values inline with var() fallbacks for chart tokens -- matches UI-SPEC semantic status colors exactly"
  - "Removed APROBADO reference from decision_service trace parsing since airline_rules.py now returns English-only strings"

patterns-established:
  - "State machine pattern: useReducer + discriminated unions for complex page flows"
  - "Translation pattern: GDS code -> display string mapping in translations.ts, used by all segment/status displays"
  - "Badge variant pattern: semantic status variants (approved/rejected/escalated/scheduled/cancelled/confirmed) on Badge component"
  - "Component structure: processor/ directory for page-specific components, ui/ for shadcn primitives"
  - "Mutation chaining: lookupMutation.onSuccess dispatches EVALUATE_START and calls evaluateMutation.mutate"

requirements-completed: [PNR-01, PNR-02, PNR-03, PNR-04, PNR-05, UI-04, UI-05]

duration: 6min
completed: 2026-03-31
---

# Phase 2 Plan 1: PNR Lookup Flow Summary

**PNR lookup form with reservation display (passengers + segments tables), useReducer state machine (13 states), GDS translation layer, skeleton screens, and error states -- plus backend Spanish-to-English string fixes**

## Performance

- **Duration:** 6 min
- **Started:** 2026-03-31T03:56:19Z
- **Completed:** 2026-03-31T04:02:19Z
- **Tasks:** 2
- **Files modified:** 27

## Accomplishments
- Full TypeScript type system matching Pydantic schemas with discriminated union state machine
- PNR lookup form that submits, shows skeleton loading, displays reservation with passengers/segments tables
- GDS status code translation (HK->SCHEDULED, XX->CANCELLED) with semantic badge variants
- Error states for PNR not found and evaluation failure with exact UI-SPEC copywriting
- Backend airline_rules.py and decision_service.py now return English-only strings

## Task Commits

Each task was committed atomically:

1. **Task 1: Install shadcn components, create types, translations, API functions, state machine, and fix backend Spanish strings** - `3718bb6` (feat)
2. **Task 2: Build PNR lookup form, reservation panel, skeleton screens, error states, and wire into Processor page** - `1984a84` (feat)

## Files Created/Modified
- `axiom-ui/src/lib/types.ts` - TypeScript interfaces for all API responses + discriminated union state machine types
- `axiom-ui/src/lib/translations.ts` - GDS code translation, badge variant mapping, seat availability level
- `axiom-ui/src/lib/api.ts` - Extended with lookupReservation, evaluateReservation, selectOption typed functions
- `axiom-ui/src/app/processor/reducer.ts` - processorReducer with 12 action handlers and state guards
- `axiom-ui/src/components/ui/badge.tsx` - Extended with 6 semantic status variants (approved, rejected, escalated, scheduled, cancelled, confirmed)
- `axiom-ui/src/components/ui/` - 11 shadcn components (button, input, label, card, skeleton, alert, separator, dialog, table, tooltip, badge)
- `axiom-ui/src/components/processor/pnr-lookup-form.tsx` - PNR + last name form with validation and loading
- `axiom-ui/src/components/processor/passengers-table.tsx` - Passenger name, ticket, fare class, type, SSR with tooltips
- `axiom-ui/src/components/processor/segments-table.tsx` - Flight, route, date, time, status with GDS translation and cancelled row highlighting
- `axiom-ui/src/components/processor/reservation-panel.tsx` - Card with passengers + segments tables, disruption badge
- `axiom-ui/src/components/processor/reservation-skeleton.tsx` - Skeleton matching reservation panel layout
- `axiom-ui/src/components/processor/rule-trace-skeleton.tsx` - 5 staggered-opacity step rows
- `axiom-ui/src/components/processor/decision-skeleton.tsx` - Centered badge + text block placeholders
- `axiom-ui/src/app/processor/page.tsx` - Processor page with useReducer, lookup->evaluate mutation chain, conditional rendering
- `axiom/rules/airline_rules.py` - Spanish justification strings replaced with English
- `axiom/services/decision_service.py` - APPROVED justification hardcoded to English, removed APROBADO reference

## Decisions Made
- Used discriminated union types for state machine -- makes invalid states unrepresentable at compile time
- Translation layer in lib/translations.ts maps GDS codes rather than transforming in backend -- keeps raw codes stable for future GDS integration
- Removed APROBADO reference from decision_service trace parsing since the airline_rules.py source now returns English-only

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed TypeScript narrowing error in showReservation flag**
- **Found during:** Task 2 (Processor page wiring)
- **Issue:** `state.step !== "LOOKUP_LOADING"` comparison was redundant after `"reservation" in state` check -- TypeScript reported TS2367 (comparison with no overlap)
- **Fix:** Removed the redundant check since LOOKUP_LOADING state does not carry `reservation` property
- **Files modified:** axiom-ui/src/app/processor/page.tsx
- **Verification:** `npx tsc --noEmit` passes, `npm run build` succeeds
- **Committed in:** 1984a84 (Task 2 commit)

**2. [Rule 1 - Bug] Removed stale APROBADO reference from trace parsing**
- **Found during:** Task 1 (Backend Spanish string fixes)
- **Issue:** decision_service.py line 106 checked for "APROBADO" in trace strings to set result to "PASS", but airline_rules.py no longer returns that string
- **Fix:** Removed the `or "APROBADO" in str(t)` condition, keeping only `"True" in str(t)` check
- **Files modified:** axiom/services/decision_service.py
- **Verification:** Code logic verified -- trace entries like "flight_cancelled=True" still correctly produce PASS result
- **Committed in:** 3718bb6 (Task 1 commit)

---

**Total deviations:** 2 auto-fixed (2 bug fixes via Rule 1)
**Impact on plan:** Both fixes necessary for correctness. No scope creep.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Known Stubs
None - all components render real data from API responses or show appropriate loading/error states.

## Next Phase Readiness
- Types, translations, badge variants, and state machine are ready for Plan 02 (rule evaluation trace, decision panel, reprotection options, selection dialog, audit trail)
- The reducer already handles all 12 actions including DECISION_APPROVED/REJECTED/ESCALATED, SELECT_OPTION, CONFIRM_START/SUCCESS/ERROR, and RESET
- API functions evaluateReservation and selectOption are already exported and typed
- Plan 02 only needs to add the remaining visual components and wire them into the existing page.tsx

## Self-Check: PASSED

- All 22 files verified present on disk
- Both commit hashes (3718bb6, 1984a84) verified in git log
- `npx tsc --noEmit` passes with zero errors
- `npm run build` succeeds with all routes generated

---
*Phase: 02-core-workflow*
*Completed: 2026-03-31*
