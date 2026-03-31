---
phase: 03-kpi-dashboard-demo-polish
plan: 01
subsystem: ui
tags: [recharts, tanstack-query, dashboard, kpi, charts, metrics]

# Dependency graph
requires:
  - phase: 02-core-workflow
    provides: Decision records created via processor workflow that populate metrics
  - phase: 01-foundation
    provides: Backend /api/metrics endpoint, shadcn UI components, TanStack Query provider, CSS chart variables
provides:
  - MetricsResponse TypeScript types matching backend schema
  - fetchMetrics API function
  - StatCard reusable KPI component
  - DecisionsTrendChart stacked area chart (14-day decisions breakdown)
  - TopRulesChart horizontal bar chart with humanized rule names
  - MetricsSkeleton loading state
  - Complete KPI dashboard page with 30s auto-refresh
affects: [03-02-brand-polish]

# Tech tracking
tech-stack:
  added: []
  patterns: [recharts-v2-with-css-variables, useQuery-refetchInterval-polling, chart-date-string-splitting]

key-files:
  created:
    - axiom-ui/src/components/metrics/stat-card.tsx
    - axiom-ui/src/components/metrics/decisions-trend-chart.tsx
    - axiom-ui/src/components/metrics/top-rules-chart.tsx
    - axiom-ui/src/components/metrics/metrics-skeleton.tsx
  modified:
    - axiom-ui/src/lib/types.ts
    - axiom-ui/src/lib/api.ts
    - axiom-ui/src/app/metrics/page.tsx

key-decisions:
  - "Used Recharts v2 directly with var(--color-chart-*) CSS variables instead of upgrading to v3 or installing shadcn chart wrapper"
  - "Date formatting via string splitting (not new Date) to avoid timezone shift on chart axis labels"
  - "30-second refetchInterval for KPI auto-refresh (simple polling, no cross-component invalidation wiring)"

patterns-established:
  - "Chart color pattern: use var(--color-chart-N) and var(--color-destructive) CSS variables directly in Recharts stroke/fill props"
  - "Dark tooltip pattern: contentStyle with var(--color-card), var(--color-border), var(--color-foreground) for all chart tooltips"
  - "Chart container pattern: div with h-[300px] wrapping ResponsiveContainer to prevent zero-height collapse"
  - "Rule name humanization: replace(/_/g, ' ').replace(/\\b\\w/g, c => c.toUpperCase()) for snake_case to Title Case"

requirements-completed: [KPI-01, KPI-02, KPI-03, KPI-04, KPI-05]

# Metrics
duration: 6min
completed: 2026-03-31
---

# Phase 3 Plan 1: KPI Dashboard Summary

**Recharts v2 KPI dashboard with stat cards, stacked area trend chart, horizontal bar chart, skeleton loading, empty/error states, and 30s auto-refresh via TanStack Query**

## Performance

- **Duration:** 6 min
- **Started:** 2026-03-31T04:33:44Z
- **Completed:** 2026-03-31T04:40:00Z
- **Tasks:** 2
- **Files modified:** 7

## Accomplishments
- Full KPI dashboard replacing Phase 3 placeholder with 4 stat cards (total decisions, automation rate, avg processing time, recent day count)
- Stacked area chart showing 14 days of decisions with approved/escalated/rejected breakdown using oklch CSS variables
- Horizontal bar chart for top triggered rules with humanized snake_case-to-Title-Case labels
- Auto-refresh every 30 seconds via useQuery refetchInterval (KPI-05), skeleton loading state, empty state message, error Alert

## Task Commits

Each task was committed atomically:

1. **Task 1: Add MetricsResponse types, fetchMetrics API, and StatCard component** - `66549b8` (feat)
2. **Task 2: Build chart components and complete metrics page with useQuery auto-refresh** - `98e455c` (feat)

## Files Created/Modified
- `axiom-ui/src/lib/types.ts` - Added DailyDecisions, RuleCount, MetricsResponse interfaces
- `axiom-ui/src/lib/api.ts` - Added fetchMetrics() function using apiFetch<MetricsResponse>
- `axiom-ui/src/components/metrics/stat-card.tsx` - Reusable KPI stat card with icon, value, unit, description, hover state
- `axiom-ui/src/components/metrics/decisions-trend-chart.tsx` - Stacked AreaChart for decisions per day with chart-1/chart-4/destructive colors
- `axiom-ui/src/components/metrics/top-rules-chart.tsx` - Horizontal BarChart for top rules with chart-2 color and humanized labels
- `axiom-ui/src/components/metrics/metrics-skeleton.tsx` - Skeleton loading state matching 4-card + 2-chart grid layout
- `axiom-ui/src/app/metrics/page.tsx` - Complete dashboard page with useQuery, stat cards, charts, status distribution, loading/error/empty states

## Decisions Made
- Used Recharts v2 directly with CSS variable references rather than upgrading to v3 or installing the shadcn chart wrapper -- avoids version mismatch risk since project pins v2.15.3
- Implemented date formatting via string splitting (`dateStr.split("-")`) instead of `new Date()` to avoid timezone-shift issues on chart axis labels (per research pitfall 5)
- Used `refetchInterval: 30_000` for polling rather than event-driven query invalidation -- simpler, no cross-component wiring needed for investor demo

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None.

## Known Stubs
None - all components are fully wired to live data from the /api/metrics endpoint.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- KPI dashboard is fully functional and ready for brand polish (Plan 03-02)
- The metrics page renders real data when seed data exists (run `python -m axiom.db.seed` to populate)
- All chart colors use CSS variables, making brand polish adjustments straightforward

## Self-Check: PASSED

- All 7 created/modified files verified present on disk
- Commit 66549b8 (Task 1) verified in git log
- Commit 98e455c (Task 2) verified in git log
- TypeScript `tsc --noEmit` passes with zero errors
- `npm run build` succeeds with metrics page at 113 kB

---
*Phase: 03-kpi-dashboard-demo-polish*
*Completed: 2026-03-31*
