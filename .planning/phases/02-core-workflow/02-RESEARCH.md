# Phase 2: Core Workflow - Research

**Researched:** 2026-03-30
**Domain:** React component architecture, TanStack Query mutation/query patterns, shadcn/ui component composition, state machine with useReducer, backend API contract mapping
**Confidence:** HIGH

## Summary

Phase 2 builds the complete operator workflow on the Processor page: PNR lookup form, reservation display, rule evaluation trace, decision panel, reprotection option selection, confirmation dialog, and audit trail. The foundation is fully in place from Phase 1 -- the backend has working endpoints (`POST /api/lookup`, `POST /api/evaluate`, `POST /api/select`), SQLAlchemy models with seed data, and the Next.js shell with TanStack Query provider, API proxy rewrites, and AXIOM dark theme CSS variables.

The core challenge is implementing a multi-stage linear state machine (11 states from IDLE to DECISION_RECORDED) that orchestrates sequential API calls and conditionally renders 7 distinct UI panels. The recommended approach is a `useReducer` with TypeScript discriminated unions for the page state, combined with TanStack Query `useMutation` for each API call (lookup, evaluate, select). The evaluate step auto-triggers after successful lookup, creating a dependent mutation chain via `mutateAsync` in the `onSuccess` callback.

**Primary recommendation:** Implement the Processor page as a single `"use client"` page component using `useReducer` for state machine transitions, three `useMutation` hooks (lookup, evaluate, select), and 7 child components extracted into `src/components/processor/`. Install all 11 shadcn/ui components before implementation. Map backend GDS status codes ("XX" -> "CANCELLED", "HK" -> "SCHEDULED", "TK" -> "SCHEDULE CHANGE") and Spanish strings in the API client layer.

## Project Constraints (from CLAUDE.md)

- **Backend**: Python/FastAPI -- extend existing, do not rewrite core
- **Frontend**: React/Next.js with AXIOM brand dark theme (replacing Flutter)
- **Storage**: Local database for demo (SQLite)
- **Demo quality**: Investor-ready UI polish following exact brand guidelines
- **No real integrations**: All data simulated, all actions are decision records
- **NEVER use Bash heredocs** for file creation -- always use Write tool
- **NEVER embed secrets** in Bash commands
- **GSD workflow enforcement**: Use GSD commands for planned work

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| PNR-01 | Operator can enter PNR code and passenger last name in a structured form | PNR Lookup Form component with shadcn Input + Button, validation pattern, uppercase transform |
| PNR-02 | System retrieves and displays full reservation after successful lookup | `useMutation` calling POST /api/lookup, ReservationPanel component rendering response |
| PNR-03 | Reservation display shows all passengers with names, ticket numbers, and fare class | PassengersTable sub-component using shadcn Table, data mapped from PassengerSchema |
| PNR-04 | Reservation display shows all flight segments with dates, routes, times, and status | SegmentsTable sub-component using shadcn Table, GDS status code translation layer |
| PNR-05 | System shows clear error state when PNR + last name combination is not found | Error handling in mutation onError, shadcn Alert (destructive) below form |
| DEC-01 | System evaluates sequential rules against structured reservation data | Auto-trigger evaluate mutation after successful lookup, backend rule engine processes structured data |
| DEC-02 | System displays rule evaluation trace showing which rules fired and why | RuleTracePanel component rendering trace array with step indicators and connectors |
| DEC-03 | System generates 2-5 reprotection flight options when decision is APPROVED | Options rendered from EvaluateResponse.options array, FlightOptionCard grid |
| DEC-04 | Each flight option shows flight number, time, availability, and fare impact | FlightOptionCard component with structured layout per UI-SPEC |
| DEC-05 | Operator can select a reprotection option from the generated list | Radio-group card selection behavior + "Select Flight" button opens confirmation dialog |
| DEC-06 | System records the decision with selected option, timestamp, justification, and audit trail | POST /api/select mutation, SelectResponse rendered in AuditTrailPanel |
| DEC-07 | Decision panel shows real-time status (APPROVED/REJECTED/ESCALATED) with justification | DecisionPanel component with oversized status badge, semantic colors, justification text |
| UI-04 | Loading states with skeleton screens for all API calls | Skeleton components matching exact layout of resolved components per UI-SPEC |
| UI-05 | Graceful error states for invalid PNR, no results, and API errors | 4 distinct error states (PNR not found, API generic, evaluation error, selection error) using shadcn Alert |
</phase_requirements>

## Standard Stack

### Core (Already Installed -- Phase 1)

| Library | Version | Purpose | Status |
|---------|---------|---------|--------|
| Next.js | 15.2.4 | React framework with App Router | Installed |
| React | ^19.0.0 | UI library | Installed |
| TypeScript | ^5 | Type safety | Installed |
| Tailwind CSS | ^4 | Utility-first CSS | Installed |
| @tanstack/react-query | ^5.95.2 | Server state management | Installed |
| lucide-react | ^0.469.0 | Icons | Installed |
| next-themes | ^0.4.6 | Dark mode | Installed |
| class-variance-authority | ^0.7.1 | Component variants | Installed |
| clsx | ^2.1.1 | Conditional classnames | Installed |
| tailwind-merge | ^3.0.2 | Class deduplication | Installed |

### To Install (Phase 2)

| Library | Source | Purpose |
|---------|--------|---------|
| shadcn/ui button | `npx shadcn@latest add button` | Primary CTAs |
| shadcn/ui input | `npx shadcn@latest add input` | Form fields |
| shadcn/ui label | `npx shadcn@latest add label` | Form labels |
| shadcn/ui card | `npx shadcn@latest add card` | Panel containers |
| shadcn/ui badge | `npx shadcn@latest add badge` | Status indicators |
| shadcn/ui skeleton | `npx shadcn@latest add skeleton` | Loading states |
| shadcn/ui alert | `npx shadcn@latest add alert` | Error states |
| shadcn/ui separator | `npx shadcn@latest add separator` | Section dividers |
| shadcn/ui dialog | `npx shadcn@latest add dialog` | Confirmation modal |
| shadcn/ui table | `npx shadcn@latest add table` | Data tables |
| shadcn/ui tooltip | `npx shadcn@latest add tooltip` | Data explanations |

**Installation command (batch):**
```bash
cd axiom-ui && npx shadcn@latest add button input label card badge skeleton alert separator dialog table tooltip
```

This installs Radix UI primitives as transitive dependencies. No additional npm installs needed.

### Don't Install

| Library | Reason |
|---------|--------|
| react-hook-form | Overkill for a 2-field form; native form handling + controlled inputs sufficient |
| zod | Validation is PNR length + non-empty, not complex schemas |
| zustand/jotai/recoil | Page-local state via useReducer is simpler; no cross-page state needed |
| framer-motion | CSS transitions per UI-SPEC animation contract; no JS animation lib needed |
| xstate | Full state machine library is overkill; useReducer + discriminated unions sufficient |

## Architecture Patterns

### Recommended Component Structure

```
axiom-ui/src/
  app/
    processor/
      page.tsx                    # "use client", state machine, mutation hooks, layout composition
  components/
    processor/
      pnr-lookup-form.tsx         # Form with PNR + last name inputs + submit button
      reservation-panel.tsx       # Card with passengers table + segments table
      passengers-table.tsx        # shadcn Table for passenger data
      segments-table.tsx          # shadcn Table for segment data with status badges
      rule-trace-panel.tsx        # Card with stepped rule evaluation trace
      decision-panel.tsx          # Card with oversized status badge + justification
      flight-option-card.tsx      # Individual option card with Select button
      reprotection-options.tsx    # Grid of flight option cards
      confirmation-dialog.tsx     # shadcn Dialog for confirming selection
      audit-trail-panel.tsx       # Timeline of actions
      reservation-skeleton.tsx    # Skeleton matching reservation panel layout
      rule-trace-skeleton.tsx     # Skeleton matching trace layout
      decision-skeleton.tsx       # Skeleton matching decision panel layout
    ui/
      badge.tsx                   # Extended with status-badge variant
      ... (other shadcn components)
  lib/
    api.ts                        # Existing fetch wrapper (extend with typed functions)
    types.ts                      # TypeScript interfaces matching backend schemas
    translations.ts               # Spanish-to-English mapping + GDS status code translation
    utils.ts                      # Existing cn() utility
```

### Pattern 1: State Machine with useReducer + Discriminated Unions

**What:** A TypeScript-safe state machine where each state carries only the data relevant to that state, making invalid states unrepresentable.

**When to use:** The Processor page has 11 distinct states with different visible components per state (see UI-SPEC visible components table).

```typescript
// src/lib/types.ts

// -- Backend response types (match Pydantic schemas exactly) --

interface Reservation {
  id: number;
  pnr: string;
  booking_reference: string | null;
  created_at: string;
  passengers: Passenger[];
  segments: Segment[];
}

interface Passenger {
  id: number;
  last_name: string;
  first_name: string;
  ticket_number: string | null;
  fare_class: string;
  fare_basis: string | null;
  passenger_type: string;
  ssr_records: SSRRecord[];
}

interface SSRRecord {
  id: number;
  ssr_type: string;
  ssr_detail: string | null;
}

interface Segment {
  id: number;
  flight_number: string;
  airline: string;
  origin: string;
  destination: string;
  departure_date: string;
  departure_time: string;
  arrival_time: string;
  status: string;    // Raw GDS codes: "HK", "XX", "TK"
  cabin_class: string;
  aircraft_type: string | null;
}

interface EvaluateResponse {
  decision_id: number;
  status: "APPROVED" | "REJECTED" | "ESCALATED";
  rule_applied: string;
  justification: string;
  trace: RuleTraceItem[];
  options: FlightOption[];
}

interface RuleTraceItem {
  step: string;
  result: string;  // "PASS" | "FAIL" | "WARN" | "INFO" | other
  detail: string;
}

interface FlightOption {
  id: number;
  flight_number: string;
  airline: string;
  origin: string;
  destination: string;
  departure_date: string;
  departure_time: string;
  arrival_time: string;
  available_seats: number;
  fare_class: string;
  aircraft_type: string | null;
  status: string;
}

interface SelectResponse {
  id: number;
  status: string;
  selected_option: string;
  pnr: string;
  timestamp: string;
}

// -- State machine types --

type ProcessorState =
  | { step: "IDLE" }
  | { step: "LOOKUP_LOADING"; pnr: string; lastName: string }
  | { step: "LOOKUP_ERROR"; error: string; pnr: string; lastName: string }
  | { step: "RESERVATION_LOADED"; reservation: Reservation }
  | { step: "EVALUATING"; reservation: Reservation }
  | { step: "EVALUATION_ERROR"; reservation: Reservation; error: string }
  | { step: "DECISION_APPROVED"; reservation: Reservation; decision: EvaluateResponse }
  | { step: "DECISION_REJECTED"; reservation: Reservation; decision: EvaluateResponse }
  | { step: "DECISION_ESCALATED"; reservation: Reservation; decision: EvaluateResponse }
  | { step: "CONFIRMING"; reservation: Reservation; decision: EvaluateResponse; selectedOptionId: number }
  | { step: "SELECTION_LOADING"; reservation: Reservation; decision: EvaluateResponse; selectedOptionId: number }
  | { step: "SELECTION_ERROR"; reservation: Reservation; decision: EvaluateResponse; selectedOptionId: number; error: string }
  | { step: "DECISION_RECORDED"; reservation: Reservation; decision: EvaluateResponse; confirmation: SelectResponse };

type ProcessorAction =
  | { type: "LOOKUP_START"; pnr: string; lastName: string }
  | { type: "LOOKUP_SUCCESS"; reservation: Reservation }
  | { type: "LOOKUP_ERROR"; error: string }
  | { type: "EVALUATE_START" }
  | { type: "EVALUATE_SUCCESS"; decision: EvaluateResponse }
  | { type: "EVALUATE_ERROR"; error: string }
  | { type: "SELECT_OPTION"; optionId: number }
  | { type: "CANCEL_SELECTION" }
  | { type: "CONFIRM_START" }
  | { type: "CONFIRM_SUCCESS"; confirmation: SelectResponse }
  | { type: "CONFIRM_ERROR"; error: string }
  | { type: "RESET" };
```

**Reducer implementation pattern:**

```typescript
function processorReducer(state: ProcessorState, action: ProcessorAction): ProcessorState {
  switch (action.type) {
    case "LOOKUP_START":
      return { step: "LOOKUP_LOADING", pnr: action.pnr, lastName: action.lastName };

    case "LOOKUP_SUCCESS":
      return { step: "RESERVATION_LOADED", reservation: action.reservation };

    case "LOOKUP_ERROR":
      if (state.step !== "LOOKUP_LOADING") return state;
      return { step: "LOOKUP_ERROR", error: action.error, pnr: state.pnr, lastName: state.lastName };

    case "EVALUATE_START":
      if (state.step !== "RESERVATION_LOADED") return state;
      return { step: "EVALUATING", reservation: state.reservation };

    case "EVALUATE_SUCCESS":
      if (state.step !== "EVALUATING") return state;
      const decisionStep =
        action.decision.status === "APPROVED" ? "DECISION_APPROVED" as const :
        action.decision.status === "ESCALATED" ? "DECISION_ESCALATED" as const :
        "DECISION_REJECTED" as const;
      return { step: decisionStep, reservation: state.reservation, decision: action.decision };

    case "SELECT_OPTION":
      if (state.step !== "DECISION_APPROVED") return state;
      return { step: "CONFIRMING", reservation: state.reservation, decision: state.decision, selectedOptionId: action.optionId };

    case "CANCEL_SELECTION":
      if (state.step !== "CONFIRMING" && state.step !== "SELECTION_ERROR") return state;
      return { step: "DECISION_APPROVED", reservation: state.reservation, decision: state.decision };

    case "CONFIRM_START":
      if (state.step !== "CONFIRMING") return state;
      return { step: "SELECTION_LOADING", reservation: state.reservation, decision: state.decision, selectedOptionId: state.selectedOptionId };

    case "CONFIRM_SUCCESS":
      if (state.step !== "SELECTION_LOADING") return state;
      return { step: "DECISION_RECORDED", reservation: state.reservation, decision: state.decision, confirmation: action.confirmation };

    case "RESET":
      return { step: "IDLE" };

    default:
      return state;
  }
}
```

### Pattern 2: TanStack Query Mutations for Sequential API Flow

**What:** Three `useMutation` hooks orchestrated by the state machine reducer. The lookup mutation auto-chains into evaluate via `onSuccess`.

```typescript
// In processor/page.tsx

const lookupMutation = useMutation({
  mutationFn: (data: { pnr: string; lastName: string }) =>
    apiFetch<Reservation>("/lookup", {
      method: "POST",
      body: JSON.stringify({ pnr: data.pnr, last_name: data.lastName }),
    }),
  onMutate: (variables) => {
    dispatch({ type: "LOOKUP_START", pnr: variables.pnr, lastName: variables.lastName });
  },
  onSuccess: (reservation) => {
    dispatch({ type: "LOOKUP_SUCCESS", reservation });
    // Auto-trigger evaluation
    dispatch({ type: "EVALUATE_START" });
    evaluateMutation.mutate({ pnr: reservation.pnr, reservationId: reservation.id });
  },
  onError: (error: Error) => {
    dispatch({ type: "LOOKUP_ERROR", error: error.message });
  },
});

const evaluateMutation = useMutation({
  mutationFn: (data: { pnr: string; reservationId: number }) =>
    apiFetch<EvaluateResponse>("/evaluate", {
      method: "POST",
      body: JSON.stringify({ pnr: data.pnr, reservation_id: data.reservationId }),
    }),
  onSuccess: (decision) => {
    dispatch({ type: "EVALUATE_SUCCESS", decision });
  },
  onError: (error: Error) => {
    dispatch({ type: "EVALUATE_ERROR", error: error.message });
  },
});

const selectMutation = useMutation({
  mutationFn: (data: { decisionId: number; selectedOption: string; operatorNotes: string }) =>
    apiFetch<SelectResponse>("/select", {
      method: "POST",
      body: JSON.stringify({
        decision_id: data.decisionId,
        selected_option: data.selectedOption,
        operator_notes: data.operatorNotes,
      }),
    }),
  onMutate: () => {
    dispatch({ type: "CONFIRM_START" });
  },
  onSuccess: (confirmation) => {
    dispatch({ type: "CONFIRM_SUCCESS", confirmation });
  },
  onError: (error: Error) => {
    dispatch({ type: "CONFIRM_ERROR", error: error.message });
  },
});
```

### Pattern 3: Conditional Rendering from State Machine

**What:** Each component's visibility is determined solely by the current state machine step, following the UI-SPEC visible components table.

```typescript
// In processor/page.tsx render body

const showReservation = state.step !== "IDLE" && state.step !== "LOOKUP_ERROR";
const showReservationSkeleton = state.step === "LOOKUP_LOADING";
const showRuleTrace = "reservation" in state && state.step !== "RESERVATION_LOADED";
const showRuleTraceSkeleton = state.step === "EVALUATING";
const showDecision = state.step.startsWith("DECISION_") || state.step === "CONFIRMING" || state.step === "SELECTION_LOADING" || state.step === "SELECTION_ERROR";
const showOptions = state.step === "DECISION_APPROVED" || state.step === "CONFIRMING" || state.step === "SELECTION_LOADING" || state.step === "SELECTION_ERROR" || state.step === "DECISION_RECORDED";
const showDialog = state.step === "CONFIRMING" || state.step === "SELECTION_LOADING" || state.step === "SELECTION_ERROR";
const showAudit = state.step === "DECISION_RECORDED";
```

### Pattern 4: Status Badge Variant Extension

**What:** Extend the default shadcn Badge component with a `status` variant that maps decision/segment statuses to semantic colors per UI-SPEC.

```typescript
// Extend badge.tsx variants after shadcn installation:
const badgeVariants = cva(
  "inline-flex items-center rounded-md border px-2.5 py-0.5 text-xs font-semibold transition-colors",
  {
    variants: {
      variant: {
        default: "border-transparent bg-primary text-primary-foreground",
        secondary: "border-transparent bg-secondary text-secondary-foreground",
        destructive: "border-transparent bg-destructive text-destructive-foreground",
        outline: "text-foreground",
        // Custom status variants for AXIOM
        approved: "border-[oklch(0.72_0.15_185/0.3)] bg-[oklch(0.72_0.15_185/0.15)] text-primary",
        rejected: "border-[oklch(0.55_0.2_25/0.3)] bg-[oklch(0.55_0.2_25/0.15)] text-destructive",
        escalated: "border-[oklch(0.7_0.15_55/0.3)] bg-[oklch(0.7_0.15_55/0.15)] text-[--color-chart-4]",
        scheduled: "border-[oklch(0.72_0.15_185/0.3)] bg-[oklch(0.72_0.15_185/0.15)] text-primary",
        cancelled: "border-[oklch(0.55_0.2_25/0.3)] bg-[oklch(0.55_0.2_25/0.15)] text-destructive",
        confirmed: "border-[oklch(0.7_0.15_145/0.3)] bg-[oklch(0.7_0.15_145/0.15)] text-[--color-chart-3]",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
);
```

### Anti-Patterns to Avoid

- **Separate useState for each piece of state:** Leads to impossible combinations (e.g., having a reservation but no PNR). Use a single discriminated union state.
- **useQuery for mutation-like operations:** Lookup, evaluate, and select are imperative actions triggered by user/system events, not declarative data fetching. Use useMutation.
- **Fetching inside useEffect:** The sequential flow (lookup -> evaluate) should be triggered via mutation onSuccess callbacks, not via useEffect watchers. useEffect dependencies on mutation results create race conditions.
- **Rendering raw backend strings:** Backend returns GDS codes ("XX", "HK", "TK") and Spanish text. Always pass through translation layer before rendering.
- **Building custom modals:** shadcn Dialog wraps Radix Dialog with focus trap, escape handling, and portal rendering. Do not hand-roll.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Form submission | Custom fetch + loading state | TanStack Query `useMutation` | Handles loading, error, retry, deduplication |
| Modal dialogs | Custom overlay + portal | shadcn Dialog (Radix) | Focus trap, escape key, scroll lock, aria attributes |
| Status badges | Inline styled spans | shadcn Badge + custom variants | Consistent styling, variant system, accessibility |
| Data tables | Custom divs + flexbox | shadcn Table | Proper th/td/thead/tbody semantic markup, accessibility |
| Loading skeletons | Custom pulsing divs | shadcn Skeleton | Consistent animation, composable sizing |
| Error alerts | Custom colored boxes | shadcn Alert (destructive) | Consistent structure, icon placement, accessibility |
| Tooltips | Title attribute | shadcn Tooltip (Radix) | Accessible, positioned, animated, portal-rendered |
| Class conditional joining | String concatenation | `cn()` utility (clsx + tailwind-merge) | Deduplicates conflicting Tailwind classes |

**Key insight:** Every UI primitive needed for Phase 2 exists in the shadcn/ui registry. The only custom work is composition (assembling primitives into domain components) and the state machine logic.

## Critical Data Mapping Layer

### Backend Status Codes -> Frontend Display

The backend uses GDS-standard segment status codes in the database. The frontend must translate these before display.

**Segment status mapping (GDS -> Display):**

| GDS Code | Display Value | Badge Variant |
|----------|--------------|---------------|
| HK | SCHEDULED | scheduled |
| XX | CANCELLED | cancelled |
| TK | SCHEDULE CHANGE | escalated (amber) |
| UN | UNABLE | destructive |

**Decision status mapping:** The `decision_service.py` already returns English status strings ("APPROVED", "REJECTED", "ESCALATED") so no translation is needed for decision statuses.

**Justification text:** The `involuntary_change_rule()` function returns Spanish justification strings ("Se cumplen condiciones de proteccion tarifaria..."). However, `decision_service.py` overrides `rule_applied` with custom English values in lines 98-103. For the APPROVED case via `involuntary_change_rule`, the justification IS the Spanish string from the rule function. The frontend must either:
1. Translate known Spanish strings to English (fragile, strings may change)
2. Override the justification in `decision_service.py` with English equivalents (better)

**Recommendation:** Modify `decision_service.py` to always set English justification strings, so the frontend translation layer only handles segment status codes, not free-text justification. This is a minor backend change (3-5 lines) that eliminates an entire class of frontend translation bugs.

### TypeScript Interface vs Backend Schema Alignment

The UI-SPEC defines TypeScript interfaces that closely match the Pydantic schemas in `axiom/models/schemas.py`. Key differences to handle:

| Field | Backend Schema | UI-SPEC Interface | Resolution |
|-------|---------------|-------------------|------------|
| `departure_date` | `date` (Python) -> `"YYYY-MM-DD"` JSON string | `string` | Match -- parse in display components using `new Date()` |
| `created_at` | `datetime` -> ISO string | `string` | Match -- format with `toLocaleString()` or manual formatting |
| Segment `status` | GDS codes ("HK", "XX", "TK") | Display strings ("SCHEDULED", etc.) | Frontend translation function |
| Segment `cabin_class` | Default "Y" | Not in UI-SPEC interfaces | Available in response, display if desired |

## Common Pitfalls

### Pitfall 1: Auto-Evaluate Race Condition

**What goes wrong:** After lookup succeeds, evaluate auto-triggers. If the user quickly submits a new lookup while evaluate is in-flight, the evaluate response may arrive for the wrong reservation.
**Why it happens:** Two mutations are in-flight for different PNRs.
**How to avoid:** Cancel the evaluate mutation before starting a new lookup. In the RESET action, call `evaluateMutation.reset()`. Guard the reducer: only process EVALUATE_SUCCESS if current state is EVALUATING.
**Warning signs:** Decision panel shows data for a different PNR than the reservation panel.

### Pitfall 2: GDS Status Code Display

**What goes wrong:** Raw GDS codes ("XX", "HK") appear in the UI instead of human-readable labels.
**Why it happens:** Backend stores standard airline industry codes, frontend assumes display-ready strings.
**How to avoid:** Create a `translateSegmentStatus()` function in `lib/translations.ts` that maps codes to display values. Call it in the segments table component, never pass raw status to Badge.
**Warning signs:** Two-letter codes in status badges.

### Pitfall 3: Missing Skeleton Layout Shift

**What goes wrong:** When data loads, the page layout jumps as skeleton content is replaced with real content of different dimensions.
**Why it happens:** Skeletons don't match the exact dimensions of the resolved component.
**How to avoid:** Follow UI-SPEC skeleton specifications precisely (exact heights, widths, and element counts that match resolved components). Use the same Card container for both skeleton and resolved state.
**Warning signs:** Visual "jump" when loading completes. Test with throttled network in DevTools.

### Pitfall 4: Dialog State Leak

**What goes wrong:** Confirmation dialog stays open or shows stale data after an error or after navigating.
**Why it happens:** Dialog open state is managed separately from the page state machine.
**How to avoid:** Derive dialog visibility entirely from the state machine step (CONFIRMING, SELECTION_LOADING, SELECTION_ERROR -> dialog open). Never use independent `useState` for dialog open/close.
**Warning signs:** Dialog flashes old content, or remains open after successful confirmation.

### Pitfall 5: Spanish Strings in UI

**What goes wrong:** Spanish text ("Se cumplen condiciones de proteccion tarifaria...") appears in the justification field.
**Why it happens:** `involuntary_change_rule()` returns Spanish, and `decision_service.py` passes it through for approved decisions.
**How to avoid:** Fix in backend: override justification in `decision_service.py` with English text for all cases. Alternatively, create a frontend mapping for known Spanish strings.
**Warning signs:** Mixed-language text in the decision panel.

### Pitfall 6: Form Remains Editable During Loading

**What goes wrong:** Operator can submit another lookup while a previous one is processing, causing overlapping mutations.
**Why it happens:** Form inputs aren't disabled during loading states.
**How to avoid:** Disable form inputs and button when state is LOOKUP_LOADING, EVALUATING, or SELECTION_LOADING. The UI-SPEC specifies "disabled" for the form during LOOKUP_LOADING and SELECTION_LOADING states.
**Warning signs:** Multiple overlapping API calls visible in network tab.

## Code Examples

### Example 1: Typed API Functions

```typescript
// src/lib/api.ts (extend existing)
const API_BASE = "/api";

export async function apiFetch<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const url = `${API_BASE}${path}`;
  const res = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
    ...options,
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || `API error: ${res.status}`);
  }

  return res.json();
}

// Typed API functions for Phase 2
export function lookupReservation(pnr: string, lastName: string) {
  return apiFetch<Reservation>("/lookup", {
    method: "POST",
    body: JSON.stringify({ pnr, last_name: lastName }),
  });
}

export function evaluateReservation(pnr: string, reservationId: number) {
  return apiFetch<EvaluateResponse>("/evaluate", {
    method: "POST",
    body: JSON.stringify({ pnr, reservation_id: reservationId }),
  });
}

export function selectOption(decisionId: number, selectedOption: string, operatorNotes: string) {
  return apiFetch<SelectResponse>("/select", {
    method: "POST",
    body: JSON.stringify({
      decision_id: decisionId,
      selected_option: selectedOption,
      operator_notes: operatorNotes,
    }),
  });
}
```

### Example 2: Translation Layer

```typescript
// src/lib/translations.ts

// GDS segment status codes -> display values
const SEGMENT_STATUS_MAP: Record<string, string> = {
  HK: "SCHEDULED",
  XX: "CANCELLED",
  TK: "SCHEDULE CHANGE",
  UN: "UNABLE",
  UC: "UNABLE - CLOSED",
  NO: "NO ACTION",
};

export function translateSegmentStatus(gdsCode: string): string {
  return SEGMENT_STATUS_MAP[gdsCode.toUpperCase()] || gdsCode;
}

// Map segment status to badge variant name
export function segmentStatusVariant(gdsCode: string): string {
  switch (gdsCode.toUpperCase()) {
    case "HK": return "scheduled";
    case "XX": return "cancelled";
    case "TK": return "escalated";
    default: return "secondary";
  }
}

// Map decision status to badge variant name
export function decisionStatusVariant(status: string): string {
  switch (status.toUpperCase()) {
    case "APPROVED": return "approved";
    case "REJECTED": return "rejected";
    case "ESCALATED": return "escalated";
    case "CONFIRMED": return "confirmed";
    default: return "secondary";
  }
}

// Availability level for seat count display
export function seatAvailabilityLevel(seats: number): "high" | "medium" | "low" {
  if (seats > 20) return "high";
  if (seats >= 5) return "medium";
  return "low";
}
```

### Example 3: Processor Page Structure

```typescript
// src/app/processor/page.tsx (structural outline)
"use client";

import { useReducer } from "react";
import { useMutation } from "@tanstack/react-query";
import { lookupReservation, evaluateReservation, selectOption } from "@/lib/api";
import { processorReducer, initialState } from "./reducer";
import { PnrLookupForm } from "@/components/processor/pnr-lookup-form";
import { ReservationPanel } from "@/components/processor/reservation-panel";
import { ReservationSkeleton } from "@/components/processor/reservation-skeleton";
import { RuleTracePanel } from "@/components/processor/rule-trace-panel";
import { RuleTraceSkeleton } from "@/components/processor/rule-trace-skeleton";
import { DecisionPanel } from "@/components/processor/decision-panel";
import { DecisionSkeleton } from "@/components/processor/decision-skeleton";
import { ReprotectionOptions } from "@/components/processor/reprotection-options";
import { ConfirmationDialog } from "@/components/processor/confirmation-dialog";
import { AuditTrailPanel } from "@/components/processor/audit-trail-panel";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { AlertCircle } from "lucide-react";

export default function ProcessorPage() {
  const [state, dispatch] = useReducer(processorReducer, { step: "IDLE" });

  // ... mutation hooks wired to dispatch ...

  const isFormDisabled = state.step === "LOOKUP_LOADING" || state.step === "SELECTION_LOADING";

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Processor</h1>
        <p className="text-muted-foreground">
          Look up a PNR and process involuntary change decisions.
        </p>
      </div>

      {/* PNR Lookup Form -- always visible */}
      <PnrLookupForm
        onSubmit={(pnr, lastName) => lookupMutation.mutate({ pnr, lastName })}
        disabled={isFormDisabled}
        loading={state.step === "LOOKUP_LOADING"}
      />

      {/* Error alert */}
      {state.step === "LOOKUP_ERROR" && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>PNR not found</AlertTitle>
          <AlertDescription>{state.error}</AlertDescription>
        </Alert>
      )}

      {/* Reservation -- skeleton or resolved */}
      {state.step === "LOOKUP_LOADING" && <ReservationSkeleton />}
      {"reservation" in state && <ReservationPanel reservation={state.reservation} />}

      {/* Rule Trace + Decision -- two column grid */}
      {/* ... conditional rendering based on state.step ... */}

      {/* Reprotection Options */}
      {/* ... only when DECISION_APPROVED or later ... */}

      {/* Confirmation Dialog */}
      {/* ... when CONFIRMING or SELECTION_LOADING ... */}

      {/* Audit Trail */}
      {state.step === "DECISION_RECORDED" && (
        <AuditTrailPanel confirmation={state.confirmation} decision={state.decision} reservation={state.reservation} />
      )}
    </div>
  );
}
```

## API Response Shape Reference

These are the exact response shapes from the existing backend endpoints. Verified by reading the router files and Pydantic schemas.

### POST /api/lookup -- Response (Confidence: HIGH)

```json
{
  "id": 1,
  "pnr": "XKJR4T",
  "booking_reference": null,
  "created_at": "2026-03-30T00:00:00",
  "passengers": [
    {
      "id": 1,
      "last_name": "MARTINEZ",
      "first_name": "DANIELA",
      "ticket_number": "045-1234567890",
      "fare_class": "Y",
      "fare_basis": "YLNR",
      "passenger_type": "ADT",
      "ssr_records": []
    }
  ],
  "segments": [
    {
      "id": 1,
      "flight_number": "AV123",
      "airline": "AV",
      "origin": "BOG",
      "destination": "MDE",
      "departure_date": "2026-04-15",
      "departure_time": "08:30",
      "arrival_time": "09:45",
      "status": "XX",
      "cabin_class": "Y",
      "aircraft_type": "A320"
    }
  ]
}
```

**Key note:** `status` field contains GDS codes ("XX", "HK", "TK"), NOT display strings. Frontend MUST translate.

### POST /api/evaluate -- Response (Confidence: HIGH)

```json
{
  "decision_id": 42,
  "status": "APPROVED",
  "rule_applied": "involuntary_change",
  "justification": "Se cumplen condiciones de proteccion tarifaria y reproteccion en vuelo equivalente.",
  "trace": [
    { "step": "INPUT_VALIDATION", "result": "PASS", "detail": "PNR XKJR4T found with 1 passenger(s), 2 segment(s)" },
    { "step": "EVENT_CLASSIFICATION", "result": "CANCELLATION", "detail": "Segment status check: AV123=XX" },
    { "step": "RULE_CHECK", "result": "PASS", "detail": "flight_cancelled=True" },
    { "step": "RULE_CHECK", "result": "PASS", "detail": "same_airline=True" },
    { "step": "RULE_CHECK", "result": "PASS", "detail": "same_route=True" },
    { "step": "RULE_CHECK", "result": "PASS", "detail": "no_sensitive_ssr=True" },
    { "step": "RULE_CHECK", "result": "PASS", "detail": "same_fare_class=True" },
    { "step": "RULE_EVALUATION", "result": "APPROVED", "detail": "Approved for automatic reprotection" },
    { "step": "OPTIONS_GENERATION", "result": "3 OPTIONS", "detail": "Route BOG-MDE, 3 available flights found" }
  ],
  "options": [
    {
      "id": 5,
      "flight_number": "AV125",
      "airline": "AV",
      "origin": "BOG",
      "destination": "MDE",
      "departure_date": "2026-04-15",
      "departure_time": "10:30",
      "arrival_time": "11:45",
      "available_seats": 42,
      "fare_class": "Y",
      "aircraft_type": "A320",
      "status": "SCHEDULED"
    }
  ]
}
```

**Key notes:**
- `justification` may be in Spanish (from `involuntary_change_rule`)
- `trace[].result` values are mixed: "PASS", "FAIL", "CANCELLATION", "APPROVED", "REJECTED", "ESCALATED", "INFO", "3 OPTIONS" -- not just PASS/FAIL/WARN
- `options` array is empty when status is REJECTED or ESCALATED
- Options use `"SCHEDULED"` as status (not GDS codes), since they come from the flights table directly

### POST /api/select -- Response (Confidence: HIGH)

```json
{
  "id": 42,
  "status": "CONFIRMED",
  "selected_option": "AV125",
  "pnr": "XKJR4T",
  "timestamp": "2026-03-30T15:30:00"
}
```

### Error Responses (Confidence: HIGH)

All error responses follow FastAPI's default pattern:

```json
// 404 Not Found
{ "detail": "Reservation not found or last name does not match" }

// 400 Bad Request
{ "detail": "Cannot select option for decision with status REJECTED" }

// 500 Internal Server Error (unhandled)
{ "detail": "Internal Server Error" }
```

The existing `apiFetch` in `lib/api.ts` already parses the `detail` field from error responses and throws it as `Error.message`. This works correctly with the mutation `onError` callbacks.

## Trace Result Value Normalization

The UI-SPEC assumes trace results are "PASS", "FAIL", or "WARN" for the step indicators. But the backend returns mixed values. The frontend needs a normalization function:

```typescript
function normalizeTraceResult(result: string): "PASS" | "FAIL" | "WARN" | "INFO" {
  const upper = result.toUpperCase();
  if (upper === "PASS" || upper === "APPROVED" || upper.includes("OPTIONS")) return "PASS";
  if (upper === "FAIL" || upper === "REJECTED") return "FAIL";
  if (upper === "WARN" || upper === "ESCALATED" || upper.includes("SENSITIVE")) return "WARN";
  return "INFO"; // CANCELLATION, SCHEDULE_CHANGE, etc.
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| useState per field | useReducer with discriminated union | Standard since TS 4.x | Invalid states become impossible |
| useQuery for mutations | useMutation for imperative operations | TanStack Query v5 | Clearer intent, better loading/error states |
| Custom CSS animations | Tailwind `transition-*` + `animate-pulse` | Tailwind v3+ | No JS animation runtime needed |
| jQuery modals | Radix Dialog (via shadcn) | 2023+ | Focus management, aria, portal rendering |
| Manual error boundaries | useMutation onError + Alert component | TanStack Query v4+ | Granular per-operation error handling |

## Open Questions

1. **Trace step normalization**
   - What we know: Backend returns mixed result strings ("PASS", "CANCELLATION", "3 OPTIONS", "APPROVED")
   - What's unclear: Whether the UI-SPEC trace step icons (circle indicators) should handle all these variations or just PASS/FAIL/WARN
   - Recommendation: Normalize to PASS/FAIL/WARN/INFO in frontend, map INFO to a neutral color (muted-foreground)

2. **Spanish justification in APPROVED case**
   - What we know: `involuntary_change_rule()` returns Spanish; `decision_service.py` passes it through for APPROVED
   - What's unclear: Whether to fix in backend or frontend
   - Recommendation: Quick backend fix (override justification string in decision_service.py line ~99 with English) is cleaner than frontend string matching. Include as Wave 0 / prerequisite task.

3. **Selected option card ring after DECISION_RECORDED**
   - What we know: UI-SPEC says "visible(selected)" for Options in DECISION_RECORDED state
   - What's unclear: How to show which card was selected without the dialog being open
   - Recommendation: Persist `selectedOptionId` in DECISION_RECORDED state (already in the type); render that card with `ring-2 ring-primary` and disable all "Select Flight" buttons

## Sources

### Primary (HIGH confidence)
- **Backend routers**: Direct code reading of `axiom/api/routers/lookup.py`, `evaluate.py`, `select.py` -- verified exact request/response shapes
- **Pydantic schemas**: `axiom/models/schemas.py` -- verified field names, types, optional vs required
- **ORM models**: `axiom/db/models.py` -- verified database column types and GDS status codes
- **Decision service**: `axiom/services/decision_service.py` -- verified rule evaluation flow, trace generation, Spanish string source
- **Seed data**: `axiom/db/seed.py` -- verified status code values ("XX", "HK", "TK"), airline codes, route patterns
- **UI-SPEC**: `.planning/phases/02-core-workflow/02-UI-SPEC.md` -- verified component inventory, state machine, skeleton specs, color tokens
- **Phase 1 research**: `.planning/phases/01-foundation-backend-app-shell/01-RESEARCH.md` -- verified stack decisions and architecture patterns
- **Existing frontend**: Direct reading of `layout.tsx`, `globals.css`, `api.ts`, `query-provider.tsx`, `app-sidebar.tsx`, `processor/page.tsx`

### Secondary (MEDIUM confidence)
- [TanStack Query v5 Mutations docs](https://tanstack.com/query/v5/docs/framework/react/guides/mutations) -- verified useMutation patterns for sequential operations
- [TanStack Query v5 Dependent Queries](https://tanstack.com/query/latest/docs/framework/react/guides/dependent-queries) -- verified enabled pattern for dependent queries
- [shadcn/ui Components](https://ui.shadcn.com/docs/components) -- verified all 11 required components are available in official registry
- [Writing State Machine in React with TypeScript Using useReducer](https://undefined.technology/blog/state-machine-in-react-with-usereducer/) -- verified useReducer + discriminated union pattern

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- all libraries already installed, versions verified from package.json
- Architecture (state machine, mutations): HIGH -- patterns verified from TanStack Query docs and existing codebase
- Backend API shapes: HIGH -- verified by direct code reading of routers, schemas, and services
- Data mapping layer: HIGH -- verified GDS codes in seed data, Spanish strings in rule function
- Pitfalls: HIGH -- identified through code reading (GDS codes, Spanish strings, race conditions)

**Research date:** 2026-03-30
**Valid until:** 2026-04-30 (stable stack, no fast-moving dependencies)
