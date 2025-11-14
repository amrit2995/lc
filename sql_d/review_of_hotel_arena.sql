select hotel_name, reviewer_score, count(*) as no_of_reviews
from hotel_reviews
where hotel_name = 'Hotel Arena'
group by hotel_name, reviewer_score
;