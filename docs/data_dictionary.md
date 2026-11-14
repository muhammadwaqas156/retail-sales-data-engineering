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
