# dbt setup (Phase 4)

    source ~/.venvs/retail/bin/activate
    pip install dbt-snowflake
    mkdir -p ~/.dbt && cp dbt/retail_analytics/profiles.yml.example ~/.dbt/profiles.yml
    export SNOWFLAKE_ACCOUNT=<orgname-accountname> SNOWFLAKE_USER=<user> SNOWFLAKE_PASSWORD=<password>
    cd dbt/retail_analytics
    dbt debug          # connection test
    dbt seed && dbt build
    dbt docs generate && dbt docs serve   # lineage graph, screenshot for LinkedIn

Layers: BRONZE (raw, loaded by COPY) -> SILVER (staging views, int_transactions_classified, dq_exceptions, seed) -> GOLD (fact_sales, dim_customer, dim_product, dim_date).
Dedup switch: `dbt build --vars '{dedupe_exact_rows: false}'` to compare revenue with and without R1.
Never commit ~/.dbt/profiles.yml or passwords.
