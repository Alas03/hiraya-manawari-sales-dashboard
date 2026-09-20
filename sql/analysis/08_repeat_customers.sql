-- Q7: Do customers come back?
-- Repeat customer = a customer with 2 or more orders.
-- Rate is measured against customers who placed at least one order.

WITH orders_per_customer AS (
    SELECT customer_id, COUNT(*) AS n_orders
    FROM orders
    GROUP BY customer_id
)
SELECT
    COUNT(*) AS customers_who_ordered,
    SUM(CASE WHEN n_orders >= 2 THEN 1 ELSE 0 END) AS repeat_customers,
    ROUND(SUM(CASE WHEN n_orders >= 2 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS repeat_rate_pct
FROM orders_per_customer;
