-- Types the raw text, normalises ids, adds row_hash. No rows are dropped here.
select
    trim(invoice)                                              as invoice_no,
    upper(trim(stock_code))                                    as stock_code,
    nullif(trim(description), '')                              as description,
    try_cast(quantity as integer)                              as quantity,
    try_cast(invoice_date as timestamp)                        as invoice_ts,
    try_cast(price as decimal(18,4))                           as unit_price,
    nullif(regexp_replace(trim(customer_id), '[.]0$', ''), '') as customer_id,
    trim(country)                                              as country,
    source_sheet,
    _batch_id,
    _source_file,
    _file_row_number,
    md5(concat_ws('|',
        coalesce(trim(invoice), ''), coalesce(upper(trim(stock_code)), ''),
        coalesce(trim(description), ''), coalesce(quantity, ''), coalesce(invoice_date, ''),
        coalesce(price, ''), coalesce(customer_id, ''), coalesce(trim(country), ''))) as row_hash
from {{ source('bronze', 'raw_transactions') }}
