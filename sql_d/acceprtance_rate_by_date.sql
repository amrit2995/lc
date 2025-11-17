WITH sent_request AS (
    SELECT user_id_receiver, user_id_sender, date
    FROM fb_friend_requests
    WHERE action = 'sent'
), accepted_request AS (
    SELECT user_id_receiver, user_id_sender, date
    FROM fb_friend_requests
    WHERE action = 'accepted'
)

SELECT sr.date,
    COUNT(sr.user_id_receiver)/CAST(count(ar.user_id_sender) AS decimal) AS percentage_acceptance
FROM sent_request AS sr
LEFT JOIN accepted_request AS ar
ON sr.user_id_sender = ar.user_id_sender
AND sr.user_id_receiver = ar.user_id_receiver
GROUP BY sr.date