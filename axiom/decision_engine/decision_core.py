import re
import time
from typing import List

from axiom.config import RULE_ENGINE_MODE
from axiom.decision_engine.event_classifier import classify_event
from axiom.decision_engine.options_generator import generate_flight_options
from axiom.decision_engine.rule_engine import execute_rules
from axiom.decision_engine.validators import validate_problem
from axiom.models.response import (
    FlightOption,
    OriginalFlightSummary,
    ProcessResponse,
    TriggeredRuleSummary,
    ValidationResult,
)
from axiom.rule_platform.rule_engine_db import RuleEngineDB, append_decision_log

_ALLOWED_RULE_ENGINES = {"python", "database"}


class DecisionCore:
    """Orchestrates the AXIOM decision flow."""

    flow: List[str] = ["INPUT", "VALIDACION", "CLASIFICACION", "REGLAS", "OPCIONES", "ACCION"]

    def __init__(self, rule_engine_mode: str | None = None):
        selected_mode = (rule_engine_mode or RULE_ENGINE_MODE).strip().lower()
        self.rule_engine_mode = selected_mode if selected_mode in _ALLOWED_RULE_ENGINES else "python"
        self.db_engine = RuleEngineDB()

    # ---------------------------------------------------------
    # TEXT PARSER (NUEVO)
    # ---------------------------------------------------------

    @staticmethod
    def _extract_field(problem: str, label: str):
        pattern = rf"{label}\s*:\s*(.+)"
        match = re.search(pattern, problem, re.IGNORECASE)
        return match.group(1).strip() if match else None

    @staticmethod
    def _extract_delay_minutes(problem: str) -> int:
        match = re.search(r"delay_minutes\s*:\s*(\d+)", problem.lower())
        if match:
            return int(match.group(1))

        match = re.search(r"(\d{1,4})\s*(?:min|minutos)", problem.lower())
        if match:
            return int(match.group(1))

        return 0

    # ---------------------------------------------------------

    def _build_action_required(self, approved: bool, options: list[FlightOption]) -> str:
        available_options = [item for item in options if item.status == "disponible"]

        if approved and available_options:
            return (
                f"Confirmar reproteccion del pasajero al vuelo {available_options[0].flight} "
                "y emitir boleto sin penalidad."
            )

        if approved:
            return "Buscar alternativa equivalente y confirmar disponibilidad manualmente."

        return "Escalar el caso para revision operativa manual."

    # ---------------------------------------------------------

    def process(self, problem: str) -> ProcessResponse:

        start = time.perf_counter()
        audit_trace: List[str] = [f"input_received={len(problem)}_chars"]

        # -------------------------------------------
        # EXTRAER CAMPOS DEL TEXTO
        # -------------------------------------------

        parsed_pnr = self._extract_field(problem, "PNR")
        parsed_passenger = self._extract_field(problem, "Passenger")
        parsed_event = self._extract_field(problem, "event_type")
        parsed_delay = self._extract_delay_minutes(problem)

        # -------------------------------------------

        validation_payload = validate_problem(problem)

        # Si el validador no detectó datos, usamos el parser
        if not validation_payload["details"].get("pnr") and parsed_pnr:
            validation_payload["details"]["pnr"] = parsed_pnr

        if not validation_payload["details"].get("passenger") and parsed_passenger:
            validation_payload["details"]["passenger"] = parsed_passenger

        validation = ValidationResult(**validation_payload["validation"])
        audit_trace.append(f"validation={validation.model_dump()}")

        # -------------------------------------------------------
        # BLOQUEO SI FALTAN DATOS CRITICOS
        # -------------------------------------------------------

        if validation_payload["missing_critical"]:

            audit_trace.append("classification=skipped")
            audit_trace.append("rules=blocked_by_validation")

            elapsed_ms = int((time.perf_counter() - start) * 1000)

            response = ProcessResponse(
                status="RECHAZADO",
                event_type="Pendiente de datos obligatorios",
                validation=validation,
                rule_applied="Datos obligatorios faltantes",
                justification="No es posible continuar el analisis sin PNR y nombre del pasajero.",
                options=[],
                action_required="Proporcionar PNR y nombre del pasajero.",
                analysis_time_ms=elapsed_ms,
                flow=self.flow,
                original_flight=OriginalFlightSummary(),
                audit_trace=audit_trace,
                engine_mode=self.rule_engine_mode,
                triggered_rules=[],
            )

            append_decision_log(
                event_type=response.event_type,
                rule_triggered=response.rule_applied,
                action=response.action_required or "",
                processing_time_ms=elapsed_ms,
            )

            return response

        # -------------------------------------------------------
        # CLASIFICACION
        # -------------------------------------------------------

        classification = classify_event(problem)
        audit_trace.append(f"event_type={classification['event_type']}")

        # -------------------------------------------------------
        # CONTEXTO PARA REGLAS
        # -------------------------------------------------------

        evaluation_context = {
            "event_type": parsed_event or (
                "delay" if classification["event_type"] == "Demora operacional" else "cancellation"
            ),
            "delay_minutes": parsed_delay,
            "passenger_name": validation_payload["details"]["passenger"],
            "pnr": validation_payload["details"]["pnr"],
            "flight_cancelled": classification["flight_cancelled"],
            "same_airline": classification["same_airline"],
            "same_route": classification["same_route"],
            "has_sensitive_ssr": classification["has_sensitive_ssr"],
            "same_fare_class": classification["same_fare_class"],
        }

        action_required: str | None = None
        triggered_rules: list[TriggeredRuleSummary] = []

        # -------------------------------------------------------
        # RULE ENGINE
        # -------------------------------------------------------

        if self.rule_engine_mode == "database":

            db_result = self.db_engine.evaluate(evaluation_context)

            audit_trace.append("engine_mode=database")
            audit_trace.extend(db_result.get("trace", []))

            if db_result.get("applied"):

                rule_result = {
                    "status": db_result["status"],
                    "rule_applied": db_result["rule_applied"],
                    "justification": db_result["justification"],
                    "trace": db_result.get("trace", []),
                }

                action_required = db_result.get("action_required")

                triggered_rules = [
                    TriggeredRuleSummary(**item.model_dump())
                    for item in db_result.get("triggered_rules", [])
                ]

            else:

                audit_trace.append("rule_platform=fallback_python")
                rule_result = execute_rules(classification, validation_payload)
                audit_trace.extend(rule_result.get("trace", []))

        else:

            audit_trace.append("engine_mode=python")

            rule_result = execute_rules(classification, validation_payload)

            audit_trace.extend(rule_result.get("trace", []))

        # -------------------------------------------------------
        # GENERAR OPCIONES
        # -------------------------------------------------------

        approved = rule_result["status"] == "APROBADO"

        options = [
            FlightOption(**item)
            for item in generate_flight_options(classification, approved)
        ]

        if not action_required:
            action_required = self._build_action_required(approved, options)

        # -------------------------------------------------------
        # RESPUESTA FINAL
        # -------------------------------------------------------

        elapsed_ms = int((time.perf_counter() - start) * 1000)

        response = ProcessResponse(
            status=rule_result["status"],
            event_type=classification["event_type"],
            validation=validation,
            rule_applied=rule_result["rule_applied"],
            justification=rule_result["justification"],
            options=options,
            action_required=action_required,
            analysis_time_ms=elapsed_ms,
            flow=self.flow,
            original_flight=OriginalFlightSummary(**classification["original_flight"]),
            audit_trace=audit_trace,
            engine_mode=self.rule_engine_mode,
            triggered_rules=triggered_rules,
        )

        append_decision_log(
            event_type=response.event_type,
            rule_triggered=response.rule_applied,
            action=response.action_required or "",
            processing_time_ms=elapsed_ms,
        )

        return response