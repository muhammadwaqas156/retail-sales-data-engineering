-- Applies business rules R1-R7 (docs/business_rules.md).
with ranked as (
    select
        t.*,
        row_number() over (partition by row_hash order by _source_file, _file_row_number) as dup_rank
    from {{ ref('stg_transactions') }} t
),
deduped as (
    select * from ranked
    {% if var('dedupe_exact_rows') %} where dup_rank = 1 {% endif %}
),
classified as (
    select
        d.*,
        coalesce(c.product_class,
                 case when lower(d.stock_code) like 'gift_0001%' then 'gift_voucher' end,
                 'product') as product_class
    from deduped d
    left join {{ ref('ref_stockcode_class') }} c on d.stock_code = upper(c.stock_code)
)
select
    md5(row_hash || '|' || cast(dup_rank as varchar))              as line_id,
    *,
    invoice_no like 'C%'                                           as is_cancellation,
    (invoice_no not like 'C%' and quantity <= 0) or unit_price < 0 as is_adjustment,
    unit_price = 0                                                 as is_zero_price,
    product_class <> 'product'                                     as is_non_product,
    quantity * unit_price                                          as line_amount
from classified
