-- Cleaned per-task daily savings (optimiser output). One row per
-- date x community x household x device.
with src as (
    select * from {{ ref('seed_daily_savings') }}
)
select
    cast(savings_date as date)          as savings_date,
    cast(community_id as varchar)        as community_id,
    cast(household_id as varchar)        as household_id,
    cast(device_type as varchar)         as device_type,
    cast(baseline_cost_p as double)      as baseline_cost_p,
    cast(optimised_cost_p as double)     as optimised_cost_p,
    cast(cost_saving_p as double)        as cost_saving_p,
    cast(carbon_saving_g as double)      as carbon_saving_g,
    cast(peak_slots_avoided as integer)  as peak_slots_avoided,
    cast(confidence as double)           as confidence,
    cast(confidence_band as varchar)     as confidence_band
from src
