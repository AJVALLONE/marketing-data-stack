"""Column contracts for the raw tables. Every source must produce exactly these columns."""

META_COLUMNS = [
    "date_start", "campaign_id", "campaign_name", "spend",
    "impressions", "clicks", "purchases", "purchase_value",
]

GOOGLE_COLUMNS = [
    "segments_date", "campaign_id", "campaign_name", "cost_micros",
    "impressions", "clicks", "conversions", "conversions_value",
]

ORDER_COLUMNS = ["order_id", "customer_id", "order_date", "revenue", "utm_source"]
