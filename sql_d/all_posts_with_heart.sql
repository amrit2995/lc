with heart_posts as (
    select distinct(post_id)
    from facebook_reactions as fr
    where reaction = 'heart'
)

select * 
from facebook_posts
where post_id in (select post_id from heart_posts)
;