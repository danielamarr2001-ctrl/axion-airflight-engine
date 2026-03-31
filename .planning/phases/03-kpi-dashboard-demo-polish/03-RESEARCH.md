# Phase 3: KPI Dashboard + Demo Polish - Research

**Researched:** 2026-03-30
**Domain:** Recharts charting in Next.js dark theme + investor-demo brand polish
**Confidence:** HIGH

## Summary

Phase 3 builds the KPI dashboard on a fully-prepared foundation. The backend `/api/metrics` endpoint already returns all required data: `total_decisions`, `automation_rate`, `avg_processing_time_ms`, `decisions_by_day` (with per-status breakdown), `top_rules`, and `decisions_by_status`. The seed script pre-populates 80-100 historical decisions across 14 days with realistic distributions (~87% APPROVED, ~8% ESCALATED, ~5% REJECTED). The frontend has Recharts 2.15.4 installed, TanStack Query configured with a `QueryProvider`, and a full dark theme with chart-specific CSS variables (`--color-chart-1` through `--color-chart-5`) already defined in `globals.css`.

The primary work is: (1) add a `fetchMetrics` function to `api.ts`, (2) add a `MetricsResponse` TypeScript type to `types.ts`, (3) install the shadcn/ui chart component (or build chart wrappers directly with Recharts v2), (4) replace the placeholder `metrics/page.tsx` with stat cards + line chart + bar chart, (5) wire `useQuery` with a short `refetchInterval` so KPIs update after new decisions, and (6) do a brand polish pass across the entire app.

**Primary recommendation:** Use Recharts v2 directly with the project's existing CSS variables for chart colors. Do NOT upgrade to Recharts v3 -- the v2 API is stable, the project already pins it, and the upgrade would introduce unnecessary risk. Build reusable chart wrapper components that read from the `--color-chart-*` CSS variables for consistent dark theme integration.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| KPI-01 | Dashboard shows automation rate (% auto-approved vs escalated) | Backend `automation_rate` field returns percentage 0-100; display as stat card with donut/radial indicator |
| KPI-02 | Dashboard shows average processing time | Backend `avg_processing_time_ms` field returns float; display as stat card with "ms" unit |
| KPI-03 | Dashboard shows decisions-per-day trend chart (last 14 days) | Backend `decisions_by_day` returns `[{date, count, approved, escalated, rejected}]`; use AreaChart or LineChart |
| KPI-04 | Dashboard shows top triggered rules as bar chart | Backend `top_rules` returns `[{rule, count}]` up to 10; use horizontal BarChart |
| KPI-05 | All KPI metrics update after new decisions | TanStack Query `useQuery` with `refetchInterval: 30000` (30s) or invalidation on decision creation |
| UI-07 | Professional investor-demo quality polish | Brand consistency pass: typography, spacing, hover states, loading states, empty states, animation polish |
</phase_requirements>

## Standard Stack

### Core (Already Installed)

| Library | Version | Purpose | Status |
|---------|---------|---------|--------|
| Recharts | 2.15.4 | SVG-based composable charts (line, bar, area, pie) | Installed in `package.json` |
| TanStack Query | 5.95.2 | Server state, caching, auto-refetch for live KPIs | Installed, `QueryProvider` configured |
| shadcn/ui | latest | Card, Badge, Skeleton, Tooltip components | 13 components already installed |
| Tailwind CSS | 4.x | Dark theme via `@theme inline` CSS variables | Configured with AXIOM palette |
| Lucide React | 0.469.0 | Icons for stat cards and UI elements | Installed |

### To Add

| Library | Purpose | How to Add |
|---------|---------|------------|
| shadcn/ui `chart` component | Optional: provides `ChartContainer`, `ChartTooltip`, `ChartTooltipContent` wrappers around Recharts | `pnpm dlx shadcn@latest add chart` |

**Note on Recharts version:** The project pins `"recharts": "^2.15.3"` (installed: 2.15.4). The latest shadcn/ui chart component targets Recharts v3.x. Two valid approaches:

1. **Recommended: Use Recharts v2 directly** -- Build chart components using standard Recharts v2 `<ResponsiveContainer>`, `<BarChart>`, `<LineChart>`, `<AreaChart>` with inline color props referencing CSS variables via `getComputedStyle`. This avoids any version mismatch risk.
2. **Alternative: Install shadcn chart component** -- Run `shadcn add chart` which may try to upgrade recharts to v3. If so, the upgrade is acceptable (v3 is backward-compatible for basic chart types) but adds migration overhead.

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Recharts v2 direct | shadcn/ui chart wrapper (v3) | Prettier tooltips but requires recharts upgrade |
| `refetchInterval` | Query invalidation via `queryClient.invalidateQueries` | More precise but requires cross-component coordination |
| Static CSS variable reading | Runtime `getComputedStyle()` for chart colors | CSS variables in oklch format may need conversion for Recharts |

## Architecture Patterns

### Recommended Project Structure (New Files)

```
axiom-ui/src/
  app/metrics/
    page.tsx                 # Server component wrapper (or "use client" with useQuery)
  components/metrics/
    stat-card.tsx            # Reusable KPI stat card (value + label + icon + trend)
    decisions-trend-chart.tsx # Area/Line chart: decisions per day over 14 days
    top-rules-chart.tsx      # Horizontal bar chart: top triggered rules
    automation-rate-card.tsx  # Stat card with visual indicator for automation %
    processing-time-card.tsx  # Stat card for avg processing time
    status-breakdown.tsx     # Small donut or grouped display for APPROVED/ESCALATED/REJECTED
  lib/
    api.ts                   # Add: fetchMetrics()
    types.ts                 # Add: MetricsResponse type
```

### Pattern 1: Metrics Data Fetching with useQuery

**What:** Use `useQuery` (not `useMutation`) since metrics is a GET endpoint that returns read-only aggregate data. Set `refetchInterval` for live updating.

**When to use:** Dashboard pages that show aggregate data and need periodic refresh.

**Example:**
```typescript
// In metrics/page.tsx (must be "use client" for useQuery)
"use client";
import { useQuery } from "@tanstack/react-query";
import { fetchMetrics } from "@/lib/api";
import type { MetricsResponse } from "@/lib/types";

export default function MetricsPage() {
  const { data, isLoading, error } = useQuery<MetricsResponse>({
    queryKey: ["metrics"],
    queryFn: fetchMetrics,
    refetchInterval: 30_000, // Refresh every 30 seconds
  });

  if (isLoading) return <MetricsSkeleton />;
  if (error || !data) return <MetricsError />;

  return (
    <div className="space-y-6">
      {/* Stat cards row */}
      {/* Charts grid */}
    </div>
  );
}
```

**Note:** The processor page uses `useMutation` for POST requests. Metrics is different -- it's a pure data fetch with no side effects.

### Pattern 2: Chart Color Strategy for Dark Theme

**What:** The AXIOM theme defines 5 chart colors as oklch CSS variables. Recharts v2 accepts string color values (hex, rgb, hsl, oklch) for `fill`, `stroke`, and similar props.

**Critical detail:** Recharts v2 `fill` and `stroke` props accept CSS color strings directly. For CSS variables, you can either:

1. Reference them via `var(--color-chart-1)` in inline style objects (works in SVG)
2. Use the computed hex/rgb value at runtime

**Existing chart CSS variables (from globals.css):**
```css
--color-chart-1: oklch(0.72 0.15 185);  /* Teal/primary -- AXIOM brand */
--color-chart-2: oklch(0.65 0.15 250);  /* Blue/purple */
--color-chart-3: oklch(0.7 0.15 145);   /* Green */
--color-chart-4: oklch(0.7 0.15 55);    /* Amber/yellow */
--color-chart-5: oklch(0.65 0.15 310);  /* Purple/magenta */
```

**Approach:** Define chart colors as a constant map in the chart component:

```typescript
const CHART_COLORS = {
  primary: "var(--color-chart-1)",   // Teal -- approved, main trend
  secondary: "var(--color-chart-2)", // Blue -- secondary series
  success: "var(--color-chart-3)",   // Green -- confirmed
  warning: "var(--color-chart-4)",   // Amber -- escalated
  accent: "var(--color-chart-5)",    // Purple -- tertiary
  destructive: "var(--color-destructive)", // Red -- rejected
};
```

### Pattern 3: Stat Card Component

**What:** A reusable card showing a single KPI metric with title, value, optional unit, optional trend indicator, and icon.

**Example:**
```typescript
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { LucideIcon } from "lucide-react";

interface StatCardProps {
  title: string;
  value: string | number;
  unit?: string;
  icon: LucideIcon;
  description?: string;
}

export function StatCard({ title, value, unit, icon: Icon, description }: StatCardProps) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">{title}</CardTitle>
        <Icon className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">
          {value}{unit && <span className="text-lg font-normal text-muted-foreground ml-1">{unit}</span>}
        </div>
        {description && (
          <p className="text-xs text-muted-foreground mt-1">{description}</p>
        )}
      </CardContent>
    </Card>
  );
}
```

### Pattern 4: Dashboard Layout Grid

**What:** Stat cards in a responsive row (4 columns on desktop), charts in a 2-column grid below.

```typescript
{/* Stat cards row */}
<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
  <StatCard ... />  {/* Total Decisions */}
  <StatCard ... />  {/* Automation Rate */}
  <StatCard ... />  {/* Avg Processing Time */}
  <StatCard ... />  {/* Decisions Today */}
</div>

{/* Charts grid */}
<div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
  <Card>{/* Decisions per day trend -- AreaChart */}</Card>
  <Card>{/* Top rules -- horizontal BarChart */}</Card>
</div>

{/* Full-width status breakdown */}
<Card>{/* Status distribution: APPROVED / ESCALATED / REJECTED */}</Card>
```

### Anti-Patterns to Avoid

- **Do NOT use `ResponsiveContainer` with 0 height:** Always set `height` or `min-h-*` on the chart container. Recharts `ResponsiveContainer` collapses to 0px height without an explicit height on the parent.
- **Do NOT hardcode colors:** Always use CSS variables or the CHART_COLORS constant. Hardcoded hex values break theme consistency.
- **Do NOT use `useMutation` for GET data:** The metrics endpoint is a read operation. Use `useQuery` with `refetchInterval`, not `useMutation`.
- **Do NOT show raw rule names:** The backend returns `rule_applied` values like `"involuntary_change"`, `"fare_protection"`, `"ssr_check"`, `"delay_rule"`. These must be humanized in the UI (e.g., "Involuntary Change", "Fare Protection", "SSR Check", "Delay Rule").

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Chart tooltips | Custom tooltip div with positioning math | Recharts `<Tooltip>` with `contentStyle` for dark bg | Tooltip positioning, scroll handling, overflow clipping are hard |
| Responsive charts | Manual resize observers | Recharts `<ResponsiveContainer>` | Handles resize, debounce, SSR hydration edge cases |
| Number formatting | Manual string templates | `Intl.NumberFormat` or `toLocaleString()` | Handles decimals, thousands separators, locale |
| Date formatting for chart axis | Manual `date.split('-')` | `new Date(dateStr).toLocaleDateString('en', { month: 'short', day: 'numeric' })` | Handles locale, timezone edge cases |
| Loading skeletons for charts | Empty divs with bg color | shadcn `<Skeleton>` component (already installed) | Consistent with rest of UI, animated pulse |

## Common Pitfalls

### Pitfall 1: Recharts ResponsiveContainer Collapses to Zero Height

**What goes wrong:** Charts render as invisible because `ResponsiveContainer` has no height constraint. The parent div has no explicit height, so Recharts computes 0px.

**Why it happens:** Recharts `ResponsiveContainer` requires its parent to have a defined height. CSS `height: auto` or flexbox without constraints does not provide this.

**How to avoid:** Always wrap charts in a div with explicit height:
```typescript
<div className="h-[300px] w-full">
  <ResponsiveContainer width="100%" height="100%">
    <AreaChart data={data}>...</AreaChart>
  </ResponsiveContainer>
</div>
```

Or use the shadcn `ChartContainer` which handles this with `min-h-*` and `aspect-*` classes.

**Warning signs:** Chart area renders but no visual elements appear. Inspect element shows 0px height on the SVG container.

### Pitfall 2: oklch CSS Variables Not Rendering in Recharts SVG

**What goes wrong:** `var(--color-chart-1)` with oklch values may not render correctly in SVG `fill` attributes in older browsers. SVG inline styles handle CSS variables, but SVG attributes (used by Recharts internally) may not resolve them in all cases.

**Why it happens:** Recharts applies colors as SVG attributes (`fill`, `stroke`), not CSS properties. CSS variable resolution in SVG attributes depends on browser support.

**How to avoid:** Test in target browser (Chrome). If oklch variables do not resolve in SVG:
- Option A: Define chart colors as hex constants alongside the CSS variables
- Option B: Use `style={{ fill: 'var(--color-chart-1)' }}` instead of `fill="var(--color-chart-1)"` (CSS property vs SVG attribute)
- Option C: Read computed values at runtime with `getComputedStyle()`

**Warning signs:** Charts render with black/default fills instead of theme colors.

### Pitfall 3: Empty Metrics on First Load Before Seed Data

**What goes wrong:** The metrics endpoint returns `{ total_decisions: 0, automation_rate: 0.0, ... }` when no decisions exist. The dashboard shows "0%" and empty charts, communicating "nobody uses this."

**Why it happens:** Developer forgets to run `python -m axiom.db.seed` before testing the dashboard.

**How to avoid:**
- The seed script already creates 80-100 decisions. Document that `python -m axiom.db.seed` must run before dashboard development/testing.
- Handle the zero-data case gracefully: show "No decisions recorded yet" message instead of broken charts with zero values.
- In the plan, ensure seed data step is a prerequisite for dashboard testing.

**Warning signs:** Automation rate shows "0%" with empty trend chart.

### Pitfall 4: Chart Tooltip White Background in Dark Theme

**What goes wrong:** Recharts default tooltip has a white background. On a dark dashboard, this creates a jarring flash of white.

**Why it happens:** Recharts `<Tooltip>` defaults to `{ backgroundColor: '#fff', border: '1px solid #ccc' }`.

**How to avoid:** Always override tooltip styles:
```typescript
<Tooltip
  contentStyle={{
    backgroundColor: 'var(--color-card)',
    borderColor: 'var(--color-border)',
    borderRadius: 'var(--radius-md)',
    color: 'var(--color-foreground)',
  }}
  labelStyle={{ color: 'var(--color-muted-foreground)' }}
/>
```

Or use the shadcn `ChartTooltip` + `ChartTooltipContent` which handles dark theme automatically.

### Pitfall 5: date Strings from Backend Misaligned with Chart Axis

**What goes wrong:** The backend returns `decisions_by_day[].date` as ISO date strings like `"2026-04-01"`. If the frontend parses these naively with `new Date("2026-04-01")`, timezone differences can shift dates by one day. The chart shows "Mar 31" instead of "Apr 1".

**Why it happens:** `new Date("2026-04-01")` creates a UTC date. `toLocaleDateString()` converts to local timezone, which can shift the date back one day in negative UTC offsets.

**How to avoid:** Parse date strings manually or use `new Date(dateStr + "T12:00:00")` to avoid midnight-edge timezone issues. Or simply split the date string and format directly:
```typescript
function formatChartDate(dateStr: string): string {
  const [, month, day] = dateStr.split("-");
  const months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
  return `${months[parseInt(month, 10) - 1]} ${parseInt(day, 10)}`;
}
```

## Code Examples

### MetricsResponse TypeScript Type (matches backend schema exactly)

```typescript
// Add to axiom-ui/src/lib/types.ts

export interface DailyDecisions {
  date: string;       // "2026-04-01" ISO date
  count: number;      // total decisions that day
  approved: number;
  escalated: number;
  rejected: number;
}

export interface RuleCount {
  rule: string;       // rule_applied value e.g. "involuntary_change"
  count: number;
}

export interface MetricsResponse {
  total_decisions: number;
  automation_rate: number;           // 0-100 percentage
  avg_processing_time_ms: number;
  decisions_by_day: DailyDecisions[];
  top_rules: RuleCount[];
  decisions_by_status: {
    APPROVED: number;
    REJECTED: number;
    ESCALATED: number;
  };
}
```

### fetchMetrics API Function

```typescript
// Add to axiom-ui/src/lib/api.ts

export function fetchMetrics() {
  return apiFetch<MetricsResponse>("/metrics");
}
```

### Decisions Trend AreaChart (Recharts v2)

```typescript
"use client";

import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface Props {
  data: Array<{
    date: string;
    approved: number;
    escalated: number;
    rejected: number;
  }>;
}

export function DecisionsTrendChart({ data }: Props) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Decisions per Day</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-[300px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data}>
              <CartesianGrid
                strokeDasharray="3 3"
                stroke="var(--color-border)"
                opacity={0.3}
              />
              <XAxis
                dataKey="date"
                tickFormatter={(v) => formatChartDate(v)}
                tick={{ fill: "var(--color-muted-foreground)", fontSize: 12 }}
                axisLine={{ stroke: "var(--color-border)" }}
                tickLine={false}
              />
              <YAxis
                tick={{ fill: "var(--color-muted-foreground)", fontSize: 12 }}
                axisLine={false}
                tickLine={false}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "var(--color-card)",
                  borderColor: "var(--color-border)",
                  borderRadius: "var(--radius-md)",
                  color: "var(--color-foreground)",
                }}
              />
              <Area
                type="monotone"
                dataKey="approved"
                stackId="1"
                stroke="var(--color-chart-1)"
                fill="var(--color-chart-1)"
                fillOpacity={0.4}
                name="Approved"
              />
              <Area
                type="monotone"
                dataKey="escalated"
                stackId="1"
                stroke="var(--color-chart-4)"
                fill="var(--color-chart-4)"
                fillOpacity={0.4}
                name="Escalated"
              />
              <Area
                type="monotone"
                dataKey="rejected"
                stackId="1"
                stroke="var(--color-destructive)"
                fill="var(--color-destructive)"
                fillOpacity={0.4}
                name="Rejected"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}
```

### Top Rules Horizontal BarChart (Recharts v2)

```typescript
"use client";

import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface Props {
  data: Array<{ rule: string; count: number }>;
}

function humanizeRuleName(rule: string): string {
  return rule.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

export function TopRulesChart({ data }: Props) {
  const formatted = data.map((d) => ({
    ...d,
    label: humanizeRuleName(d.rule),
  }));

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Top Triggered Rules</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-[300px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={formatted} layout="vertical">
              <CartesianGrid
                strokeDasharray="3 3"
                stroke="var(--color-border)"
                opacity={0.3}
                horizontal={false}
              />
              <XAxis
                type="number"
                tick={{ fill: "var(--color-muted-foreground)", fontSize: 12 }}
                axisLine={false}
                tickLine={false}
              />
              <YAxis
                type="category"
                dataKey="label"
                width={140}
                tick={{ fill: "var(--color-muted-foreground)", fontSize: 12 }}
                axisLine={false}
                tickLine={false}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "var(--color-card)",
                  borderColor: "var(--color-border)",
                  borderRadius: "var(--radius-md)",
                  color: "var(--color-foreground)",
                }}
              />
              <Bar
                dataKey="count"
                fill="var(--color-chart-2)"
                radius={[0, 4, 4, 0]}
                name="Decisions"
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}
```

### Rule Name Humanization Mapping

```typescript
// For consistent display across the dashboard
const RULE_LABELS: Record<string, string> = {
  involuntary_change: "Involuntary Change",
  fare_protection: "Fare Protection",
  ssr_check: "SSR Check",
  delay_rule: "Delay Rule",
};

export function humanizeRuleName(rule: string): string {
  return RULE_LABELS[rule] ?? rule.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}
```

## Backend Data Shape Reference

The `/api/metrics` endpoint (already implemented) returns exactly this shape:

```json
{
  "total_decisions": 87,
  "automation_rate": 87.4,
  "avg_processing_time_ms": 42.3,
  "decisions_by_day": [
    {"date": "2026-04-01", "count": 8, "approved": 7, "escalated": 1, "rejected": 0},
    {"date": "2026-04-02", "count": 6, "approved": 5, "escalated": 0, "rejected": 1},
    ...
  ],
  "top_rules": [
    {"rule": "involuntary_change", "count": 52},
    {"rule": "fare_protection", "count": 18},
    {"rule": "ssr_check", "count": 9},
    {"rule": "delay_rule", "count": 8}
  ],
  "decisions_by_status": {
    "APPROVED": 76,
    "REJECTED": 4,
    "ESCALATED": 7
  }
}
```

**Seed data characteristics (from `seed.py`):**
- 80-100 decisions spread across April 1-14, 2026
- Weekday peaks (6-10/day), weekend dips (2-4/day)
- Status distribution: ~87% APPROVED, ~8% ESCALATED, ~5% REJECTED
- Processing times: 70% between 15-60ms, 30% between 8-120ms
- Four rule types with weighted distribution: involuntary_change (60%), fare_protection (20%), ssr_check (10%), delay_rule (10%)

This means the charts will show meaningful data patterns out of the box.

## Brand Polish Checklist (UI-07)

### What Already Exists (from Phase 1 and 2)

- Dark theme with AXIOM palette in CSS variables
- Sidebar navigation with brand logo
- shadcn/ui components with consistent Card, Badge, Table, Button styling
- Skeleton loading states for processor workflow
- Error states with Alert component
- `animate-in fade-in` transitions on dynamic content
- Badge variants for decision statuses (approved, rejected, escalated, confirmed, scheduled, cancelled)
- Translations layer for GDS codes to human-readable labels

### What Needs Polish Attention

| Area | Current State | Polish Target |
|------|---------------|---------------|
| Metrics page | Placeholder "Phase 3" text | Full KPI dashboard |
| Rules page | Placeholder "Phase 2" text | Either implement or show meaningful placeholder |
| Page transitions | `animate-in fade-in` on some elements | Consistent animation on all dynamic content |
| Typography hierarchy | h1 varies (`font-bold` vs `font-semibold`) | Consistent heading styles across all pages |
| Stat card hover | Not implemented | Subtle `hover:border-primary/50` on stat cards |
| Chart interactions | N/A | Tooltip on hover, smooth animation on data load |
| Empty states | Not all paths covered | All pages handle zero-data gracefully |
| Sidebar active state | Basic bg-accent highlight | Ensure sidebar "Metrics" link highlights correctly |
| Loading state for metrics | Not implemented | Skeleton grid matching stat card + chart layout |

### Brand Consistency Checks

1. **Primary color usage:** `oklch(0.72 0.15 185)` (teal) -- used for primary buttons, links, sidebar active, chart-1. Verify it appears on every page.
2. **Card backgrounds:** `oklch(0.18 0.02 260)` -- all Card components should use `bg-card` consistently.
3. **Border colors:** `oklch(0.28 0.02 260)` -- no hardcoded border colors.
4. **Text hierarchy:** Primary foreground `oklch(0.95 0.01 260)`, muted `oklch(0.6 0.01 260)`. No raw `text-white` or `text-gray-*`.
5. **Spacing:** `space-y-6` for page sections (already used consistently). `gap-4` for grid cards, `gap-6` for chart grid.
6. **Border radius:** Use `rounded-lg` (0.5rem) for cards. No `rounded-xl` or `rounded-full` unless for specific avatar/badge use cases.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Recharts v2 | Recharts v3 (March 2025) | v3.0.0 release | New API for labels, improved tree-shaking. Project uses v2 -- no need to upgrade for this phase. |
| Manual chart theming | shadcn/ui chart component | Mid-2024 | Provides `ChartContainer` + `ChartTooltip` wrappers. Optional for this project since v2 is already installed. |
| `staleTime` in minutes | `refetchInterval` for polling | TanStack Query v5 | Both work; `refetchInterval` is simpler for dashboard auto-refresh. |

## Open Questions

1. **Rules page placeholder:**
   - What we know: Rules page is still a placeholder from Phase 1. Phase 2 focused on processor workflow.
   - What's unclear: Should the rules page be implemented in Phase 3 as part of UI-07 polish, or remain as a placeholder?
   - Recommendation: Leave rules page as-is unless time permits. The investor demo narrative focuses on Processor -> Metrics flow. Rules management is explicitly called out in PITFALLS.md as an anti-pattern to show during demos ("Investors do not care about admin screens").

2. **Recharts CSS variable compatibility with oklch:**
   - What we know: Recharts v2 applies colors as SVG attributes. oklch is a newer color format.
   - What's unclear: Whether `var(--color-chart-1)` with oklch values resolves correctly in SVG `fill` attributes across all browsers.
   - Recommendation: Test early with a simple BarChart. If oklch does not resolve, define fallback hex constants for chart colors.

3. **KPI-05 refetch mechanism:**
   - What we know: TanStack Query supports `refetchInterval` for polling and `queryClient.invalidateQueries` for event-driven invalidation.
   - What's unclear: Whether the planner should wire up cross-page invalidation (processor creates decision -> metrics query invalidates).
   - Recommendation: Start with `refetchInterval: 30000` (30 seconds). Simple, no cross-component wiring needed. If the demo script involves checking metrics immediately after processing a PNR, reduce to 10 seconds or add a manual refresh button.

## Sources

### Primary (HIGH confidence)
- Direct codebase analysis: `axiom/services/metrics_service.py`, `axiom/models/schemas.py`, `axiom/db/seed.py`, `axiom-ui/src/app/globals.css`, `axiom-ui/package.json`
- [shadcn/ui Chart Documentation](https://ui.shadcn.com/docs/components/radix/chart) - Component API, theming, ChartConfig pattern
- [shadcn/ui Charts Gallery](https://ui.shadcn.com/charts/area) - Visual examples and code patterns

### Secondary (MEDIUM confidence)
- [Recharts v3 support issue](https://github.com/shadcn-ui/ui/issues/7669) - shadcn moving to Recharts v3
- [shadcn/ui chart discussion](https://github.com/shadcn-ui/ui/discussions/4133) - Community patterns for charts with shadcn
- npm registry: Recharts v2.15.4 (installed) vs v3.8.1 (latest)

### Tertiary (LOW confidence)
- oklch color support in SVG attributes -- needs runtime verification in target browser

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All libraries already installed, backend endpoint already implemented, data shape verified from source code
- Architecture: HIGH - Pattern follows existing project conventions (useQuery, shadcn Card, existing CSS variables)
- Pitfalls: HIGH - Chart-specific dark theme issues verified against Recharts documentation and existing codebase analysis
- Brand polish: MEDIUM - Checklist based on visual inspection of code, not rendered output

**Research date:** 2026-03-30
**Valid until:** 2026-04-30 (stable libraries, no anticipated breaking changes)
