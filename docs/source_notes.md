# Source notes

## UCI Online Retail II
- Page: https://archive.ics.uci.edu/dataset/502/online+retail+ii
- Format: Excel workbook, two sheets (2009-2010, 2010-2011). Transactions of a UK-based online giftware retailer.
- Historical only; no live updates. Check licence/terms on the UCI page before publishing any derived data.
- Known quirks to confirm in profiling: missing Customer ID, invoices prefixed `C` (cancellations), negative quantities, zero prices, non-product stock codes (postage, adjustments), duplicate rows.

## DummyJSON
- Docs: https://dummyjson.com/docs. Endpoints: `/products`, `/carts`, `/users` (paged with `limit`/`skip`).
- Synthetic data; product/user IDs do **not** join to UCI StockCode/Customer ID. Use for ingestion practice and catalogue enrichment demos only, and say so in all outputs.

## Not used
Scraping Tesco or assuming a public Tesco sales API: retailer sales data is restricted to approved partners.
