-- Device dimension with an integer surrogate key (low-cardinality join key,
-- per the Power BI model-design review).
with devices as (
    select distinct device_type from {{ ref('stg_daily_savings') }}
)
select
    row_number() over (order by device_type) as device_key,
    device_type
from devices
