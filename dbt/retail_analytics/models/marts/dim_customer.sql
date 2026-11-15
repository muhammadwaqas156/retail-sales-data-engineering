with lines as (
    select * from {{ ref('fact_sales') }} where customer_key <> '-1'
),
latest as (
    select customer_key, country,
        row_number() over (partition by customer_key order by invoice_ts desc) as rn
    from lines
),
agg as (
    select customer_key,
        min(invoice_date) as first_invoice_date,
        max(invoice_date) as last_invoice_date,
        count(distinct case when is_revenue_line then invoice_no end) as order_count
    from lines group by customer_key
)
select a.customer_key, l.country, a.first_invoice_date, a.last_invoice_date, a.order_count
from agg a join latest l on a.customer_key = l.customer_key and l.rn = 1
union all
select '-1', 'Unknown', null, null, 0
