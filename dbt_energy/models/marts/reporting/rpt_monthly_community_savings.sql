-- Monthly savings per community for the Community Comparison page.
select
    com.community_key,
    com.community_name,
    d.year,
    d.month,
    d.month_start,
    sum(f.cost_saving_p)        as total_cost_saving_p,
    sum(f.carbon_saving_g)      as total_carbon_saving_g,
    sum(f.peak_slots_avoided)   as peak_slots_avoided,
    avg(f.confidence)           as avg_confidence,
    count(distinct f.household_id) as household_count
from {{ ref('fct_daily_savings') }} f
join {{ ref('dim_date') }} d       on d.date_key = f.date_key
join {{ ref('dim_community') }} com on com.community_key = f.community_key
group by com.community_key, com.community_name, d.year, d.month, d.month_start
