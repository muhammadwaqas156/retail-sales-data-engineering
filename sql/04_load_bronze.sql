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
-- Audit the COPY result (skip this INSERT if the result says "0 files processed")
INSERT INTO LOAD_AUDIT (batch_id, source, file_name, status, rows_parsed, rows_loaded, errors_seen, first_error)
  SELECT $batch_id, 'transactions', "file", "status", "rows_parsed", "rows_loaded", "errors_seen", "first_error"
  FROM TABLE(RESULT_SCAN(LAST_QUERY_ID()));

-- 2. JSON sources (repeat for carts, users)
COPY INTO RAW_PRODUCTS (record, _source_file, _file_row_number)
FROM (SELECT $1, metadata$filename, metadata$file_row_number FROM @STG_RAW/products/)
FILE_FORMAT = (FORMAT_NAME = FF_NDJSON) ON_ERROR = ABORT_STATEMENT;
INSERT INTO LOAD_AUDIT (batch_id, source, file_name, status, rows_parsed, rows_loaded, errors_seen, first_error)
  SELECT $batch_id, 'products', "file", "status", "rows_parsed", "rows_loaded", "errors_seen", "first_error"
  FROM TABLE(RESULT_SCAN(LAST_QUERY_ID()));

COPY INTO RAW_CARTS (record, _source_file, _file_row_number)
FROM (SELECT $1, metadata$filename, metadata$file_row_number FROM @STG_RAW/carts/)
FILE_FORMAT = (FORMAT_NAME = FF_NDJSON) ON_ERROR = ABORT_STATEMENT;
INSERT INTO LOAD_AUDIT (batch_id, source, file_name, status, rows_parsed, rows_loaded, errors_seen, first_error)
  SELECT $batch_id, 'carts', "file", "status", "rows_parsed", "rows_loaded", "errors_seen", "first_error"
  FROM TABLE(RESULT_SCAN(LAST_QUERY_ID()));

COPY INTO RAW_USERS (record, _source_file, _file_row_number)
FROM (SELECT $1, metadata$filename, metadata$file_row_number FROM @STG_RAW/users/)
FILE_FORMAT = (FORMAT_NAME = FF_NDJSON) ON_ERROR = ABORT_STATEMENT;
INSERT INTO LOAD_AUDIT (batch_id, source, file_name, status, rows_parsed, rows_loaded, errors_seen, first_error)
  SELECT $batch_id, 'users', "file", "status", "rows_parsed", "rows_loaded", "errors_seen", "first_error"
  FROM TABLE(RESULT_SCAN(LAST_QUERY_ID()));

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
