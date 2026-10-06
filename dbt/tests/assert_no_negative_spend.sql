-- Spend should never be negative. Any rows returned = test failure.
select *
from {{ ref('fct_channel_daily') }}
where spend < 0
