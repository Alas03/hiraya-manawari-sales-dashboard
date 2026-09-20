-- Q9: Which day of the week has the most orders?
-- All orders (any status), busiest day first.

SELECT
    d.day_of_week,
    COUNT(*) AS orders,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS pct_of_orders
FROM orders o
JOIN dim_date d ON d.date_id = o.order_date
GROUP BY d.day_of_week, d.day_of_week_no
ORDER BY orders DESC;
