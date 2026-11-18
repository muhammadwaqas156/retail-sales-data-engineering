{# Continuous calendar: every day from 1 Jan of the first sales year to 31 Dec of the last sales year.
   Power BI needs a gap-free, unique date column to mark a Date table. #}
with bounds as (
    select
        cast(cast(extract(year from min(invoice_date)) as varchar) || '-01-01' as date) as start_date,
        cast(cast(extract(year from max(invoice_date)) as varchar) || '-12-31' as date) as end_date
    from {{ ref('fact_sales') }}
    where invoice_date is not null
),
digits as (
    select 0 as d union all select 1 union all select 2 union all select 3 union all select 4
    union all select 5 union all select 6 union all select 7 union all select 8 union all select 9
),
numbers as (   -- 0..9999 days (about 27 years), independent of how much data exists
    select cast(a.d + 10 * b.d + 100 * c.d + 1000 * e.d as integer) as n
    from digits a cross join digits b cross join digits c cross join digits e
),
spine as (
    select b.start_date + n.n as date_key
    from bounds b
    join numbers n on b.start_date + n.n <= b.end_date
)
select
    date_key,
    extract(year from date_key)         as year,
    extract(quarter from date_key)      as quarter,
    extract(month from date_key)        as month,
    extract(day from date_key)          as day,
    extract(dayofweek from date_key)    as day_of_week,
    cast(date_trunc('month', date_key) as date) as month_start,
    cast(cast(extract(year from date_key) as varchar) || '-' ||
         lpad(cast(extract(month from date_key) as varchar), 2, '0') as varchar) as year_month
from spine
