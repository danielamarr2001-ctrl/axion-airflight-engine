import re
from typing import Any, Dict

# Acepta PNR de 4 a 6 caracteres (ej: AX123, ABC123)
PNR_PATTERN = re.compile(r"\b([A-Z0-9]{4,6})\b")

# Acepta etiquetas:
# Passenger:
# Pasajero:
# Nombre:
# Nombre del pasajero:
PASSENGER_PATTERN = re.compile(
    r"(?:passenger|pasajero|nombre(?: del pasajero)?)\s*[:\-]?\s*([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s]{2,})",
    re.IGNORECASE,
)


def validate_problem(problem: str) -> Dict[str, Any]:
    normalized = " ".join(problem.strip().split())

    pnr_match = PNR_PATTERN.search(normalized.upper())
    passenger_match = PASSENGER_PATTERN.search(normalized)

    pnr_status = "present" if pnr_match else "missing"
    passenger_status = "present" if passenger_match else "unknown"

    return {
        "validation": {
            "pnr": pnr_status,
            "passenger": passenger_status,
        },
        "missing_critical": pnr_status != "present" or passenger_status != "present",
        "details": {
            "pnr": pnr_match.group(1) if pnr_match else None,
            "passenger": passenger_match.group(1).strip() if passenger_match else None,
        },
    }