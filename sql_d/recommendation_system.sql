select distinct uf.user_id, up.page_id
from users_friends as uf
join users_pages as up
on uf.friend_id = up.user_id
where not exists (
    select *
    from users_pages as pg
    where pg.user_id = uf.user_id
    and pg.page_id = up.page_id
)