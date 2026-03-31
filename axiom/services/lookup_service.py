from sqlalchemy.orm import Session
from axiom.db.models import Reservation

def lookup_reservation(db: Session, pnr: str, last_name: str) -> Reservation | None:
    """Look up reservation by PNR and verify passenger last name."""
    reservation = (
        db.query(Reservation)
        .filter(Reservation.pnr == pnr.upper().strip())
        .first()
    )
    if not reservation:
        return None
    # Check at least one passenger matches the last name
    match = any(
        p.last_name.upper() == last_name.upper().strip()
        for p in reservation.passengers
    )
    if not match:
        return None
    return reservation
