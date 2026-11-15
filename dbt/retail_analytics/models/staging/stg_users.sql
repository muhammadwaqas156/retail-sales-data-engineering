-- Sensitive fake fields were already removed before upload; only safe columns are selected.
select
    record:id::integer          as user_id,
    record:firstName::string    as first_name,
    record:lastName::string     as last_name,
    record:age::integer         as age,
    record:gender::string       as gender,
    record:address:city::string as city,
    record:address:country::string as country,
    _batch_id, _source_file
from {{ source('bronze', 'raw_users') }}
