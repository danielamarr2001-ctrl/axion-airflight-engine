---
phase: 2
slug: core-workflow
status: draft
shadcn_initialized: true
preset: default (neutral base, css variables)
created: 2026-03-30
---

# Phase 2 -- UI Design Contract

> Visual and interaction contract for the Core Workflow phase: PNR lookup, reservation display, rule evaluation, reprotection options, decision recording, and audit trail.

---

## Design System

| Property | Value |
|----------|-------|
| Tool | shadcn/ui (components.json present, default style) |
| Preset | default -- neutral baseColor, cssVariables: true, rsc: true |
| Component library | Radix UI (via shadcn/ui primitives) |
| Icon library | Lucide React (lucide-react ^0.469.0) |
| Font | Inter (Google Fonts, variable --font-sans) |

### shadcn Components Required for Phase 2

Install via `npx shadcn@latest add {name}` before implementation:

| Component | Usage |
|-----------|-------|
| button | Primary CTA, option selection, form submit |
| input | PNR code field, last name field |
| label | Form field labels |
| card | Reservation card, flight option cards, decision panel |
| badge | Status badges (APPROVED, REJECTED, ESCALATED, CANCELLED) |
| skeleton | Loading states for reservation, rule trace, options |
| alert | Error states (PNR not found, API errors) |
| separator | Section dividers within panels |
| dialog | Confirmation dialog for flight selection |
| table | Passenger list, segment list |
| tooltip | Abbreviated data explanations (fare class, SSR codes) |

---

## Spacing Scale

Declared values (all multiples of 4):

| Token | Value | Usage |
|-------|-------|-------|
| xs | 4px | Icon-to-text gaps, inline badge padding |
| sm | 8px | Compact element spacing, table cell padding |
| md | 16px | Default element spacing, card internal padding |
| lg | 24px | Section padding, form field vertical gaps |
| xl | 32px | Layout gaps between major panels |
| 2xl | 48px | Page header to content gap |
| 3xl | 64px | Not used in Phase 2 (no page-level breaks needed) |

Exceptions:
- Touch targets on flight option "Select" buttons: minimum 36px height (dense operational layout, not 44px mobile targets)
- Table rows: 40px minimum height for readable data density
- Form inputs: 40px height to match existing shadcn/ui default

---

## Typography

| Role | Size | Weight | Line Height | Usage |
|------|------|--------|-------------|-------|
| Body | 14px | 400 (regular) | 1.5 | Table cells, descriptions, trace details |
| Label | 12px | 400 (regular) | 1.4 | Form labels, column headers, badge text, metadata |
| Heading | 20px | 600 (semibold) | 1.2 | Section titles ("Reservation", "Rule Evaluation", "Reprotection Options") |
| Page Title | 24px | 600 (semibold) | 1.2 | Page heading ("Processor"), matches existing page.tsx pattern |

Only two weights are used: 400 (regular) for body and label text, 600 (semibold) for headings, page title, and CTAs. No other weights are permitted.

Font stack: `Inter, system-ui, -apple-system, sans-serif` (via `--font-sans` CSS variable, already configured in layout.tsx).

Monospace for data values: `ui-monospace, SFMono-Regular, Menlo, monospace` for PNR codes, flight numbers, ticket numbers, fare basis codes, and timestamps. Applied via Tailwind `font-mono` class.

---

## Color

All colors reference existing CSS custom properties from `globals.css`. No new color tokens are introduced.

| Role | Token | oklch Value | Usage |
|------|-------|-------------|-------|
| Dominant (60%) | --color-background | oklch(0.145 0.02 260) | Page background, main content area |
| Secondary (30%) | --color-card | oklch(0.18 0.02 260) | Reservation card, option cards, decision panel, form container |
| Accent (10%) | --color-primary | oklch(0.72 0.15 185) | See reserved list below |
| Destructive | --color-destructive | oklch(0.55 0.2 25) | REJECTED badge, CANCELLED segment status, error alerts |

### Accent Reserved For (exhaustive list)

The teal accent (`--color-primary`, oklch(0.72 0.15 185)) is used ONLY on:

1. "Look Up" primary CTA button (solid fill)
2. "Select Flight" primary CTA button (solid fill)
3. "Confirm Selection" button in selection dialog (solid fill)
4. APPROVED status badge (text color on muted background)
5. Active/selected flight option card border (1px ring)
6. Rule trace "PASS" step indicator icon
7. Focus rings on form inputs (via --color-ring, already set)
8. Sidebar active nav item text (already implemented)

Everything else uses foreground, muted-foreground, secondary, or border tokens. No accent on headings, body text, separators, or card backgrounds.

### Semantic Status Colors

| Status | Background | Text | Border |
|--------|-----------|------|--------|
| APPROVED | oklch(0.72 0.15 185 / 0.15) | --color-primary | oklch(0.72 0.15 185 / 0.3) |
| REJECTED | oklch(0.55 0.2 25 / 0.15) | --color-destructive | oklch(0.55 0.2 25 / 0.3) |
| ESCALATED | oklch(0.7 0.15 55 / 0.15) | --color-chart-4 | oklch(0.7 0.15 55 / 0.3) |
| CANCELLED | oklch(0.55 0.2 25 / 0.15) | --color-destructive | oklch(0.55 0.2 25 / 0.3) |
| SCHEDULED | oklch(0.72 0.15 185 / 0.15) | --color-primary | oklch(0.72 0.15 185 / 0.3) |
| CONFIRMED | oklch(0.7 0.15 145 / 0.15) | --color-chart-3 | oklch(0.7 0.15 145 / 0.3) |

Badge pattern: 15% opacity background + full-color text + 30% opacity border. Consistent across all status values. Applied via a shared `status-badge` variant in the Badge component.

### Availability Seat Indicator Colors

Seat availability on flight option cards uses existing chart and destructive tokens, not raw green/yellow/red:

| Availability Level | Token | oklch Value | Rendering |
|--------------------|-------|-------------|-----------|
| High (> 20 seats) | --color-chart-3 | oklch(0.7 0.15 145) | 15% opacity background, full-color text |
| Medium (5-20 seats) | --color-chart-4 | oklch(0.7 0.15 55) | 15% opacity background, full-color text |
| Low (< 5 seats) | --color-destructive | oklch(0.55 0.2 25) | 15% opacity background, full-color text |

Applied as an inline badge on the "X seats available" text within each flight option card. Pattern mirrors the status badge approach: `bg-[token/0.15] text-[token]`.

---

## Layout Contract

### Page Structure (Processor page)

```
+--sidebar(264px)--+---main content (flex-1, p-6)-------------------+
|                  |                                                  |
| AXIOM            | Page Title: "Processor"                         |
| AirFlight Engine | Subtitle: "Look up a PNR and process..."       |
|                  |                                                  |
| > Processor      | +--PNR Lookup Form (max-w-md)----------------+  |
|   Rules          | | PNR Code [______] Last Name [______] [Look Up]|
|   Metrics        | +--------------------------------------------+  |
|                  |                                                  |
| Decision Intel.  | +--Reservation Panel (full width)-------------+ |
| Platform         | | Passengers | Segments                        | |
|                  | | (table)    | (table with status badges)      | |
|                  | +--------------------------------------------+  |
|                  |                                                  |
|                  | +--two-column layout (grid cols-2 gap-8)------+ |
|                  | | Rule Evaluation    | Decision Panel          | |
|                  | | (trace steps)      | (status + justification)| |
|                  | +--------------------------------------------+  |
|                  |                                                  |
|                  | +--Reprotection Options (full width)----------+ |
|                  | | [Option Card] [Option Card] [Option Card]    | |
|                  | +--------------------------------------------+  |
|                  |                                                  |
|                  | +--Audit Trail (full width, collapsed)--------+ |
|                  | | Timeline of actions with timestamps          | |
|                  | +--------------------------------------------+  |
+------------------+--------------------------------------------------+
```

### Responsive Breakpoints

| Breakpoint | Layout Change |
|-----------|---------------|
| >= 1280px (default) | Two-column grid for Rule Evaluation + Decision Panel |
| 1024-1279px | Two-column grid maintained, narrower cards |
| < 1024px | Not targeted (desktop-only per UI-06), but stack to single column as graceful fallback |

Minimum supported width: 1280px (per PITFALLS.md: projector-safe at 1280x720).

---

## Component Inventory

### 1. PNR Lookup Form

**Location:** Top of Processor page, always visible.
**State machine:** `idle` -> `loading` -> `success` | `error`

| Element | Component | Details |
|---------|-----------|---------|
| PNR Code input | shadcn Input | placeholder: "e.g. XKJR4T", maxLength: 6, uppercase transform, font-mono |
| Last Name input | shadcn Input | placeholder: "e.g. MARTINEZ", uppercase transform |
| Submit button | shadcn Button (default variant) | label: "Look Up", accent background |
| Form container | div with flex row | max-w-md, gap-sm (8px) between fields, gap-md (16px) to button |

**Behavior:**
- Both fields required. Button disabled until both non-empty.
- On submit: button shows spinner + "Looking up..." text.
- On success: form remains visible with entered values, reservation panel appears below.
- On error: form remains editable, error alert appears below form.
- PNR field auto-uppercases on input (CSS `uppercase` + JS transform on submit).
- Enter key submits form when focused on either field.

### 2. Reservation Panel

**Location:** Below PNR Lookup Form, appears after successful lookup.
**Enter animation:** fade-in + slide-up (150ms ease-out).

**Structure:**
```
+--Card (bg-card, border-border, rounded-lg, p-md)--+
| Heading: "Reservation [PNR]"     Badge: [status]   |
| Separator                                           |
| +--Passengers Table---------+ +--Segments Table---+ |
| | Name | Ticket | Fare | Type| | Flight | Route |  | |
| | ...  |  ...   | ...  | ... | | Date | Time |    | |
| +---------------------------+ | Status |           | |
|                               +-------------------+ |
+-----------------------------------------------------+
```

**Passengers Table:**

| Column | Source Field | Format | Width |
|--------|------------|--------|-------|
| Passenger | `last_name` + `first_name` | "MARTINEZ/DANIELA" format, font-mono | auto |
| Ticket | `ticket_number` | "045-1234567890" format, font-mono | 160px |
| Fare Class | `fare_class` | Single letter badge, e.g. "Y", font-mono | 80px |
| Type | `passenger_type` | "ADT", "CHD", "INF" | 60px |
| SSR | `ssr_records` | Count badge or icon if present, tooltip for details | 60px |

**Segments Table:**

| Column | Source Field | Format | Width |
|--------|------------|--------|-------|
| Flight | `flight_number` | "AV123" format, font-mono, semibold (600) | 80px |
| Route | `origin` + `destination` | "BOG -> MDE" with arrow, font-mono | 120px |
| Date | `departure_date` | "15 Apr 2026" format (dd MMM yyyy) | 100px |
| Departure | `departure_time` | "08:30" 24h format, font-mono | 70px |
| Arrival | `arrival_time` | "09:45" 24h format, font-mono | 70px |
| Status | `status` | Status badge (SCHEDULED, CANCELLED, DELAYED) | 100px |

The CANCELLED segment row gets a subtle destructive background tint: `oklch(0.55 0.2 25 / 0.05)` to draw operator attention.

### 3. Rule Evaluation Trace

**Location:** Left column of two-column grid, below reservation panel.
**Appears:** Automatically after reservation loads (auto-evaluate flow).
**Enter animation:** staggered fade-in per step (50ms delay between steps).

**Structure:**
```
+--Card (bg-card)---------------------------+
| Heading: "Rule Evaluation"                 |
| Separator                                  |
| Step 1: [icon] Flight Status    [PASS]     |
|   detail text in muted-foreground          |
| Step 2: [icon] Same Airline     [PASS]     |
|   detail text                              |
| Step 3: [icon] Same Route       [PASS]     |
|   detail text                              |
| Step 4: [icon] SSR Check        [PASS]     |
|   detail text                              |
| Step 5: [icon] Fare Protection  [PASS]     |
|   detail text                              |
+--------------------------------------------+
```

Each trace step is a row with:
- **Left:** 16px circle indicator (teal fill for PASS, destructive fill for FAIL, chart-4 fill for WARN)
- **Vertical connector line** between steps (2px, border color, dashed)
- **Step label:** `trace[].step` value, 14px regular (400)
- **Result badge:** `trace[].result` as small badge (PASS/FAIL/WARN)
- **Detail:** `trace[].detail` in muted-foreground, 12px regular (400)

### 4. Decision Panel

**Location:** Right column of two-column grid, beside Rule Evaluation.
**Shows:** The overall decision result.

**Structure:**
```
+--Card (bg-card)--------------------------+
| Heading: "Decision"                       |
| Separator                                 |
|                                           |
| [====APPROVED====]   <-- large badge      |
|                                           |
| Rule Applied: involuntary_change          |
|                                           |
| Justification:                            |
| "Flight cancelled, same airline, same     |
|  route, no sensitive SSR, same fare class"|
|                                           |
+-------------------------------------------+
```

**Decision status display:**
- Status badge is oversized: 24px text (Page Title size), semibold (600), centered, full-width within card, with extra padding (24px vertical) for visual prominence
- Uses semantic status color scheme (see Color section)
- When APPROVED: shows "Reprotection Approved" with checkmark icon
- When REJECTED: shows "Reprotection Rejected" with X icon, justification explains why
- When ESCALATED: shows "Manual Review Required" with alert-triangle icon, justification explains trigger

**REJECTED/ESCALATED behavior:**
- No reprotection options section appears
- Decision panel expands to full width (no two-column split needed)
- A muted card below says: "No reprotection options available for this decision."

### 5. Reprotection Options

**Location:** Full-width section below the two-column rule/decision grid.
**Appears only when:** Decision status is APPROVED.
**Enter animation:** fade-in + slide-up (200ms ease-out), 100ms delay after decision panel.

**Structure:**
```
+--Section heading: "Reprotection Options"--+
| Select an alternative flight                |
|                                             |
| +--Option Card--+ +--Option Card--+ +--+   |
| | AV125          | | AV127          | |..|  |
| | BOG -> MDE     | | BOG -> MDE     | |  |  |
| | 10:30 - 11:45  | | 14:00 - 15:15  | |  |  |
| | Seats: 42      | | Seats: 18      | |  |  |
| | Fare: Y (+$0)  | | Fare: Y (+$0)  | |  |  |
| | [Select Flight]| | [Select Flight]| |  |  |
| +----------------+ +----------------+ +--+  |
+---------------------------------------------+
```

**Flight Option Card layout:**

| Field | Source | Format |
|-------|--------|--------|
| Flight number | `flight_number` | "AV125", font-mono, 16px semibold (600) |
| Route | `origin` + `destination` | "BOG -> MDE", font-mono |
| Date | `departure_date` | "15 Apr 2026" |
| Time window | `departure_time` + `arrival_time` | "10:30 - 11:45", font-mono |
| Aircraft | `aircraft_type` | "A320" or omit if null |
| Availability | `available_seats` | "42 seats available" -- uses availability seat indicator colors: `--color-chart-3` bg at 15% + text if > 20, `--color-chart-4` bg at 15% + text if 5-20, `--color-destructive` bg at 15% + text if < 5 |
| Fare class | `fare_class` | "Class Y" |
| CTA | button | "Select Flight" -- accent button, full width at bottom of card |

Card grid: `grid grid-cols-3 gap-md` for 3 options, `grid-cols-2 lg:grid-cols-4` for 4-5 options. Each card: `bg-card border-border rounded-lg p-md`. Selected card: `ring-2 ring-primary` border.

**Interaction:**
- Clicking "Select Flight" opens a confirmation dialog (not immediate action).
- Only one card can be in "selected" state at a time (radio-group behavior on the cards).
- Hover: card border transitions to muted-foreground over 150ms.

### 6. Selection Confirmation Dialog

**Trigger:** Operator clicks "Select Flight" on an option card.
**Component:** shadcn Dialog.

**Content:**
```
+--Dialog--------------------------------------+
| Confirm Reprotection                          |
|                                               |
| Rebook passengers on flight AV125?            |
|                                               |
| From: AV123 BOG-MDE 08:30 (CANCELLED)        |
| To:   AV125 BOG-MDE 10:30                    |
|                                               |
| Operator Notes (optional):                    |
| [____________________________________]        |
|                                               |
| [Back to Options]          [Confirm Selection]|
+-----------------------------------------------+
```

| Element | Details |
|---------|---------|
| Title | "Confirm Reprotection" |
| Body | "Rebook passengers on flight {flight_number}?" |
| From line | Original cancelled flight details, font-mono, with CANCELLED badge |
| To line | Selected replacement flight details, font-mono |
| Notes field | shadcn Input, optional, placeholder: "Optional notes for audit trail" |
| Cancel button | shadcn Button (outline variant), label: "Back to Options" |
| Confirm button | shadcn Button (default variant), label: "Confirm Selection", accent background |

**Behavior:**
- "Back to Options" closes dialog, returns to options view with no card selected.
- "Confirm Selection" sends POST /api/select, button shows spinner + "Recording decision..."
- On success: dialog closes, audit trail section appears/updates.
- On error: inline alert within dialog, buttons re-enabled.

### 7. Audit Trail Panel

**Location:** Full-width section at bottom of page, below options.
**Appears:** After successful selection confirmation.
**Can also appear:** As part of initial state if viewing a previously-processed PNR.

**Structure:**
```
+--Card (bg-card)----------------------------------+
| Heading: "Audit Trail"                            |
| Separator                                         |
|                                                   |
| [timestamp] Decision recorded                     |
|   Status: CONFIRMED                               |
|   Selected: AV125 BOG-MDE 10:30                   |
|   Operator notes: (if any)                        |
|                                                   |
| [timestamp] Reprotection approved                 |
|   Rule: involuntary_change                        |
|   5/5 checks passed                               |
|                                                   |
| [timestamp] PNR XKJR4T retrieved                  |
|   2 passengers, 3 segments                        |
|   1 segment CANCELLED                             |
|                                                   |
+---------------------------------------------------+
```

Each entry is a vertical timeline item with:
- Timestamp: font-mono, 12px regular (400), muted-foreground
- Title: 14px, semibold (600)
- Details: 12px regular (400), muted-foreground, indented 24px from timeline marker
- Timeline marker: 8px filled circle + 2px vertical line connector

---

## State Machine

The Processor page follows a linear state machine. Each state determines which components are visible.

```
IDLE
  -> (operator submits PNR + last name)
LOOKUP_LOADING
  -> (API success) RESERVATION_LOADED
  -> (API error)   LOOKUP_ERROR

LOOKUP_ERROR
  -> (operator re-submits) LOOKUP_LOADING

RESERVATION_LOADED
  -> (auto-trigger evaluate) EVALUATING

EVALUATING
  -> (API success, APPROVED)   DECISION_APPROVED
  -> (API success, REJECTED)   DECISION_REJECTED
  -> (API success, ESCALATED)  DECISION_ESCALATED
  -> (API error)               EVALUATION_ERROR

DECISION_APPROVED
  -> (operator clicks Select Flight) CONFIRMING

DECISION_REJECTED
  (terminal -- operator can start new lookup)

DECISION_ESCALATED
  (terminal -- operator can start new lookup)

CONFIRMING
  -> (operator confirms) SELECTION_LOADING
  -> (operator clicks Back to Options)  DECISION_APPROVED

SELECTION_LOADING
  -> (API success) DECISION_RECORDED
  -> (API error)   SELECTION_ERROR

SELECTION_ERROR
  -> (retry) SELECTION_LOADING
  -> (Back to Options) DECISION_APPROVED

DECISION_RECORDED
  (terminal -- audit trail visible, operator can start new lookup)
```

### Visible Components Per State

| State | Form | Reservation | Rule Trace | Decision | Options | Dialog | Audit |
|-------|------|-------------|------------|----------|---------|--------|-------|
| IDLE | editable | hidden | hidden | hidden | hidden | hidden | hidden |
| LOOKUP_LOADING | disabled | skeleton | hidden | hidden | hidden | hidden | hidden |
| LOOKUP_ERROR | editable | hidden | hidden | hidden | hidden | hidden | hidden |
| RESERVATION_LOADED | editable | visible | skeleton | hidden | hidden | hidden | hidden |
| EVALUATING | editable | visible | animating | skeleton | hidden | hidden | hidden |
| DECISION_APPROVED | editable | visible | visible | visible | visible | hidden | hidden |
| DECISION_REJECTED | editable | visible | visible | visible | hidden | hidden | hidden |
| DECISION_ESCALATED | editable | visible | visible | visible | hidden | hidden | hidden |
| CONFIRMING | editable | visible | visible | visible | visible | open | hidden |
| SELECTION_LOADING | disabled | visible | visible | visible | visible | open+loading | hidden |
| DECISION_RECORDED | editable | visible | visible | visible | visible(selected) | hidden | visible |

---

## Skeleton Screens (UI-04)

Each skeleton matches the exact layout of its resolved component:

### Reservation Skeleton
- Card container with correct dimensions
- Two skeleton rows for heading area (h-6 w-48, h-4 w-32)
- Separator line
- Two-column skeleton grid:
  - Left: 4 skeleton rows (h-4) simulating passenger table
  - Right: 4 skeleton rows (h-4) simulating segments table
- Skeleton pulse animation: `animate-pulse` (Tailwind default)
- Duration on screen: 200-800ms typical API response

### Rule Trace Skeleton
- 5 skeleton step rows, each with:
  - Circle placeholder (h-4 w-4 rounded-full)
  - Text line (h-4 w-40)
  - Badge placeholder (h-5 w-12)
- Staggered opacity: steps further down are more transparent (0.8, 0.6, 0.4, 0.3, 0.2)

### Decision Panel Skeleton
- Large centered badge placeholder (h-10 w-48)
- Two text line placeholders (h-4 w-full)
- One longer text block placeholder (h-16 w-full)

---

## Error States (UI-05)

### PNR Not Found (PNR-05)

**Component:** shadcn Alert (destructive variant).
**Location:** Below PNR Lookup Form, replacing reservation panel.

```
+--Alert (destructive)---------------------------+
| [AlertCircle icon]                              |
| PNR not found                                   |
|                                                 |
| No reservation matches PNR "XKJR4T" with       |
| last name "MARTINEZ". Verify the PNR code and   |
| passenger last name, then try again.             |
+------------------------------------------------+
```

### API Error (generic)

**Component:** shadcn Alert (destructive variant).
**Copy:** "Something went wrong. The server returned an unexpected error. Please try again in a moment."

### Evaluation Error

**Component:** Inline alert below reservation panel.
**Copy:** "Rule evaluation failed. The decision engine could not process this reservation. Please try the lookup again."

### Selection Error

**Component:** Inline alert within confirmation dialog.
**Copy:** "Could not record the selection. Please try confirming again."

---

## Copywriting Contract

All user-facing text for Phase 2 components.

| Element | Copy |
|---------|------|
| Page title | "Processor" |
| Page subtitle | "Look up a PNR and process involuntary change decisions." |
| PNR field label | "PNR Code" |
| PNR field placeholder | "e.g. XKJR4T" |
| Last name field label | "Last Name" |
| Last name field placeholder | "e.g. MARTINEZ" |
| Primary CTA (lookup) | "Look Up" |
| Loading CTA (lookup) | "Looking up..." |
| Reservation heading | "Reservation {PNR}" |
| Rule evaluation heading | "Rule Evaluation" |
| Decision heading | "Decision" |
| APPROVED display | "Reprotection Approved" |
| REJECTED display | "Reprotection Rejected" |
| ESCALATED display | "Manual Review Required" |
| Options heading | "Reprotection Options" |
| Options subtitle | "Select an alternative flight for the affected passengers." |
| Option CTA | "Select Flight" |
| No options (rejected) | "No reprotection options available. This reservation does not qualify for automated reprotection." |
| No options (escalated) | "This case requires manual review. Escalate to a senior agent for further assessment." |
| Dialog title | "Confirm Reprotection" |
| Dialog body | "Rebook passengers on flight {flight_number}?" |
| Dialog from label | "From:" |
| Dialog to label | "To:" |
| Notes field label | "Operator Notes" |
| Notes field placeholder | "Optional notes for audit trail" |
| Dialog cancel | "Back to Options" |
| Dialog confirm | "Confirm Selection" |
| Dialog loading | "Recording decision..." |
| Audit trail heading | "Audit Trail" |
| Error: PNR not found heading | "PNR not found" |
| Error: PNR not found body | "No reservation matches PNR \"{pnr}\" with last name \"{last_name}\". Verify the PNR code and passenger last name, then try again." |
| Error: API generic | "Something went wrong. The server returned an unexpected error. Please try again in a moment." |
| Error: Evaluation failure | "Rule evaluation failed. The decision engine could not process this reservation. Please try the lookup again." |
| Error: Selection failure | "Could not record the selection. Please try confirming again." |

### Language Rule

All backend responses that may contain Spanish strings (e.g., "APROBADO", "RECHAZADO", "Escalar el caso para revision manual") must be mapped to English in the frontend API client layer (`lib/api.ts` or a dedicated transform utility). The UI never displays raw backend string values for status or justification fields without passing through a translation map.

Status mapping:
- "APROBADO" -> "APPROVED"
- "RECHAZADO" -> "REJECTED"
- "ESCALADO" / "ESCALATED" -> "ESCALATED"
- "CONFIRMADO" -> "CONFIRMED"

---

## Animation Contract

| Transition | Duration | Easing | Trigger |
|-----------|----------|--------|---------|
| Reservation panel enter | 150ms | ease-out | Lookup success |
| Rule trace step stagger | 50ms per step | ease-out | Evaluation starts |
| Decision badge enter | 200ms | ease-out | Evaluation complete |
| Options section enter | 200ms, 100ms delay | ease-out | After decision renders |
| Option card hover | 150ms | ease-in-out | Mouse enter/leave |
| Dialog open/close | 150ms | ease-out / ease-in | Click trigger |
| Skeleton pulse | 2000ms loop | ease-in-out | While loading |
| Audit trail enter | 200ms | ease-out | Selection confirmed |
| Error alert enter | 150ms | ease-out | Error received |

All animations use CSS transitions or Tailwind `transition-*` utilities. No JavaScript animation libraries required. The `prefers-reduced-motion: reduce` media query disables all non-essential animations (skeletons still pulse, but enter animations are instant).

---

## Data Shape Reference

These are the exact TypeScript interfaces the frontend consumes, derived from the backend Pydantic schemas in `axiom/models/schemas.py`.

```typescript
// From POST /api/lookup response
interface Reservation {
  id: number;
  pnr: string;
  booking_reference: string | null;
  created_at: string; // ISO datetime
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
  passenger_type: string; // "ADT" | "CHD" | "INF"
  ssr_records: SSRRecord[];
}

interface Segment {
  id: number;
  flight_number: string;
  airline: string;
  origin: string; // 3-letter IATA
  destination: string; // 3-letter IATA
  departure_date: string; // "YYYY-MM-DD"
  departure_time: string; // "HH:MM"
  arrival_time: string; // "HH:MM"
  status: string; // "SCHEDULED" | "CANCELLED" | "DELAYED"
  cabin_class: string;
  aircraft_type: string | null;
}

interface SSRRecord {
  id: number;
  ssr_type: string;
  ssr_detail: string | null;
}

// From POST /api/evaluate response
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
  result: string; // "PASS" | "FAIL" | "WARN"
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

// From POST /api/select response
interface SelectResponse {
  id: number;
  status: string; // "CONFIRMED"
  selected_option: string;
  pnr: string;
  timestamp: string; // ISO datetime
}
```

---

## Registry Safety

| Registry | Blocks Used | Safety Gate |
|----------|-------------|-------------|
| shadcn official | button, input, label, card, badge, skeleton, alert, separator, dialog, table, tooltip | not required (official registry) |

No third-party registries are used. All components come from the official shadcn/ui registry at https://ui.shadcn.com.

---

## Accessibility Requirements

| Requirement | Implementation |
|-------------|---------------|
| Focus management | Tab order follows visual flow: PNR field -> last name -> Look Up -> reservation content -> options -> audit trail |
| Keyboard navigation | Enter submits form, Escape closes dialog, Arrow keys navigate option cards |
| Screen reader labels | Form inputs have associated labels, status badges have aria-label with full text, tables use proper thead/tbody/th markup |
| Color contrast | All text meets WCAG AA (4.5:1 body, 3:1 large text). Teal on dark bg: oklch(0.72 0.15 185) on oklch(0.145 0.02 260) passes AA |
| Status indicators | Never rely on color alone: badges include text labels, trace steps include text result alongside colored indicator |
| Loading announcements | aria-live="polite" region announces loading and completion states |
| Dialog focus trap | Confirmation dialog traps focus while open per Radix Dialog behavior |

---

## Checker Sign-Off

- [ ] Dimension 1 Copywriting: PASS
- [ ] Dimension 2 Visuals: PASS
- [ ] Dimension 3 Color: PASS
- [ ] Dimension 4 Typography: PASS
- [ ] Dimension 5 Spacing: PASS
- [ ] Dimension 6 Registry Safety: PASS

**Approval:** pending
