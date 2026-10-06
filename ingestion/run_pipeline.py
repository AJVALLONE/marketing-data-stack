"""Extract + load entry point.

Examples:
    python -m ingestion.run_pipeline                       # sample data -> DuckDB
    python -m ingestion.run_pipeline --source live --target bigquery --start 2026-01-01
"""
import argparse
from datetime import date, timedelta

from ingestion import config
from ingestion.load import load


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract ad + order data and load it raw.")
    parser.add_argument("--source", choices=["sample", "live"], default="sample")
    parser.add_argument("--target", choices=["duckdb", "bigquery"], default="duckdb")
    parser.add_argument("--start", type=date.fromisoformat, help="YYYY-MM-DD")
    parser.add_argument("--end", type=date.fromisoformat, help="YYYY-MM-DD (default: yesterday)")
    args = parser.parse_args()

    end = args.end or date.today() - timedelta(days=1)
    start = args.start or end - timedelta(days=364)
    print(f"Running {args.source} pipeline for {start} to {end} -> {args.target}")

    if args.source == "sample":
        from ingestion.generate_sample_data import generate_all
        tables = generate_all(start, end)
    else:
        from ingestion.google_ads import fetch_google_ads
        from ingestion.meta_ads import fetch_meta_insights
        from ingestion.orders import load_orders_csv
        tables = {
            "meta_ads_daily": fetch_meta_insights(start, end),
            "google_ads_daily": fetch_google_ads(start, end),
            "orders": load_orders_csv(config.ORDERS_CSV_PATH),
        }

    load(tables, target=args.target)
    print("Done. Next: dbt build --project-dir dbt --profiles-dir dbt")


if __name__ == "__main__":
    main()
