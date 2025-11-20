with acc_metrics as (
    select country,city, sum(area) as total_area, sum(population) as total_population 
    from cities_population
    group by country, city
), density_metrics as (
    select country, city, round(total_population/nullif(total_area, 0)) as density
    from acc_metrics
    where total_area > 0
), ranking_metrics as (
    select country, city, density,
    rank() over ( order by density) as high_density_rank,
    rank() over ( order by density desc) as low_density_rank
    from density_metrics
)

select city, country, density
from ranking_metrics
where high_density_rank = 1 or low_density_rank = 1
;