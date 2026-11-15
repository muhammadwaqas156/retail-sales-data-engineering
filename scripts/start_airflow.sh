#!/usr/bin/env bash
# Starts Airflow (API server + scheduler + UI) locally in WSL. Stop with Ctrl+C.
# Export SNOWFLAKE_ACCOUNT / SNOWFLAKE_USER / SNOWFLAKE_PASSWORD in this terminal first.
set -euo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export AIRFLOW_HOME="$HOME/airflow"
export AIRFLOW__CORE__DAGS_FOLDER="$REPO/dags"
export AIRFLOW__CORE__LOAD_EXAMPLES=False
export RETAIL_PROJECT_DIR="$REPO"
export RETAIL_VENV="${RETAIL_VENV:-$HOME/.venvs/retail}"
# shellcheck disable=SC1090
source "$HOME/.venvs/airflow/bin/activate"
exec airflow standalone
