-- Business-level daily view: what did we spend, what came in, what did a customer cost?
select
    date_day,
    sum(spend)                                               as total_spend,
    sum(revenue)                                             as total_revenue,
    sum(orders)                                              as total_orders,
    sum(new_customers)                                       as new_customers,
    sum(case when channel in ('meta', 'google') then new_customers else 0 end)
                                                             as paid_new_customers,
    {{ safe_divide('sum(revenue)', 'sum(spend)') }}          as mer,
    {{ safe_divide('sum(spend)', 'sum(new_customers)') }}    as blended_cac
from {{ ref('fct_channel_daily') }}
group by 1
