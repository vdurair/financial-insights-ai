import pandas as pd
from categorisation import categorise

def load_and_prepare(df):
    df = df.copy()

    # Standardise column names
    df.columns = [c.lower().strip() for c in df.columns]

    # Parse dates
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df["month"] = df["date"].dt.month
        df["year"] = df["date"].dt.year

    # Clean description
    if "description" in df.columns:
        df["description"] = df["description"].astype(str).str.upper()

    # Categorise
    df["category"] = df["description"].apply(categorise)

    return df