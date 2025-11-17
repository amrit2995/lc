WITH log_with_date AS (
    SELECT *, DATE(timestamp) AS date
    FROM facebook_web_log
), log_with_load AS (
    SELECT user_id, date,
    MAX(timestamp) AS load_timestamp
    FROM log_with_date
    WHERE action = 'page_load'
    GROUP BY date, user_id
), log_with_exit AS (
    SELECT user_id, date,
    MIN(timestamp) AS exit_timestamp
    FROM log_with_date
    WHERE action = 'page_exit'
    GROUP BY date, user_id
), log_with_diff AS (
    SELECT lwl.user_id,
    AVG(exit_timestamp - load_timestamp) AS timestamp_diff
    FROM log_with_load as lwl
    JOIN log_with_exit as lwe
    ON lwl.user_id = lwe.user_id AND lwl.date = lwe.date
    GROUP BY lwl.user_id
)

SELECT * FROM log_with_diff;