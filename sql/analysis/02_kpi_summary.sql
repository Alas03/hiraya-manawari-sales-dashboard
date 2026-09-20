-- Q2: Headline KPIs: total orders, revenue, and average order value (AOV)
-- Revenue and AOV only count completed orders.

WITH order_totals AS (
    SELECT
        order_id,
        SUM(quantity * unit_price) AS order_value
    FROM order_items
    GROUP BY order_id
)
SELECT
    COUNT(*) AS total_orders,
    SUM(CASE WHEN o.status = 'Completed' THEN 1 ELSE 0 END) AS completed_orders,
    ROUND(SUM(CASE WHEN o.status = 'Completed' THEN t.order_value ELSE 0 END), 2) AS total_revenue,
    ROUND(
        SUM(CASE WHEN o.status = 'Completed' THEN t.order_value ELSE 0 END)
        / SUM(CASE WHEN o.status = 'Completed' THEN 1 ELSE 0 END), 2
    ) AS avg_order_value
FROM orders o
JOIN order_totals t ON t.order_id = o.order_id;