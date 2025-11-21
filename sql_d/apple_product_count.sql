select pu.language, count(pu.user_id) as t_users,
    (
        count(distinct case when device in ('macbook pro','iphone 5s','ipad air') then pe.user_id
        else null end )
    ) as a_users
from playbook_events as pe
join playbook_users as pu
on pe.user_id = pu.user_id
group by pu.language
order by t_users desc
;