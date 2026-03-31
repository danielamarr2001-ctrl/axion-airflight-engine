from pydantic import BaseModel, Field


class ProcessRequest(BaseModel):
    """Inbound request for natural-language operational problems."""

    problem: str = Field(
        ...,
        min_length=5,
        description="Descripción del problema operativo en lenguaje natural.",
        examples=["Mi vuelo con Iberia desde Bogotá a Madrid IB156 fue cancelado."],
    )
