"""Load raw DataFrames into the warehouse (DuckDB locally, BigQuery in the cloud).

Each run fully replaces the raw tables. That keeps the pipeline idempotent:
running it twice gives the same result as running it once.
"""
from pathlib import Path

import pandas as pd

from ingestion import config


def _add_metadata(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["_loaded_at"] = pd.Timestamp.now(tz="UTC")
    return df


def load_to_duckdb(tables: dict[str, pd.DataFrame]) -> None:
    import duckdb

    Path(config.DUCKDB_PATH).parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(config.DUCKDB_PATH)
    try:
        con.execute(f"create schema if not exists {config.RAW_SCHEMA}")
        for name, df in tables.items():
            con.register("incoming_df", _add_metadata(df))
            con.execute(f"create or replace table {config.RAW_SCHEMA}.{name} as select * from incoming_df")
            con.unregister("incoming_df")
            print(f"Loaded {len(df):>7,} rows -> {config.RAW_SCHEMA}.{name} (DuckDB)")
    finally:
        con.close()


def load_to_bigquery(tables: dict[str, pd.DataFrame]) -> None:
    from google.cloud import bigquery

    if not config.GCP_PROJECT:
        raise RuntimeError("Set GCP_PROJECT in your .env file.")

    client = bigquery.Client(project=config.GCP_PROJECT)
    dataset = bigquery.Dataset(f"{config.GCP_PROJECT}.{config.RAW_SCHEMA}")
    dataset.location = config.BQ_LOCATION
    client.create_dataset(dataset, exists_ok=True)

    job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
    for name, df in tables.items():
        table_id = f"{config.GCP_PROJECT}.{config.RAW_SCHEMA}.{name}"
        client.load_table_from_dataframe(_add_metadata(df), table_id, job_config=job_config).result()
        print(f"Loaded {len(df):>7,} rows -> {table_id} (BigQuery)")


def load(tables: dict[str, pd.DataFrame], target: str) -> None:
    if target == "duckdb":
        load_to_duckdb(tables)
    elif target == "bigquery":
        load_to_bigquery(tables)
    else:
        raise ValueError(f"Unknown target: {target}")
