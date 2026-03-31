import re
from typing import Any, Dict

AIRLINES = {
    "iberia": "Iberia",
    "latam": "LATAM",
    "avianca": "Avianca",
    "air europa": "Air Europa",
    "air france": "Air France",
    "klm": "KLM",
}
SENSITIVE_SSR_KEYWORDS = [
    "silla de ruedas",
    "oxigeno",
    "oxígeno",
    "unaccompanied",
    "menor no acompañado",
    "medical",
    "medico",
    "médico",
    "ssr",
]



def _extract_route(lower_problem: str) -> str:
    match = re.search(
        r"desde\s+([a-záéíóúñ\s]+?)\s+(?:a|hasta)\s+([a-záéíóúñ\s]+?)(?:\.|,|\scon\s|\svuelo\s|\sib\d+|$)",
        lower_problem,
    )
    if not match:
        return "unknown"

    origin = " ".join(match.group(1).split()).title()
    destination = " ".join(match.group(2).split()).title()
    return f"{origin} - {destination}"



def _detect_airline(lower_problem: str) -> str:
    for key, value in AIRLINES.items():
        if key in lower_problem:
            return value
    return "unknown"



def _extract_flight(problem: str) -> str:
    match = re.search(r"\b([A-Z]{2}\d{2,4})\b", problem, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    return "unknown"



def classify_event(problem: str) -> Dict[str, Any]:
    lower_problem = problem.lower()
    airline = _detect_airline(lower_problem)
    route = _extract_route(lower_problem)
    flight_number = _extract_flight(problem)

    is_cancelled = any(
        keyword in lower_problem
        for keyword in ["cancelado", "cancelada", "cancelaron", "canceled", "cancelled"]
    )
    is_delayed = any(
        keyword in lower_problem
        for keyword in ["demora", "retraso", "delayed", "delay"]
    )

    if is_cancelled:
        event_type = "Cancelación de vuelo por parte de la aerolínea"
    elif is_delayed:
        event_type = "Demora operacional"
    else:
        event_type = "Evento operacional no clasificado"

    has_sensitive_ssr = any(keyword in lower_problem for keyword in SENSITIVE_SSR_KEYWORDS)
    same_fare_class = not any(
        keyword in lower_problem for keyword in ["upgrade", "downgrade", "cambio de cabina", "cambio de clase"]
    )

    return {
        "event_type": event_type,
        "flight_cancelled": is_cancelled,
        "same_airline": airline != "unknown",
        "same_route": route != "unknown",
        "has_sensitive_ssr": has_sensitive_ssr,
        "same_fare_class": same_fare_class,
        "original_flight": {
            "airline": airline,
            "flight": flight_number,
            "route": route,
            "date": "unknown",
            "status": "cancelado" if is_cancelled else "reportado",
        },
    }
