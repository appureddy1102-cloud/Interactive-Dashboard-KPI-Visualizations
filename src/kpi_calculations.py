"""Safe, filter-aware executive KPI calculations."""
import numpy as np
import pandas as pd

def calculate_kpis(df, prior_df=None):
    revenue = float(df["Revenue"].sum()) if len(df) else 0.0
    orders = int(df["Order ID"].nunique()) if len(df) else 0
    customers = int(df["Customer ID"].nunique()) if len(df) else 0
    profit = float(df["Profit"].sum()) if len(df) else 0.0
    aov = revenue / orders if orders else np.nan
    discount = float(df["Discount"].mean()) if len(df) else np.nan
    prior = float(prior_df["Revenue"].sum()) if prior_df is not None and len(prior_df) else np.nan
    growth = (revenue / prior - 1) if pd.notna(prior) and prior != 0 else np.nan
    return {"revenue": revenue, "orders": orders, "customers": customers, "profit": profit,
            "aov": aov, "discount": discount, "growth": growth,
            "cac": np.nan, "churn": np.nan}
