# Data dictionary – UCI Online Retail II (raw)
| Column | Type | Description |
|---|---|---|
| Invoice | string | Invoice number; 6 digits, prefix `C` = cancellation |
| StockCode | string | Product code |
| Description | string | Product name |
| Quantity | int | Units per line (negative for returns) |
| InvoiceDate | datetime | Invoice date/time |
| Price | float | Unit price (GBP) |
| Customer ID | string | 5-digit customer id; may be null |
| Country | string | Customer country |

Column meanings follow the UCI dataset page; verify against `docs/source_profile.md` once generated.

## Profile facts (generated 2026-11-14)
Rows 1,067,371 | invoices 53,628 | customers 5,942 | stock codes 5,305 | 2009-12-01 to 2011-12-09.
Nulls: Description 4,382 (0.41%), Customer ID 243,007 (22.77%); all other columns complete.
See `business_rules.md` for derived flags (`is_cancellation`, `is_adjustment`, `is_zero_price`, `is_non_product`, `row_hash`).

## DummyJSON (synthetic)
- products (194): id, title, category, brand, price, stock, rating, sku, ...
- carts (208): id, userId, products[], total, discountedTotal, totalProducts, totalQuantity
- users (208): id, name/contact fields, address, company; contains fake sensitive fields to drop (see `source_limitations.md`)
