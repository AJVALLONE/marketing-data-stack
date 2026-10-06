"""Pull daily campaign performance from the Google Ads API using GAQL."""
from datetime import date

import pandas as pd

from ingestion import config
from ingestion.schemas import GOOGLE_COLUMNS

QUERY = """
    SELECT
        segments.date,
        campaign.id,
        campaign.name,
        metrics.cost_micros,
        metrics.impressions,
        metrics.clicks,
        metrics.conversions,
        metrics.conversions_value
    FROM campaign
    WHERE segments.date BETWEEN '{start}' AND '{end}'
"""


def fetch_google_ads(start: date, end: date) -> pd.DataFrame:
    # Imported here so sample-data runs don't need the google-ads package installed.
    from google.ads.googleads.client import GoogleAdsClient

    if not config.GOOGLE_ADS_CUSTOMER_ID:
        raise RuntimeError("Set GOOGLE_ADS_CUSTOMER_ID in your .env file.")

    client = GoogleAdsClient.load_from_env()  # reads the GOOGLE_ADS_* variables
    service = client.get_service("GoogleAdsService")
    stream = service.search_stream(
        customer_id=config.GOOGLE_ADS_CUSTOMER_ID,
        query=QUERY.format(start=start.isoformat(), end=end.isoformat()),
    )

    rows = []
    for batch in stream:
        for row in batch.results:
            rows.append({
                "segments_date": row.segments.date,
                "campaign_id": str(row.campaign.id),
                "campaign_name": row.campaign.name,
                "cost_micros": int(row.metrics.cost_micros),
                "impressions": int(row.metrics.impressions),
                "clicks": int(row.metrics.clicks),
                "conversions": float(row.metrics.conversions),
                "conversions_value": float(row.metrics.conversions_value),
            })

    print(f"Google Ads: fetched {len(rows)} rows")
    return pd.DataFrame(rows, columns=GOOGLE_COLUMNS)
