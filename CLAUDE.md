<!-- GSD:project-start source:PROJECT.md -->
## Project

**AXIOM AirFlight Engine**

AXIOM is a rule-based decision engine for automating involuntary flight changes in airline post-sale operations. It takes a PNR + passenger last name, retrieves the reservation, evaluates sequential business rules (cancellation, delay, fare protection, SSR checks), generates reprotection options, and lets the operator select an alternative flight — logging every decision with full traceability. The target audience is small airlines and travel agencies with high-volume post-sale operations.

**Core Value:** When a flight is cancelled or delayed, the right reprotection decision is made consistently, instantly, and with complete audit trail — eliminating human error in high-volume involuntary change processing.

### Constraints

- **Data**: Simulated PNR/flight data (structured like real GDS for future integration)
- **Frontend**: React/Next.js with AXIOM brand dark theme (replacing Flutter)
- **Backend**: Python/FastAPI (extend existing, don't rewrite core)
- **Storage**: Local database for demo (SQLite or equivalent)
- **Demo quality**: Investor-ready UI polish following exact brand guidelines
- **No real integrations**: All data simulated, all actions are decision records
<!-- GSD:project-end -->

<!-- GSD:stack-start source:codebase/STACK.md -->
## Technology Stack

## Languages
- Python 3.14 (runtime on dev machine) — Backend decision engine, rule platform, API
- Dart 3.x (SDK `>=3.3.0 <4.0.0`) — Flutter Web dashboard
- CSV — Rule storage format at `axiom/rule_platform/rules.csv`
- JSON — Decision log persistence at `axiom/logs/decision_log.json`
## Runtime
- Python 3.14+ (dev machine); minimum Python version not pinned in requirements.txt — any Python 3.10+ should work given type hint syntax used (`str | None`, `dict[str, Any]`)
- Dart SDK `>=3.3.0 <4.0.0` (Flutter enforces this via `pubspec.yaml`)
- Python: pip (no lockfile — `requirements.txt` only, 3 direct deps)
- Dart/Flutter: pub (`axiom_dashboard/pubspec.lock` present)
- Python: not present (no `requirements.lock` or `pip freeze` output committed)
- Flutter: `axiom_dashboard/pubspec.lock` present and committed
## Frameworks
- FastAPI `0.116.1` — HTTP API layer; defines all REST endpoints in `axiom/api/main.py`
- Pydantic `2.11.7` — Data validation and serialization for all request/response models; used throughout `axiom/models/` and `axiom/rule_platform/rule_models.py`
- Flutter `stable` (Material 3, dark theme) — Web UI in `axiom_dashboard/lib/`
- Not detected — no test framework configured, no test files found
- Uvicorn `0.35.0` with `[standard]` extras — ASGI server; run command: `uvicorn axiom.api.main:app --reload --port 8000`
- Flutter build toolchain — Web target; run command: `flutter run -d chrome --dart-define=AXIOM_API_URL=http://127.0.0.1:8000`
## Key Dependencies
- `fastapi==0.116.1` — All HTTP routing, request parsing, CORS middleware; defined in `axiom/api/main.py`
- `pydantic==2.11.7` — All model validation; used in `axiom/models/request.py`, `axiom/models/response.py`, `axiom/rule_platform/rule_models.py`
- `uvicorn[standard]==0.35.0` — Production-grade ASGI server with websocket and HTTP/2 extras
- `http: ^1.2.1` (Flutter) — HTTP client for all API calls in `axiom_dashboard/lib/services/axiom_api.dart`
- `fl_chart: ^1.1.1` (Flutter) — Charting library for metrics visualizations
- `google_fonts: ^6.2.1` (Flutter) — Typography
- Python `csv` stdlib — Rule persistence read/write in `axiom/rule_platform/rule_repository.py`
- Python `json` stdlib — Decision log persistence in `axiom/rule_platform/rule_engine_db.py`
- Python `pathlib` stdlib — All file path handling
- Python `threading` stdlib — Thread-safe locking on CSV writes in `axiom/rule_platform/rule_repository.py`
- Python `re` stdlib — NLP-style text parsing for PNR, passenger name, flight number extraction in `axiom/decision_engine/validators.py`, `axiom/decision_engine/event_classifier.py`, `axiom/decision_engine/decision_core.py`
## Configuration
- Single env var: `RULE_ENGINE_MODE` — controls which rule engine runs (`"python"` or `"database"`); defaults to `"python"` if unset; read in `axiom/config.py`
- Flutter API URL: `AXIOM_API_URL` — passed at build time via `--dart-define`; defaults to `http://127.0.0.1:8000`; consumed in `axiom_dashboard/lib/services/axiom_api.dart`
- No `.env` file management detected — environment vars set manually via shell or `set` command
- No `pyproject.toml`, `setup.py`, or `Makefile` present
- No Dockerfile or container configuration detected
- Flutter web build: standard `flutter build web` using `axiom_dashboard/pubspec.yaml`
## Platform Requirements
- Python 3.10+ (for union type hints `X | Y` and dict/list generics without `from __future__` import)
- Flutter SDK with Dart `>=3.3.0`
- Chrome browser for Flutter web dev target
- pip for backend dependency installation
- Backend: Any ASGI-capable host (uvicorn serves directly; no Nginx or proxy config present)
- Frontend: Flutter Web output at `axiom_dashboard/build/web/` — serves as static HTML/JS
- No cloud provider, containerization, or CI/CD configuration detected
## Data Storage
- Rules: `axiom/rule_platform/rules.csv` — CSV file, read/written by `axiom/rule_platform/rule_repository.py`
- Decision log: `axiom/logs/decision_log.json` — append-only JSON array, written by `axiom/rule_platform/rule_engine_db.py`
- Both paths are relative to the Python package root, resolved via `pathlib.Path(__file__)`
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

Conventions not yet established. Will populate as patterns emerge during development.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

## Pattern Overview
- Linear, ordered processing pipeline: each stage receives the output of the previous stage
- Two pluggable rule engine implementations (Python hard-coded rules vs. CSV table-based rules), selected at startup via environment variable
- Stateless API layer — all processing context is constructed fresh per request; the only persistent state is the append-only JSON decision log and the CSV rule store
- Thin orchestrator (`DecisionCore`) that owns the pipeline and delegates every stage to a focused module
- Symmetric data contracts: Pydantic models on the Python side, plain Dart classes on the Flutter side, mirroring the same shape
## Component Diagram
```
```
## Layers
- Purpose: HTTP entry point; routes requests and delegates entirely to domain services
- Location: `axiom/api/main.py`
- Contains: FastAPI app instance, route definitions, CORS middleware, singleton `DecisionCore`, singleton `RuleRepository`
- Depends on: `DecisionCore`, `RuleRepository`, `compute_metrics`, Pydantic models
- Used by: Flutter dashboard (`AxiomApiService`)
- Purpose: Orchestrates the full processing pipeline for a single natural-language problem
- Location: `axiom/decision_engine/`
- Contains: `DecisionCore` (orchestrator), `validators.py` (regex-based extraction), `event_classifier.py` (keyword-based classification), `rule_engine.py` (Python rule adapter), `options_generator.py` (simulated flight options)
- Depends on: `axiom/rules/`, `axiom/rule_platform/`, `axiom/models/`
- Used by: API layer only
- Purpose: Hard-coded, logic-based reprotection rule
- Location: `axiom/rules/airline_rules.py`
- Contains: `involuntary_change_rule()` — evaluates five boolean conditions and returns APROBADO/RECHAZADO
- Depends on: nothing (pure function)
- Used by: `rule_engine.py` (Python mode path)
- Purpose: Configurable, operator-driven rules stored in a CSV file, editable at runtime through the API
- Location: `axiom/rule_platform/`
- Contains: `rule_loader.py` (CSV reader), `rule_repository.py` (CRUD with thread lock), `rule_evaluator.py` (condition evaluator for operators `=`, `>`, `<`, `>=`, `<=`, `missing`), `rule_engine_db.py` (evaluator + log + metrics), `rule_models.py` (Pydantic schemas)
- Depends on: `axiom/rule_platform/rules.csv` (file-system persistence)
- Used by: API layer (CRUD endpoints), `DecisionCore` (database mode path), metrics endpoint
- Purpose: Shared data contracts for API input/output
- Location: `axiom/models/`
- Contains: `request.py` (`ProcessRequest`), `response.py` (`ProcessResponse`, `ValidationResult`, `FlightOption`, `OriginalFlightSummary`, `TriggeredRuleSummary`)
- Depends on: Pydantic v2
- Used by: API layer, `DecisionCore`, rule platform
- Purpose: Operator UI — submit problems, view decisions, manage rules, view metrics
- Location: `axiom_dashboard/lib/`
- Contains: `main.dart` (app bootstrap), `app_shell.dart` (responsive nav shell), `dashboard_page.dart` (Processor view), `rules_page.dart` (Rule Platform CRUD), `metrics_page.dart` (Analytics)
- Depends on: `AxiomApiService` (HTTP), `fl_chart` (charts), `google_fonts`
- Used by: End operators (browser)
## Data Flow
## Entry Points
- Location: `axiom/api/main.py`
- Triggers: `uvicorn axiom.api.main:app` (or `uvicorn axiom.api.main:app --reload`)
- Responsibilities: Mount CORS middleware, instantiate `DecisionCore` and `RuleRepository` as module-level singletons, register all routes
- Location: `axiom_dashboard/lib/main.dart`
- Triggers: `flutter run -d chrome` or served as compiled web assets
- Responsibilities: Bootstrap `AxiomApp`, apply dark Material3 theme, render `AppShell`
- Location: `axiom/config.py`
- Key setting: `RULE_ENGINE_MODE` env var (`"python"` or `"database"`, defaults to `"python"`)
## API Surface
| Method | Path | Purpose | Request / Response |
|--------|------|---------|-------------------|
| GET | `/health` | Liveness probe | `{"status": "ok"}` |
| POST | `/process` | Run decision pipeline | `ProcessRequest` → `ProcessResponse` |
| GET | `/rules` | List all CSV rules | `list[RuleRecord]` |
| POST | `/rules` | Create a rule | `RuleCreate` → `RuleRecord` |
| PUT | `/rules/{rule_id}` | Update a rule | `RuleUpdate` → `RuleRecord` |
| DELETE | `/rules/{rule_id}` | Delete a rule | `{"deleted": bool, "rule_id": int}` |
| GET | `/metrics` | Decision telemetry | `MetricsSummary` dict |
```python
```
```python
```
## Key Abstractions
- Purpose: Single orchestrator for the entire pipeline; owns flow definition, error short-circuits, and audit trace accumulation
- Pattern: Template method — fixed stage sequence, delegating each stage to a collaborator
- Purpose: Table-based rule evaluation with fallback semantics
- Pattern: Strategy — implements the same `evaluate(context) -> dict` interface that `execute_rules()` fulfills in Python mode
- Purpose: CSV file as a pseudo-database with CRUD semantics
- Pattern: Repository — abstracts file I/O behind `get_rules()`, `add_rule()`, `update_rule()`, `delete_rule()`; uses `threading.Lock` for write safety
- Purpose: Stateless rule function for the Python engine mode
- Pattern: Pure function — receives context dict, returns result dict with `allow_reprotection`, `rule_applied`, `justification`, `trace`
- Purpose: Single HTTP client encapsulating all API calls from the Flutter side
- Pattern: Service class — all pages obtain an instance directly (`const AxiomApiService()`) without a DI container
## Rule Engine Modes
```
```
```
```
```
```
- `delay_minutes > 180` → `offer_voucher` (priority 1)
- `passenger_name missing` → `request_name` (priority 1)
- `pnr missing` → `request_pnr` (priority 1)
- `event_type = delay` → `process_delay` (priority 2)
## Persistence
- Location: `axiom/logs/decision_log.json`
- Format: JSON array of objects `{timestamp, event_type, rule_triggered, action, processing_time_ms}`
- Access pattern: Append-only writes on every `/process` call; full read on every `/metrics` call
- No rotation or size limit
- Location: `axiom/rule_platform/rules.csv`
- Format: CSV with headers `rule_id,field,operator,value,action,priority`
- Access pattern: Full read on every rule evaluation; full rewrite on CRUD mutations (thread-locked)
## Error Handling
- Missing critical data (no PNR or no passenger name) short-circuits in `DecisionCore.process()` before any rule stage and returns a `RECHAZADO` `ProcessResponse` immediately
- Rule platform "no match" falls back to Python mode rather than raising an error
- HTTP 404 returned from `update_rule` and `delete_rule` when `rule_id` not found
- No try/except inside the pipeline stages — errors would propagate as FastAPI 500s (unhandled)
- Flutter side wraps all `AxiomApiService` calls in try/catch and surfaces error strings in the UI
## Cross-Cutting Concerns
- Structured decision log appended to `axiom/logs/decision_log.json` after every `/process` call via `append_decision_log()`
- Audit trace (list of strings) is included in every `ProcessResponse`, providing per-field step visibility
- Input validated via Pydantic at the API boundary (`ProcessRequest` with `min_length=5`)
- Domain validation (PNR presence, passenger name presence) performed inside `validate_problem()` using compiled regex patterns
- Rule model validation performed by Pydantic validators in `RuleBase` (operator whitelist, field sanitization)
- `allow_origins=["*"]` — open to all origins; suitable for local development, must be restricted before production deployment
- `RuleRepository` uses `threading.Lock` on all write operations against `rules.csv`
- No async/await in domain logic; all route handlers are synchronous (FastAPI runs them in a thread pool by default)
- Single env var: `RULE_ENGINE_MODE` (read once at process start via `axiom/config.py`)
- Flutter API URL: injected via `--dart-define=AXIOM_API_URL=...` at build time, defaults to `http://127.0.0.1:8000`
<!-- GSD:architecture-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd:quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd:debug` for investigation and bug fixing
- `/gsd:execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->



<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd:profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
