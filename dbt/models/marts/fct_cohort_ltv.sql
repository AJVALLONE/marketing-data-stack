-- Cumulative revenue per customer by acquisition month and channel.
-- Grain: one row per cohort_month + acquisition_channel + months_since_first_order.
with orders as (
    select * from {{ ref('int_customer_orders') }}
),

cohort_sizes as (
    select
        cohort_month,
        acquisition_channel,
        count(distinct customer_id) as cohort_size
    from orders
    where is_first_order
    group by 1, 2
),

cohort_revenue as (
    select
        cohort_month,
        acquisition_channel,
        months_since_first_order,
        count(distinct customer_id) as active_customers,
        sum(revenue)                as revenue
    from orders
    group by 1, 2, 3
),

cumulative as (
    select
        r.cohort_month,
        r.acquisition_channel,
        r.months_since_first_order,
        s.cohort_size,
        r.active_customers,
        r.revenue,
        sum(r.revenue) over (
            partition by r.cohort_month, r.acquisition_channel
            order by r.months_since_first_order
            rows between unbounded preceding and current row
        ) as cumulative_revenue
    from cohort_revenue as r
    inner join cohort_sizes as s
        on r.cohort_month = s.cohort_month
        and r.acquisition_channel = s.acquisition_channel
)

select
    cast(cohort_month as {{ dbt.type_string() }}) || '|' || acquisition_channel
        || '|' || cast(months_since_first_order as {{ dbt.type_string() }}) as cohort_key,
    *,
    {{ safe_divide('active_customers', 'cohort_size') }}   as retention_rate,
    {{ safe_divide('cumulative_revenue', 'cohort_size') }} as cumulative_ltv_per_customer
from cumulative
