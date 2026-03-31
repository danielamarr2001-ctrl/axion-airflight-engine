import os
from pathlib import Path

RULE_ENGINE_MODE = os.getenv("RULE_ENGINE_MODE", "python").strip().lower()

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/axiom_demo.db")
