WITH paid_orders AS (
  SELECT order_id, customer_id, amount, order_date
  FROM raw.orders
  WHERE status = 'paid'
)
SELECT
  customer_id,
  COUNT(DISTINCT order_id) AS paid_orders,
  SUM(amount) AS paid_revenue
FROM paid_orders
GROUP BY customer_id;
