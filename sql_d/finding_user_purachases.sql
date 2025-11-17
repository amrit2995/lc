WITH daily AS (
  SELECT DISTINCT user_id, created_at::date AS purchase_date
  FROM amazon_transactions
),
ranked AS (
  SELECT
    user_id,
    purchase_date,
    ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY purchase_date) AS rn
  FROM daily
),
first_two AS (
  SELECT
    user_id,
    MAX(CASE WHEN rn = 1 THEN purchase_date END) AS first_date,
    MAX(CASE WHEN rn = 2 THEN purchase_date END) AS second_date
  FROM ranked
  WHERE rn <= 2
  GROUP BY user_id
)
SELECT user_id
FROM first_two
WHERE second_date IS NOT NULL
  AND (second_date - first_date) BETWEEN 1 AND 7
ORDER BY user_id;