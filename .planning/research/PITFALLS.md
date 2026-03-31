# Domain Pitfalls

**Domain:** Airline involuntary change decision engine + investor demo dashboard
**Researched:** 2026-03-30
**Confidence:** HIGH (based on direct codebase analysis + domain knowledge)

---

## Critical Pitfalls

Mistakes that cause rewrites, kill investor confidence, or make the demo non-functional.

### Pitfall 1: Simulated Data That Screams "Fake"

**What goes wrong:** The demo uses obviously fabricated data -- three hardcoded LATAM flights (LA513/515/517), PNRs like "AX123", city names in Spanish without IATA codes, and flight dates that always say "unknown". An investor who has flown commercially (all of them) immediately spots that the data looks nothing like what they see on their own boarding passes or itineraries. The illusion of a working product evaporates.

**Why it happens:** Developers simulate what the code needs, not what the domain looks like. The current `options_generator.py` returns the same three flights regardless of airline, route, or time context. There is no date, no fare class, no booking class, no cabin indicator -- data that even a non-technical airline stakeholder would expect to see.

**Consequences:** Investor questions shift from "how does this scale?" to "is this real at all?" The demo loses credibility on the first screen.

**Prevention:**
- Build a simulated PNR data store with 15-25 realistic reservations using proper structure: 6-character alphanumeric PNR locators (e.g., "XKJR4T"), IATA 3-letter airport codes (BOG, MAD, MIA), 2-letter IATA airline designators + 3-4 digit flight numbers (IB6543, LA801), ISO dates, fare basis codes (YOWCO, HLXP3M), booking class letters (Y, B, M, H, Q)
- Flight options must vary by route, show realistic departure windows, and include details like aircraft type and duration
- Mark every simulated response with a `"source": "simulated"` field but make the structure indistinguishable from real GDS output
- Use a seed data generation script that produces internally consistent reservations (routes that real airlines actually fly, connection times that make sense, fare classes that match the airline)

**Detection:** Show the demo to anyone who works in travel -- if they say "that's not what a PNR looks like," the data is too thin.

**Phase:** Phase 1 (Data Layer) -- this must be solved before any UI work begins, because the UI design depends on what data fields exist.

---

### Pitfall 2: Building a Dashboard Instead of Telling a Story

**What goes wrong:** The demo shows a dashboard with charts and tables, but no clear narrative arc. Investors see metrics (total requests, avg processing time) with no context for why those numbers matter. The demo becomes a tour of features rather than a demonstration of value.

**Why it happens:** Engineers build screens. Investor demos need a scripted walkthrough: a specific flight gets cancelled, AXIOM processes it in real time, the operator sees the decision rationale, selects a reprotection option, and the audit trail is complete. The current Flutter dashboard is a form + response dump -- there is no workflow visible.

**Consequences:** The investor asks "so what does this do?" after a 10-minute demo. The founder must narrate the value verbally because the product does not show it.

**Prevention:**
- Design the demo around one golden path: PNR lookup -> reservation display -> cancellation detected -> rules evaluated with visible justification -> options presented with recommendation -> operator selects -> decision recorded with audit trail
- Every screen should advance the story. The KPI dashboard is the epilogue showing "here is the aggregate impact," not the opening slide
- Pre-load the simulated data store with one perfectly crafted scenario that highlights every rule check (cancelled flight, same airline, same route, no sensitive SSR, same fare class = approved reprotection)
- Include one contrasting scenario: a case that triggers manual escalation (sensitive SSR passenger) to show the system handles edge cases

**Detection:** If you cannot demo the product in under 3 minutes without touching the keyboard (just clicking through a pre-set scenario), the story is not baked into the UI.

**Phase:** Phase 2 (Frontend Shell) -- the page layout and navigation must be designed around the demo narrative, not around a generic dashboard template.

---

### Pitfall 3: Extending the Free-Text Input Instead of Replacing It

**What goes wrong:** The current backend accepts a free-text `problem` string and parses it with fragile regex to extract PNR, passenger name, airline, route, and event type. The temptation is to keep this interface and just "improve the regex" or add more parsing. Every new field added to the regex makes the parser exponentially more fragile.

**Why it happens:** The existing `DecisionCore.process()` is built around a single string input. Refactoring to structured input feels like "rewriting the backend," so teams keep patching the parser.

**Consequences:** The demo breaks on unexpected input. The PNR regex `[A-Z0-9]{4,6}` already matches flight numbers and airport codes. During a live investor demo, a slightly different phrasing produces wrong classifications, and the presenter has to use the exact pre-tested sentence. Investors notice when the presenter types carefully from a script.

**Prevention:**
- Create a new structured endpoint: `POST /api/v2/process` accepting `{"pnr": "XKJR4T", "passenger_last_name": "MARTINEZ"}` -- this is a PNR lookup, not a natural-language problem
- Keep the old `/process` endpoint intact (do not break existing code), but the new React frontend should never use it
- The new endpoint should look up the PNR in the simulated data store, return the full reservation, then run the decision pipeline on structured data
- The UI drives the structure: PNR field + last name field, not a text area

**Detection:** If the React frontend ever passes a natural-language string to the backend, this pitfall was not avoided.

**Phase:** Phase 1 (API layer) -- the new endpoint must exist before the frontend can be built against it.

---

### Pitfall 4: Over-Engineering the Backend When the Demo Is the Frontend

**What goes wrong:** The team spends weeks adding PostgreSQL, proper auth, rate limiting, RBAC, and CI/CD to the backend -- all real concerns from CONCERNS.md -- while the frontend remains a basic form. The investor never sees the backend infrastructure. They see screens.

**Why it happens:** The CONCERNS.md file (correctly) identifies serious backend issues: no database, no auth, race conditions, no tests. Engineering instinct says "fix the foundation first." But an investor demo is not a production system. SQLite is sufficient. Auth is explicitly out of scope. The race condition on file writes does not manifest in a single-user demo.

**Consequences:** The demo date arrives with a solid backend and an unfinished UI. The founder cannot show investors anything impressive because the visible product is incomplete.

**Prevention:**
- Scope backend changes to exactly what the demo needs: (1) simulated data store (SQLite), (2) structured PNR lookup endpoint, (3) decision pipeline fed by structured data. Nothing else.
- Do NOT add auth, rate limiting, or production deployment infrastructure in this milestone
- Do NOT migrate the existing decision log from JSON to a database unless the KPI dashboard specifically needs it (it does -- but keep it to SQLite, not PostgreSQL)
- Every backend task should answer: "Does this make a visible difference in the demo?" If no, defer it.

**Detection:** If any PR in this milestone adds auth middleware, Dockerfile, or CI/CD pipeline, the team has drifted from the investor demo goal.

**Phase:** All phases -- this is a discipline issue that must be enforced throughout.

---

### Pitfall 5: Dark Theme That Looks Unreadable or Inconsistent

**What goes wrong:** Dark themes have specific readability constraints that light themes do not. Text on dark backgrounds needs carefully managed contrast ratios. Teal (#2ABFBF) on dark gray can either look stunning or completely unreadable depending on the exact background shade. Charts and data tables become especially problematic: alternating row colors, axis labels, gridlines, and data point colors all need re-evaluation for dark backgrounds.

**Why it happens:** Developers pick a dark background color, set text to white, apply the brand teal accent, and call it done. The result is inconsistent contrast, some elements too dim, others too harsh, and charts that worked in light mode becoming illegible.

**Consequences:** The investor cannot read key information on screen. The demo looks amateur despite having good underlying functionality. Worse, inconsistent theming across pages (some properly dark, some with leftover light-theme elements) looks unfinished.

**Prevention:**
- Define the full dark palette upfront as CSS custom properties / Tailwind theme tokens: background shades (3-4 levels: surface, card, elevated, overlay), text colors (primary at 87% opacity, secondary at 60%, disabled at 38% -- Material Design dark theme ratios), the brand teal range (lighter variant for text on dark bg, standard for interactive elements, darker for hover states)
- Use WCAG AA minimum contrast (4.5:1 for text, 3:1 for large text and interactive elements). Test the teal accent against every background shade -- `#2ABFBF` on `#1a1a2e` passes AA, but on `#2d2d44` it may not
- Charts need explicit dark-mode color palettes: no white gridlines (use 15% opacity), no default tooltip styles (they often have white backgrounds), axis labels in secondary text color
- Build the theme system once in Phase 2 and enforce it with Tailwind/CSS variables so no component uses hardcoded colors

**Detection:** Screenshot every page and check contrast ratios with a browser dev tools audit. If any text element fails WCAG AA, the theme is broken.

**Phase:** Phase 2 (Frontend Shell) -- the design tokens must be established before any component is built. Retrofitting a dark theme onto components built without one is 3-5x more work.

---

## Moderate Pitfalls

### Pitfall 6: Mixing Spanish and English in the UI

**What goes wrong:** The existing backend returns messages in Spanish ("Cancelacion de vuelo por parte de la aerolinea," "APROBADO," "RECHAZADO," "Escalar el caso para revision manual"). The new React frontend will likely be designed in English for an investor audience. The result is a UI that switches languages unpredictably -- English labels with Spanish values, English headers with Spanish rule descriptions.

**Prevention:**
- Decide the demo language upfront: English for international investors, Spanish for LATAM-specific investors. Do not mix.
- If English: add an i18n mapping layer in the frontend that translates backend response strings. The backend stays in Spanish (avoid rewriting existing logic), but the UI presents everything in English.
- If Spanish: ensure ALL UI chrome (buttons, labels, headers, tooltips) is also in Spanish. No "Submit" buttons next to "Estado: APROBADO."
- Status values ("APROBADO"/"RECHAZADO") should be mapped to localized display values in the frontend, not displayed raw from the API.

**Detection:** Read every visible string in the demo screenshots. If you find both languages on the same screen, this pitfall was hit.

**Phase:** Phase 2 (Frontend Shell) -- the translation layer should be part of the API response transformation, not sprinkled into individual components.

---

### Pitfall 7: KPI Dashboard with Empty or Meaningless Metrics

**What goes wrong:** The KPI dashboard shows "Total Requests: 3" and "Average Processing Time: 12ms" because the demo data store has only a few pre-seeded decisions. The charts show a single spike on one day and flatlines everywhere else. The dashboard, intended to show aggregate value, instead communicates "nobody uses this."

**Prevention:**
- Pre-seed the decision log with 200-500 realistic historical entries spread across 14-30 days, with realistic variation: weekday peaks, occasional manual escalations, processing times between 5ms-150ms (not uniformly fast)
- The KPI dashboard must show: (1) automation rate (% of decisions made without manual escalation -- target: show 85-92%), (2) processing time trend (show improvement over time), (3) volume handled per day, (4) top triggered rules
- Use a seed script that generates this data with intentional patterns an investor can see: "automation rate improved from 78% to 91% as more rules were configured"
- Never show real-time-only metrics in the demo. Pre-populate enough history that charts have visual substance.

**Detection:** If any chart on the KPI page has fewer than 10 data points, or if the "total decisions" number is under 50, the seed data is insufficient.

**Phase:** Phase 1 (Data Layer) -- the seed script must populate both PNR data and historical decision logs.

---

### Pitfall 8: React/FastAPI Integration Assuming Same-Origin

**What goes wrong:** During development, Next.js runs on port 3000 and FastAPI on port 8000. CORS issues appear immediately. The existing CORS config is `allow_origins=["*"]` which works but masks the real problem: in a deployed demo (even on a single machine), the frontend and backend may be served from different origins, and cookies/credentials will not work as expected.

**Prevention:**
- Use Next.js API routes as a proxy during development: `/api/axiom/*` routes in Next.js forward to `localhost:8000`. The React frontend never calls FastAPI directly. This eliminates CORS entirely for the client.
- For the deployed demo, either serve both from the same origin (Next.js proxies to FastAPI) or configure CORS with the specific frontend origin, not wildcard
- Do NOT rely on `allow_credentials=True` with wildcard origins -- browsers will reject this per the CORS spec
- Test the full integration with both servers running early in development, not at the end

**Detection:** If the browser console shows any CORS error during development, the integration strategy is wrong.

**Phase:** Phase 2 (Frontend Shell) -- the proxy configuration should be in the Next.js config from day one.

---

### Pitfall 9: Airline Domain Vocabulary Errors in the UI

**What goes wrong:** The UI uses incorrect airline terminology. Common mistakes: "booking" instead of "reservation" or "PNR," "rebooking" instead of "reprotection," "rules" without specifying "fare rules" vs "business rules" vs "operational rules," "ticket" when meaning "reservation" (they are different things in GDS systems). An investor with airline industry knowledge (the target buyer) loses confidence when the product's vocabulary is wrong.

**Prevention:**
- Establish a glossary before building UI copy:
  - **PNR** (Passenger Name Record): the reservation locator, always 6 alphanumeric characters
  - **Reprotection**: rebooking a passenger on an alternative flight due to involuntary change (not "rebooking" which implies voluntary)
  - **Involuntary change**: airline-initiated schedule change, cancellation, or significant delay (not passenger-initiated)
  - **Fare protection**: maintaining the original fare basis when reprotecting (the passenger should not pay more)
  - **SSR** (Special Service Request): accessibility needs, medical requirements, unaccompanied minors
  - **EMD** (Electronic Miscellaneous Document): vouchers, excess baggage, ancillaries
  - **Fare basis code**: the alphanumeric code defining fare rules (e.g., YOWCO, not "ticket class")
  - **Booking class**: the single letter (Y, B, M, H, Q, etc.) indicating inventory bucket
- Have the founder (Daniela, with operational experience) review all UI copy before the demo

**Detection:** Show the UI to an airline operations professional. If they correct your terminology, this pitfall was hit.

**Phase:** Phase 2 (Frontend Shell) and Phase 3 (Core Features) -- terminology must be correct from the first component.

---

### Pitfall 10: Decision Audit Trail That Is Not Visually Traceable

**What goes wrong:** The decision pipeline has 6 steps (INPUT -> VALIDATION -> CLASSIFICATION -> RULES -> OPTIONS -> ACTION) but the UI shows only the final result. The investor cannot see the reasoning. The current `audit_trace` is a list of raw strings like `"flight_cancelled=True"` and `"same_airline=True"` -- useful for debugging, not for demonstrating to an investor.

**Prevention:**
- Build a visual decision pipeline component: 6 connected steps shown as a horizontal stepper or vertical timeline. Each step shows its status (pass/fail/warning), the key data point, and when clicked/hovered, the full detail.
- The rule evaluation step should show each of the 5 checks individually with pass/fail indicators: "Flight cancelled: YES," "Same airline: YES," "Same route: YES," "No sensitive SSR: YES," "Same fare class: YES" -> "Result: APPROVED for reprotection"
- This is the product's core value proposition -- making the decision logic transparent. If the investor cannot see the reasoning chain, the demo fails to communicate the product's purpose.
- Format the audit trail for human consumption, not as raw key=value pairs. Transform `flight_cancelled=True` into a labeled card with an icon.

**Detection:** If explaining the decision logic requires the presenter to point at raw text instead of a visual component, the audit trail is not properly rendered.

**Phase:** Phase 3 (Core Features) -- this is the most important UI component in the entire demo.

---

## Minor Pitfalls

### Pitfall 11: Next.js App Router vs Pages Router Choice Causing Confusion

**What goes wrong:** Next.js has two routing paradigms (App Router with RSC, and the legacy Pages Router). Mixing them or choosing App Router without understanding its constraints (server components cannot use hooks, client components need `"use client"` directive, data fetching patterns differ completely) leads to confusing errors and inconsistent patterns.

**Prevention:** Use App Router (it is the standard for new projects) but establish clear conventions: pages are server components that fetch data, interactive elements are client components in a `components/` directory with explicit `"use client"` directives. Do not mix paradigms.

**Phase:** Phase 2 (Frontend Shell) -- the routing architecture is decided at project creation.

---

### Pitfall 12: Chart Library That Does Not Support Dark Theme Natively

**What goes wrong:** The team picks a chart library (Chart.js, Recharts, Victory) and discovers that dark theme support requires manual override of every color, tooltip, legend, and axis style. The charts end up with white backgrounds floating inside a dark dashboard, or invisible gridlines, or unreadable legends.

**Prevention:** Use Recharts (best React integration, supports custom themes via CSS variables and component props) or Nivo (built-in dark theme support, visually polished). Avoid Chart.js for React projects -- the react-chartjs-2 wrapper adds complexity without benefit. Configure chart theme tokens alongside the main dark theme in Phase 2.

**Phase:** Phase 2 (Frontend Shell) -- chart library choice is made when setting up the project.

---

### Pitfall 13: Not Having a Demo Reset Mechanism

**What goes wrong:** The founder demos the product to Investor A, processes several PNRs, modifies some rules. When demoing to Investor B the next day, the data store is in a dirty state -- KPI metrics reflect test data from the previous demo, the decision log has test entries, and the carefully crafted scenarios no longer produce the expected results because rules were changed.

**Prevention:**
- Build a seed/reset script: `python scripts/seed_demo.py` that drops and recreates the SQLite database with pristine demo data. This should take under 5 seconds.
- Optionally, add a hidden `/api/admin/reset` endpoint (removed before any real deployment) that triggers the same reset from the UI.
- Document the demo setup: "Before each investor meeting, run the reset script."

**Detection:** If the second demo does not produce identical results to the first, the reset mechanism is missing.

**Phase:** Phase 1 (Data Layer) -- the seed script should be built alongside the data store.

---

### Pitfall 14: Slow Initial Page Load Killing the Demo Impression

**What goes wrong:** Next.js cold starts can be slow in development mode. The first page load takes 3-5 seconds, showing a blank screen or loading spinner. In a live demo, this dead air is awkward and undermines the "instant automation" narrative.

**Prevention:**
- Run the demo from a production build (`next build && next start`), never `next dev`
- Pre-render the landing/main page as a static page where possible
- Ensure the API health check (`/health` or `/docs`) is hit before the demo starts so FastAPI's first-request overhead is absorbed
- Add a branded loading state (AXIOM logo + subtle animation) so even a 1-second load feels intentional, not broken

**Detection:** Time the cold start. If it exceeds 2 seconds to first meaningful content, optimize.

**Phase:** Phase 4 (Polish) -- optimization is final phase work, but the loading state should be designed in Phase 2.

---

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|---------------|------------|
| Data Layer (Phase 1) | Simulated PNRs missing critical fields (fare basis, booking class, segments) that the UI later needs | Define the full PNR data schema before writing the seed script. Include every field the UI will display, even if the decision engine does not use it yet. |
| Data Layer (Phase 1) | SQLite schema that mirrors the flat-file structure instead of being properly normalized | Design separate tables: `reservations`, `passengers`, `segments`, `flight_options`, `decision_log`, `rules`. The PNR is a reservation with multiple segments and passengers. |
| API Layer (Phase 1) | Breaking the existing `/process` endpoint while building the new structured one | Keep the old endpoint untouched. Add a new `/api/v2/` namespace. The React frontend uses only v2. The old Flutter dashboard (if anyone references it) still works. |
| Frontend Shell (Phase 2) | Choosing a component library that fights the dark theme (e.g., MUI defaults require extensive dark mode overrides) | Use shadcn/ui (headless, fully themeable, Tailwind-native) or Radix UI primitives. Avoid opinionated component libraries with built-in light themes. |
| Frontend Shell (Phase 2) | Building responsive layouts that break at presentation screen sizes (projectors are often 1024x768) | Test at both 1920x1080 (laptop) and 1280x720 (projector). The demo must look good on both. Design for 1280px minimum width. |
| Core Features (Phase 3) | Decision pipeline visualization that is technically accurate but visually boring (just a list of pass/fail text) | Design the pipeline as the hero component. Use progressive disclosure: summary view shows the 6-step pipeline with status icons, expanded view shows each rule check. Animation on state transitions makes it feel alive. |
| Core Features (Phase 3) | Flight option selection that does not feel like an operational tool (too much whitespace, no urgency indicators) | Airline ops tools are dense by design. Show departure time, arrival time, aircraft type, availability status, fare class, and a "Select" action in a compact card or table row. Do not use large spacious cards -- operators work with dense data. |
| KPI Dashboard (Phase 3) | Charts that all look the same (all line charts or all bar charts) | Mix chart types: area chart for volume over time, donut/pie for automation rate, horizontal bar for top rules triggered, sparkline for latency trend. Visual variety keeps the dashboard interesting. |
| Polish (Phase 4) | Spending too long on micro-animations while core flows have bugs | Polish means: consistent spacing, correct typography hierarchy, loading/error/empty states for every component. It does not mean: parallax effects, complex page transitions, or custom SVG animations. |
| Polish (Phase 4) | The demo works perfectly on the developer's machine and breaks on the founder's laptop | Build a `docker-compose.yml` for the demo that runs both Next.js (production build) and FastAPI behind a single port. One command to start the entire demo: `docker compose up`. Test on a clean machine. |

---

## Codebase-Specific Warnings

These pitfalls are specific to extending the existing AXIOM codebase.

| Current Code Issue | Pitfall If Not Addressed | When to Fix |
|---|---|---|
| `options_generator.py` returns hardcoded LATAM flights | New frontend built around 3 static flights; adding dynamic options later requires UI restructuring | Phase 1 -- replace with data-store-driven options before any frontend work |
| `classify_event()` always returns `"date": "unknown"` | UI date fields are permanently empty; investors notice | Phase 1 -- structured PNR data includes flight dates; bypass the classifier for structured input |
| `validate_problem()` PNR regex matches flight numbers | If the new structured endpoint still calls the old validator, structured PNR input gets re-parsed and potentially mismatched | Phase 1 -- new endpoint should not call `validate_problem()` at all; it receives validated structured data |
| Dual rule engine with silent fallback | Demo behavior is unpredictable: sometimes CSV rules run, sometimes Python rules run, with no visible difference | Phase 1 -- set a fixed engine mode for the demo; disable fallback or make it explicit in the API response |
| Spanish-language response strings baked into `decision_core.py`, `event_classifier.py`, `rule_engine_db.py` | Frontend displays untranslated Spanish strings next to English UI labels | Phase 2 -- add a response transformation layer in the frontend API client |
| `append_decision_log()` has no request ID | KPI dashboard cannot link a metric back to a specific decision | Phase 1 -- add `request_id` (UUID) to log entries and API responses |

---

## Investor Demo Anti-Patterns

| Anti-Pattern | Why It Fails | What to Do Instead |
|-------------|-------------|-------------------|
| "It can do everything" | Investors sense vaporware | "It solves involuntary change reprotection -- here, watch it work" |
| Empty state on first load | Communicates "nobody uses this" | Pre-seeded with 30 days of realistic decision history |
| Over-technical UI (JSON responses, debug traces) | Investor sees a developer tool, not a product | Operator-friendly language, visual pipeline, airline terminology |
| Slow or broken features shown anyway | One broken interaction kills confidence in all features | Fewer features that work flawlessly; hide anything incomplete |
| Generic SaaS dashboard template | Looks like every other startup demo | Branded, domain-specific, dense operational data layout |
| "Future roadmap" slides after demo | Implies the product does not work yet | Working demo that speaks for itself; roadmap is verbal only |
| Showing the rules management CRUD | Investors do not care about admin screens | Show the decision flow; mention rules are configurable |

---

## Sources

- Direct codebase analysis of `axiom/` directory (HIGH confidence -- primary evidence)
- Existing `.planning/codebase/CONCERNS.md` analysis (HIGH confidence -- verified against code)
- Existing `.planning/codebase/QUALITY.md` analysis (HIGH confidence -- verified against code)
- Airline domain knowledge: PNR format standards, IATA coding conventions, GDS data structures (MEDIUM confidence -- training data, not verified against current IATA specs)
- React/Next.js dark theme patterns and component library ecosystem (MEDIUM confidence -- training data, consistent with known ecosystem as of early 2025)
- Investor demo best practices (MEDIUM confidence -- training data from SaaS/startup domain)

---

*Pitfalls audit: 2026-03-30*
