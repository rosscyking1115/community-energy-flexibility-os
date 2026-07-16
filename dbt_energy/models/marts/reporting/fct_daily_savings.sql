-- The single fact table: one row per date x community x household x device, at a
-- consistent grain, with integer surrogate FKs to the dimensions. Power BI
-- imports this plus the dims and joins on the keys (a clean star, not a flat
-- wide table).
with s as (
    select * from {{ ref('stg_daily_savings') }}
)
select
    d.date_key,
    dev.device_key,
    com.community_key,
    s.household_id,
    s.baseline_cost_p,
    s.optimised_cost_p,
    s.cost_saving_p,
    s.carbon_saving_g,
    s.peak_slots_avoided,
    s.robustness_score
from s
join {{ ref('dim_date') }} d        on d.full_date = s.savings_date
join {{ ref('dim_device') }} dev     on dev.device_type = s.device_type
join {{ ref('dim_community') }} com   on com.community_id = s.community_id
