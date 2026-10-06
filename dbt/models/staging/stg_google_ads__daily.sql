with source as (
    select * from {{ source('raw', 'google_ads_daily') }}
),

renamed as (
    select
        cast(segments_date as date)                           as date_day,
        'google'                                              as channel,
        cast(campaign_id as {{ dbt.type_string() }})          as campaign_id,
        campaign_name,
        -- Google reports cost in micros: 1,000,000 micros = 1 unit of currency
        cast(cost_micros as {{ dbt.type_float() }}) / 1000000 as spend,
        cast(impressions as {{ dbt.type_int() }})             as impressions,
        cast(clicks as {{ dbt.type_int() }})                  as clicks,
        cast(conversions as {{ dbt.type_float() }})           as platform_conversions,
        cast(conversions_value as {{ dbt.type_float() }})     as platform_conversion_value
    from source
)

select
    cast(date_day as {{ dbt.type_string() }}) || '|' || campaign_id as campaign_day_id,
    *
from renamed
