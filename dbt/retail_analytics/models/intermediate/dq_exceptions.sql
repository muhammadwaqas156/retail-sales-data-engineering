-- Rows that break an expected pattern (R2: cancellation with non-negative quantity).
select line_id, invoice_no, stock_code, quantity, unit_price, 'cancellation_with_non_negative_quantity' as issue
from {{ ref('int_transactions_classified') }}
where is_cancellation and quantity >= 0
