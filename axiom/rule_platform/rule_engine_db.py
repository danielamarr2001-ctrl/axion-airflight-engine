from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

from axiom.rule_platform.rule_evaluator import evaluate_rules
from axiom.rule_platform.rule_models import TriggeredRule
from axiom.rule_platform.rule_repository import RuleRepository

LOG_PATH = Path(__file__).resolve().parents[1] / "logs" / "decision_log.json"

_ACTION_MESSAGES = {
    "offer_voucher": "Aplicar compensacion por demora y emitir voucher.",
    "process_delay": "Procesar el caso de demora bajo politica vigente.",
    "request_name": "Solicitar nombre del pasajero para continuar.",
    "request_pnr": "Solicitar PNR para continuar.",
}



def _ensure_log_file() -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not LOG_PATH.exists():
        LOG_PATH.write_text("[]\n", encoding="utf-8")



def _read_log() -> list[dict]:
    _ensure_log_file()
    try:
        content = LOG_PATH.read_text(encoding="utf-8").lstrip("\ufeff").strip()
        if not content:
            return []
        parsed = json.loads(content)
        if isinstance(parsed, list):
            return parsed
    except json.JSONDecodeError:
        pass
    return []



def _write_log(items: list[dict]) -> None:
    _ensure_log_file()
    LOG_PATH.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")



def append_decision_log(
    *,
    event_type: str,
    rule_triggered: str,
    action: str,
    processing_time_ms: int,
) -> None:
    logs = _read_log()
    logs.append(
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "rule_triggered": rule_triggered,
            "action": action,
            "processing_time_ms": processing_time_ms,
        }
    )
    _write_log(logs)



def compute_metrics() -> dict:
    logs = _read_log()
    total = len(logs)

    if total == 0:
        return {
            "total_requests": 0,
            "rules_triggered": [],
            "avg_processing_time_ms": 0.0,
            "manual_reviews": 0,
            "decisions_per_day": [],
            "top_triggered_rules": [],
            "latency_series_ms": [],
        }

    avg_processing = round(
        sum(float(item.get("processing_time_ms", 0.0)) for item in logs) / total,
        2,
    )

    rule_counter: Counter[str] = Counter(
        str(item.get("rule_triggered", "unknown")) for item in logs
    )
    rules_triggered = [
        {"rule": rule_name, "count": count}
        for rule_name, count in rule_counter.most_common()
    ]

    manual_reviews = sum(
        1
        for item in logs
        if "manual" in str(item.get("action", "")).lower()
        or "escalar" in str(item.get("action", "")).lower()
        or "request_" in str(item.get("rule_triggered", "")).lower()
    )

    # last 14 days grouped counts
    now = datetime.now(timezone.utc)
    day_counter: Counter[str] = Counter()
    for item in logs:
        raw_ts = str(item.get("timestamp", ""))
        try:
            ts = datetime.fromisoformat(raw_ts.replace("Z", "+00:00"))
        except ValueError:
            continue
        day_counter[ts.date().isoformat()] += 1

    decisions_per_day: list[dict[str, int | str]] = []
    for offset in range(13, -1, -1):
        day = (now - timedelta(days=offset)).date().isoformat()
        decisions_per_day.append({"day": day, "count": int(day_counter.get(day, 0))})

    top_triggered_rules = rules_triggered[:5]

    latency_series_ms = [
        float(item.get("processing_time_ms", 0.0))
        for item in logs[-30:]
    ]

    return {
        "total_requests": total,
        "rules_triggered": rules_triggered,
        "avg_processing_time_ms": avg_processing,
        "manual_reviews": manual_reviews,
        "decisions_per_day": decisions_per_day,
        "top_triggered_rules": top_triggered_rules,
        "latency_series_ms": latency_series_ms,
    }


class RuleEngineDB:
    """Table-based rule engine backed by CSV repository."""

    def __init__(self, repository: RuleRepository | None = None):
        self.repository = repository or RuleRepository()

    def evaluate(self, data: dict) -> dict:
        rules = self.repository.get_rules()
        triggered = evaluate_rules(data, rules)

        if not triggered:
            return {
                "applied": False,
                "status": "RECHAZADO",
                "rule_applied": "Sin regla en tabla",
                "justification": "No se dispararon reglas de la plataforma tabular.",
                "action_required": "Escalar el caso para revision manual.",
                "trace": ["rule_platform=no_match"],
                "triggered_rules": [],
                "manual_review": True,
            }

        top = triggered[0]
        action = top.action

        manual_review = action.startswith("request_")
        status = "RECHAZADO" if manual_review else "APROBADO"
        action_required = _ACTION_MESSAGES.get(action, f"Ejecutar accion de regla: {action}.")

        trace = [f"rule_id={rule.rule_id},action={rule.action}" for rule in triggered]

        return {
            "applied": True,
            "status": status,
            "rule_applied": f"RulePlatform::{action}",
            "justification": f"Regla tabular activada con prioridad {top.priority}.",
            "action_required": action_required,
            "trace": trace,
            "triggered_rules": [TriggeredRule(**rule.model_dump()) for rule in triggered],
            "manual_review": manual_review,
        }
