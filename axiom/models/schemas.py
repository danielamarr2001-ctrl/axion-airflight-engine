"""Pydantic v2 response schemas for AXIOM API endpoints."""

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel


class SSRRecordSchema(BaseModel):
    id: int
    ssr_type: str
    ssr_detail: Optional[str] = None
    model_config = {"from_attributes": True}


class PassengerSchema(BaseModel):
    id: int
    last_name: str
    first_name: str
    ticket_number: Optional[str] = None
    fare_class: str
    fare_basis: Optional[str] = None
    passenger_type: str = "ADT"
    ssr_records: List[SSRRecordSchema] = []
    model_config = {"from_attributes": True}


class SegmentSchema(BaseModel):
    id: int
    flight_number: str
    airline: str
    origin: str
    destination: str
    departure_date: date
    departure_time: str
    arrival_time: str
    status: str
    cabin_class: str = "Y"
    aircraft_type: Optional[str] = None
    model_config = {"from_attributes": True}


class ReservationResponse(BaseModel):
    id: int
    pnr: str
    booking_reference: Optional[str] = None
    created_at: datetime
    passengers: List[PassengerSchema] = []
    segments: List[SegmentSchema] = []
    model_config = {"from_attributes": True}


class LookupRequest(BaseModel):
    pnr: str
    last_name: str


class EvaluateRequest(BaseModel):
    pnr: str
    reservation_id: int


class SelectRequest(BaseModel):
    decision_id: int
    selected_option: str
    operator_notes: str = ""


class FlightOptionSchema(BaseModel):
    id: int
    flight_number: str
    airline: str
    origin: str
    destination: str
    departure_date: date
    departure_time: str
    arrival_time: str
    available_seats: int
    fare_class: str
    aircraft_type: Optional[str] = None
    status: str = "SCHEDULED"
    model_config = {"from_attributes": True}


class RuleTraceItem(BaseModel):
    step: str
    result: str
    detail: str = ""


class EvaluateResponse(BaseModel):
    decision_id: int
    status: str  # APPROVED, REJECTED, ESCALATED
    rule_applied: str
    justification: str
    trace: List[RuleTraceItem] = []
    options: List[FlightOptionSchema] = []


class SelectResponse(BaseModel):
    id: int
    status: str  # CONFIRMED
    selected_option: str
    pnr: str
    timestamp: datetime


class DecisionSchema(BaseModel):
    id: int
    pnr: Optional[str] = None
    reservation_id: Optional[int] = None
    rule_applied: Optional[str] = None
    status: str
    justification: Optional[str] = None
    selected_option: Optional[str] = None
    processing_time_ms: Optional[int] = None
    created_at: datetime
    model_config = {"from_attributes": True}


class PaginatedDecisions(BaseModel):
    items: List[DecisionSchema] = []
    total: int
    page: int
    per_page: int
    pages: int


class MetricsResponse(BaseModel):
    total_decisions: int
    automation_rate: float  # percentage 0-100
    avg_processing_time_ms: float
    decisions_by_day: List[dict]  # [{date, count, approved, escalated, rejected}]
    top_rules: List[dict]  # [{rule, count}]
    decisions_by_status: dict  # {APPROVED: int, REJECTED: int, ESCALATED: int}


class RuleSchema(BaseModel):
    id: int
    field: str
    operator: str
    value: str
    action: str
    priority: int
    active: bool
    created_at: datetime
    model_config = {"from_attributes": True}


class RuleCreateSchema(BaseModel):
    field: str
    operator: str
    value: str = ""
    action: str
    priority: int = 1
    active: bool = True


class RuleUpdateSchema(BaseModel):
    field: Optional[str] = None
    operator: Optional[str] = None
    value: Optional[str] = None
    action: Optional[str] = None
    priority: Optional[int] = None
    active: Optional[bool] = None
