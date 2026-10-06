"""Pull daily campaign performance from the Meta Marketing API (Insights endpoint)."""
import json
from datetime import date

import pandas as pd
import requests

from ingestion import config
from ingestion.schemas import META_COLUMNS

# Meta reports results as a list of {"action_type": ..., "value": ...} dicts.
# "purchase" is the de-duplicated purchase count across pixel and Conversions API.
PURCHASE_ACTION = "purchase"
FIELDS = "campaign_id,campaign_name,spend,impressions,clicks,actions,action_values"


def _action_value(actions: list | None, action_type: str) -> float:
    for action in actions or []:
        if action.get("action_type") == action_type:
            return float(action.get("value", 0))
    return 0.0


def fetch_meta_insights(start: date, end: date) -> pd.DataFrame:
    if not config.META_ACCESS_TOKEN or not config.META_AD_ACCOUNT_ID:
        raise RuntimeError("Set META_ACCESS_TOKEN and META_AD_ACCOUNT_ID in your .env file.")

    url = (f"https://graph.facebook.com/{config.META_API_VERSION}"
           f"/act_{config.META_AD_ACCOUNT_ID}/insights")
    params = {
        "access_token": config.META_ACCESS_TOKEN,
        "level": "campaign",
        "time_increment": 1,  # one row per campaign per day
        "time_range": json.dumps({"since": start.isoformat(), "until": end.isoformat()}),
        "fields": FIELDS,
        "limit": 500,
    }

    rows = []
    while url:
        response = requests.get(url, params=params, timeout=60)
        if response.status_code != 200:
            raise RuntimeError(f"Meta API error {response.status_code}: {response.text}")
        payload = response.json()

        for record in payload.get("data", []):
            rows.append({
                "date_start": record["date_start"],
                "campaign_id": record["campaign_id"],
                "campaign_name": record.get("campaign_name"),
                "spend": float(record.get("spend", 0)),
                "impressions": int(record.get("impressions", 0)),
                "clicks": int(record.get("clicks", 0)),
                "purchases": _action_value(record.get("actions"), PURCHASE_ACTION),
                "purchase_value": _action_value(record.get("action_values"), PURCHASE_ACTION),
            })

        # The "next" URL already contains every query parameter, including the token.
        url = payload.get("paging", {}).get("next")
        params = None

    print(f"Meta: fetched {len(rows)} rows")
    return pd.DataFrame(rows, columns=META_COLUMNS)
