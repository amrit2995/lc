SELECT company, continent
FROM (
    SELECT *,
           RANK() OVER (PARTITION BY sector ORDER BY profits DESC) AS profit_rank
    FROM forbes_global_2010_2014
) t
WHERE sector = 'Financials' AND profit_rank = 1;