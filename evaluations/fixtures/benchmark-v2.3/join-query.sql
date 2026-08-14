SELECT
  o.customer_id,
  c.segment,
  SUM(o.amount) AS revenue
FROM raw.orders AS o
LEFT JOIN dim.customers AS c
  ON o.customer_id = c.customer_id
 AND c.is_current = true
WHERE o.status = 'paid'
GROUP BY o.customer_id, c.segment;
