-- ==========================================
-- ==========================================
-- CREATE VIEW: ORDER ITEMS WITH SELLERS
-- ==========================================

CREATE OR REPLACE VIEW order_items_with_sellers AS
SELECT
    oi.order_id,
    oi.order_item_id,
    oi.product_id,
    oi.seller_id,
    oi.shipping_limit_date,
    oi.price,
    oi.freight_value,
    s.seller_zip_code_prefix,
    s.seller_city,
    s.seller_state
FROM order_items oi
LEFT JOIN sellers s
    ON oi.seller_id = s.seller_id;

-- ==========================================
-- 01. ORDER PERFORMANCE
-- ==========================================


-- 1. Total Orders
-- Measures the total number of unique orders.

SELECT
    COUNT(DISTINCT order_id) AS total_orders
FROM order_items_with_sellers;


-- 2. Total Items Sold
-- Measures the total number of items purchased.

SELECT
    COUNT(order_item_id) AS total_items_sold
FROM order_items_with_sellers;


-- 3. Total Revenue
-- Calculates total revenue from item prices.

SELECT
    SUM(price) AS total_revenue
FROM order_items_with_sellers;


-- 4. Average Order Value
-- Calculates the average revenue generated per order.

SELECT
    SUM(price) / COUNT(DISTINCT order_id) AS average_order_value
FROM order_items_with_sellers;


-- 5. Average Items per Order
-- Measures how many items are purchased per order on average.

SELECT
    COUNT(order_item_id) * 1.0
    / COUNT(DISTINCT order_id) AS average_items_per_order
FROM order_items_with_sellers;


-- 6. Delivery Performance
-- Classifies completed orders as Early or Late
-- by comparing actual delivery date with estimated delivery date.

SELECT
    CASE
        WHEN order_delivered_customer_date <= order_estimated_delivery_date
            THEN 'Early'
        ELSE 'Late'
    END AS delivery_performance,

    COUNT(*) AS total_orders,

    ROUND(
        COUNT(*) * 100.0
        / SUM(COUNT(*)) OVER (),
        2
    ) AS percentage

FROM orders

WHERE order_delivered_customer_date IS NOT NULL
  AND order_estimated_delivery_date IS NOT NULL

GROUP BY
    CASE
        WHEN order_delivered_customer_date <= order_estimated_delivery_date
            THEN 'Early'
        ELSE 'Late'
    END

ORDER BY total_orders DESC;