"""Load an orders export (Shopify, WooCommerce, your ESP...) from CSV."""
from pathlib import Path

import pandas as pd

from ingestion.schemas import ORDER_COLUMNS


def load_orders_csv(path: str) -> pd.DataFrame:
    if not Path(path).exists():
        raise FileNotFoundError(f"Orders file not found: {path}")

    df = pd.read_csv(path, dtype={"order_id": str, "customer_id": str, "utm_source": str})
    missing = set(ORDER_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"Orders CSV is missing columns: {sorted(missing)}")

    df["order_date"] = pd.to_datetime(df["order_date"]).dt.date.astype(str)
    df["revenue"] = df["revenue"].astype(float)
    print(f"Orders: loaded {len(df)} rows from {path}")
    return df[ORDER_COLUMNS]
