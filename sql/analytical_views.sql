-- ============================================================
-- BUSINESSPULSE
-- ANALYTICAL SQL VIEWS
-- ============================================================


-- ============================================================
-- 1. MONTHLY REVENUE
-- ============================================================

DROP VIEW IF EXISTS vw_monthly_revenue;

CREATE VIEW vw_monthly_revenue AS
SELECT
    DATE_TRUNC(
        'month',
        o.order_purchase_timestamp
    )::date AS month,

    COUNT(DISTINCT o.order_id) AS total_orders,

    COUNT(oi.order_item_id) AS items_sold,

    ROUND(
        SUM(oi.price),
        2
    ) AS revenue,

    ROUND(
        SUM(oi.freight_value),
        2
    ) AS freight_value

FROM orders o

JOIN order_items oi
    ON o.order_id = oi.order_id

GROUP BY
    DATE_TRUNC(
        'month',
        o.order_purchase_timestamp
    )::date

ORDER BY month;


-- ============================================================
-- 2. CATEGORY PERFORMANCE
-- ============================================================

DROP VIEW IF EXISTS vw_category_performance;

CREATE VIEW vw_category_performance AS
SELECT
    COALESCE(
        p.product_category_name,
        'Unknown'
    ) AS product_category,

    COUNT(DISTINCT oi.order_id) AS total_orders,

    COUNT(oi.order_item_id) AS items_sold,

    ROUND(
        SUM(oi.price),
        2
    ) AS total_revenue,

    ROUND(
        SUM(oi.freight_value),
        2
    ) AS total_freight

FROM order_items oi

JOIN products p
    ON oi.product_id = p.product_id

GROUP BY
    COALESCE(
        p.product_category_name,
        'Unknown'
    )

ORDER BY total_revenue DESC;


-- ============================================================
-- 3. TOP PRODUCTS
-- ============================================================

DROP VIEW IF EXISTS vw_top_products;

CREATE VIEW vw_top_products AS
SELECT
    oi.product_id,

    COALESCE(
        p.product_category_name,
        'Unknown'
    ) AS product_category,

    COUNT(oi.order_item_id) AS items_sold,

    ROUND(
        SUM(oi.price),
        2
    ) AS total_revenue,

    ROUND(
        AVG(oi.price),
        2
    ) AS average_price

FROM order_items oi

JOIN products p
    ON oi.product_id = p.product_id

GROUP BY
    oi.product_id,
    p.product_category_name

ORDER BY total_revenue DESC;


-- ============================================================
-- 4. CUSTOMER TYPE
-- ============================================================

DROP VIEW IF EXISTS vw_customer_type;

CREATE VIEW vw_customer_type AS

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

    COUNT(*) AS total_customers

FROM customer_orders

GROUP BY

    CASE
        WHEN order_count = 1
            THEN 'One-Time Customer'

        ELSE 'Repeat Customer'
    END

ORDER BY total_customers DESC;


-- ============================================================
-- 5. DELIVERY PERFORMANCE
-- ============================================================

DROP VIEW IF EXISTS vw_delivery_performance;

CREATE VIEW vw_delivery_performance AS

SELECT

    CASE

        WHEN order_delivered_customer_date
             <= order_estimated_delivery_date

            THEN 'Early'

        ELSE 'Late'

    END AS delivery_status,

    COUNT(*) AS total_orders

FROM orders

WHERE order_delivered_customer_date IS NOT NULL

  AND order_estimated_delivery_date IS NOT NULL

GROUP BY

    CASE

        WHEN order_delivered_customer_date
             <= order_estimated_delivery_date

            THEN 'Early'

        ELSE 'Late'

    END

ORDER BY total_orders DESC;


-- ============================================================
-- 6. PAYMENT METHOD ANALYSIS
-- ============================================================

DROP VIEW IF EXISTS vw_payment_methods;

CREATE VIEW vw_payment_methods AS

SELECT

    payment_type,

    COUNT(DISTINCT order_id) AS total_orders,

    ROUND(
        SUM(payment_value),
        2
    ) AS total_payment_value,

    ROUND(
        AVG(payment_value),
        2
    ) AS average_payment_value

FROM order_payments

GROUP BY payment_type

ORDER BY total_payment_value DESC;


-- ============================================================
-- 7. REVIEW ANALYSIS
-- ============================================================

DROP VIEW IF EXISTS vw_review_analysis;

CREATE VIEW vw_review_analysis AS

SELECT

    review_score,

    COUNT(*) AS total_reviews

FROM order_reviews

GROUP BY review_score

ORDER BY review_score;


-- ============================================================
-- 8. SELLER PERFORMANCE
-- ============================================================

DROP VIEW IF EXISTS vw_seller_performance;

CREATE VIEW vw_seller_performance AS

SELECT

    oi.seller_id,

    s.seller_city,

    s.seller_state,

    COUNT(DISTINCT oi.order_id) AS total_orders,

    COUNT(oi.order_item_id) AS items_sold,

    ROUND(
        SUM(oi.price),
        2
    ) AS total_revenue,

    ROUND(
        AVG(oi.price),
        2
    ) AS average_item_price

FROM order_items oi

JOIN sellers s
    ON oi.seller_id = s.seller_id

GROUP BY

    oi.seller_id,

    s.seller_city,

    s.seller_state

ORDER BY total_revenue DESC;


-- ============================================================
-- 9. ORDER STATUS ANALYSIS
-- ============================================================

DROP VIEW IF EXISTS vw_order_status;

CREATE VIEW vw_order_status AS

SELECT

    order_status,

    COUNT(*) AS total_orders

FROM orders

GROUP BY order_status

ORDER BY total_orders DESC;


-- ============================================================
-- 10. STATE PERFORMANCE
-- ============================================================

DROP VIEW IF EXISTS vw_state_performance;

CREATE VIEW vw_state_performance AS

SELECT

    c.customer_state,

    COUNT(DISTINCT o.order_id) AS total_orders,

    COUNT(oi.order_item_id) AS items_sold,

    ROUND(
        SUM(oi.price),
        2
    ) AS total_revenue,

    ROUND(
        SUM(oi.freight_value),
        2
    ) AS total_freight

FROM customers c

JOIN orders o
    ON c.customer_id = o.customer_id

JOIN order_items oi
    ON o.order_id = oi.order_id

GROUP BY c.customer_state

ORDER BY total_revenue DESC;


-- ============================================================
-- 11. MONTHLY ORDER STATUS
-- ============================================================

DROP VIEW IF EXISTS vw_monthly_orders;

CREATE VIEW vw_monthly_orders AS

SELECT

    DATE_TRUNC(
        'month',
        order_purchase_timestamp
    )::date AS month,

    order_status,

    COUNT(*) AS total_orders

FROM orders

GROUP BY

    DATE_TRUNC(
        'month',
        order_purchase_timestamp
    )::date,

    order_status

ORDER BY month;


-- ============================================================
-- 12. CUSTOMER VALUE
-- ============================================================

DROP VIEW IF EXISTS vw_customer_value;

CREATE VIEW vw_customer_value AS

SELECT

    c.customer_unique_id,

    COUNT(DISTINCT o.order_id) AS total_orders,

    COUNT(oi.order_item_id) AS total_items,

    ROUND(
        SUM(oi.price),
        2
    ) AS total_spend,

    ROUND(
        AVG(oi.price),
        2
    ) AS average_item_value

FROM customers c

JOIN orders o
    ON c.customer_id = o.customer_id

JOIN order_items oi
    ON o.order_id = oi.order_id

GROUP BY

    c.customer_unique_id;


-- ============================================================
-- 13. DASHBOARD KPI SUMMARY
-- ============================================================

DROP VIEW IF EXISTS vw_dashboard_kpis;

CREATE VIEW vw_dashboard_kpis AS

SELECT

    COUNT(DISTINCT oi.order_id)
        AS total_orders,

    COUNT(oi.order_item_id)
        AS total_items,

    ROUND(
        SUM(oi.price),
        2
    ) AS total_revenue,

    ROUND(
        SUM(oi.price)
        / COUNT(DISTINCT oi.order_id),
        2
    ) AS average_order_value,

    COUNT(DISTINCT c.customer_unique_id)
        AS unique_customers

FROM order_items oi

JOIN orders o
    ON oi.order_id = o.order_id

JOIN customers c
    ON o.customer_id = c.customer_id;


-- ============================================================
-- COMPLETE
-- ============================================================

SELECT 'BusinessPulse analytical views created successfully'
    AS status;