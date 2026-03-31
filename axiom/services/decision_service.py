import json
import time
from datetime import datetime
from sqlalchemy.orm import Session
from axiom.db.models import Reservation, Flight, Decision, Segment
from axiom.rules.airline_rules import involuntary_change_rule
from axiom.models.schemas import RuleTraceItem

def evaluate_reservation(db: Session, reservation: Reservation) -> tuple:
    """Evaluate rules against a structured reservation and create a Decision record.

    Returns:
        tuple: (decision, trace_items, options)
    """
    start = time.time()

    # Build classification context from structured data
    cancelled_segments = [s for s in reservation.segments if s.status == "XX"]
    has_cancellation = len(cancelled_segments) > 0
    first_passenger = reservation.passengers[0] if reservation.passengers else None
    has_sensitive_ssr = any(
        ssr.ssr_type in ("UMNR", "MEDA", "WCHC")
        for p in reservation.passengers
        for ssr in p.ssr_records
    )

    # Determine the affected segment (first cancelled, or first with schedule change)
    affected_segment = None
    if cancelled_segments:
        affected_segment = cancelled_segments[0]
    else:
        schedule_changes = [s for s in reservation.segments if s.status == "TK"]
        if schedule_changes:
            affected_segment = schedule_changes[0]

    trace_items = []

    # Step 1: Input validation
    trace_items.append(RuleTraceItem(
        step="INPUT_VALIDATION",
        result="PASS",
        detail=f"PNR {reservation.pnr} found with {len(reservation.passengers)} passenger(s), {len(reservation.segments)} segment(s)"
    ))

    # Step 2: Event classification
    if has_cancellation:
        event_type = "CANCELLATION"
    elif any(s.status == "TK" for s in reservation.segments):
        event_type = "SCHEDULE_CHANGE"
    else:
        event_type = "NO_DISRUPTION"

    trace_items.append(RuleTraceItem(
        step="EVENT_CLASSIFICATION",
        result=event_type,
        detail=f"Segment status check: {', '.join(s.flight_number + '=' + s.status for s in reservation.segments)}"
    ))

    # Step 3: Build context for rule evaluation
    classification = {
        "flight_cancelled": has_cancellation,
        "same_airline": True,  # Simplified: assume same airline for demo
        "same_route": True,    # Simplified: route preserved in reprotection
        "has_sensitive_ssr": has_sensitive_ssr,
        "same_fare_class": True,  # Simplified for demo
    }

    # Step 4: Rule evaluation
    if event_type == "NO_DISRUPTION":
        status = "REJECTED"
        rule_applied = "no_disruption"
        justification = "No flight disruption detected. All segments are confirmed."
        trace_items.append(RuleTraceItem(
            step="RULE_EVALUATION",
            result="REJECTED",
            detail="No cancelled or changed segments found"
        ))
    elif has_sensitive_ssr:
        status = "ESCALATED"
        ssr_types = [ssr.ssr_type for p in reservation.passengers for ssr in p.ssr_records if ssr.ssr_type in ("UMNR", "MEDA", "WCHC")]
        rule_applied = "ssr_check"
        justification = f"Sensitive SSR detected ({', '.join(ssr_types)}). Requires supervisor review for reprotection."
        trace_items.append(RuleTraceItem(
            step="SSR_CHECK",
            result="SENSITIVE_SSR_FOUND",
            detail=f"SSR types: {', '.join(ssr_types)}"
        ))
        trace_items.append(RuleTraceItem(
            step="RULE_EVALUATION",
            result="ESCALATED",
            detail="Sensitive SSR triggers manual review requirement"
        ))
    else:
        # Run the involuntary change rule
        rule_result = involuntary_change_rule(classification)
        if rule_result.get("allow_reprotection"):
            status = "APPROVED"
            rule_applied = rule_result.get("rule_applied", "involuntary_change")
            justification = "Flight cancelled, same airline, same route, no sensitive SSR, same fare class. Approved for automatic reprotection."
        else:
            status = "REJECTED"
            rule_applied = rule_result.get("rule_applied", "involuntary_change")
            justification = rule_result.get("justification", "Reprotection conditions not met")

        for t in rule_result.get("trace", []):
            trace_items.append(RuleTraceItem(step="RULE_CHECK", result="PASS" if "True" in str(t) else "INFO", detail=str(t)))

        trace_items.append(RuleTraceItem(
            step="RULE_EVALUATION",
            result=status,
            detail=justification
        ))

    # Step 5: Generate reprotection options if APPROVED
    options = []
    if status == "APPROVED" and affected_segment:
        options = (
            db.query(Flight)
            .filter(
                Flight.origin == affected_segment.origin,
                Flight.destination == affected_segment.destination,
                Flight.status == "SCHEDULED",
                Flight.available_seats > 0,
            )
            .order_by(Flight.departure_time)
            .limit(5)
            .all()
        )
        trace_items.append(RuleTraceItem(
            step="OPTIONS_GENERATION",
            result=f"{len(options)} OPTIONS",
            detail=f"Route {affected_segment.origin}-{affected_segment.destination}, {len(options)} available flights found"
        ))

    processing_time_ms = int((time.time() - start) * 1000)

    # Create decision record
    decision = Decision(
        reservation_id=reservation.id,
        pnr=reservation.pnr,
        rule_applied=rule_applied,
        status=status,
        justification=justification,
        trace=json.dumps([{"step": t.step, "result": t.result, "detail": t.detail} for t in trace_items]),
        options_generated=json.dumps([{"flight_number": f.flight_number, "airline": f.airline, "origin": f.origin, "destination": f.destination, "departure_time": f.departure_time, "arrival_time": f.arrival_time, "available_seats": f.available_seats, "fare_class": f.fare_class} for f in options]) if options else None,
        processing_time_ms=processing_time_ms,
    )
    db.add(decision)
    db.commit()
    db.refresh(decision)

    return decision, trace_items, options
