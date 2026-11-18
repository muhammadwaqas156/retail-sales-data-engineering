-- Business rule R1: when dedupe is on, no exact-duplicate row (same row_hash) may remain.
{% if var('dedupe_exact_rows') %}
select row_hash, count(*) as n
from {{ ref('int_transactions_classified') }}
group by row_hash
having count(*) > 1
{% else %}
select 1 as row_hash, 0 as n where 1 = 0
{% endif %}
