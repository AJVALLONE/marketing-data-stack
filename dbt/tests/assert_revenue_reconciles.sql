-- Every dollar of order revenue in staging must land in the mart (nothing dropped in joins).
with staged as (
    select sum(revenue) as staging_revenue from {{ ref('stg_shop__orders') }}
),
mart as (
    select sum(revenue) as mart_revenue from {{ ref('fct_channel_daily') }}
)
select *
from staged
cross join mart
where abs(staging_revenue - mart_revenue) > 0.01
