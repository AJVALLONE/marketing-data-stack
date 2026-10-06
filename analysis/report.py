"""Build the README charts from the dbt marts (DuckDB).

Run after `dbt build`:  python analysis/report.py
"""
import os
from pathlib import Path

import duckdb
import matplotlib

matplotlib.use("Agg")  # render to files, no display needed
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = os.getenv("DUCKDB_PATH", str(ROOT / "data" / "marketing.duckdb"))
OUT_DIR = ROOT / "docs" / "images"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(DB_PATH, read_only=True)

    # 1. Monthly spend vs revenue, with MER
    monthly = con.sql("""
        select
            date_trunc('month', date_day) as month,
            sum(total_spend)   as spend,
            sum(total_revenue) as revenue,
            sum(total_revenue) / nullif(sum(total_spend), 0) as mer
        from analytics.fct_blended_daily
        group by 1 order by 1
    """).df()

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(monthly["month"], monthly["revenue"], width=20, label="Revenue")
    ax.bar(monthly["month"], monthly["spend"], width=20, label="Ad spend")
    ax2 = ax.twinx()
    ax2.plot(monthly["month"], monthly["mer"], color="black", marker="o", label="MER")
    ax2.set_ylabel("MER (revenue / spend)")
    ax.set_title("Monthly revenue vs. ad spend")
    ax.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(OUT_DIR / "monthly_mer.png", dpi=120)
    plt.close(fig)

    # 2. Platform-reported vs. first-party ROAS
    roas = con.sql("""
        select
            channel,
            sum(platform_conversion_value) / sum(spend) as platform_roas,
            sum(revenue) / sum(spend)                   as attributed_roas
        from analytics.fct_channel_daily
        where channel in ('meta', 'google')
        group by 1 order by 1
    """).df()

    fig, ax = plt.subplots(figsize=(7, 4.5))
    x = range(len(roas))
    ax.bar([i - 0.2 for i in x], roas["platform_roas"], width=0.4, label="Platform-reported")
    ax.bar([i + 0.2 for i in x], roas["attributed_roas"], width=0.4, label="First-party (UTM)")
    ax.set_xticks(list(x), roas["channel"])
    ax.set_ylabel("ROAS")
    ax.set_title("What the platforms claim vs. what the store recorded")
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT_DIR / "roas_comparison.png", dpi=120)
    plt.close(fig)

    # 3. Cohort LTV curves by acquisition channel
    ltv = con.sql("""
        select
            acquisition_channel,
            months_since_first_order,
            sum(cumulative_revenue) / sum(cohort_size) as ltv
        from analytics.fct_cohort_ltv
        where months_since_first_order <= 6
        group by 1, 2 order by 1, 2
    """).df()

    fig, ax = plt.subplots(figsize=(8, 5))
    for channel, group in ltv.groupby("acquisition_channel"):
        ax.plot(group["months_since_first_order"], group["ltv"], marker="o", label=channel)
    ax.set_xlabel("Months since first order")
    ax.set_ylabel("Cumulative revenue per customer ($)")
    ax.set_title("Customer LTV by acquisition channel")
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT_DIR / "cohort_ltv.png", dpi=120)
    plt.close(fig)

    con.close()
    print(f"Charts saved to {OUT_DIR}")


if __name__ == "__main__":
    main()
