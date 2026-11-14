# Business requirements (draft)
Questions the platform should answer:
1. Revenue and order-count trends by day/month, by country.
2. Top products by revenue and units.
3. Customer analysis: new vs repeat, revenue concentration (known customers only).
4. Returns/cancellations: volume and value, as a share of gross sales.

## Business rules (to confirm after profiling – Phase 6)
- Invoice starting `C` = cancellation/return; kept in a separate measure, not netted silently.
- Rows with Quantity <= 0 or Price <= 0 are flagged, not deleted, at Bronze.
- Missing Customer ID rows stay in sales totals but are excluded from customer metrics.
