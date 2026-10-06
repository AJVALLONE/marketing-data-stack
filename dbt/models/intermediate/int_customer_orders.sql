-- Enrich each order with the customer's order sequence and acquisition channel.
with orders as (
    select * from {{ ref('stg_shop__orders') }}
),

sequenced as (
    select
        order_id,
        customer_id,
        order_date,
        revenue,
        channel,
        row_number() over (
            partition by customer_id order by order_date, order_id
        ) as order_number,
        min(order_date) over (partition by customer_id) as first_order_date,
        -- First-touch attribution: the channel of the customer's first order
        first_value(channel) over (
            partition by customer_id order by order_date, order_id
            rows between unbounded preceding and unbounded following
        ) as acquisition_channel
    from orders
)

select
    *,
    order_number = 1 as is_first_order,
    cast({{ dbt.date_trunc('month', 'first_order_date') }} as date) as cohort_month,
    (extract(year from order_date) - extract(year from first_order_date)) * 12
        + (extract(month from order_date) - extract(month from first_order_date))
        as months_since_first_order
from sequenced
