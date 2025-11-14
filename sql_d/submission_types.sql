with type_count_table as (SELECT 
  user_id, type
FROM loans
WHERE type IN ('Refinance', 'InSchool')
GROUP BY user_id,type
HAVING COUNT(*) > 0
)

select user_id
from type_count_table
group by user_id
having count(*) >= 2
