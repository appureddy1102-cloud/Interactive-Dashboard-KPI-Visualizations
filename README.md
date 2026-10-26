# Interactive Dashboard & KPI Visualizations

A working Streamlit + Plotly executive dashboard for exploring revenue, profit, customers, orders, discounts, product mix and US regional performance. The app updates every KPI/chart from the sidebar selections and supports a downloadable PDF based on the currently filtered data.

> **Dataset disclosure:** This uses the Sample Superstore educational dataset (fictional instructional retail transactions), not live company data. It is not evidence of actual business performance. The source mirror's redistribution license is unclear, so the CSV is deliberately not checked in. The app downloads it to `data/business_data.csv` on first launch; see [`data/README.md`](data/README.md).

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Internet access is needed on first run to retrieve the source CSV. Once downloaded, the app uses the local ignored data file. It offers date, country, region, product category, segment and month/quarter/year trend-grain controls; use **Reset filters** to restore defaults. Click/select treemap tiles to drill into geography.

## KPIs and important limitations

- **Revenue**: sum of source `Sales` for the selected lines.
- **AOV**: filtered revenue divided by distinct `Order ID`.
- **Orders / customers**: distinct order/customer identifiers.
- **Revenue growth**: filtered revenue over the selected range versus the immediately preceding equal-length date window with the same dimension filters. Displays — if the comparison window is missing/zero.
- **Average discount**: arithmetic mean of source line-item `Discount`.
- **CAC and churn**: explicitly unavailable. No marketing cost/new-customer attribution, or well-defined active customer/status measure is provided. The dashboard does not substitute a made-up proxy.
- **Sales channel and marketing efficiency**: not present; corresponding breakouts are disclosed rather than fabricated.
- Profit is the source-provided value, preserved as-is, including losses. No profit is imputed.

The line-level sample can contain dependence within orders/customers, and US-only geographic coverage limits generalization. Cleaning details and provenance are in `data/README.md` and `src/data_processing.py`.

## PDF and preview

The repository includes `reports/Dashboard_Report.pdf`, generated from the source dataset's full-period computed KPIs and charts. The app's **Download filtered executive report (PDF)** button exports a fresh report from the current filters. [`assets/dashboard_preview.png`](assets/dashboard_preview.png) is a static portfolio preview, not a screenshot of a live deployed app.

## Deploy to Streamlit Community Cloud

1. Push this repository to GitHub.
2. In Streamlit Community Cloud, create an app from the repo, choose `main` and `app.py`.
3. Deploy. The app downloads the data source on startup; no secrets or credentials are required.

## Contents
`app.py` Streamlit dashboard · `src/` data and KPI functions · `data/README.md` provenance · `reports/Dashboard_Report.pdf` report · `assets/dashboard_preview.png` preview.
