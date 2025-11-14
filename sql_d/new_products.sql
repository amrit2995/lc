WITH metrics_2020 AS (
    SELECT company_name, COUNT(*) AS prod_count
    FROM car_launches
    WHERE year = 2020
    GROUP BY company_name
),
metrics_2019 AS (
    SELECT company_name, COUNT(*) AS prod_count
    FROM car_launches
    WHERE year = 2019
    GROUP BY company_name
)
SELECT 
    m20.company_name,
    (m20.prod_count - m19.prod_count) AS net_diff
FROM metrics_2020 AS m20
JOIN metrics_2019 AS m19
  ON m20.company_name = m19.company_name;
