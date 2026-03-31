import os
from pathlib import Path

RULE_ENGINE_MODE = os.getenv("RULE_ENGINE_MODE", "python").strip().lower()

BASE_DIR = Path(__file__).resolve().parent.parent

# Use /tmp for serverless environments (Vercel), local path otherwise
_default_db_path = "/tmp/axiom_demo.db" if os.getenv("VERCEL") else f"{BASE_DIR}/axiom_demo.db"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{_default_db_path}")
