"""Shared configuration, loaded from environment / .env (never hard-code secrets)."""
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:  # dotenv optional
    pass

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / os.getenv("DATA_DIR", "data")
RAW_DIR = DATA_DIR / "raw"
DUMMYJSON_BASE_URL = os.getenv("DUMMYJSON_BASE_URL", "https://dummyjson.com")
