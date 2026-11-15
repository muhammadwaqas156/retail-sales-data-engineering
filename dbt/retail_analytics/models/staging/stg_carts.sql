select
    record:id::integer               as cart_id,
    record:userId::integer           as user_id,
    record:total::decimal(18,2)      as total,
    record:discountedTotal::decimal(18,2) as discounted_total,
    record:totalProducts::integer    as total_products,
    record:totalQuantity::integer    as total_quantity,
    _batch_id, _source_file
from {{ source('bronze', 'raw_carts') }}
