with source as (
    select * from {{ source('raw', 'orders') }}
)

select
    cast(order_id as {{ dbt.type_string() }})       as order_id,
    cast(customer_id as {{ dbt.type_string() }})    as customer_id,
    cast(order_date as date)                        as order_date,
    cast(revenue as {{ dbt.type_float() }})         as revenue,
    lower(trim(utm_source))                         as utm_source,
    -- Map messy UTM values onto a clean, fixed set of channels
    case
        when lower(trim(utm_source)) in ('facebook', 'fb', 'instagram', 'ig', 'meta') then 'meta'
        when lower(trim(utm_source)) in ('google', 'adwords', 'youtube') then 'google'
        when lower(trim(utm_source)) in ('email', 'klaviyo', 'newsletter') then 'email'
        when utm_source is null
          or trim(utm_source) = ''
          or lower(trim(utm_source)) in ('organic', 'direct') then 'organic'
        else 'other'
    end                                             as channel
from source
