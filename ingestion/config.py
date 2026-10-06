"""Central configuration. Values come from environment variables (or a .env file)."""
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

# Warehouse
DUCKDB_PATH = os.getenv("DUCKDB_PATH", str(ROOT_DIR / "data" / "marketing.duckdb"))
RAW_SCHEMA = os.getenv("RAW_SCHEMA", "raw")
GCP_PROJECT = os.getenv("GCP_PROJECT", "")
BQ_LOCATION = os.getenv("BQ_LOCATION", "US")

# Meta
META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN", "")
META_AD_ACCOUNT_ID = os.getenv("META_AD_ACCOUNT_ID", "").removeprefix("act_")
META_API_VERSION = os.getenv("META_API_VERSION", "v21.0")

# Google Ads (credentials are read directly by the google-ads library)
GOOGLE_ADS_CUSTOMER_ID = os.getenv("GOOGLE_ADS_CUSTOMER_ID", "").replace("-", "")

# Orders
ORDERS_CSV_PATH = os.getenv("ORDERS_CSV_PATH", str(ROOT_DIR / "data" / "orders_export.csv"))
