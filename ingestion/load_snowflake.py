"""Run sql/04_load_bronze.sql against Snowflake (idempotent COPY INTO + audit).
Credentials come from environment variables only:
  SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER, SNOWFLAKE_PASSWORD
Usage: python -m ingestion.load_snowflake
"""
import os
import sys

from src.config import ROOT

SQL_FILE = ROOT / "sql" / "04_load_bronze.sql"


def split_statements(sql: str) -> list[str]:
    """Drop comment lines, split on ';'. Fine for our file (no ';' inside strings)."""
    lines = [ln for ln in sql.splitlines() if not ln.strip().startswith("--")]
    return [s.strip() for s in "\n".join(lines).split(";") if s.strip()]


def main() -> None:
    import snowflake.connector

    missing = [k for k in ("SNOWFLAKE_ACCOUNT", "SNOWFLAKE_USER", "SNOWFLAKE_PASSWORD") if not os.getenv(k)]
    if missing:
        sys.exit(f"Missing environment variables: {', '.join(missing)}")
    conn = snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"], user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"], role="RETAIL_ROLE", warehouse="RETAIL_WH",
        database="RETAIL_DB", schema="BRONZE")
    try:
        cur = conn.cursor()
        for stmt in split_statements(SQL_FILE.read_text()):
            cur.execute(stmt)
            if stmt.lstrip().upper().startswith("SELECT"):
                for row in cur.fetchall():
                    print(row)
        print("Bronze load finished")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
