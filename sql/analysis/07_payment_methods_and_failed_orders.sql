-- Q5 + Q6: How do people pay, and how many orders fail?
-- Shows each payment method's share of orders, plus its cancellation
-- and return rates. The "ALL ORDERS" row gives the overall rates.

WITH by_method AS (
    SELECT
        payment_method AS method,
        COUNT(*) AS orders,
        SUM(status = 'Cancelled') AS cancelled,
        SUM(status = 'Returned')  AS returned
    FROM orders
    GROUP BY payment_method
)
SELECT
    method,
    orders,
    ROUND(orders * 100.0 / (SELECT COUNT(*) FROM orders), 1) AS pct_of_orders,
    ROUND(cancelled * 100.0 / orders, 1) AS cancel_rate_pct,
    ROUND(returned * 100.0 / orders, 1)  AS return_rate_pct
FROM by_method

UNION ALL

SELECT
    'ALL ORDERS',
    COUNT(*),
    100.0,
    ROUND(SUM(status = 'Cancelled') * 100.0 / COUNT(*), 1),
    ROUND(SUM(status = 'Returned')  * 100.0 / COUNT(*), 1)
FROM orders

ORDER BY orders DESC;
