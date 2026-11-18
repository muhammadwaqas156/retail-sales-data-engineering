# Troubleshooting notes (problems actually hit)

| Symptom | Cause | Fix |
|---|---|---|
| `aws: cannot execute: required file not found` | Virtualenv inside a path with a space (`Muhammad Waqas`); script shebangs break | Create the venv in the WSL home folder (`~/.venvs/...`) |
| `Package 'awscli' has no installation candidate` | Removed from newer Ubuntu apt | `pip install awscli` in the venv |
| Same file re-uploaded every run, different SHA-256 | gzip stores a timestamp in its header | Write gzip with `mtime=0` (deterministic output) |
| Identical-content files from different sources skipped | Duplicate check used hash only | Check source + hash together |
| `Table 'RAW_TRANSACTIONS' does not exist` / `File format 'FF_CSV' does not exist` | Only part of a SQL script was run | Run each file in full (Run all), in order |
| `invalid identifier '"file"'` on the second load | `COPY` returns no file rows when nothing is loaded | Audit from `INFORMATION_SCHEMA.COPY_HISTORY` instead of `RESULT_SCAN` |
| Airflow task: `Missing environment variables: SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER` | `.env` (copied from the example) had blank `SNOWFLAKE_*` lines that overrode the exported values | Remove Snowflake lines from `.env` and `.env.example`; keep credentials outside the repo |
| Power BI cannot mark Date table | Calendar only had days with sales (gaps) | `dim_date` is now a continuous calendar with a dbt continuity test |
| Airflow cannot be typed into | It runs in the foreground | Open a second terminal |
| Disk space (8 GB on C:) | Docker Desktop is heavy | Run Airflow directly in WSL in its own venv |
