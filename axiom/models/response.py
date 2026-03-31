from typing import List, Optional

from pydantic import BaseModel, Field


class ValidationResult(BaseModel):
    pnr: str
    passenger: str


class FlightOption(BaseModel):
    flight: str
    time: str
    status: str


class OriginalFlightSummary(BaseModel):
    airline: str = "unknown"
    flight: str = "unknown"
    route: str = "unknown"
    date: str = "unknown"
    status: str = "unknown"


class TriggeredRuleSummary(BaseModel):
    rule_id: int
    field: str
    operator: str
    value: str
    action: str
    priority: int


class ProcessResponse(BaseModel):
    status: str
    event_type: str
    validation: ValidationResult
    rule_applied: str
    justification: str
    options: List[FlightOption] = Field(default_factory=list)
    action_required: Optional[str] = None
    analysis_time_ms: int
    flow: List[str] = Field(default_factory=list)
    original_flight: OriginalFlightSummary
    audit_trace: List[str] = Field(default_factory=list)
    engine_mode: str = "python"
    triggered_rules: List[TriggeredRuleSummary] = Field(default_factory=list)
