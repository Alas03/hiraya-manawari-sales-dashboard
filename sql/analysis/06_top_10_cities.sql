-- Q4b: Top 10 cities by revenue
-- Completed orders only.

SELECT
    RANK() OVER (ORDER BY SUM(oi.quantity * oi.unit_price) DESC) AS rank,
    c.city,
    c.region,
    COUNT(DISTINCT o.order_id) AS orders,
    ROUND(SUM(oi.quantity * oi.unit_price), 2) AS revenue
FROM orders o
JOIN order_items oi ON oi.order_id = o.order_id
JOIN customers c    ON c.customer_id = o.customer_id
WHERE o.status = 'Completed'
GROUP BY c.city, c.region
ORDER BY revenue DESC
LIMIT 10;
