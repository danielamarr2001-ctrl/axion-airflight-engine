from sqlalchemy.orm import Session
from sqlalchemy import func, case
from axiom.db.models import Decision
from collections import defaultdict

def compute_metrics_from_db(db: Session) -> dict:
    """Compute KPI metrics from decision records in the database."""
    total = db.query(Decision).count()
    if total == 0:
        return {
            "total_decisions": 0,
            "automation_rate": 0.0,
            "avg_processing_time_ms": 0.0,
            "decisions_by_day": [],
            "top_rules": [],
            "decisions_by_status": {"APPROVED": 0, "REJECTED": 0, "ESCALATED": 0},
        }

    # Automation rate: APPROVED / total * 100
    approved_count = db.query(Decision).filter(Decision.status == "APPROVED").count()
    automation_rate = round((approved_count / total) * 100, 1)

    # Average processing time
    avg_time_result = db.query(func.avg(Decision.processing_time_ms)).scalar()
    avg_processing_time_ms = round(float(avg_time_result or 0), 1)

    # Decisions by status
    status_counts = (
        db.query(Decision.status, func.count(Decision.id))
        .group_by(Decision.status)
        .all()
    )
    decisions_by_status = {s: 0 for s in ["APPROVED", "REJECTED", "ESCALATED"]}
    for status, count in status_counts:
        decisions_by_status[status] = count

    # Decisions by day (last 14 days worth of data)
    daily_query = (
        db.query(
            func.date(Decision.created_at).label("day"),
            func.count(Decision.id).label("count"),
            func.sum(case((Decision.status == "APPROVED", 1), else_=0)).label("approved"),
            func.sum(case((Decision.status == "ESCALATED", 1), else_=0)).label("escalated"),
            func.sum(case((Decision.status == "REJECTED", 1), else_=0)).label("rejected"),
        )
        .group_by(func.date(Decision.created_at))
        .order_by(func.date(Decision.created_at))
        .all()
    )
    decisions_by_day = [
        {
            "date": str(row.day),
            "count": row.count,
            "approved": int(row.approved or 0),
            "escalated": int(row.escalated or 0),
            "rejected": int(row.rejected or 0),
        }
        for row in daily_query
    ]

    # Top rules
    top_rules_query = (
        db.query(Decision.rule_applied, func.count(Decision.id).label("count"))
        .filter(Decision.rule_applied.isnot(None))
        .group_by(Decision.rule_applied)
        .order_by(func.count(Decision.id).desc())
        .limit(10)
        .all()
    )
    top_rules = [{"rule": row.rule_applied, "count": row.count} for row in top_rules_query]

    return {
        "total_decisions": total,
        "automation_rate": automation_rate,
        "avg_processing_time_ms": avg_processing_time_ms,
        "decisions_by_day": decisions_by_day,
        "top_rules": top_rules,
        "decisions_by_status": decisions_by_status,
    }
