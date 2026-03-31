from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from axiom.db.engine import get_db
from axiom.models.schemas import MetricsResponse
from axiom.services.metrics_service import compute_metrics_from_db

router = APIRouter(prefix="/api", tags=["metrics"])

@router.get("/metrics", response_model=MetricsResponse)
def api_metrics(db: Session = Depends(get_db)):
    return compute_metrics_from_db(db)
