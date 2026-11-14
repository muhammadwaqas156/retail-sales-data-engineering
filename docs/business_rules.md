# Business rules (v1, based on docs/source_profile.md)

| # | Observation (from profile) | Rule | Layer |
|---|---|---|---|
| R1 | 34,335 fully duplicated rows (3.2%) | Land all rows in Bronze with a `row_hash`. Silver keeps one row per hash. Duplicates counted in the audit log, not silently dropped. Caveat: identical lines on one invoice can be genuine repeat scans, so review a sample before finalising. | Bronze/Silver |
| R2 | 19,494 rows on `C` invoices | `is_cancellation = true`. Kept in `fact_sales`, reported as a separate measure (returns), never netted away silently. | Silver |
| R3 | 22,950 rows with Quantity <= 0, more than the C rows | The extra non-C rows are likely stock adjustments or write-offs. Set `is_adjustment = true` and exclude them from revenue and units sold. Verify by querying non-C rows with Quantity <= 0. | Silver |
| R4 | 6,207 rows with Price <= 0 | Flag `is_zero_price`. Exclude from revenue. Keep for data-quality reporting. | Silver |
| R5 | 243,007 rows (22.77%) with null Customer ID | Keep in sales and order totals. Exclude from customer metrics (repeat rate, LTV). Surrogate `customer_key = -1` ("Guest/Unknown"). | Gold |
| R6 | 4,382 null Descriptions (0.41%) | Keep the row. Take the product name from another row with the same StockCode where possible, else "Unknown". | Silver |
| R7 | Non-product StockCodes (e.g. POST, M, DOT, BANK CHARGES) | Check with a query for non-numeric-pattern StockCodes. Flag `is_non_product`. Exclude from product rankings. | Silver |
| R8 | Customer ID read as text | Normalise (strip a trailing `.0`) in staging so it joins cleanly. | Staging |

Revenue = Quantity x Price for rows that are not cancellations, adjustments, zero-price or non-product.
Return value = the same calculation for `C` invoices, reported as a positive amount.

## Open checks before Phase 4
1. Are all `C` rows Quantity < 0? (expected yes)
2. What do the non-C, Quantity <= 0 rows look like (Price, Customer ID, Description)?
3. List StockCodes not matching `^\d{5}[A-Za-z]*$`.
4. Sample the duplicate rows.
