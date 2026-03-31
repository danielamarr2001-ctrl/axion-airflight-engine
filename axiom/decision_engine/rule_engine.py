from typing import Any, Dict

from axiom.rules.airline_rules import involuntary_change_rule



def execute_rules(classification: Dict[str, Any], validation: Dict[str, Any]) -> Dict[str, Any]:
    if validation.get("missing_critical", False):
        return {
            "status": "RECHAZADO",
            "rule_applied": "Datos obligatorios faltantes",
            "justification": "No es posible ejecutar reglas de elegibilidad sin PNR y nombre del pasajero.",
            "trace": ["validation_blocked=True"],
        }

    rule_result = involuntary_change_rule(classification)
    if rule_result["allow_reprotection"]:
        return {
            "status": "APROBADO",
            "rule_applied": rule_result["rule_applied"],
            "justification": rule_result["justification"],
            "trace": rule_result["trace"],
        }

    return {
        "status": "RECHAZADO",
        "rule_applied": rule_result["rule_applied"],
        "justification": rule_result["justification"],
        "trace": rule_result["trace"],
    }
