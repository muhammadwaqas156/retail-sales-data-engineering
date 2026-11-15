-- DummyJSON demo catalogue (synthetic). Snowflake VARIANT syntax.
select
    record:id::integer          as product_id,
    record:title::string        as title,
    record:category::string     as category,
    record:brand::string        as brand,
    record:price::decimal(18,2) as price,
    record:stock::integer       as stock,
    record:rating::float        as rating,
    _batch_id, _source_file
from {{ source('bronze', 'raw_products') }}
