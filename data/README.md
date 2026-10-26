# Business data and provenance

This project uses the public Sample Superstore order-line teaching dataset from Tableau, retrieved from the publicly accessible mirror at https://raw.githubusercontent.com/leonism/sample-superstore/master/data/superstore.csv. The source mirror's redistribution license is unclear, so the CSV is not committed. `src/data_processing.py` downloads it on first run to `data/business_data.csv`. Please verify upstream redistribution rights before rehosting the data.

It is fictional/educational retail data (not actual company results). Fields include Order Date, Order ID, Customer ID, Category/Sub-Category, Segment, Region, State, Sales (USD), Profit (USD), Discount and Quantity. Country is the United States. No marketing spend, acquisition flag, explicit sales channel, or subscription/activity status is provided, so CAC, marketing efficiency, channel comparisons and formal customer churn cannot be calculated. No new fields or profit values are fabricated.

Preparation: exact duplicate lines removed; dates parsed with invalid dates coercible to missing; core analysis fields required; missing core values excluded; nonnegative sales retained; valid negative profit remains. Derived fields Revenue (= Sales), monthly date, year, and quarter are for dashboard slicing only.
