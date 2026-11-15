"""Fail fast if today's extracts are missing or empty. Exit code != 0 fails the Airflow task.
Usage: python -m ingestion.validate_extracts
"""
import json
import sys
import time

from src.config import RAW_DIR

MAX_AGE_HOURS = 24
API_SOURCES = ("products", "carts", "users")


def check() -> list[str]:
    problems = []
    if not (RAW_DIR / "online_retail_II.xlsx").exists():
        problems.append("missing data/raw/online_retail_II.xlsx")
    for name in API_SOURCES:
        files = sorted((RAW_DIR / name).glob(f"{name}_*.json"))
        if not files:
            problems.append(f"{name}: no extract found")
            continue
        latest = files[-1]
        age_h = (time.time() - latest.stat().st_mtime) / 3600
        if age_h > MAX_AGE_HOURS:
            problems.append(f"{name}: latest extract is {age_h:.1f}h old")
        try:
            records = json.loads(latest.read_text())[name]
        except (ValueError, KeyError) as exc:
            problems.append(f"{name}: unreadable extract ({exc})")
            continue
        if not records:
            problems.append(f"{name}: extract has 0 records")
    return problems


def main() -> None:
    problems = check()
    for p in problems:
        print("VALIDATION FAILED:", p)
    if problems:
        sys.exit(1)
    print("Validation passed")


if __name__ == "__main__":
    main()
