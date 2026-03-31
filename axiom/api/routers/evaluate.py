import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from axiom.db.engine import get_db
from axiom.db.models import Reservation
from axiom.models.schemas import EvaluateRequest, EvaluateResponse, FlightOptionSchema, RuleTraceItem
from axiom.services.decision_service import evaluate_reservation

router = APIRouter(prefix="/api", tags=["evaluate"])

@router.post("/evaluate", response_model=EvaluateResponse)
def api_evaluate(request: EvaluateRequest, db: Session = Depends(get_db)):
    reservation = db.query(Reservation).filter(Reservation.pnr == request.pnr.upper()).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")

    decision, trace_items, options = evaluate_reservation(db, reservation)

    return EvaluateResponse(
        decision_id=decision.id,
        status=decision.status,
        rule_applied=decision.rule_applied or "",
        justification=decision.justification or "",
        trace=trace_items,
        options=[FlightOptionSchema.model_validate(o) for o in options],
    )
