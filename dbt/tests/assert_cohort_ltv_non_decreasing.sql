-- Cumulative LTV can only go up over time within a cohort.
with ordered as (
    select
        *,
        lag(cumulative_ltv_per_customer) over (
            partition by cohort_month, acquisition_channel
            order by months_since_first_order
        ) as previous_ltv
    from {{ ref('fct_cohort_ltv') }}
)
select *
from ordered
where cumulative_ltv_per_customer < previous_ltv - 0.0001
