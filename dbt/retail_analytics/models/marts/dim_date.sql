select
    invoice_date                                   as date_key,
    extract(year from invoice_date)                as year,
    extract(quarter from invoice_date)             as quarter,
    extract(month from invoice_date)               as month,
    extract(day from invoice_date)                 as day,
    extract(dayofweek from invoice_date)           as day_of_week,
    date_trunc('month', invoice_date)              as month_start
from (select distinct invoice_date from {{ ref('fact_sales') }} where invoice_date is not null) d
