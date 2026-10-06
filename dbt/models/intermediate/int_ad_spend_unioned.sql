-- Combine both ad platforms into one shape so downstream models treat them identically.
{% set columns = [
    'campaign_day_id', 'date_day', 'channel', 'campaign_id', 'campaign_name',
    'spend', 'impressions', 'clicks', 'platform_conversions', 'platform_conversion_value'
] %}

select {{ columns | join(', ') }} from {{ ref('stg_meta_ads__daily') }}
union all
select {{ columns | join(', ') }} from {{ ref('stg_google_ads__daily') }}
