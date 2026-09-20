-- Q10: Flat table for the Excel dashboard (one row per product in an order)
-- Helper columns let a PivotTable count orders and rates correctly:
--   order_weight = 1 / (number of items in the order), so SUM() = number of orders

SELECT
    o.order_id,
    o.order_date,
    strftime('%Y-%m', o.order_date) AS year_month,
    d.year,
    d.month_name,
    d.day_of_week,
    d.is_sale_day,
    c.region,
    c.city,
    o.payment_method,
    o.status,
    p.category,
    p.product_name,
    oi.quantity,
    oi.unit_price,
    CASE WHEN o.status = 'Completed'
         THEN ROUND(oi.quantity * oi.unit_price, 2) ELSE 0 END AS revenue,
    1.0 / COUNT(*) OVER (PARTITION BY o.order_id) AS order_weight,
    CASE WHEN o.status = 'Completed'
         THEN 1.0 / COUNT(*) OVER (PARTITION BY o.order_id) ELSE 0 END AS completed_weight,
    CASE WHEN o.status = 'Cancelled'
         THEN 1.0 / COUNT(*) OVER (PARTITION BY o.order_id) ELSE 0 END AS cancelled_weight
FROM order_items oi
JOIN orders o     ON o.order_id = oi.order_id
JOIN dim_date d   ON d.date_id = o.order_date
JOIN customers c  ON c.customer_id = o.customer_id
JOIN products p   ON p.product_id = oi.product_id
ORDER BY o.order_date, o.order_id;
