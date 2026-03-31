from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from axiom.decision_engine.decision_core import DecisionCore
from axiom.models.request import ProcessRequest
from axiom.models.response import ProcessResponse
from axiom.rule_platform.rule_engine_db import compute_metrics
from axiom.rule_platform.rule_models import RuleCreate, RuleRecord, RuleUpdate
from axiom.rule_platform.rule_repository import RuleRepository

import os
from axiom.db.engine import init_db, SessionLocal
from axiom.db.models import Reservation
from axiom.api.routers import lookup, evaluate, select, decisions, metrics, rules_api

app = FastAPI(
    title="AXIOM Decision Intelligence API",
    description="Motor de decisiones explicable para operaciones empresariales.",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

core = DecisionCore()
rule_repository = RuleRepository()

# Initialize database tables and seed if empty (serverless cold start)
init_db()
_db = SessionLocal()
if _db.query(Reservation).count() == 0:
    _db.close()
    from axiom.db.seed import seed_database
    seed_database()
else:
    _db.close()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/process", response_model=ProcessResponse)
def process(request: ProcessRequest) -> ProcessResponse:
    return core.process(request.problem)


@app.get("/rules", response_model=list[RuleRecord])
def get_rules() -> list[RuleRecord]:
    return rule_repository.get_rules()


@app.post("/rules", response_model=RuleRecord)
def add_rule(payload: RuleCreate) -> RuleRecord:
    return rule_repository.add_rule(payload)


@app.put("/rules/{rule_id}", response_model=RuleRecord)
def update_rule(rule_id: int, payload: RuleUpdate) -> RuleRecord:
    updated = rule_repository.update_rule(rule_id, payload)
    if updated is None:
        raise HTTPException(status_code=404, detail="Rule not found")
    return updated


@app.delete("/rules/{rule_id}")
def delete_rule(rule_id: int) -> dict[str, Any]:
    deleted = rule_repository.delete_rule(rule_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Rule not found")
    return {"deleted": True, "rule_id": rule_id}


@app.get("/metrics")
def get_metrics() -> dict[str, Any]:
    return compute_metrics()


# New structured API endpoints (frontend uses these)
app.include_router(lookup.router)
app.include_router(evaluate.router)
app.include_router(select.router)
app.include_router(decisions.router)
app.include_router(metrics.router)
app.include_router(rules_api.router)
