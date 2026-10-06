"""Generate realistic synthetic ad and order data.

This lets anyone clone the repo and run the full pipeline without API credentials.
The shapes match what the real Meta and Google Ads APIs return (for example,
Google reports cost in micros: 1,000,000 micros = $1).
"""
import random
from datetime import date, timedelta

import pandas as pd

from ingestion.schemas import GOOGLE_COLUMNS, META_COLUMNS, ORDER_COLUMNS

META_CAMPAIGNS = [
    ("23850000000000001", "Prospecting - Broad", 220, 0.020),
    ("23850000000000002", "Retargeting - 30d Visitors", 80, 0.050),
]
GOOGLE_CAMPAIGNS = [
    ("1100000001", "Search - Brand", 60, 0.080),
    ("1100000002", "Search - Non-Brand", 150, 0.030),
    ("1100000003", "Performance Max", 120, 0.025),
]
# (utm_source, min, max) new customers per day before seasonality
NEW_CUSTOMER_SOURCES = [("facebook", 4, 9), ("google", 3, 8), ("organic", 2, 6), ("email", 1, 3)]
REPEAT_SOURCES = ["email", "email", "organic", "google", "facebook"]


def _daterange(start: date, end: date):
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


def _seasonality(d: date) -> float:
    """Weekend dip plus a Q4 holiday lift."""
    weekday = 0.85 if d.weekday() >= 5 else 1.0
    q4 = 1.35 if d.month in (11, 12) else 1.0
    return weekday * q4


def _binomial(rng: random.Random, n: int, p: float) -> int:
    return sum(1 for _ in range(n) if rng.random() < p)


def generate_meta(start: date, end: date, rng: random.Random) -> pd.DataFrame:
    rows = []
    for d in _daterange(start, end):
        for campaign_id, name, base_spend, cvr in META_CAMPAIGNS:
            spend = round(base_spend * _seasonality(d) * rng.uniform(0.8, 1.2), 2)
            impressions = int(spend / rng.uniform(9, 16) * 1000)  # CPM of $9-16
            clicks = int(impressions * rng.uniform(0.008, 0.018))
            purchases = _binomial(rng, clicks, cvr)
            rows.append({
                "date_start": d.isoformat(),
                "campaign_id": campaign_id,
                "campaign_name": name,
                "spend": spend,
                "impressions": impressions,
                "clicks": clicks,
                "purchases": float(purchases),
                "purchase_value": round(purchases * rng.uniform(45, 75), 2),
            })
    return pd.DataFrame(rows, columns=META_COLUMNS)


def generate_google(start: date, end: date, rng: random.Random) -> pd.DataFrame:
    rows = []
    for d in _daterange(start, end):
        for campaign_id, name, base_spend, cvr in GOOGLE_CAMPAIGNS:
            spend = base_spend * _seasonality(d) * rng.uniform(0.8, 1.2)
            clicks = int(spend / rng.uniform(0.9, 2.5))  # CPC of $0.90-2.50
            impressions = int(clicks / rng.uniform(0.03, 0.08))
            conversions = _binomial(rng, clicks, cvr)
            rows.append({
                "segments_date": d.isoformat(),
                "campaign_id": campaign_id,
                "campaign_name": name,
                "cost_micros": int(spend * 1_000_000),
                "impressions": impressions,
                "clicks": clicks,
                "conversions": float(conversions),
                "conversions_value": round(conversions * rng.uniform(45, 75), 2),
            })
    return pd.DataFrame(rows, columns=GOOGLE_COLUMNS)


def generate_orders(start: date, end: date, rng: random.Random) -> pd.DataFrame:
    orders = []
    customer_seq = 0
    for d in _daterange(start, end):
        for source, low, high in NEW_CUSTOMER_SOURCES:
            for _ in range(int(rng.randint(low, high) * _seasonality(d))):
                customer_seq += 1
                customer_id = f"C{customer_seq:06d}"
                orders.append((customer_id, d, round(rng.uniform(35, 90), 2), source))
                # Repeat purchases: each one has a 35% chance of leading to another
                next_date = d
                while rng.random() < 0.35:
                    next_date += timedelta(days=rng.randint(20, 75))
                    if next_date > end:
                        break
                    orders.append((customer_id, next_date, round(rng.uniform(35, 90), 2),
                                   rng.choice(REPEAT_SOURCES)))

    orders.sort(key=lambda o: (o[1], o[0]))
    rows = [
        {
            "order_id": f"O{i:07d}",
            "customer_id": customer_id,
            "order_date": order_date.isoformat(),
            "revenue": revenue,
            "utm_source": source,
        }
        for i, (customer_id, order_date, revenue, source) in enumerate(orders, start=1)
    ]
    return pd.DataFrame(rows, columns=ORDER_COLUMNS)


def generate_all(start: date, end: date, seed: int = 42) -> dict[str, pd.DataFrame]:
    rng = random.Random(seed)
    return {
        "meta_ads_daily": generate_meta(start, end, rng),
        "google_ads_daily": generate_google(start, end, rng),
        "orders": generate_orders(start, end, rng),
    }
