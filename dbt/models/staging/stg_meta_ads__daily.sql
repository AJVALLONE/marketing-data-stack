with source as (
    select * from {{ source('raw', 'meta_ads_daily') }}
),

renamed as (
    select
        cast(date_start as date)                              as date_day,
        'meta'                                                as channel,
        cast(campaign_id as {{ dbt.type_string() }})          as campaign_id,
        campaign_name,
        cast(spend as {{ dbt.type_float() }})                 as spend,
        cast(impressions as {{ dbt.type_int() }})             as impressions,
        cast(clicks as {{ dbt.type_int() }})                  as clicks,
        cast(purchases as {{ dbt.type_float() }})             as platform_conversions,
        cast(purchase_value as {{ dbt.type_float() }})        as platform_conversion_value
    from source
)

select
    cast(date_day as {{ dbt.type_string() }}) || '|' || campaign_id as campaign_day_id,
    *
from renamed
