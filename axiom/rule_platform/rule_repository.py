from __future__ import annotations

import csv
import threading
from pathlib import Path

from axiom.rule_platform.rule_loader import DEFAULT_RULES_PATH, load_rules
from axiom.rule_platform.rule_models import RuleCreate, RuleRecord, RuleUpdate

_HEADERS = ["rule_id", "field", "operator", "value", "action", "priority"]


class RuleRepository:
    def __init__(self, csv_path: Path | str = DEFAULT_RULES_PATH):
        self.csv_path = Path(csv_path)
        self._lock = threading.Lock()

    def get_rules(self) -> list[RuleRecord]:
        rules = load_rules(self.csv_path)
        rules.sort(key=lambda item: (item.priority, item.rule_id))
        return rules

    def add_rule(self, new_rule: RuleCreate) -> RuleRecord:
        with self._lock:
            rules = load_rules(self.csv_path)
            next_id = max((rule.rule_id for rule in rules), default=0) + 1
            created = RuleRecord(rule_id=next_id, **new_rule.model_dump())
            rules.append(created)
            self._save(rules)
            return created

    def delete_rule(self, rule_id: int) -> bool:
        with self._lock:
            rules = load_rules(self.csv_path)
            kept_rules = [rule for rule in rules if rule.rule_id != rule_id]
            if len(kept_rules) == len(rules):
                return False
            self._save(kept_rules)
            return True

    def update_rule(self, rule_id: int, updates: RuleUpdate) -> RuleRecord | None:
        with self._lock:
            rules = load_rules(self.csv_path)
            updated_rule: RuleRecord | None = None
            update_payload = updates.model_dump(exclude_none=True)

            rewritten: list[RuleRecord] = []
            for rule in rules:
                if rule.rule_id != rule_id:
                    rewritten.append(rule)
                    continue

                merged = rule.model_dump()
                merged.update(update_payload)
                updated_rule = RuleRecord(**merged)
                rewritten.append(updated_rule)

            if updated_rule is None:
                return None

            self._save(rewritten)
            return updated_rule

    def _save(self, rules: list[RuleRecord]) -> None:
        self.csv_path.parent.mkdir(parents=True, exist_ok=True)
        with self.csv_path.open("w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=_HEADERS)
            writer.writeheader()
            for rule in sorted(rules, key=lambda item: (item.priority, item.rule_id)):
                writer.writerow(
                    {
                        "rule_id": rule.rule_id,
                        "field": rule.field,
                        "operator": rule.operator,
                        "value": rule.value,
                        "action": rule.action,
                        "priority": rule.priority,
                    }
                )
