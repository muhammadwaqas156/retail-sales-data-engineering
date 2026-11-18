# Retail Sales Data Engineering Platform

An end-to-end, repeatable data platform for retail sales analytics: **Python → Amazon S3 → Snowflake (Bronze / Silver / Gold) → dbt → Apache Airflow → Power BI**, with data-quality rules, audit logging, idempotent loads and a tested failure/recovery drill.

![Architecture](docs/architecture.png)

> **Data disclaimer.** The primary data is the public UCI *Online Retail II* dataset (a UK online giftware retailer, Dec 2009 to Dec 2011). A synthetic DummyJSON API is used only to practise API ingestion. **This is not Tesco data and not a live retailer integration.**

## What it does
- Ingests 1,067,371 historical invoice lines (53,628 invoices, 5,942 customers) and three demo API sources.
- Lands raw files in S3 with row counts, SHA-256 checksums and an audit log; unchanged files are skipped.
- Loads Snowflake Bronze through a **storage integration (IAM role, no AWS keys in code)** with a load-audit table.
- Applies documented business rules in dbt (cancellations, stock write-offs, zero prices, non-product codes, duplicates, unknown customers) to produce a tested star schema.
- Orchestrates the daily run in Airflow with retries, timeouts and a failure log.
- Serves a Power BI dashboard from the Gold layer.

## Stack
Python (requests, pandas, boto3) · Amazon S3 + IAM · Snowflake · dbt-snowflake · Apache Airflow 3 · Power BI Desktop · GitHub

## Data quality at a glance (from profiling the source)
| Finding | Rows | Handling |
|---|---|---|
| Exact duplicate rows | 34,335 (3.2%) | Flagged with a row hash; removed in Silver behind a switch (`dedupe_exact_rows`) |
| Cancellation (`C`) invoice rows | 19,494 | Kept; reported as returns, never silently netted |
| Non-cancellation rows with quantity <= 0 | 3,457 | Stock write-offs (damaged, missing...): excluded from revenue |
| Missing customer ID | 243,007 (22.8%) | Kept in sales totals, excluded from customer metrics |
| Non-product stock codes | 63 codes | Classified (postage, fees, discounts, vouchers...) and reported separately |
| Cancellation with positive quantity | 1 | Quarantined in `dq_exceptions` |

Full rules: [docs/business_rules.md](docs/business_rules.md) · Evidence: [failure drill](docs/failure_recovery_evidence.md), [reconciliation](docs/reconciliation.md), [data quality and recovery](docs/data_quality.md).

## Dashboard
Built in Power BI on the Gold layer (Import mode). Setup and DAX: [docs/powerbi_guide.md](docs/powerbi_guide.md), [powerbi/measures.dax](powerbi/measures.dax).

| Overview | Products |
|---|---|
| ![Overview](docs/screenshots/overview.png) | ![Products](docs/screenshots/products.png) |
| **Customers** | **Returns and cancellations** |
| ![Customers](docs/screenshots/customers.png) | ![Returns](docs/screenshots/returns.png) |

Source limitations are listed on the dashboard's data-notes page and in [docs/source_limitations.md](docs/source_limitations.md).

## Repository layout
```
dags/            Airflow DAG (retail_pipeline)
ingestion/       Extract, validate, upload to S3, load Snowflake, reconcile
src/             Shared config
sql/             Snowflake setup, stage, Bronze tables and load
dbt/retail_analytics/   Staging, intermediate and Gold models, seeds, tests
powerbi/         DAX measures
scripts/         start_airflow.sh, failure_drill.py
docs/            Architecture, data dictionary, rules, guides, evidence
tests/           Python tests
```

## Setup (summary)
Detailed guides: [AWS](docs/aws_setup.md) · [Snowflake](docs/snowflake_setup.md) · [dbt](docs/dbt_setup.md) · [Airflow](docs/airflow_setup.md) · [Power BI](docs/powerbi_guide.md)

1. `python3 -m venv ~/.venvs/retail && source ~/.venvs/retail/bin/activate && pip install -r requirements.txt snowflake-connector-python dbt-snowflake`
2. Download `online_retail_II.xlsx` from the [UCI page](https://archive.ics.uci.edu/dataset/502/online+retail+ii) into `data/raw/`.
3. Copy `.env.example` to `.env`; set `S3_BUCKET` and `AWS_PROFILE`. Keep Snowflake credentials in environment variables, never in files in the repo.
4. Create the S3 bucket and least-privilege IAM user ([docs/aws_setup.md](docs/aws_setup.md)); run `python -m ingestion.fetch_dummyjson` then `python -m ingestion.upload_to_s3`.
5. Run the Snowflake scripts in `sql/` in order, then `dbt seed && dbt build` in `dbt/retail_analytics`.
6. Start Airflow with `./scripts/start_airflow.sh` and trigger `retail_pipeline`.

Run the tests: `pytest` and `python -m scripts.failure_drill`.

## Reliability design
- **Idempotent by layer:** upload skips unchanged files (deterministic gzip + per-source SHA-256); `COPY INTO` skips loaded files; Silver dedupes by row hash; Gold keys are unique and tested.
- **Fail fast:** `validate_extracts` stops the run before anything is uploaded; `COPY ... ON_ERROR = ABORT_STATEMENT` never leaves a partial file in Bronze.
- **Recovery:** clear the failed Airflow task and rerun; everything downstream is safe to repeat. Runbook in [docs/data_quality.md](docs/data_quality.md).
- **Cost and security:** XSMALL warehouse with 60 s auto-suspend and a 5-credit resource monitor; no secrets in Git; the fake sensitive fields in the API users data (password, ssn, bank...) are stripped before upload.

## Lessons learned
See [docs/troubleshooting.md](docs/troubleshooting.md) for the real problems hit and how they were fixed (a space in the project path breaking venv scripts, non-deterministic gzip hashes breaking idempotency, `.env` blanks overriding real credentials, a date table with gaps).

## Possible next steps
Incremental dbt models for larger volumes, Docker Compose / Kubernetes deployment, email or Slack alerts, CI with GitHub Actions.
