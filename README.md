# Retail Sales Data Engineering Platform

**End-to-end cloud data engineering platform using Python, Amazon S3,
Snowflake, dbt, Apache Airflow and Power BI.**

This project demonstrates a complete retail data pipeline: source
extraction, validation, cloud storage, warehouse loading,
transformation, data-quality management, orchestration and business
intelligence.

## 1. Project Overview

The platform transforms historical retail transactions and supplementary
API data into analytics-ready datasets.

Python extracts and validates data, Amazon S3 stores raw files,
Snowflake provides the warehouse, dbt manages transformations and tests,
and Apache Airflow orchestrates pipeline execution. Power BI consumes
curated Gold-layer datasets.

### Objectives

-   Build an end-to-end ETL/ELT pipeline.
-   Ingest historical retail data and supplementary API data.
-   Store raw data in Amazon S3.
-   Load data into Snowflake using secure storage integration.
-   Implement Bronze, Silver and Gold data layers.
-   Apply business rules and data-quality checks with dbt.
-   Orchestrate workflows using Apache Airflow.
-   Implement audit logging, file validation and idempotent processing.
-   Deliver analytics-ready datasets for Power BI.
-   Document failure handling and recovery procedures.

## 2. Solution Architecture

``` mermaid
flowchart TD
    A["UCI Online Retail II"] --> B["Python Extraction"]
    C["DummyJSON API"] --> B
    B --> D["Source Validation"]
    D --> E["Hashing and Audit"]
    E --> F["Amazon S3 - Raw"]
    F --> G["Snowflake Storage Integration"]
    G --> H["Bronze Layer"]
    H --> I["dbt Staging"]
    I --> J["dbt Intermediate"]
    J --> K["Gold Layer"]
    K --> L["Power BI"]
    M["Apache Airflow"] --> B
    M --> G
    M --> I
    M --> K
```

  Technology       Responsibility
  ---------------- ---------------------------------------
  Python           Extraction, validation and ingestion
  Amazon S3        Raw data storage
  AWS IAM          Secure access permissions
  Snowflake        Cloud data warehouse
  dbt              Transformation, modelling and testing
  Apache Airflow   Workflow orchestration
  Docker           Local orchestration environment
  Power BI         Business intelligence and reporting
  Git and GitHub   Version control

## 3. Data Sources

### UCI Online Retail II

Primary source: [UCI Online Retail
II](https://archive.ics.uci.edu/dataset/502/online+retail+ii)

The dataset contains historical transactions from a UK-based online
giftware retailer between December 2009 and December 2011.

**Reported source profile**

  Metric                                         Value
  ------------------- --------------------------------
  Transaction lines                          1,067,371
  Invoices                                      53,628
  Customers                                      5,942
  Historical period     December 2009 -- December 2011

### DummyJSON API

Supplementary synthetic API sources:

-   [Products](https://dummyjson.com/products?limit=0)
-   [Carts](https://dummyjson.com/carts?limit=0)
-   [Users](https://dummyjson.com/users?limit=0)
-   [API documentation](https://dummyjson.com/docs)

> **Source limitation:** DummyJSON is synthetic demonstration data. It
> is not part of the UCI transaction dataset and does not represent a
> live retailer integration. This project does not claim access to Tesco
> or any other retailer's private systems.

## 4. Pipeline Components

### Python extraction and validation

-   Reads and profiles the historical Excel dataset.
-   Extracts product, cart and user data from API endpoints.
-   Validates source availability and expected structures.
-   Records source metadata and processing information.

### Amazon S3 data lake

-   Structured raw-data storage.
-   SHA-256 checksums.
-   Row-count metadata and audit logging.
-   Deterministic gzip compression.
-   Hash-based change detection to skip unchanged files.

### Snowflake data warehouse

AWS IAM and Snowflake storage integration provide access between S3 and
Snowflake without embedding AWS access keys in application code.

-   **Bronze:** ingested source records, source metadata and load audit
    information.
-   **Silver:** standardised data, duplicate handling, business rules
    and data-quality exceptions.
-   **Gold:** curated analytical models for sales, products, customers
    and returns.

### dbt transformation

-   Staging models for source standardisation.
-   Intermediate models for business logic.
-   Gold models for analytical consumption.
-   Schema and data-quality tests.
-   Model documentation and lineage.

### Apache Airflow orchestration

The `retail_pipeline` DAG coordinates ingestion, validation, S3 upload,
Snowflake loading, transformations and downstream verification.

Reliability features include task dependencies, retries, timeouts,
execution logging, failure handling and controlled reruns.

### Power BI

Power BI consumes curated Snowflake Gold datasets using Import mode.
Reporting covers sales performance, product performance, customer
analysis, returns, revenue trends and business KPIs.

## 5. Data Quality and Business Rules

Source profiling identified the following characteristics.

  ------------------------------------------------------------------------
  Finding                           Reported records Treatment
  --------------------- ---------------------------- ---------------------
  Exact duplicate rows                        34,335 Flagged using row
                                                     hashes; configurable
                                                     deduplication in
                                                     Silver

  Cancellation invoice                        19,494 Retained and
  rows                                               classified as returns

  Non-cancellation rows                        3,457 Classified as stock
  with quantity ≤ 0                                  write-offs and
                                                     excluded from revenue

  Missing customer IDs                       243,007 Retained in sales
                                                     totals but excluded
                                                     from
                                                     customer-specific
                                                     metrics

  Non-product stock                         63 codes Classified separately
  codes                                              from product sales

  Cancellation with                      1 exception Quarantined for
  positive quantity                                  investigation
  ------------------------------------------------------------------------

These are reported profiling results and should be interpreted alongside
the documented business rules and reconciliation checks.

The platform distinguishes product sales, customer activity,
cancellations and returns, stock write-offs, postage and service
charges, discounts and vouchers, missing customer information, and
duplicate source records.

A configurable `dedupe_exact_rows` switch controls exact-row
deduplication.

Supporting documentation:

-   `docs/business_rules.md`
-   `docs/data_quality.md`
-   `docs/reconciliation.md`
-   `docs/source_limitations.md`

## 6. Reliability, Idempotency and Recovery

### Idempotent ingestion

Deterministic compression and SHA-256 checksums identify unchanged
source files and help avoid unnecessary uploads. Snowflake load history
is used to prevent previously loaded files from being loaded again.

### Validation and loading

Source validation takes place before upload. Invalid extracts fail
validation rather than silently continuing.

Snowflake loading uses:

``` sql
ON_ERROR = ABORT_STATEMENT
```

This prevents a partially loaded file from being treated as a successful
ingestion.

### Failure handling

-   Airflow retries and timeouts.
-   Execution and failure logging.
-   Load-audit tracking.
-   Data-quality exception handling.
-   Documented recovery procedures.
-   Safe rerun design.

See `docs/failure_recovery_evidence.md` and `docs/reconciliation.md`.

## 7. Repository Structure

``` text
retail-sales-data-engineering/
├── dags/
│   └── retail_pipeline.py
├── ingestion/
│   ├── extract/
│   ├── validate/
│   ├── upload/
│   ├── load/
│   └── reconciliation/
├── src/
├── sql/
│   ├── snowflake_setup/
│   ├── stages/
│   ├── bronze/
│   └── loading/
├── dbt/
│   └── retail_analytics/
│       ├── models/
│       │   ├── staging/
│       │   ├── intermediate/
│       │   └── marts/
│       ├── seeds/
│       ├── tests/
│       └── dbt_project.yml
├── powerbi/
│   └── measures.dax
├── scripts/
│   ├── start_airflow.sh
│   └── failure_drill.py
├── docs/
├── tests/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

*This is a logical overview. Adjust the tree to match the actual
repository files and directories.*

## 8. Setup and Execution

### Prerequisites

-   Python 3.12
-   Git
-   Docker and Docker Compose
-   AWS account, S3 bucket and configured IAM permissions
-   Snowflake account and warehouse
-   dbt with the Snowflake adapter
-   Power BI Desktop

### 1. Clone the repository

``` bash
git clone https://github.com/muhammadwaqas156/retail-sales-data-engineering.git
cd retail-sales-data-engineering
```

### 2. Create a Python environment

``` bash
python -m venv .venv
```

Activate on Windows PowerShell:

``` powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

``` bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a local `.env` file using `.env.example` as a template. Configure
the required AWS, S3 and Snowflake settings.

**Never commit `.env`, passwords, private keys or cloud credentials to
GitHub.**

### 4. Prepare the source data

Download the [UCI Online Retail II
dataset](https://archive.ics.uci.edu/dataset/502/online+retail+ii) and
place the workbook in the configured raw-data directory. Run the
project's extraction and validation scripts according to the ingestion
instructions.

### 5. Configure AWS and Snowflake

-   Configure the S3 bucket.
-   Configure the required IAM role and permissions.
-   Create the Snowflake storage integration.
-   Configure the external stage.
-   Create the required database, schemas and Bronze tables.
-   Verify Snowflake access to the S3 source location.

Refer to the AWS and Snowflake setup documentation in `docs/`.

### 6. Run dbt

``` bash
cd dbt/retail_analytics
dbt debug
dbt build
```

### 7. Start Airflow

Return to the repository root and follow the documented startup
procedure:

``` bash
./scripts/start_airflow.sh
```

Open the Airflow web interface, locate the `retail_pipeline` DAG,
trigger the pipeline and inspect the task logs.

### 8. Validate outputs

Verify S3 source files and metadata, Snowflake Bronze load history,
Silver data-quality results, Gold model outputs, dbt test results,
Airflow task status and Power BI reporting figures.

Use `docs/reconciliation.md` for cross-layer validation guidance.

## 9. Testing and Validation

  Validation area     Purpose
  ------------------- -------------------------------------------
  Source validation   Check source files and structure
  File integrity      Verify SHA-256 checksums
  S3 ingestion        Confirm uploaded files and metadata
  Snowflake loading   Verify load history and audit status
  dbt tests           Validate transformed models
  Data quality        Identify invalid and exceptional records
  Reconciliation      Compare counts and metrics between layers
  Airflow             Verify task execution and recovery

Run Python tests using the repository's test configuration.

The project also includes a failure-drill script:

``` bash
python -m scripts.failure_drill
```

## 10. Cost and Security

### Cost controls

-   Snowflake X-Small warehouse configuration.
-   60-second warehouse auto-suspend.
-   Five-credit resource monitor.
-   Avoid unnecessary warehouse execution.
-   Stop unused local services and containers.

### Security controls

-   AWS IAM role-based access.
-   Snowflake storage integration.
-   No hardcoded AWS access keys in application code.
-   Environment-based credential configuration.
-   `.gitignore` protection for sensitive files.
-   Removal of unnecessary sensitive DummyJSON user fields before
    upload.

## 11. Documentation and Evidence

  Document                         Purpose
  -------------------------------- -------------------------------------
  `business_rules.md`              Retail business logic
  `data_quality.md`                Data-quality findings and treatment
  `reconciliation.md`              Cross-layer validation
  `failure_recovery_evidence.md`   Failure and recovery scenarios
  `powerbi_guide.md`               Dashboard guidance
  `source_limitations.md`          Dataset limitations

Power BI screenshots and execution evidence are maintained in the
repository.

## 12. Engineering Challenges and Solutions

**Non-deterministic file compression**\
Different compressed outputs could produce different hashes even when
the source data had not changed. Deterministic gzip settings and
source-level SHA-256 checksums improve repeatable file identification.

**Duplicate retail transactions**\
Exact duplicate records are identified through row hashing and handled
through configurable deduplication in Silver.

**Missing customer identifiers**\
Transactions without customer IDs remain in sales reporting but are
excluded from customer-specific metrics.

**Returns and cancellations**\
Cancellation records are classified separately rather than treated as
ordinary positive sales.

**API data sensitivity**\
Unnecessary sensitive fields from synthetic user API responses are
removed before cloud upload.

**Pipeline recovery**\
Ingestion audit records, load history, idempotent processing and
documented recovery procedures support controlled reruns.

## 13. Future Improvements

-   Incremental dbt models for larger data volumes.
-   GitHub Actions for automated CI/CD.
-   Automated pipeline notifications through email or Slack.
-   Expanded monitoring and observability.
-   Additional analytical dimensions.
-   Further Snowflake performance optimisation.
-   Production cloud deployment of orchestration services.

## 14. Project Outcome

This project demonstrates a modern data engineering workflow from raw
data extraction to business intelligence reporting. It brings together
cloud storage, secure data access, warehouse architecture,
transformation engineering, data-quality management, workflow
orchestration, operational recovery and analytical consumption.

------------------------------------------------------------------------

## Author

**Muhammad Waqas**\
MSc Advanced Computer Science \| Data Engineering \| Analytics

-   **GitHub:** [muhammadwaqas156](https://github.com/muhammadwaqas156)
-   **LinkedIn:** [Muhammad
    Waqas](https://linkedin.com/in/muhammadwaqas2798156)
-   **Project repository:**
    [retail-sales-data-engineering](https://github.com/muhammadwaqas156/retail-sales-data-engineering)
