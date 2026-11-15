# Airflow setup (Phase 5) - local, no Docker

Airflow runs in its own virtualenv (`~/.venvs/airflow`) so it never clashes with dbt. The pipeline code runs in the project venv (`~/.venvs/retail`).

## Install (once, in WSL)
    python3 -m venv ~/.venvs/airflow
    source ~/.venvs/airflow/bin/activate
    PYV=$(python -c 'import sys;print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    pip install "apache-airflow==3.4.0" --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-3.4.0/constraints-${PYV}.txt"
    deactivate
    source ~/.venvs/retail/bin/activate
    pip install snowflake-connector-python dbt-snowflake
    deactivate

## Run
    export SNOWFLAKE_ACCOUNT=...  SNOWFLAKE_USER=...  SNOWFLAKE_PASSWORD=...   # this terminal only
    ./scripts/start_airflow.sh
Open http://localhost:8080. Airflow 3 prints a generated admin password in the terminal (also in `~/airflow/simple_auth_manager_passwords.json.generated`). Unpause `retail_pipeline` and trigger a run.

## Pipeline
extract_api -> validate_extracts -> upload_to_s3 -> load_snowflake -> dbt_run -> dbt_test
- Retries: 2 (2 min apart). Timeout: 30 min per task. Schedule: daily 06:00, no catch-up, one run at a time.
- Failures: logged and appended to `data/audit/pipeline_failures.jsonl`.
- Secrets come from the environment / `.env` / `~/.aws`, never from the DAG.

## Notes
- Keep Airflow's home in WSL (`~/airflow`), not on /mnt/c.
- Stop Airflow with Ctrl+C when done; it is not a background service.
- Docker Compose can be added later as an alternative to this setup.
