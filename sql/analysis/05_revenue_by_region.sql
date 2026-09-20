-- Q4a: Where are our customers? Revenue and orders by region
-- Completed orders only.

SELECT
    c.region,
    COUNT(DISTINCT o.order_id) AS orders,
    ROUND(SUM(oi.quantity * oi.unit_price), 2) AS revenue,
    ROUND(
        SUM(oi.quantity * oi.unit_price) * 100.0
        / SUM(SUM(oi.quantity * oi.unit_price)) OVER (), 1
    ) AS pct_of_revenue
FROM orders o
JOIN order_items oi ON oi.order_id = o.order_id
JOIN customers c    ON c.customer_id = o.customer_id
WHERE o.status = 'Completed'
GROUP BY c.region
ORDER BY revenue DESC;
