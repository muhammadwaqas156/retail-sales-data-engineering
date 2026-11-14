# Business rules (v2, validated against docs/rule_checks.md on 2026-11-14)

| # | Evidence | Rule | Layer |
|---|---|---|---|
| R1 | 34,335 extra duplicate rows across 5,391 invoices. Sample shows identical lines (same invoice, timestamp, product, price) repeated 2-3 times. | Cannot be proven as errors vs genuine repeat scans. Assumption: treat as duplicates. Land all rows in Bronze with `row_hash` + `row_num_in_hash`. Silver drops repeats via a dbt var `dedupe_exact_rows` (default true). Report revenue with and without dedupe and state the difference in the dashboard notes. | Bronze/Silver |
| R2 | 19,494 `C` invoice rows; 19,493 have Quantity < 0, 1 has Quantity >= 0. | `is_cancellation = Invoice starts with 'C'`. Kept in `fact_sales`, reported as returns, not netted silently. The 1 anomaly row goes to a `dq_exceptions` table. | Silver |
| R3 | 3,457 non-C rows with Quantity <= 0: all Price 0, all no Customer ID, descriptions like damaged, missing, check, smashed, thrown away. | Confirmed as stock write-offs. `is_adjustment = true`. Excluded from revenue and units sold. Reported separately as stock loss rows. | Silver |
| R4 | 6,207 rows with Price <= 0: 3,457 are the R3 rows, 5 are negative "Adjust bad debt", the remainder (about 2,745, to verify) are free or zero-priced lines. | Price < 0 is a finance adjustment (`is_adjustment`). Price = 0 sets `is_zero_price`. Both excluded from revenue. | Silver |
| R5 | 22.77% null Customer ID. | Keep in sales and order totals. Exclude from customer metrics. `customer_key = -1` for unknown. | Gold |
| R6 | 4,382 null Descriptions, mostly the R3 rows (2,689). | Fill from another row with the same StockCode, else "Unknown". Nulls outside R3 should be near zero. | Silver |
| R7 | 63 non-standard StockCodes, 6,094 rows. | Seed table `ref_stockcode_class` (below). Non-product rows excluded from product rankings. Postage and fees reported as a separate revenue line. | Silver |
| R8 | Customer ID read as text. | Strip trailing `.0`. | Staging |

## ref_stockcode_class (seed, review before Phase 4)
| StockCode | Class |
|---|---|
| POST, DOT, C2 | postage / carriage |
| M | manual entry |
| D | discount |
| S | samples |
| BANK CHARGES, AMAZONFEE | fees |
| ADJUST, B | adjustment |
| CRUK | charity |
| TEST001 | test (exclude entirely) |
| gift_0001_* | gift voucher |
| DCGS*, PADS | probably real products, keep (verify) |

Revenue = Quantity x Price for rows that are not cancellations, adjustments, zero-price, non-product or test.
Return value = same calculation on `C` invoices, shown as a positive amount.
