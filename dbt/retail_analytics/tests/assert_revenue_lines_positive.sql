-- Revenue lines must have positive amounts (business rules R2-R4).
select line_id from {{ ref('fact_sales') }}
where is_revenue_line and (line_amount <= 0 or quantity <= 0 or unit_price <= 0)
