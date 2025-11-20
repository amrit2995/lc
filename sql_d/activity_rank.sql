SELECT
    from_user AS user_id,
    COUNT(*) AS total_emails,
    ROW_NUMBER() OVER (
        ORDER BY COUNT(*) DESC, from_user ASC
    ) AS activity_rank
FROM google_gmail_emails
GROUP BY from_user
ORDER BY activity_rank;