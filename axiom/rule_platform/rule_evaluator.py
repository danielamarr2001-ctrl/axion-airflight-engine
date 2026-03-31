from __future__ import annotations

from typing import Sequence

from axiom.rule_platform.rule_loader import load_rules
from axiom.rule_platform.rule_models import RuleRecord



def _is_missing(value: object) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == ""
    return False



def _to_number(value: object) -> float | None:
    if value is None:
        return None

    if isinstance(value, (int, float)):
        return float(value)

    if isinstance(value, str):
        text = value.strip().replace(",", ".")
        if text == "":
            return None
        try:
            return float(text)
        except ValueError:
            return None

    return None



def _evaluate(rule: RuleRecord, data: dict) -> bool:
    value = data.get(rule.field)
    operator = rule.operator

    if operator == "missing":
        return _is_missing(value)

    if operator == "=":
        left = "" if value is None else str(value).strip().lower()
        right = rule.value.strip().lower()
        return left == right

    left_number = _to_number(value)
    right_number = _to_number(rule.value)
    if left_number is None or right_number is None:
        return False

    if operator == ">":
        return left_number > right_number
    if operator == "<":
        return left_number < right_number
    if operator == ">=":
        return left_number >= right_number
    if operator == "<=":
        return left_number <= right_number

    return False



def evaluate_rules(data: dict, rules: Sequence[RuleRecord] | None = None) -> list[RuleRecord]:
    selected_rules = list(rules) if rules is not None else load_rules()

    triggered = [rule for rule in selected_rules if _evaluate(rule, data)]
    triggered.sort(key=lambda item: (item.priority, item.rule_id))
    return triggered
