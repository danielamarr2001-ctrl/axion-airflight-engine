from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from axiom.db.engine import get_db
from axiom.db.models import Decision
from axiom.models.schemas import PaginatedDecisions

router = APIRouter(prefix="/api", tags=["decisions"])

@router.get("/decisions", response_model=PaginatedDecisions)
def api_list_decisions(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    total = db.query(Decision).count()
    items = (
        db.query(Decision)
        .order_by(Decision.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )
    return PaginatedDecisions(
        items=items,
        total=total,
        page=page,
        per_page=per_page,
        pages=max(1, (total + per_page - 1) // per_page),
    )
