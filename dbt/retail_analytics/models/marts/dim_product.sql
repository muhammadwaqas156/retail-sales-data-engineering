with lines as (select * from {{ ref('fact_sales') }}),
latest_desc as (
    select product_key, description_value,
        row_number() over (partition by product_key order by invoice_ts desc) as rn
    from (
        select f.product_key, f.invoice_ts, t.description as description_value
        from lines f
        join {{ ref('int_transactions_classified') }} t on f.line_id = t.line_id
        where t.description is not null
    ) x
),
keys as (
    select product_key, max(product_class) as product_class, max(case when is_non_product then 1 else 0 end) as np
    from lines group by product_key
)
select k.product_key,
       coalesce(d.description_value, 'Unknown') as description,
       k.product_class,
       k.np = 1 as is_non_product
from keys k
left join latest_desc d on k.product_key = d.product_key and d.rn = 1
