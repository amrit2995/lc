SELECT city
FROM zillow_transactions a
GROUP BY city
HAVING avg(a.mkt_price) >
  (SELECT avg(mkt_price)
   FROM zillow_transactions)
ORDER BY city ASC