from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from axiom.db.engine import get_db
from axiom.models.schemas import LookupRequest, ReservationResponse
from axiom.services.lookup_service import lookup_reservation

router = APIRouter(prefix="/api", tags=["lookup"])

@router.post("/lookup", response_model=ReservationResponse)
def api_lookup(request: LookupRequest, db: Session = Depends(get_db)):
    reservation = lookup_reservation(db, request.pnr, request.last_name)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found or last name does not match")
    return reservation
