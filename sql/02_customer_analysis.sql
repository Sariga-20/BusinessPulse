-- ==========================================
-- 02. CUSTOMER ANALYSIS
-- ==========================================


-- ==========================================
-- 1. Total Unique Customers
-- ==========================================
-- Counts actual customers using customer_unique_id.

SELECT
    COUNT(DISTINCT customer_unique_id) AS total_unique_customers
FROM customers;


-- ==========================================
-- 2. One-Time vs Repeat Customers
-- ==========================================
-- One-Time = exactly 1 order
-- Repeat = more than 1 order

WITH customer_orders AS (
    SELECT
        c.customer_unique_id,
        COUNT(DISTINCT o.order_id) AS order_count

    FROM customers c

    JOIN orders o
        ON c.customer_id = o.customer_id

    GROUP BY
        c.customer_unique_id
)

SELECT
    CASE
        WHEN order_count = 1
            THEN 'One-Time Customer'
        ELSE 'Repeat Customer'
    END AS customer_type,

    COUNT(*) AS total_customers,

    ROUND(
        COUNT(*) * 100.0
        / SUM(COUNT(*)) OVER (),
        2
    ) AS percentage

FROM customer_orders

GROUP BY
    CASE
        WHEN order_count = 1
            THEN 'One-Time Customer'
        ELSE 'Repeat Customer'
    END

ORDER BY
    total_customers DESC;


-- ==========================================
-- 3. Average Orders per Customer
-- ==========================================

WITH customer_orders AS (
    SELECT
        c.customer_unique_id,
        COUNT(DISTINCT o.order_id) AS order_count

    FROM customers c

    JOIN orders o
        ON c.customer_id = o.customer_id

    GROUP BY
        c.customer_unique_id
)

SELECT
    ROUND(
        AVG(order_count),
        2
    ) AS average_orders_per_customer

FROM customer_orders;


-- ==========================================
-- 4. Top 10 Customers by Revenue
-- ==========================================
-- Correct relationship:
-- customers → orders → order_items

SELECT
    c.customer_unique_id,

    COUNT(DISTINCT o.order_id) AS total_orders,

    ROUND(
        SUM(oi.price),
        2
    ) AS total_revenue

FROM customers c

JOIN orders o
    ON c.customer_id = o.customer_id

JOIN order_items oi
    ON o.order_id = oi.order_id

GROUP BY
    c.customer_unique_id

ORDER BY
    total_revenue DESC

LIMIT 10;


-- ==========================================
-- 5. Customers by State
-- ==========================================

SELECT
    customer_state,

    COUNT(DISTINCT customer_unique_id) AS total_customers

FROM customers

GROUP BY
    customer_state

ORDER BY
    total_customers DESC;


-- ==========================================
-- 6. Average Customer Revenue
-- ==========================================
-- Calculates revenue for each customer first,
-- then calculates the average.

WITH customer_revenue AS (
    SELECT
        c.customer_unique_id,

        SUM(oi.price) AS revenue

    FROM customers c

    JOIN orders o
        ON c.customer_id = o.customer_id

    JOIN order_items oi
        ON o.order_id = oi.order_id

    GROUP BY
        c.customer_unique_id
)

SELECT
    ROUND(
        AVG(revenue),
        2
    ) AS average_customer_revenue

FROM customer_revenue;