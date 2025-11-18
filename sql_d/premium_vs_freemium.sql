WITH download_totals AS (
    SELECT c.date AS download_date,
           SUM(CASE WHEN paying_customer = 'yes' THEN downloads END) AS paying,
           SUM(CASE WHEN paying_customer = 'no' THEN downloads END) AS non_paying
    FROM ms_user_dimension a
    INNER JOIN ms_acc_dimension b ON a.acc_id = b.acc_id
    INNER JOIN ms_download_facts c ON a.user_id = c.user_id
    GROUP BY c.date
)

SELECT download_date,
       non_paying,
       paying
FROM download_totals
WHERE (non_paying - paying) > 0
ORDER BY download_date ASC;