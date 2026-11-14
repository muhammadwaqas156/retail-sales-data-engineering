# Source data profile

## UCI Online Retail II (online_retail_II.xlsx)

- Sheets: Year 2009-2010, Year 2010-2011 | Rows: 1,067,371 | Columns: Invoice, StockCode, Description, Quantity, InvoiceDate, Price, Customer ID, Country
- Date range: 2009-12-01 07:45:00 to 2011-12-09 12:50:00
- Distinct invoices: 53,628 | customers: 5,942 | stock codes: 5,305
- Fully duplicated rows: 34,335
- Cancelled invoices (prefix 'C') rows: 19,494
- Rows with Quantity <= 0: 22,950
- Rows with Price <= 0: 6,207

### Nulls per column

| Column | Nulls | % |
|---|---|---|
| Invoice | 0 | 0.00% |
| StockCode | 0 | 0.00% |
| Description | 4,382 | 0.41% |
| Quantity | 0 | 0.00% |
| InvoiceDate | 0 | 0.00% |
| Price | 0 | 0.00% |
| Customer ID | 243,007 | 22.77% |
| Country | 0 | 0.00% |

## DummyJSON extracts (synthetic demo data)

- products: 194 records; fields: availabilityStatus, brand, category, description, dimensions, discountPercentage, id, images, meta, minimumOrderQuantity, price, rating, returnPolicy, reviews, shippingInformation, sku, stock, tags, thumbnail, title, warrantyInformation, weight
- carts: 208 records; fields: discountedTotal, id, products, total, totalProducts, totalQuantity, userId
- users: 208 records; fields: address, age, bank, birthDate, bloodGroup, company, crypto, ein, email, eyeColor, firstName, gender, hair, height, id, image, ip, lastName, macAddress, maidenName, password, phone, role, ssn, university, userAgent, username, weight
