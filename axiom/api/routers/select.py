from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from axiom.db.engine import get_db
from axiom.db.models import Decision
from axiom.models.schemas import SelectRequest, SelectResponse

router = APIRouter(prefix="/api", tags=["select"])

@router.post("/select", response_model=SelectResponse)
def api_select(request: SelectRequest, db: Session = Depends(get_db)):
    decision = db.query(Decision).filter(Decision.id == request.decision_id).first()
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")
    if decision.status != "APPROVED":
        raise HTTPException(status_code=400, detail=f"Cannot select option for decision with status {decision.status}")

    decision.selected_option = request.selected_option
    decision.operator_notes = request.operator_notes
    db.commit()
    db.refresh(decision)

    return SelectResponse(
        id=decision.id,
        status="CONFIRMED",
        selected_option=decision.selected_option,
        pnr=decision.pnr or "",
        timestamp=decision.created_at or datetime.utcnow(),
    )
