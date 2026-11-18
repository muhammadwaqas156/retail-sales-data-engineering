"""Reconcile row counts across S3 audit log -> Snowflake Bronze -> Silver/Gold.
Writes docs/reconciliation.md. Needs SNOWFLAKE_ACCOUNT / SNOWFLAKE_USER / SNOWFLAKE_PASSWORD.
Usage: python -m ingestion.reconcile
"""
import json
import os
import sys
from datetime import datetime, timezone

from src.config import DATA_DIR, ROOT

SOURCES = {"transactions": "RAW_TRANSACTIONS", "products": "RAW_PRODUCTS",
           "carts": "RAW_CARTS", "users": "RAW_USERS"}


def expected_rows_from_audit(records: list[dict]) -> dict[str, int]:
    """Rows per source from the LATEST 'uploaded' record per S3 key (re-uploads overwrite a key)."""
    latest: dict[str, dict] = {}
    for r in records:
        if r.get("status") == "uploaded":
            latest[r["s3_key"]] = r
    out: dict[str, int] = {}
    for r in latest.values():
        out[r["source"]] = out.get(r["source"], 0) + r["rows"]
    return out


def compare(label: str, left_name: str, left: int | None, right_name: str, right: int | None) -> dict:
    ok = left is not None and right is not None and left == right
    return {"check": label, "left": f"{left_name}={left}", "right": f"{right_name}={right}",
            "status": "PASS" if ok else "FAIL"}


def main() -> int:
    import snowflake.connector

    log = DATA_DIR / "audit" / "ingestion_log.jsonl"
    if not log.exists():
        sys.exit(f"No audit log at {log}")
    audit = expected_rows_from_audit([json.loads(x) for x in log.read_text().splitlines()])
    conn = snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"], user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"], role="RETAIL_ROLE", warehouse="RETAIL_WH", database="RETAIL_DB")
    cur = conn.cursor()

    def one(sql: str) -> int:
        cur.execute(sql)
        return int(cur.fetchone()[0])

    rows = []
    try:
        for src, table in SOURCES.items():
            bronze = one(f"select count(*) from BRONZE.{table}")
            loaded = one(f"select coalesce(sum(rows_loaded),0) from BRONZE.LOAD_AUDIT where source='{src}' and status='LOADED'")
            rows.append(compare(f"S3 audit vs Bronze ({src})", "s3_audit", audit.get(src), "bronze", bronze))
            rows.append(compare(f"Bronze load audit vs Bronze ({src})", "load_audit", loaded, "bronze", bronze))
        bronze_tx = one("select count(*) from BRONZE.RAW_TRANSACTIONS")
        distinct_hash = one("select count(distinct row_hash) from SILVER.STG_TRANSACTIONS")
        fact = one("select count(*) from GOLD.FACT_SALES")
        dups = bronze_tx - distinct_hash
        rows.append(compare("Gold fact vs Bronze minus exact duplicates", "fact_sales", fact, f"bronze-{dups} dups", bronze_tx - dups))
        rows.append(compare("Duplicate lines in Gold", "dup_line_ids", one(
            "select count(*) from (select line_id from GOLD.FACT_SALES group by 1 having count(*)>1)"), "expected", 0))
    finally:
        conn.close()

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    out = ["# Reconciliation report", "", f"Generated {ts} by `ingestion/reconcile.py`.", "",
           "| Check | Left | Right | Status |", "|---|---|---|---|"]
    out += [f"| {r['check']} | {r['left']} | {r['right']} | **{r['status']}** |" for r in rows]
    (ROOT / "docs" / "reconciliation.md").write_text("\n".join(out) + "\n")
    print("\n".join(f"{r['status']}: {r['check']} ({r['left']} vs {r['right']})" for r in rows))
    return 0 if all(r["status"] == "PASS" for r in rows) else 1


if __name__ == "__main__":
    sys.exit(main())
