-- Community dimension. Names are curated here; the fact carries only the key.
with communities as (
    select 'C1' as community_id, 'Riverside Centre' as community_name
    union all
    select 'C2' as community_id, 'Hilltop Community' as community_name
)
select
    row_number() over (order by community_id) as community_key,
    community_id,
    community_name
from communities
