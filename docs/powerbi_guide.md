# Power BI dashboard (Phase 7)

Power BI Desktop is free and Windows-only (install from the Microsoft Store). Run it on Windows, not in WSL.

## 1. Connect to Snowflake
Get data -> Snowflake.
- Server: `<orgname-accountname>.snowflakecomputing.com`
- Warehouse: `RETAIL_WH`
- Advanced options -> Role name: `RETAIL_ROLE`
- Data Connectivity mode: **Import** (about a million rows, fine)
- Authentication: Database -> your Snowflake username and password
In the navigator choose `RETAIL_DB` -> `GOLD` -> `FACT_SALES`, `DIM_CUSTOMER`, `DIM_PRODUCT`, `DIM_DATE`. In Transform data, remove columns you won't use from FACT_SALES (e.g. `_batch_id`, `line_id` if you don't need it) to keep the file small.
If Snowflake rejects password login (MFA / security policy), tell Claude and we will switch to another auth method.

## 2. Model
Create the three relationships and mark `dim_date` as a Date table (see top of `powerbi/measures.dax`). Add the measures from that file.
Filters for product views: `dim_product[is_non_product] = FALSE`.

## 3. Pages
1. **Overview**: cards (Gross Sales, Net Sales, Orders, Average Order Value), line chart Gross Sales by month, bar by country (top 10), slicers for year and country.
2. **Products**: top 10 products by Gross Sales (non-products excluded), units sold, product table with description and class.
3. **Customers**: Known Customers, Repeat Customer Rate, top 10 customers by Gross Sales, Unknown Customer Sales %.
4. **Returns and cancellations**: Returns by month, Return Rate %, top returned products, Returns vs Gross Sales.
5. **Data notes**: the limitations text below.

## 4. Data notes text (paste on page 5)
- Source: UCI Online Retail II, a UK online giftware retailer, 1 Dec 2009 to 9 Dec 2011. Historical, not current.
- Revenue excludes cancellations, stock adjustments, zero-price lines, and non-product codes (postage, fees, vouchers). Postage and fees are shown separately.
- 22.8% of lines have no customer ID: they count in sales and orders but not in customer metrics.
- 34,335 exact duplicate rows (3.2%) are removed; switching this off in dbt changes totals.
- December 2011 is a partial month, so year-on-year comparisons for it are not like for like.
- Not Tesco data. DummyJSON (synthetic) is used only to practise API ingestion and is not in the dashboard.

## 5. Evidence and safety
Screenshot each page (hide the account name). Save screenshots to `docs/screenshots/`. Do not commit the `.pbix` file: it can embed your connection details. Publishing to the Power BI service normally needs a work or school email, so a personal Gmail may not work; screenshots are enough for the portfolio.
