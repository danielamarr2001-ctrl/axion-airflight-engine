from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

SUPPORTED_OPERATORS = {"=", ">", "<", ">=", "<=", "missing"}


class RuleBase(BaseModel):
    field: str = Field(..., min_length=1)
    operator: str = Field(..., min_length=1)
    value: str = ""
    action: str = Field(..., min_length=1)
    priority: int = Field(default=1, ge=1)

    @field_validator("field", "action")
    @classmethod
    def sanitize_text(cls, value: str) -> str:
        return value.strip()

    @field_validator("operator")
    @classmethod
    def validate_operator(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in SUPPORTED_OPERATORS:
            raise ValueError(f"Unsupported operator: {value}")
        return normalized

    @field_validator("value")
    @classmethod
    def sanitize_value(cls, value: str) -> str:
        return value.strip()


class RuleCreate(RuleBase):
    pass


class RuleUpdate(BaseModel):
    field: str | None = None
    operator: str | None = None
    value: str | None = None
    action: str | None = None
    priority: int | None = Field(default=None, ge=1)

    @field_validator("field", "action")
    @classmethod
    def sanitize_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return value.strip()

    @field_validator("operator")
    @classmethod
    def validate_optional_operator(cls, value: str | None) -> str | None:
        if value is None:
            return value
        normalized = value.strip().lower()
        if normalized not in SUPPORTED_OPERATORS:
            raise ValueError(f"Unsupported operator: {value}")
        return normalized

    @field_validator("value")
    @classmethod
    def sanitize_optional_value(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return value.strip()


class RuleRecord(RuleBase):
    rule_id: int = Field(..., ge=1)


class TriggeredRule(BaseModel):
    rule_id: int
    field: str
    operator: str
    value: str
    action: str
    priority: int


class MetricsSummary(BaseModel):
    total_requests: int
    rules_triggered: list[dict[str, int | str]]
    avg_processing_time_ms: float
    manual_reviews: int
    decisions_per_day: list[dict[str, int | str]] = Field(default_factory=list)
    top_triggered_rules: list[dict[str, int | str]] = Field(default_factory=list)
    latency_series_ms: list[float] = Field(default_factory=list)
