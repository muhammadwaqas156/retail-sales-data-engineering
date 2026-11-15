"""Daily retail pipeline: extract -> validate -> S3 -> Snowflake Bronze -> dbt run -> dbt test.

Project code runs in a separate virtualenv (RETAIL_VENV, default ~/.venvs/retail) so Airflow's
dependencies never clash with dbt's. Credentials come from the environment, never from this file.
"""
import json
import logging
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

from airflow.providers.standard.operators.bash import BashOperator
from airflow.sdk import DAG

PROJECT = Path(os.environ.get("RETAIL_PROJECT_DIR", Path(__file__).resolve().parents[1]))
VENV = Path(os.environ.get("RETAIL_VENV", "~/.venvs/retail")).expanduser()
PY, DBT = VENV / "bin" / "python", VENV / "bin" / "dbt"
DBT_DIR = PROJECT / "dbt" / "retail_analytics"
FAILURE_LOG = PROJECT / "data" / "audit" / "pipeline_failures.jsonl"

log = logging.getLogger(__name__)


def notify_failure(context) -> None:
    """Failure notification: log + append to an audit file. Swap in email/Slack here later."""
    ti = context["task_instance"]
    rec = {"ts": datetime.now(timezone.utc).isoformat(), "dag": ti.dag_id, "task": ti.task_id,
           "run_id": context.get("run_id"), "try_number": ti.try_number}
    log.error("TASK FAILED: %s", rec)
    FAILURE_LOG.parent.mkdir(parents=True, exist_ok=True)
    with FAILURE_LOG.open("a") as f:
        f.write(json.dumps(rec) + "\n")


def sh(cmd: str) -> str:
    """Run from the project root, loading .env (AWS profile, bucket) without printing it."""
    return f'cd "{PROJECT}" && set -a && {{ [ -f .env ] && . ./.env || true; }} && set +a && {cmd}'


default_args = {
    "owner": "waqas",
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
    "execution_timeout": timedelta(minutes=30),
    "on_failure_callback": notify_failure,
}

with DAG(
    dag_id="retail_pipeline",
    description="UCI + DummyJSON -> S3 -> Snowflake Bronze -> dbt Silver/Gold",
    start_date=datetime(2026, 11, 1),
    schedule="0 6 * * *",
    catchup=False,
    max_active_runs=1,
    default_args=default_args,
    tags=["retail", "portfolio"],
) as dag:
    extract_api = BashOperator(task_id="extract_api", bash_command=sh(f'"{PY}" -m ingestion.fetch_dummyjson'))
    validate_extracts = BashOperator(task_id="validate_extracts", bash_command=sh(f'"{PY}" -m ingestion.validate_extracts'))
    upload_to_s3 = BashOperator(task_id="upload_to_s3", bash_command=sh(f'"{PY}" -m ingestion.upload_to_s3'))
    load_snowflake = BashOperator(task_id="load_snowflake", bash_command=sh(f'"{PY}" -m ingestion.load_snowflake'))
    dbt_run = BashOperator(task_id="dbt_run", bash_command=sh(f'cd "{DBT_DIR}" && "{DBT}" seed && "{DBT}" run'))
    dbt_test = BashOperator(task_id="dbt_test", bash_command=sh(f'cd "{DBT_DIR}" && "{DBT}" test'))

    extract_api >> validate_extracts >> upload_to_s3 >> load_snowflake >> dbt_run >> dbt_test
