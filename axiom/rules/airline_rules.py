from typing import Any, Dict



def involuntary_change_rule(context: Dict[str, Any]) -> Dict[str, Any]:
    checks = {
        "flight_cancelled": bool(context.get("flight_cancelled")),
        "same_airline": bool(context.get("same_airline")),
        "same_route": bool(context.get("same_route")),
        "no_sensitive_ssr": not bool(context.get("has_sensitive_ssr")),
        "same_fare_class": bool(context.get("same_fare_class")),
    }

    allow_reprotection = all(checks.values())
    trace = [f"{key}={value}" for key, value in checks.items()]

    if allow_reprotection:
        return {
            "allow_reprotection": True,
            "rule_applied": "involuntary_change",
            "justification": "Fare protection conditions met. Approved for reprotection on equivalent flight.",
            "trace": trace,
        }

    return {
        "allow_reprotection": False,
        "rule_applied": "involuntary_change",
        "justification": "Not all conditions met for penalty-free reprotection.",
        "trace": trace,
    }
