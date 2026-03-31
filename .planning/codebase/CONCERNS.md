# Codebase Concerns

**Analysis Date:** 2026-03-30

---

## Security Considerations

**Wildcard CORS with credentials enabled:**
- Risk: Any origin can make credentialed requests to the API. Combined with `allow_credentials=True`, this violates the CORS spec intent and exposes the API to cross-site request forgery from any domain.
- Files: `axiom/api/main.py` lines 19–25
- Current mitigation: None
- Recommendations: Replace `allow_origins=["*"]` with an explicit allowlist (e.g., the Flutter dashboard origin). Remove `allow_credentials=True` if credentials are not actively used, or restrict origins first.

**No authentication on any endpoint:**
- Risk: All endpoints — including destructive ones (`DELETE /rules/{rule_id}`, `PUT /rules/{rule_id}`, `POST /rules`) — are publicly accessible with zero identity verification. Any network-reachable client can create, modify, or delete airline decision rules that affect real passenger outcomes.
- Files: `axiom/api/main.py` (all route handlers)
- Current mitigation: None
- Recommendations: Add API key or JWT middleware before any production exposure. At minimum, protect write endpoints (`POST`, `PUT`, `DELETE`) with a dependency-injected auth guard in FastAPI.

**No rate limiting on the `/process` endpoint:**
- Risk: The `/process` endpoint runs regex parsing, rule evaluation, file I/O (log append + full JSON rewrite), and string classification on every call. There is no request throttling, making it trivially vulnerable to denial-of-service through request flooding.
- Files: `axiom/api/main.py`, `axiom/rule_platform/rule_engine_db.py`
- Current mitigation: None
- Recommendations: Add `slowapi` or equivalent rate-limiting middleware. Limit `/process` to N requests per IP per minute.

**PNR leaked into audit trace in plaintext:**
- Risk: The `audit_trace` field in `ProcessResponse` includes raw PNR and passenger name strings (e.g., `"validation={'pnr': 'AX123', ...}"`). This trace is returned in the API response body and written to the JSON log file without masking. PNR and passenger names are PII regulated under GDPR and airline data protection standards.
- Files: `axiom/decision_engine/decision_core.py` lines 98, 141–158; `axiom/logs/decision_log.json`
- Current mitigation: None
- Recommendations: Redact or hash PNR values before including them in `audit_trace`. Do not log raw passenger names. Apply masking at the point of `audit_trace.append()` in `decision_core.py`.

**Unprotected rule mutation via public API:**
- Risk: The `/rules` CRUD endpoints allow anyone to inject arbitrary rule logic (field names, operators, actions) into the CSV-backed rule store. A malicious actor could add a rule that unconditionally approves all reprotection requests or triggers incorrect passenger handling decisions.
- Files: `axiom/api/main.py`, `axiom/rule_platform/rule_repository.py`, `axiom/rule_platform/rules.csv`
- Current mitigation: `rule_models.py` validates that `operator` is within a supported set and strips whitespace from `field`/`action`. The `action` field accepts arbitrary strings with no allowlist.
- Recommendations: Add an allowlist for valid `action` values. Require authentication before any rule write. Consider an approval workflow for rule changes in a production setting.

---

## Tech Debt

**Simulated flight options are hardcoded static data:**
- Issue: `generate_flight_options()` always returns the same three LATAM flights (`LA513`, `LA515`, `LA517`) regardless of the actual route, airline, or time of day. The function signature accepts a `classification` dict but ignores the airline field entirely.
- Files: `axiom/decision_engine/options_generator.py` lines 6–18
- Impact: The `/process` endpoint returns fabricated flight availability data. Any downstream system or user relying on these options would act on fictitious information. This is the single highest-impact correctness gap in the engine.
- Fix approach: Replace with an integration to a real GDS/NDC API (e.g., Amadeus, Sabre) or accept available alternatives as part of the input payload. Until a real source is available, the response should clearly mark options as `"source": "simulated"` and the frontend should surface that label.

**Flight date always returns "unknown":**
- Issue: `classify_event()` sets `"date": "unknown"` in `original_flight` unconditionally. No date extraction logic exists anywhere in the classifier or validators.
- Files: `axiom/decision_engine/event_classifier.py` line 94
- Impact: Decision audit records and responses contain no temporal context. Rules that should depend on flight date (e.g., same-day cancellations) cannot be expressed.
- Fix approach: Add date extraction via regex in `event_classifier.py` alongside the existing flight number extraction pattern.

**Dual rule engine with silent fallback creates unpredictable behavior:**
- Issue: When `RULE_ENGINE_MODE=database` and no CSV rules match, the engine silently falls back to the Python rule engine (`execute_rules`). This is logged only in `audit_trace` with a string `"rule_platform=fallback_python"` that is not surfaced in the API response status or in the decision log.
- Files: `axiom/decision_engine/decision_core.py` lines 191–195
- Impact: Operators managing rules via the dashboard may believe the CSV rules are authoritative when a Python fallback is actually running. Rule changes made via the `/rules` API have no guaranteed effect if the fallback fires.
- Fix approach: Make fallback behavior explicit and configurable. Add a flag to disable fallback. Surface the active engine path in the API response beyond the internal `audit_trace`.

**`RuleCreate` and `RuleBase` are identical (dead abstraction):**
- Issue: `RuleCreate` is defined as `class RuleCreate(RuleBase): pass` with no additions. The distinction between `RuleCreate` and `RuleBase` provides no value and adds indirection.
- Files: `axiom/rule_platform/rule_models.py` line 35
- Impact: Low — cosmetic tech debt. Creates confusion when navigating the model layer.
- Fix approach: Either remove `RuleCreate` and use `RuleBase` directly, or add fields that genuinely differ at creation time.

**`problem` input is free-form natural language processed by fragile regex:**
- Issue: The entire input to the decision engine is an unstructured natural-language string. Field extraction relies on regex patterns in `validators.py` and `decision_core.py`. The PNR regex (`[A-Z0-9]{4,6}`) will match any 4–6 character uppercase token, including flight numbers and airport codes.
- Files: `axiom/decision_engine/validators.py` lines 5–6, `axiom/decision_engine/decision_core.py` lines 37–53
- Impact: False PNR matches cause incorrect validation outcomes. Ambiguous input silently produces wrong classifications with no error returned to the caller.
- Fix approach: Accept a structured input schema (`pnr`, `passenger_name`, `event_type`, `delay_minutes`, `flight`) alongside or instead of the free-form string. Free-form parsing should be an optional pre-processing layer, not the primary data contract.

---

## Performance Bottlenecks

**Decision log uses read-entire-file-then-rewrite-entire-file pattern:**
- Problem: Every call to `append_decision_log()` reads the entire `decision_log.json` into memory, appends one record, then writes the entire file back to disk. `compute_metrics()` also reads the entire file on every `/metrics` request.
- Files: `axiom/rule_platform/rule_engine_db.py` lines 30–68, 72–83
- Cause: JSON was chosen as the log format with no append-only mechanism. The entire array must be parsed and re-serialized on every write.
- Improvement path: Replace with append-only newline-delimited JSON (NDJSON) for writes. Compute metrics from a proper store (SQLite at minimum). At current scale (19 log entries) this is dormant, but at 10K+ daily decisions the full rewrite will block the request thread.

**No lock on `append_decision_log` (race condition under concurrent load):**
- Problem: `RuleRepository` uses `threading.Lock()` for CSV writes, but `append_decision_log` / `_write_log` in `rule_engine_db.py` has no equivalent lock. Under concurrent requests (uvicorn runs with multiple workers), two simultaneous `/process` calls can both read the log, each append one entry, then both write — one write silently overwrites the other.
- Files: `axiom/rule_platform/rule_engine_db.py` lines 30–68
- Cause: Inconsistent application of the locking pattern already established in `rule_repository.py`.
- Improvement path: Add a module-level `threading.Lock` wrapping the read-append-write sequence in `append_decision_log`, mirroring the approach in `RuleRepository`.

**CSV rules reloaded from disk on every request:**
- Problem: `RuleEngineDB.evaluate()` calls `self.repository.get_rules()`, which calls `load_rules()`, which opens and parses the CSV file on every invocation. There is no in-memory cache or invalidation strategy.
- Files: `axiom/rule_platform/rule_engine_db.py` line 149, `axiom/rule_platform/rule_repository.py` lines 18–20, `axiom/rule_platform/rule_loader.py`
- Cause: No caching layer was built when the CSV-based repository was introduced.
- Improvement path: Cache the parsed rule list in `RuleRepository` and invalidate on write operations (`add_rule`, `update_rule`, `delete_rule`). A simple `_cached_rules` attribute with a dirty flag is sufficient at this scale.

---

## Data Integrity Risks

**No database — all state lives in mutable flat files:**
- Risk: The system has two persistent stores: `axiom/rule_platform/rules.csv` (rule definitions) and `axiom/logs/decision_log.json` (audit history). Both are plain files with no transaction semantics, no backup mechanism, and no schema migration path. A partial write due to process crash or disk error leaves the system in an unrecoverable corrupt state.
- Files: `axiom/rule_platform/rules.csv`, `axiom/logs/decision_log.json`, `axiom/rule_platform/rule_repository.py` line 66, `axiom/rule_platform/rule_engine_db.py` line 47
- Current mitigation: The CSV writer uses `open("w")` (full overwrite) without writing to a temp file and renaming. A crash mid-write produces a truncated CSV. `_write_log` has the same pattern.
- Fix approach: Use atomic writes (write to `.tmp`, then `os.replace()`) for both files. Medium-term, migrate to SQLite via `aiosqlite` or SQLAlchemy — it requires zero infrastructure changes and provides proper transaction guarantees.

**Rule IDs are generated by `max(existing_ids) + 1` with no uniqueness guarantee:**
- Risk: `add_rule()` computes `next_id = max((rule.rule_id for rule in rules), default=0) + 1`. If two concurrent `POST /rules` requests both read the same set of rules before either writes, they both compute the same `next_id` and create two rules with duplicate IDs. The threading lock in `RuleRepository` mitigates this for single-process deployments, but the pattern is fragile.
- Files: `axiom/rule_platform/rule_repository.py` lines 23–29
- Fix approach: Use an auto-incrementing counter stored separately, or migrate to SQLite with `AUTOINCREMENT`. The lock partially protects this but should be documented as a known limitation.

**Decision log stores no correlation ID or request context:**
- Risk: Each log entry records `event_type`, `rule_triggered`, `action`, and `processing_time_ms`, but no identifier linking a log entry to a specific API request or PNR. Auditing a specific passenger decision requires scanning all log entries by timestamp and hoping for no collisions.
- Files: `axiom/rule_platform/rule_engine_db.py` lines 51–68
- Fix approach: Add a `request_id` (UUID) generated at the start of `DecisionCore.process()` and included in both the `ProcessResponse` and the log entry.

---

## Missing Infrastructure

**Zero test coverage:**
- What's not tested: No test files exist anywhere in the repository (`find` returns nothing for `*.test.*`, `test_*.py`, or any `tests/` directory). The decision engine, rule evaluator, event classifier, validators, and all API endpoints are completely untested.
- Files: Entire `axiom/` tree
- Risk: Regressions in rule evaluation logic, regex parsing, or the CSV read/write cycle are invisible. The dual-engine fallback behavior, the simulated options generator, and the race condition in `append_decision_log` are all undetected by any automated check.
- Priority: High. The rule evaluator (`axiom/rule_platform/rule_evaluator.py`) and validators (`axiom/decision_engine/validators.py`) have pure, side-effect-free functions that are immediately testable with `pytest`. Start there.

**No Dockerfile, no deployment configuration:**
- What's missing: No `Dockerfile`, `docker-compose.yml`, `.github/workflows/`, `Procfile`, or any deployment artifact exists. The only run instruction is a bare `uvicorn` command in `README.md`.
- Files: Project root
- Risk: No reproducible environment definition means the application cannot be deployed consistently. The file-based storage (CSV + JSON) also requires a persistent volume strategy that is not documented.
- Priority: Medium for current prototype stage; high before any production deployment.

**No `.env` file or environment variable documentation:**
- What's missing: The only configurable environment variable is `RULE_ENGINE_MODE` (documented in `README.md`). No `.env.example` file exists. The Flutter dashboard hardcodes `http://127.0.0.1:8000` as the default API URL with no production override path documented.
- Files: `axiom/config.py`, `axiom_dashboard/lib/services/axiom_api.dart` line 12
- Risk: Deploying the frontend against a production backend requires a `--dart-define` flag known only from the README. Configuration drift is likely.
- Priority: Low for prototype; medium before team expansion.

**No input sanitization against injection in rule `action` field:**
- What's missing: The `action` field in rules accepts any string. The `_ACTION_MESSAGES` dict in `rule_engine_db.py` provides a lookup for known actions, but unknown actions fall through to `f"Ejecutar accion de regla: {action}."` which embeds the raw action string in the response body. There is no allowlist enforcement at the model layer.
- Files: `axiom/rule_platform/rule_engine_db.py` line 169, `axiom/rule_platform/rule_models.py`
- Risk: Stored XSS or injection if the action string is rendered in a UI context without escaping. Currently low risk given the Flutter dashboard, but becomes relevant if the response is consumed by web contexts.
- Priority: Low now; address when adding authentication to the rule write endpoints.

---

## Scaling Limits

**Single-node file-based storage cannot scale horizontally:**
- Current capacity: The system supports exactly one running process writing to local disk files. Uvicorn's default multi-worker mode (`--workers N`) would immediately cause data corruption on `decision_log.json` writes (no cross-process lock).
- Limit: A single uvicorn worker. Running `uvicorn --workers 4` breaks log integrity.
- Scaling path: Migrate `decision_log.json` to SQLite (single-file, concurrent-safe) or PostgreSQL. Migrate `rules.csv` to the same database. This unblocks both multi-worker deployment and horizontal scaling behind a load balancer.

**`compute_metrics()` scans the full log on every `/metrics` call:**
- Current capacity: Acceptable at under ~1,000 log entries.
- Limit: At 10K+ entries, full JSON parse + Counter aggregation on every metrics poll becomes a measurable latency source, especially if the Flutter dashboard polls on a timer.
- Scaling path: Pre-aggregate metrics incrementally on write, or cache the metrics result with a short TTL (e.g., 30 seconds).

---

*Concerns audit: 2026-03-30*
