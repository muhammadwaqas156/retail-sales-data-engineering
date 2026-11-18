-- Power BI requires a gap-free date table: row count must equal days between min and max.
select 1 as problem
from (select count(*) as n, min(date_key) as d0, max(date_key) as d1 from {{ ref('dim_date') }}) t
where t.n <> (t.d1 - t.d0) + 1
