select 
dense_rank() over (order by sum(n_messages) desc) as ranking,
id_guest,
sum(n_messages) as t_messages
from airbnb_contacts
group by id_guest
order by t_messages desc
;