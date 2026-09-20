-- Q8: Do big sale days (9.9, 10.10, 11.11, 12.12) work?
-- Compares the average day of each type. Completed orders only.

WITH daily AS (
    SELECT
        d.date_id,
        d.is_sale_day,
        COUNT(DISTINCT o.order_id) AS orders,
        COALESCE(SUM(oi.quantity * oi.unit_price), 0) AS revenue
    FROM dim_date d
    LEFT JOIN orders o      ON o.order_date = d.date_id AND o.status = 'Completed'
    LEFT JOIN order_items oi ON oi.order_id = o.order_id
    GROUP BY d.date_id, d.is_sale_day
)
SELECT
    CASE WHEN is_sale_day = 1 THEN 'Sale day' ELSE 'Normal day' END AS day_type,
    COUNT(*) AS days,
    ROUND(AVG(orders), 1) AS avg_orders_per_day,
    ROUND(AVG(revenue), 0) AS avg_revenue_per_day
FROM daily
GROUP BY is_sale_day
ORDER BY is_sale_day DESC;
