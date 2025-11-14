SELECT 
  c.id, 
  c.first_name, 
  SUM(o.total_order_cost) AS total_order_cost
FROM customers AS c
JOIN orders AS o 
  ON c.id = o.cust_id
GROUP BY c.id, c.first_name;
