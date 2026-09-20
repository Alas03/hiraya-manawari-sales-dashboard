-- Q3a: Which product categories earn the most?
-- Completed orders only.

SELECT
    p.category,
    SUM(oi.quantity) AS units_sold,
    ROUND(SUM(oi.quantity * oi.unit_price), 2) AS revenue,
    ROUND(
        SUM(oi.quantity * oi.unit_price) * 100.0
        / SUM(SUM(oi.quantity * oi.unit_price)) OVER (), 1
    ) AS pct_of_revenue
FROM order_items oi
JOIN orders o   ON o.order_id = oi.order_id
JOIN products p ON p.product_id = oi.product_id
WHERE o.status = 'Completed'
GROUP BY p.category
ORDER BY revenue DESC;