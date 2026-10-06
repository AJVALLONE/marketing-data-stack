"""Unit tests for the sample data generator and the Meta response parser."""
from datetime import date

from ingestion.generate_sample_data import generate_all
from ingestion.meta_ads import _action_value
from ingestion.schemas import GOOGLE_COLUMNS, META_COLUMNS, ORDER_COLUMNS

START, END = date(2026, 1, 1), date(2026, 1, 31)


def test_tables_match_contracts():
    tables = generate_all(START, END)
    assert list(tables["meta_ads_daily"].columns) == META_COLUMNS
    assert list(tables["google_ads_daily"].columns) == GOOGLE_COLUMNS
    assert list(tables["orders"].columns) == ORDER_COLUMNS


def test_one_row_per_campaign_per_day():
    meta = generate_all(START, END)["meta_ads_daily"]
    assert not meta.duplicated(subset=["date_start", "campaign_id"]).any()
    assert meta["date_start"].nunique() == 31


def test_same_seed_is_reproducible():
    a = generate_all(START, END, seed=7)["orders"]
    b = generate_all(START, END, seed=7)["orders"]
    assert a.equals(b)


def test_orders_stay_in_range_and_ids_unique():
    orders = generate_all(START, END)["orders"]
    assert orders["order_id"].is_unique
    assert orders["order_date"].min() >= START.isoformat()
    assert orders["order_date"].max() <= END.isoformat()


def test_meta_action_parser():
    actions = [{"action_type": "link_click", "value": "40"}, {"action_type": "purchase", "value": "3"}]
    assert _action_value(actions, "purchase") == 3.0
    assert _action_value(actions, "lead") == 0.0
    assert _action_value(None, "purchase") == 0.0
