# Data quality, idempotency and recovery (Phase 6)

## Business rules
Implemented in dbt and documented in `docs/business_rules.md` (cancellations, adjustments, zero prices, non-product codes, duplicates, unknown customers).

## Idempotency and duplicate protection (by layer)
| Layer | Mechanism | Evidence |
|---|---|---|
| Upload to S3 | SHA-256 of each prepared file, checked per source against the audit log; deterministic gzip so unchanged data gives an unchanged hash | `scripts/failure_drill.py` scenario D5 |
| Snowflake Bronze | `COPY INTO` tracks loaded files (no reload); audit written from `COPY_HISTORY` | second run of `sql/04_load_bronze.sql` leaves counts unchanged |
| Silver | `row_hash` + `row_number()`; exact duplicates removed (switch `dedupe_exact_rows`) | dbt test `assert_no_duplicate_lines` |
| Gold | unique `line_id`, relationships and accepted-values tests | `dbt test` |

## Failure handling
- Every Airflow task retries twice (2 min apart) with a 30 min timeout; failures are written to `data/audit/pipeline_failures.jsonl`.
- `validate_extracts` stops the run before anything is uploaded if extracts are missing, stale or empty.
- Upload failures are written to the audit log (`status=failed`) before the task fails.
- `COPY INTO ... ON_ERROR = ABORT_STATEMENT`: a bad file loads nothing, so Bronze never holds a partial file.
- S3 versioning is on, so an overwritten object can be recovered.

## Recovery runbook
1. Open the failed task's log in Airflow and read the last lines.
2. Fix the cause (credentials, bucket name, bad extract, SQL error).
3. In Airflow, Clear Task Instance on the failed task with Downstream ticked. Earlier tasks are not rerun.
4. Re-running is safe: uploads skip unchanged files, COPY skips loaded files, dbt rebuilds Silver/Gold from Bronze.
5. Run `python -m ingestion.reconcile` and confirm all checks PASS.

## Evidence to generate (on your machine)
    python scripts/failure_drill.py        # writes docs/failure_recovery_evidence.md
    python -m ingestion.reconcile          # writes docs/reconciliation.md (needs SNOWFLAKE_* variables)
    cd dbt/retail_analytics && dbt build && dbt source freshness

## Design decision: no incremental dbt models (yet)
The full Gold rebuild is about a million rows and takes seconds on an XSMALL warehouse, and cross-batch duplicate removal needs the whole history, so incremental models would add risk for no benefit. Incrementality is handled where it matters: file-level skipping in the upload and `COPY INTO`. If data volume grows, `fact_sales` can move to an incremental `delete+insert` model keyed on `line_id`.
