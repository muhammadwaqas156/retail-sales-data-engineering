-- Re-runnable: COPY INTO skips files it has already loaded (load metadata kept 64 days).
USE ROLE RETAIL_ROLE;
USE WAREHOUSE RETAIL_WH;
USE DATABASE RETAIL_DB;
USE SCHEMA BRONZE;
SET batch_id = 'batch_' || TO_CHAR(CURRENT_TIMESTAMP(), 'YYYYMMDD_HH24MISS');

-- 1. Transactions
COPY INTO RAW_TRANSACTIONS
  (invoice, stock_code, description, quantity, invoice_date, price, customer_id, country, source_sheet,
   _source_file, _file_row_number)
FROM (SELECT $1,$2,$3,$4,$5,$6,$7,$8,$9, metadata$filename, metadata$file_row_number
      FROM @STG_RAW/transactions/)
FILE_FORMAT = (FORMAT_NAME = FF_CSV) PATTERN = '.*[.]csv[.]gz' ON_ERROR = ABORT_STATEMENT;

-- 2. JSON sources
COPY INTO RAW_PRODUCTS (record, _source_file, _file_row_number)
FROM (SELECT $1, metadata$filename, metadata$file_row_number FROM @STG_RAW/products/)
FILE_FORMAT = (FORMAT_NAME = FF_NDJSON) ON_ERROR = ABORT_STATEMENT;

COPY INTO RAW_CARTS (record, _source_file, _file_row_number)
FROM (SELECT $1, metadata$filename, metadata$file_row_number FROM @STG_RAW/carts/)
FILE_FORMAT = (FORMAT_NAME = FF_NDJSON) ON_ERROR = ABORT_STATEMENT;

COPY INTO RAW_USERS (record, _source_file, _file_row_number)
FROM (SELECT $1, metadata$filename, metadata$file_row_number FROM @STG_RAW/users/)
FILE_FORMAT = (FORMAT_NAME = FF_NDJSON) ON_ERROR = ABORT_STATEMENT;

-- Audit: one insert from Snowflake's own load history, only for files loaded since the last audit row.
-- On a repeat run nothing new was loaded, so zero rows are inserted (no error).
INSERT INTO LOAD_AUDIT (batch_id, source, file_name, status, rows_parsed, rows_loaded, errors_seen, first_error)
WITH hist AS (
  SELECT 'transactions' AS source, * FROM TABLE(INFORMATION_SCHEMA.COPY_HISTORY(TABLE_NAME=>'RAW_TRANSACTIONS', START_TIME=>DATEADD(hour,-6,CURRENT_TIMESTAMP())))
  UNION ALL
  SELECT 'products', * FROM TABLE(INFORMATION_SCHEMA.COPY_HISTORY(TABLE_NAME=>'RAW_PRODUCTS', START_TIME=>DATEADD(hour,-6,CURRENT_TIMESTAMP())))
  UNION ALL
  SELECT 'carts', * FROM TABLE(INFORMATION_SCHEMA.COPY_HISTORY(TABLE_NAME=>'RAW_CARTS', START_TIME=>DATEADD(hour,-6,CURRENT_TIMESTAMP())))
  UNION ALL
  SELECT 'users', * FROM TABLE(INFORMATION_SCHEMA.COPY_HISTORY(TABLE_NAME=>'RAW_USERS', START_TIME=>DATEADD(hour,-6,CURRENT_TIMESTAMP())))
)
SELECT $batch_id, source, file_name, status, row_parsed, row_count, error_count, first_error_message
FROM hist
WHERE last_load_time > COALESCE((SELECT MAX(loaded_at) FROM LOAD_AUDIT), '1970-01-01'::TIMESTAMP_LTZ);

-- Stamp the batch id on newly landed rows
UPDATE RAW_TRANSACTIONS SET _batch_id = $batch_id WHERE _batch_id IS NULL;
UPDATE RAW_PRODUCTS     SET _batch_id = $batch_id WHERE _batch_id IS NULL;
UPDATE RAW_CARTS        SET _batch_id = $batch_id WHERE _batch_id IS NULL;
UPDATE RAW_USERS        SET _batch_id = $batch_id WHERE _batch_id IS NULL;

-- Verify: expect 1067371 / 194 / 208 / 208
SELECT 'transactions' src, COUNT(*) n FROM RAW_TRANSACTIONS UNION ALL
SELECT 'products', COUNT(*) FROM RAW_PRODUCTS UNION ALL
SELECT 'carts', COUNT(*) FROM RAW_CARTS UNION ALL
SELECT 'users', COUNT(*) FROM RAW_USERS;
SELECT * FROM LOAD_AUDIT ORDER BY loaded_at DESC;