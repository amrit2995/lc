with total_travel as (
    select user_id,
        sum(distance) as total_dist
    from lyft_rides_log
    group by user_id
), rank_total_dist as (
    select *,
    rank() over (order by total_dist desc) as dist_rank
    from total_travel
)

select lu.id as id, lu.name as name, rtd.total_dist as dsitance_travelled
from rank_total_dist as rtd
join lyft_users as lu
on lu.id = rtd.user_id
where rtd.dist_rank <= 10
order by rtd.dist_rank
;