from __future__ import annotations

import csv
from pathlib import Path

from axiom.rule_platform.rule_models import RuleRecord

DEFAULT_RULES_PATH = Path(__file__).with_name("rules.csv")



def load_rules(csv_path: Path | str = DEFAULT_RULES_PATH) -> list[RuleRecord]:
    path = Path(csv_path)
    if not path.exists():
        return []

    rules: list[RuleRecord] = []
    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if not row:
                continue

            normalized_row = {
                (key or "").replace("\ufeff", "").strip(): (value or "").strip()
                for key, value in row.items()
            }

            rule = RuleRecord(
                rule_id=int(normalized_row.get("rule_id") or "0"),
                field=normalized_row.get("field") or "",
                operator=normalized_row.get("operator") or "",
                value=normalized_row.get("value") or "",
                action=normalized_row.get("action") or "",
                priority=int(normalized_row.get("priority") or "1"),
            )
            rules.append(rule)

    return rules
