select line_id from {{ ref('fact_sales') }}
where is_cancellation and (gross_sales_amount <> 0 or units_sold <> 0)
