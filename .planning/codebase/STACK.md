# Technology Stack

**Analysis Date:** 2026-03-30

## Languages

**Primary:**
- Python 3.14 (runtime on dev machine) — Backend decision engine, rule platform, API
- Dart 3.x (SDK `>=3.3.0 <4.0.0`) — Flutter Web dashboard

**Secondary:**
- CSV — Rule storage format at `axiom/rule_platform/rules.csv`
- JSON — Decision log persistence at `axiom/logs/decision_log.json`

## Runtime

**Environment:**
- Python 3.14+ (dev machine); minimum Python version not pinned in requirements.txt — any Python 3.10+ should work given type hint syntax used (`str | None`, `dict[str, Any]`)
- Dart SDK `>=3.3.0 <4.0.0` (Flutter enforces this via `pubspec.yaml`)

**Package Manager:**
- Python: pip (no lockfile — `requirements.txt` only, 3 direct deps)
- Dart/Flutter: pub (`axiom_dashboard/pubspec.lock` present)

**Lockfile:**
- Python: not present (no `requirements.lock` or `pip freeze` output committed)
- Flutter: `axiom_dashboard/pubspec.lock` present and committed

## Frameworks

**Core:**
- FastAPI `0.116.1` — HTTP API layer; defines all REST endpoints in `axiom/api/main.py`
- Pydantic `2.11.7` — Data validation and serialization for all request/response models; used throughout `axiom/models/` and `axiom/rule_platform/rule_models.py`
- Flutter `stable` (Material 3, dark theme) — Web UI in `axiom_dashboard/lib/`

**Testing:**
- Not detected — no test framework configured, no test files found

**Build/Dev:**
- Uvicorn `0.35.0` with `[standard]` extras — ASGI server; run command: `uvicorn axiom.api.main:app --reload --port 8000`
- Flutter build toolchain — Web target; run command: `flutter run -d chrome --dart-define=AXIOM_API_URL=http://127.0.0.1:8000`

## Key Dependencies

**Critical:**
- `fastapi==0.116.1` — All HTTP routing, request parsing, CORS middleware; defined in `axiom/api/main.py`
- `pydantic==2.11.7` — All model validation; used in `axiom/models/request.py`, `axiom/models/response.py`, `axiom/rule_platform/rule_models.py`
- `uvicorn[standard]==0.35.0` — Production-grade ASGI server with websocket and HTTP/2 extras
- `http: ^1.2.1` (Flutter) — HTTP client for all API calls in `axiom_dashboard/lib/services/axiom_api.dart`
- `fl_chart: ^1.1.1` (Flutter) — Charting library for metrics visualizations
- `google_fonts: ^6.2.1` (Flutter) — Typography

**Infrastructure:**
- Python `csv` stdlib — Rule persistence read/write in `axiom/rule_platform/rule_repository.py`
- Python `json` stdlib — Decision log persistence in `axiom/rule_platform/rule_engine_db.py`
- Python `pathlib` stdlib — All file path handling
- Python `threading` stdlib — Thread-safe locking on CSV writes in `axiom/rule_platform/rule_repository.py`
- Python `re` stdlib — NLP-style text parsing for PNR, passenger name, flight number extraction in `axiom/decision_engine/validators.py`, `axiom/decision_engine/event_classifier.py`, `axiom/decision_engine/decision_core.py`

## Configuration

**Environment:**
- Single env var: `RULE_ENGINE_MODE` — controls which rule engine runs (`"python"` or `"database"`); defaults to `"python"` if unset; read in `axiom/config.py`
- Flutter API URL: `AXIOM_API_URL` — passed at build time via `--dart-define`; defaults to `http://127.0.0.1:8000`; consumed in `axiom_dashboard/lib/services/axiom_api.dart`
- No `.env` file management detected — environment vars set manually via shell or `set` command

**Build:**
- No `pyproject.toml`, `setup.py`, or `Makefile` present
- No Dockerfile or container configuration detected
- Flutter web build: standard `flutter build web` using `axiom_dashboard/pubspec.yaml`

## Platform Requirements

**Development:**
- Python 3.10+ (for union type hints `X | Y` and dict/list generics without `from __future__` import)
- Flutter SDK with Dart `>=3.3.0`
- Chrome browser for Flutter web dev target
- pip for backend dependency installation

**Production:**
- Backend: Any ASGI-capable host (uvicorn serves directly; no Nginx or proxy config present)
- Frontend: Flutter Web output at `axiom_dashboard/build/web/` — serves as static HTML/JS
- No cloud provider, containerization, or CI/CD configuration detected

## Data Storage

**No external database.** All persistence is file-based:
- Rules: `axiom/rule_platform/rules.csv` — CSV file, read/written by `axiom/rule_platform/rule_repository.py`
- Decision log: `axiom/logs/decision_log.json` — append-only JSON array, written by `axiom/rule_platform/rule_engine_db.py`
- Both paths are relative to the Python package root, resolved via `pathlib.Path(__file__)`

---

*Stack analysis: 2026-03-30*
