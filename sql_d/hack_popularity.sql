SELECT e.location,
       AVG(s.popularity) AS avg_popularity
FROM facebook_employees e
JOIN facebook_hack_survey s ON e.id = s.employee_id
GROUP BY e.location