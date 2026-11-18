# LinkedIn drafts (publish each only when its milestone is complete and evidenced)

Rules: no credentials, account IDs, bucket names or private data in screenshots. Say plainly the data is public/historical, not Tesco.

---
## 1. Launch
I'm building an end-to-end retail data platform as a portfolio project: Python → S3 → Snowflake → dbt → Airflow → Power BI.

Data: the public UCI Online Retail II dataset (1M+ real invoice lines from a UK online retailer, 2009-2011) plus a synthetic API for ingestion practice. To be clear: this is not Tesco data and not a live retailer feed.

I'll post each milestone only once it's working and tested. First step done: profiled the source. 34,335 exact duplicate rows, 19,494 cancellation lines, and 23% of lines with no customer ID. Those findings now drive the business rules.

#DataEngineering #Snowflake #dbt #Airflow

*Image: docs/architecture.png*

---
## 2. S3 milestone
Milestone 2: raw data lake on S3.
- Least-privilege IAM user, no credentials in code or Git
- Each file logged with row count and SHA-256; unchanged files are skipped
- One bug worth sharing: my "idempotent" upload kept re-uploading identical data, because gzip embeds a timestamp in its header and changed the hash every run. Fixing it made repeat runs produce `skipped_duplicate`.

*Image: bucket folder view (name hidden) + audit-log lines*

---
## 3. Snowflake milestone
Milestone 3: Snowflake Bronze layer, loaded from S3 through a storage integration (an IAM role, so no AWS keys anywhere).
- 1,067,371 rows loaded; a load-audit table records each file, rows parsed, rows loaded and errors
- Cross-check: null customer IDs in Snowflake matched my independent Python profile exactly (243,007)
- Re-running the load adds nothing: Snowflake skips files it has already loaded

*Image: LOAD_AUDIT result (account hidden)*

---
## 4. dbt milestone
Milestone 4: dbt models and tests. Bronze → Silver → Gold star schema (fact_sales + customer, product and date dimensions).

The interesting part was the business rules: cancellations as returns, 3,457 stock write-offs excluded from revenue, postage and fees reported separately, 34,335 duplicates removed behind a switch so I can show totals with and without. One cancellation row with a positive quantity is quarantined in a data-quality table.

*Image: dbt lineage graph + passing test summary*

---
## 5. Airflow milestone
Milestone 5: orchestration. One Airflow DAG: extract → validate → S3 → Snowflake → dbt run → dbt test, with retries, timeouts and a failure log.

Honest note: with 8 GB free on my laptop I skipped Docker and ran Airflow directly in WSL in its own virtualenv. The first run failed because blank lines in a `.env` file overrode my real credentials. Reading the task log found it in minutes.

*Image: Airflow graph view, all tasks green*

---
## 6. Final showcase
Project complete: a retail data platform from raw files to dashboard.

What I'm proudest of is the reliability work, not the happy path: a failure drill that deliberately breaks the pipeline (missing files, wrong bucket), shows the audit log recording the failure, then proves recovery and a no-duplicate rerun; plus a reconciliation report that checks row counts from S3 to Bronze to Gold.

Stack: Python, S3, Snowflake, dbt, Airflow, Power BI. Data: public UCI dataset (not Tesco).

Repo, architecture diagram and write-up: <your GitHub link>

What I'd do next: incremental models for larger volumes, alerts, and CI.

*Image: dashboard overview + architecture diagram*
