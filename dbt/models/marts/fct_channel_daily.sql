-- Spend and revenue by channel by day. Grain: one row per date_day + channel.
with ad_spend as (
    select
        date_day,
        channel,
        sum(spend)                      as spend,
        sum(impressions)                as impressions,
        sum(clicks)                     as clicks,
        sum(platform_conversions)       as platform_conversions,
        sum(platform_conversion_value)  as platform_conversion_value
    from {{ ref('int_ad_spend_unioned') }}
    group by 1, 2
),

orders as (
    select
        order_date                                            as date_day,
        channel,
        count(*)                                              as orders,
        sum(revenue)                                          as revenue,
        sum(case when is_first_order then 1 else 0 end)       as new_customers,
        sum(case when is_first_order then revenue else 0 end) as new_customer_revenue
    from {{ ref('int_customer_orders') }}
    group by 1, 2
),

joined as (
    select
        coalesce(a.date_day, o.date_day)          as date_day,
        coalesce(a.channel, o.channel)            as channel,
        coalesce(a.spend, 0)                      as spend,
        coalesce(a.impressions, 0)                as impressions,
        coalesce(a.clicks, 0)                     as clicks,
        coalesce(a.platform_conversions, 0)       as platform_conversions,
        coalesce(a.platform_conversion_value, 0)  as platform_conversion_value,
        coalesce(o.orders, 0)                     as orders,
        coalesce(o.revenue, 0)                    as revenue,
        coalesce(o.new_customers, 0)              as new_customers,
        coalesce(o.new_customer_revenue, 0)       as new_customer_revenue
    from ad_spend as a
    full outer join orders as o
        on a.date_day = o.date_day
        and a.channel = o.channel
)

select
    cast(date_day as {{ dbt.type_string() }}) || '|' || channel as channel_day_id,
    *,
    {{ safe_divide('clicks', 'impressions') }}                 as ctr,
    {{ safe_divide('spend', 'clicks') }}                       as cpc,
    {{ safe_divide('platform_conversion_value', 'spend') }}    as platform_roas,
    {{ safe_divide('revenue', 'spend') }}                      as attributed_roas,
    {{ safe_divide('spend', 'new_customers') }}                as cac
from joined
