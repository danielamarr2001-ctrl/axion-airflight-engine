# Features Research: AXIOM AirFlight Engine

## Feature Landscape for Airline Involuntary Change Management

### Table Stakes (Must Have for Credible Investor Demo)

#### PNR Retrieval & Display
- **PNR + Last Name Lookup**: Structured input form (not text parsing) — **Complexity: LOW**
- **Reservation Summary**: Display passenger name, itinerary, ticket info, status — **Complexity: MEDIUM**
- **Flight Segment Display**: Show all segments with dates, routes, times, status — **Complexity: MEDIUM**
- **Passenger Details**: Name, ticket number, fare class, SSR indicators — **Complexity: LOW**

#### Decision Engine Core
- **Rule Evaluation Visualization**: Show which rules fired and why — **Complexity: MEDIUM**
- **Eligibility Assessment**: Clear APPROVED/REJECTED with justification — **Complexity: LOW** (exists)
- **Sequential Rule Trace**: Step-by-step audit trail of rule execution — **Complexity: MEDIUM** (partial)
- **Decision Status Indicators**: Visual status (approved, rejected, escalated, pending) — **Complexity: LOW**

#### Reprotection Options
- **Alternative Flight Options**: Display 2-5 alternatives with times, availability, fare impact — **Complexity: MEDIUM**
- **Option Comparison**: Side-by-side or card-based comparison view — **Complexity: MEDIUM**
- **Option Selection**: Click-to-select with confirmation flow — **Complexity: LOW**
- **Decision Recording**: Log selected option with timestamp, operator, justification — **Complexity: LOW**

#### KPI Dashboard
- **Total Decisions Count**: Running total with trend — **Complexity: LOW**
- **Automation Rate**: % decisions auto-approved vs escalated — **Complexity: LOW**
- **Average Processing Time**: Time from PNR input to decision — **Complexity: LOW**
- **Decisions Over Time**: Line/bar chart of daily volume — **Complexity: MEDIUM**
- **Top Triggered Rules**: Which rules fire most often — **Complexity: LOW** (exists)

#### UI/UX Essentials
- **Dark Theme**: Professional dark background with teal accents — **Complexity: MEDIUM**
- **Responsive Layout**: Works on desktop (primary), tablet (secondary) — **Complexity: MEDIUM**
- **Navigation Shell**: Sidebar or top nav between Processor/Rules/Metrics — **Complexity: LOW**
- **Loading States**: Skeleton screens, spinners for API calls — **Complexity: LOW**
- **Error States**: Graceful handling of invalid PNR, no results, API errors — **Complexity: LOW**

### Differentiators (Competitive Advantage / Wow Factor)

#### Decision Intelligence
- **Rule Impact Analysis**: Show what would change if a rule is modified — **Complexity: HIGH**
- **Decision Confidence Score**: Quantified confidence in automated decisions — **Complexity: MEDIUM**
- **Escalation Prediction**: Flag cases likely to need human review — **Complexity: HIGH**
- **Decision Replay**: Re-run a past decision with current rules — **Complexity: MEDIUM**

#### Advanced Visualization
- **Real-time Decision Feed**: Live ticker of decisions being made — **Complexity: MEDIUM**
- **Decision Flow Diagram**: Visual pipeline of INPUT→RULES→DECISION — **Complexity: HIGH**
- **Heatmap of Activity**: Time-of-day / day-of-week decision volume — **Complexity: MEDIUM**
- **Rule Network Graph**: Visual dependencies between rules — **Complexity: HIGH**

#### Operational Intelligence
- **Cost Savings Calculator**: Estimated $ saved by automation — **Complexity: MEDIUM**
- **SLA Monitoring**: Are decisions being made within target time? — **Complexity: MEDIUM**
- **Comparison: Manual vs Automated**: Side-by-side metrics — **Complexity: MEDIUM**

### Anti-Features (Do NOT Build in This Phase)

| Feature | Why NOT |
|---------|---------|
| Real GDS integration | Requires commercial agreements, certification, complex protocols |
| Multi-tenant / multi-airline | Adds architectural complexity without demo value |
| User authentication/RBAC | No multi-user demo needed for investors |
| Email/SMS notifications | Out of scope for decision engine demo |
| Actual ticket reissuance | Risk of real financial impact, simulated is sufficient |
| AI/ML-based predictions | Rule-based is the product — AI adds uncertainty investors may question |
| Mobile responsive (phone) | Desktop/tablet operators only |
| Localization/i18n | English + Spanish in code, no runtime switching needed |
| Payment processing | No financial transactions in demo |
| Report export (PDF/Excel) | Nice-to-have but not MVP |

## Feature Dependencies

```
PNR Lookup ──→ Reservation Display ──→ Rule Evaluation ──→ Options Generation
                                                              │
                                                              ▼
                                                     Option Selection ──→ Decision Record
                                                                              │
                                                                              ▼
                                                                     KPI Dashboard (reads)
```

- **KPI Dashboard** depends on decision records existing
- **Option Selection** depends on options generation
- **Rule Evaluation** depends on structured reservation data
- **Everything** depends on simulated data store being populated
