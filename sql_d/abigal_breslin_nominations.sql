SELECT nominee, COUNT(movie) AS movie_count
FROM oscar_nominees
WHERE nominee = 'Abigail Breslin'
GROUP BY nominee;