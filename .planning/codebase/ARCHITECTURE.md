# Architecture

**Analysis Date:** 2026-03-30

## Pattern Overview

**Overall:** Pipeline / Chain-of-Responsibility with dual rule engine strategy

**Key Characteristics:**
- Linear, ordered processing pipeline: each stage receives the output of the previous stage
- Two pluggable rule engine implementations (Python hard-coded rules vs. CSV table-based rules), selected at startup via environment variable
- Stateless API layer — all processing context is constructed fresh per request; the only persistent state is the append-only JSON decision log and the CSV rule store
- Thin orchestrator (`DecisionCore`) that owns the pipeline and delegates every stage to a focused module
- Symmetric data contracts: Pydantic models on the Python side, plain Dart classes on the Flutter side, mirroring the same shape

---

## Component Diagram

```
┌────────────────────────────────────────────────────────────────────┐
│  axiom_dashboard  (Flutter Web)                                    │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐              │
│  │ DashboardPage│  │  RulesPage  │  │  MetricsPage │              │
│  └──────┬──────┘  └──────┬──────┘  └──────┬───────┘              │
│         └────────────────┴─────────────────┘                       │
│                          │                                          │
│                   AxiomApiService                                  │
│          (http calls to http://127.0.0.1:8000)                    │
└──────────────────────────┼─────────────────────────────────────────┘
                           │ HTTP/JSON
┌──────────────────────────▼─────────────────────────────────────────┐
│  axiom/api/main.py  (FastAPI)                                      │
│  POST /process  GET/POST/PUT/DELETE /rules  GET /metrics           │
└──┬──────────────────────────────┬─────────────────────────────────┘
   │                              │
   │                   ┌──────────▼────────────┐
   │                   │  RuleRepository       │
   │                   │  (CRUD on rules.csv)  │
   │                   └──────────┬────────────┘
   │                              │
   │                   ┌──────────▼────────────┐
   │                   │  compute_metrics()    │
   │                   │  (reads decision_log) │
   │                   └───────────────────────┘
   │
┌──▼──────────────────────────────────────────────────────────────────┐
│  DecisionCore  (axiom/decision_engine/decision_core.py)            │
│                                                                     │
│  1. TEXT PARSER  (_extract_field, _extract_delay_minutes)          │
│  2. VALIDATION   validate_problem()                                │
│  3. CLASSIFICATION  classify_event()                               │
│  4. RULE ENGINE  ─── mode=python ──► execute_rules()              │
│                  └── mode=database ─► RuleEngineDB.evaluate()      │
│                      (fallback to python if no DB match)           │
│  5. OPTIONS      generate_flight_options()                         │
│  6. ACTION       _build_action_required()                          │
│  7. LOG          append_decision_log()                             │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Layers

**API Layer:**
- Purpose: HTTP entry point; routes requests and delegates entirely to domain services
- Location: `axiom/api/main.py`
- Contains: FastAPI app instance, route definitions, CORS middleware, singleton `DecisionCore`, singleton `RuleRepository`
- Depends on: `DecisionCore`, `RuleRepository`, `compute_metrics`, Pydantic models
- Used by: Flutter dashboard (`AxiomApiService`)

**Decision Engine Layer:**
- Purpose: Orchestrates the full processing pipeline for a single natural-language problem
- Location: `axiom/decision_engine/`
- Contains: `DecisionCore` (orchestrator), `validators.py` (regex-based extraction), `event_classifier.py` (keyword-based classification), `rule_engine.py` (Python rule adapter), `options_generator.py` (simulated flight options)
- Depends on: `axiom/rules/`, `axiom/rule_platform/`, `axiom/models/`
- Used by: API layer only

**Rules Layer (Python):**
- Purpose: Hard-coded, logic-based reprotection rule
- Location: `axiom/rules/airline_rules.py`
- Contains: `involuntary_change_rule()` — evaluates five boolean conditions and returns APROBADO/RECHAZADO
- Depends on: nothing (pure function)
- Used by: `rule_engine.py` (Python mode path)

**Rule Platform Layer (CSV/table-based):**
- Purpose: Configurable, operator-driven rules stored in a CSV file, editable at runtime through the API
- Location: `axiom/rule_platform/`
- Contains: `rule_loader.py` (CSV reader), `rule_repository.py` (CRUD with thread lock), `rule_evaluator.py` (condition evaluator for operators `=`, `>`, `<`, `>=`, `<=`, `missing`), `rule_engine_db.py` (evaluator + log + metrics), `rule_models.py` (Pydantic schemas)
- Depends on: `axiom/rule_platform/rules.csv` (file-system persistence)
- Used by: API layer (CRUD endpoints), `DecisionCore` (database mode path), metrics endpoint

**Models Layer:**
- Purpose: Shared data contracts for API input/output
- Location: `axiom/models/`
- Contains: `request.py` (`ProcessRequest`), `response.py` (`ProcessResponse`, `ValidationResult`, `FlightOption`, `OriginalFlightSummary`, `TriggeredRuleSummary`)
- Depends on: Pydantic v2
- Used by: API layer, `DecisionCore`, rule platform

**Dashboard Layer:**
- Purpose: Operator UI — submit problems, view decisions, manage rules, view metrics
- Location: `axiom_dashboard/lib/`
- Contains: `main.dart` (app bootstrap), `app_shell.dart` (responsive nav shell), `dashboard_page.dart` (Processor view), `rules_page.dart` (Rule Platform CRUD), `metrics_page.dart` (Analytics)
- Depends on: `AxiomApiService` (HTTP), `fl_chart` (charts), `google_fonts`
- Used by: End operators (browser)

---

## Data Flow

**Happy path — APROBADO (database mode):**

1. Flutter `DashboardPage` submits a natural-language string to `POST /process`
2. `main.py` deserializes into `ProcessRequest` and calls `DecisionCore.process(problem)`
3. `DecisionCore._extract_field()` / `_extract_delay_minutes()` parse PNR, passenger, event type, delay from text using regex
4. `validate_problem(problem)` — regex checks for PNR pattern `[A-Z0-9]{4,6}` and passenger name; if either is missing, returns `RECHAZADO` immediately
5. `classify_event(problem)` — keyword scan returns `event_type`, `flight_cancelled`, `same_airline`, `same_route`, `has_sensitive_ssr`, `same_fare_class`, and `original_flight` summary
6. An `evaluation_context` dict is assembled from parsed + classified fields
7. `RuleEngineDB.evaluate(evaluation_context)` loads rules from `rules.csv` via `RuleRepository`, runs `evaluate_rules()` (filter rules whose condition matches context), sorts by `(priority, rule_id)`, maps top match to `status` / `action_required`
8. If no CSV rule matched, `execute_rules()` is called as fallback (Python mode), which invokes `involuntary_change_rule()`
9. `generate_flight_options(classification, approved)` returns a hardcoded list of 2–3 simulated LATAM flights, filtered by `same_route` and `approved`
10. `_build_action_required()` picks the first available flight option and writes the action string
11. `append_decision_log()` writes a JSON entry to `axiom/logs/decision_log.json`
12. `ProcessResponse` is serialized and returned to the dashboard

**Rule platform CRUD flow:**

1. `RulesPage` calls `GET /rules` → `RuleRepository.get_rules()` reads and sorts `rules.csv`
2. Operator edits via dialog → `POST/PUT/DELETE /rules` → `RuleRepository` acquires thread lock, rewrites `rules.csv`
3. Changes take effect on the next `/process` call (no cache layer)

**Metrics flow:**

1. `MetricsPage` calls `GET /metrics` → `compute_metrics()` reads full `decision_log.json`, computes aggregates (total, avg latency, rule frequency, daily counts, latency series), returns as dict

---

## Entry Points

**API server:**
- Location: `axiom/api/main.py`
- Triggers: `uvicorn axiom.api.main:app` (or `uvicorn axiom.api.main:app --reload`)
- Responsibilities: Mount CORS middleware, instantiate `DecisionCore` and `RuleRepository` as module-level singletons, register all routes

**Flutter app:**
- Location: `axiom_dashboard/lib/main.dart`
- Triggers: `flutter run -d chrome` or served as compiled web assets
- Responsibilities: Bootstrap `AxiomApp`, apply dark Material3 theme, render `AppShell`

**Configuration:**
- Location: `axiom/config.py`
- Key setting: `RULE_ENGINE_MODE` env var (`"python"` or `"database"`, defaults to `"python"`)

---

## API Surface

All endpoints are on the FastAPI app defined in `axiom/api/main.py`.

| Method | Path | Purpose | Request / Response |
|--------|------|---------|-------------------|
| GET | `/health` | Liveness probe | `{"status": "ok"}` |
| POST | `/process` | Run decision pipeline | `ProcessRequest` → `ProcessResponse` |
| GET | `/rules` | List all CSV rules | `list[RuleRecord]` |
| POST | `/rules` | Create a rule | `RuleCreate` → `RuleRecord` |
| PUT | `/rules/{rule_id}` | Update a rule | `RuleUpdate` → `RuleRecord` |
| DELETE | `/rules/{rule_id}` | Delete a rule | `{"deleted": bool, "rule_id": int}` |
| GET | `/metrics` | Decision telemetry | `MetricsSummary` dict |

**ProcessRequest schema:**
```python
class ProcessRequest(BaseModel):
    problem: str  # min_length=5, natural language description
```

**ProcessResponse schema** (key fields):
```python
class ProcessResponse(BaseModel):
    status: str                    # "APROBADO" | "RECHAZADO"
    event_type: str                # e.g. "Cancelación de vuelo por parte de la aerolínea"
    validation: ValidationResult   # pnr: str, passenger: str
    rule_applied: str
    justification: str
    options: List[FlightOption]    # flight, time, status
    action_required: Optional[str]
    analysis_time_ms: int
    flow: List[str]                # ["INPUT","VALIDACION","CLASIFICACION","REGLAS","OPCIONES","ACCION"]
    original_flight: OriginalFlightSummary
    audit_trace: List[str]
    engine_mode: str               # "python" | "database"
    triggered_rules: List[TriggeredRuleSummary]
```

---

## Key Abstractions

**DecisionCore (`axiom/decision_engine/decision_core.py`):**
- Purpose: Single orchestrator for the entire pipeline; owns flow definition, error short-circuits, and audit trace accumulation
- Pattern: Template method — fixed stage sequence, delegating each stage to a collaborator

**RuleEngineDB (`axiom/rule_platform/rule_engine_db.py`):**
- Purpose: Table-based rule evaluation with fallback semantics
- Pattern: Strategy — implements the same `evaluate(context) -> dict` interface that `execute_rules()` fulfills in Python mode

**RuleRepository (`axiom/rule_platform/rule_repository.py`):**
- Purpose: CSV file as a pseudo-database with CRUD semantics
- Pattern: Repository — abstracts file I/O behind `get_rules()`, `add_rule()`, `update_rule()`, `delete_rule()`; uses `threading.Lock` for write safety

**involuntary_change_rule (`axiom/rules/airline_rules.py`):**
- Purpose: Stateless rule function for the Python engine mode
- Pattern: Pure function — receives context dict, returns result dict with `allow_reprotection`, `rule_applied`, `justification`, `trace`

**AxiomApiService (`axiom_dashboard/lib/services/axiom_api.dart`):**
- Purpose: Single HTTP client encapsulating all API calls from the Flutter side
- Pattern: Service class — all pages obtain an instance directly (`const AxiomApiService()`) without a DI container

---

## Rule Engine Modes

Two modes are selected at startup by `RULE_ENGINE_MODE` env var (`axiom/config.py`):

**`python` mode (default):**
```
execute_rules(classification, validation)
  └── involuntary_change_rule(classification)
        checks: flight_cancelled, same_airline, same_route, no_sensitive_ssr, same_fare_class
        → all True = APROBADO, any False = RECHAZADO
```

**`database` mode:**
```
RuleEngineDB.evaluate(evaluation_context)
  └── RuleRepository.get_rules()  →  load rules.csv
      evaluate_rules(context, rules)
        for each rule: _evaluate(rule, data) using operator dispatch
        sort by (priority, rule_id)
        top match → action → APROBADO | RECHAZADO
  fallback: if no rules matched → call execute_rules() (python mode)
```

CSV rule schema (`axiom/rule_platform/rules.csv`):
```
rule_id, field, operator, value, action, priority
```
Supported operators: `=`, `>`, `<`, `>=`, `<=`, `missing`
Current rules:
- `delay_minutes > 180` → `offer_voucher` (priority 1)
- `passenger_name missing` → `request_name` (priority 1)
- `pnr missing` → `request_pnr` (priority 1)
- `event_type = delay` → `process_delay` (priority 2)

---

## Persistence

**Decision log:**
- Location: `axiom/logs/decision_log.json`
- Format: JSON array of objects `{timestamp, event_type, rule_triggered, action, processing_time_ms}`
- Access pattern: Append-only writes on every `/process` call; full read on every `/metrics` call
- No rotation or size limit

**Rule store:**
- Location: `axiom/rule_platform/rules.csv`
- Format: CSV with headers `rule_id,field,operator,value,action,priority`
- Access pattern: Full read on every rule evaluation; full rewrite on CRUD mutations (thread-locked)

---

## Error Handling

**Strategy:** Fail-fast with structured responses; no unhandled exceptions reach the API caller.

**Patterns:**
- Missing critical data (no PNR or no passenger name) short-circuits in `DecisionCore.process()` before any rule stage and returns a `RECHAZADO` `ProcessResponse` immediately
- Rule platform "no match" falls back to Python mode rather than raising an error
- HTTP 404 returned from `update_rule` and `delete_rule` when `rule_id` not found
- No try/except inside the pipeline stages — errors would propagate as FastAPI 500s (unhandled)
- Flutter side wraps all `AxiomApiService` calls in try/catch and surfaces error strings in the UI

---

## Cross-Cutting Concerns

**Logging:**
- Structured decision log appended to `axiom/logs/decision_log.json` after every `/process` call via `append_decision_log()`
- Audit trace (list of strings) is included in every `ProcessResponse`, providing per-field step visibility

**Validation:**
- Input validated via Pydantic at the API boundary (`ProcessRequest` with `min_length=5`)
- Domain validation (PNR presence, passenger name presence) performed inside `validate_problem()` using compiled regex patterns
- Rule model validation performed by Pydantic validators in `RuleBase` (operator whitelist, field sanitization)

**CORS:**
- `allow_origins=["*"]` — open to all origins; suitable for local development, must be restricted before production deployment

**Concurrency:**
- `RuleRepository` uses `threading.Lock` on all write operations against `rules.csv`
- No async/await in domain logic; all route handlers are synchronous (FastAPI runs them in a thread pool by default)

**Configuration:**
- Single env var: `RULE_ENGINE_MODE` (read once at process start via `axiom/config.py`)
- Flutter API URL: injected via `--dart-define=AXIOM_API_URL=...` at build time, defaults to `http://127.0.0.1:8000`

---

*Architecture analysis: 2026-03-30*
