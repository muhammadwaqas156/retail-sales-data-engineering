{# Grain: one invoice line. All lines kept; flags + measures say how each counts. #}
with base as (
    select *,
        (not is_cancellation and not is_adjustment and not is_zero_price
            and not is_non_product and quantity > 0)                       as is_revenue_line,
        (not is_cancellation and not is_adjustment and not is_zero_price
            and is_non_product and product_class <> 'test' and quantity > 0) as is_other_revenue_line,
        (is_cancellation and quantity < 0 and not is_zero_price and not is_non_product) as is_return_line
    from {{ ref('int_transactions_classified') }}
)
select
    line_id,
    invoice_no,
    invoice_ts,
    cast(invoice_ts as date)                          as invoice_date,
    coalesce(customer_id, '-1')                       as customer_key,
    stock_code                                        as product_key,
    country,
    quantity,
    unit_price,
    line_amount,
    product_class,
    is_cancellation, is_adjustment, is_zero_price, is_non_product,
    is_revenue_line, is_other_revenue_line, is_return_line,
    case when is_revenue_line then line_amount else 0 end        as gross_sales_amount,
    case when is_revenue_line then quantity else 0 end           as units_sold,
    case when is_other_revenue_line then line_amount else 0 end  as other_revenue_amount,
    case when is_return_line then abs(line_amount) else 0 end    as return_amount,
    case when is_return_line then abs(quantity) else 0 end       as units_returned,
    _batch_id
from base
