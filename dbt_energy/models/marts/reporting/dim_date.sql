-- Date dimension for the Power BI star. Integer surrogate key (yyyymmdd).
with dates as (
    select distinct savings_date from {{ ref('stg_daily_savings') }}
)
select
    extract(year from savings_date) * 10000
        + extract(month from savings_date) * 100
        + extract(day from savings_date)        as date_key,
    savings_date                                 as full_date,
    extract(year from savings_date)              as year,
    extract(month from savings_date)             as month,
    date_trunc('month', savings_date)            as month_start,
    dayname(savings_date)                        as day_name,
    case when dayname(savings_date) in ('Saturday', 'Sunday') then true else false end
        as is_weekend
from dates
