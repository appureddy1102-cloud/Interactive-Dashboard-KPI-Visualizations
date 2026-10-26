"""Source acquisition and validation for Sample Superstore retail order lines."""
from pathlib import Path
from urllib.request import urlretrieve
import pandas as pd
SOURCE_URL = "https://raw.githubusercontent.com/leonism/sample-superstore/master/data/superstore.csv"

def load_data(path=None):
    path = Path(path) if path else Path(__file__).resolve().parents[1] / "data" / "business_data.csv"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        urlretrieve(SOURCE_URL, path)
    df = pd.read_csv(path, encoding="utf-8-sig")
    raw_rows = len(df)
    duplicate_rows_removed = int(df.duplicated().sum())
    df = df.drop_duplicates().copy()
    df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")
    df["Ship Date"] = pd.to_datetime(df["Ship Date"], errors="coerce")
    for c in ["Sales", "Profit", "Discount", "Quantity"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    required = ["Order Date", "Order ID", "Customer ID", "Sales", "Profit", "Discount", "Category", "Segment", "Region"]
    missing_required = int(df[required].isna().any(axis=1).sum())
    df = df.dropna(subset=required)
    df = df[df.Sales >= 0].copy()
    df["Country"] = df.get("Country", "United States")
    df["Revenue"] = df["Sales"]
    df["Order Month"] = df["Order Date"].dt.to_period("M").dt.to_timestamp()
    df["Year"] = df["Order Date"].dt.year
    df["Quarter"] = df["Order Date"].dt.to_period("Q").astype(str)
    audit = {"rows": len(df), "raw_rows": raw_rows, "duplicate_rows_removed": duplicate_rows_removed,
             "missing_required": missing_required,
             "date_min": df["Order Date"].min(), "date_max": df["Order Date"].max()}
    return df, audit
