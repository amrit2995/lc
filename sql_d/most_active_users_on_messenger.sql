with sent_users as (
    select user1, sum(msg_count) as sent_messages
    from fb_messages as fm
    group by user1
), received_users as (
    select user2, sum(msg_count) as received_messages
    from fb_messages as fm
    group by user2
), user_metrics as (
    select coalesce(user1, user2) as userm, 
    (coalesce(sent_messages, 0) + coalesce(received_messages, 0)) as total_messages
    from sent_users as su
    full outer join received_users as ru
    on su.user1 = ru.user2
), ranked_users as (
    select userm, total_messages,
    rank() over (order by total_messages desc) as msg_rank
    from user_metrics
)

select userm, total_messages
from ranked_users
where msg_rank <= 10
;