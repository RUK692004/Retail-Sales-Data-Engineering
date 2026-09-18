-- =============================================================================
-- Retail Sales Data Warehouse - Validation & Test Queries
-- Database : retail_sales_dw
-- Author   : Member 3 (Database / DW Layer)
-- Created  : 2026-09-18
--
-- Run these after schema creation and data load to validate correctness.
-- Each query is labelled with its purpose.
-- =============================================================================


-- ---------------------------------------------------------------------------
-- SECTION 1: Row counts — verify tables are populated
-- ---------------------------------------------------------------------------

-- Q1.1 : Row counts for all warehouse tables
SELECT 'dim_date'        AS table_name, COUNT(*) AS row_count FROM dim_date
UNION ALL
SELECT 'dim_customer',   COUNT(*) FROM dim_customer
UNION ALL
SELECT 'dim_product',    COUNT(*) FROM dim_product
UNION ALL
SELECT 'dim_store',      COUNT(*) FROM dim_store
UNION ALL
SELECT 'dim_promotion',  COUNT(*) FROM dim_promotion
UNION ALL
SELECT 'fact_sales',     COUNT(*) FROM fact_sales
UNION ALL
SELECT 'fact_inventory', COUNT(*) FROM fact_inventory
ORDER BY table_name;


-- ---------------------------------------------------------------------------
-- SECTION 2: dim_date integrity checks
-- ---------------------------------------------------------------------------

-- Q2.1 : Verify date spine has no gaps (count should equal date-range span)
SELECT
    MIN(full_date)                                        AS min_date,
    MAX(full_date)                                        AS max_date,
    COUNT(*)                                              AS row_count,
    (MAX(full_date) - MIN(full_date) + 1)                AS expected_rows,
    COUNT(*) = (MAX(full_date) - MIN(full_date) + 1)     AS no_gaps
FROM dim_date;

-- Q2.2 : Verify weekend flag is correct (should be 0 mismatches)
SELECT COUNT(*) AS weekend_flag_mismatches
FROM dim_date
WHERE is_weekend != (day_of_week IN (6,7));

-- Q2.3 : Sample dim_date rows
SELECT * FROM dim_date ORDER BY date_key LIMIT 5;


-- ---------------------------------------------------------------------------
-- SECTION 3: Dimension cardinality checks
-- ---------------------------------------------------------------------------

-- Q3.1 : Customer count by loyalty segment
SELECT loyalty_segment, COUNT(*) AS customers
FROM dim_customer
GROUP BY loyalty_segment
ORDER BY customers DESC;

-- Q3.2 : Product count by category
SELECT category, COUNT(*) AS skus
FROM dim_product
GROUP BY category
ORDER BY skus DESC;

-- Q3.3 : Store count by city and type
SELECT city, store_type, COUNT(*) AS stores
FROM dim_store
GROUP BY city, store_type
ORDER BY city, store_type;

-- Q3.4 : All promotions with duration in days
SELECT
    promo_id,
    promo_name,
    promo_type,
    start_date,
    end_date,
    (end_date - start_date + 1) AS duration_days,
    discount_pct
FROM dim_promotion
ORDER BY start_date;


-- ---------------------------------------------------------------------------
-- SECTION 4: fact_sales integrity checks
-- ---------------------------------------------------------------------------

-- Q4.1 : Null-check on mandatory FK columns (should all be 0)
SELECT
    SUM(CASE WHEN date_key    IS NULL THEN 1 ELSE 0 END) AS null_date_keys,
    SUM(CASE WHEN store_key   IS NULL THEN 1 ELSE 0 END) AS null_store_keys,
    SUM(CASE WHEN product_key IS NULL THEN 1 ELSE 0 END) AS null_product_keys
FROM fact_sales;

-- Q4.2 : Customer_key nullability rate (expected ~some percentage)
SELECT
    COUNT(*)                                              AS total_rows,
    SUM(CASE WHEN customer_key IS NULL THEN 1 ELSE 0 END) AS anonymous_sales,
    ROUND(
        100.0 * SUM(CASE WHEN customer_key IS NULL THEN 1 ELSE 0 END) / COUNT(*),
        2
    )                                                     AS anonymous_pct
FROM fact_sales;

-- Q4.3 : Check total_value is never negative (should be 0)
SELECT COUNT(*) AS negative_total_value FROM fact_sales WHERE total_value < 0;

-- Q4.4 : Check quantity is always positive (should be 0)
SELECT COUNT(*) AS non_positive_quantity FROM fact_sales WHERE quantity <= 0;

-- Q4.5 : Check discount_pct within valid range (should be 0)
SELECT COUNT(*) AS invalid_discount FROM fact_sales WHERE discount_pct NOT BETWEEN 0 AND 100;

-- Q4.6 : Orphaned FK check — date_key not in dim_date (should be 0)
SELECT COUNT(*) AS orphaned_date_keys
FROM fact_sales fs
LEFT JOIN dim_date dd ON fs.date_key = dd.date_key
WHERE dd.date_key IS NULL;

-- Q4.7 : Orphaned FK check — store_key not in dim_store (should be 0)
SELECT COUNT(*) AS orphaned_store_keys
FROM fact_sales fs
LEFT JOIN dim_store ds ON fs.store_key = ds.store_key
WHERE ds.store_key IS NULL;

-- Q4.8 : Orphaned FK check — product_key not in dim_product (should be 0)
SELECT COUNT(*) AS orphaned_product_keys
FROM fact_sales fs
LEFT JOIN dim_product dp ON fs.product_key = dp.product_key
WHERE dp.product_key IS NULL;


-- ---------------------------------------------------------------------------
-- SECTION 5: fact_inventory integrity checks
-- ---------------------------------------------------------------------------

-- Q5.1 : Verify uniqueness constraint on grain (should be 0 duplicates)
SELECT store_key, product_key, snapshot_date_key, COUNT(*) AS cnt
FROM fact_inventory
GROUP BY store_key, product_key, snapshot_date_key
HAVING COUNT(*) > 1;

-- Q5.2 : Below-reorder-point SKUs (actionable metric)
SELECT
    ds.store_name,
    dp.sku_name,
    dp.category,
    fi.stock_on_hand,
    fi.reorder_point,
    fi.safety_stock,
    dd.full_date AS snapshot_date
FROM fact_inventory fi
JOIN dim_store   ds ON fi.store_key         = ds.store_key
JOIN dim_product dp ON fi.product_key       = dp.product_key
JOIN dim_date    dd ON fi.snapshot_date_key = dd.date_key
WHERE fi.stock_on_hand < fi.reorder_point
ORDER BY fi.stock_on_hand ASC
LIMIT 20;


-- ---------------------------------------------------------------------------
-- SECTION 6: Business analytics queries
-- ---------------------------------------------------------------------------

-- Q6.1 : Monthly revenue trend
SELECT
    dd.year,
    dd.month,
    dd.month_name,
    SUM(fs.total_value)   AS revenue,
    COUNT(fs.sales_id)    AS transactions,
    SUM(fs.quantity)      AS units_sold
FROM fact_sales fs
JOIN dim_date dd ON fs.date_key = dd.date_key
GROUP BY dd.year, dd.month, dd.month_name
ORDER BY dd.year, dd.month;

-- Q6.2 : Revenue by store city and channel
SELECT
    ds.city,
    fs.channel,
    SUM(fs.total_value)   AS revenue,
    COUNT(fs.sales_id)    AS transactions
FROM fact_sales fs
JOIN dim_store ds ON fs.store_key = ds.store_key
GROUP BY ds.city, fs.channel
ORDER BY ds.city, revenue DESC;

-- Q6.3 : Top 10 best-selling SKUs by revenue
SELECT
    dp.sku_id,
    dp.sku_name,
    dp.category,
    SUM(fs.quantity)      AS units_sold,
    SUM(fs.total_value)   AS revenue
FROM fact_sales fs
JOIN dim_product dp ON fs.product_key = dp.product_key
GROUP BY dp.sku_id, dp.sku_name, dp.category
ORDER BY revenue DESC
LIMIT 10;

-- Q6.4 : Revenue by customer loyalty segment
SELECT
    dc.loyalty_segment,
    COUNT(DISTINCT fs.customer_key)  AS customers,
    SUM(fs.total_value)              AS revenue,
    ROUND(AVG(fs.total_value), 2)    AS avg_basket_value
FROM fact_sales fs
JOIN dim_customer dc ON fs.customer_key = dc.customer_key
GROUP BY dc.loyalty_segment
ORDER BY revenue DESC;

-- Q6.5 : Quarterly revenue by year (pivot-style)
SELECT
    dd.year,
    SUM(CASE WHEN dd.quarter = 1 THEN fs.total_value ELSE 0 END) AS q1_revenue,
    SUM(CASE WHEN dd.quarter = 2 THEN fs.total_value ELSE 0 END) AS q2_revenue,
    SUM(CASE WHEN dd.quarter = 3 THEN fs.total_value ELSE 0 END) AS q3_revenue,
    SUM(CASE WHEN dd.quarter = 4 THEN fs.total_value ELSE 0 END) AS q4_revenue,
    SUM(fs.total_value)                                           AS annual_revenue
FROM fact_sales fs
JOIN dim_date dd ON fs.date_key = dd.date_key
GROUP BY dd.year
ORDER BY dd.year;

-- Q6.6 : Store performance — revenue and avg discount per store
SELECT
    ds.store_id,
    ds.store_name,
    ds.city,
    ds.store_type,
    COUNT(fs.sales_id)           AS transactions,
    SUM(fs.total_value)          AS revenue,
    ROUND(AVG(fs.discount_pct),2) AS avg_discount_pct
FROM fact_sales fs
JOIN dim_store ds ON fs.store_key = ds.store_key
GROUP BY ds.store_id, ds.store_name, ds.city, ds.store_type
ORDER BY revenue DESC;

-- Q6.7 : Weekend vs weekday sales comparison
SELECT
    dd.is_weekend,
    COUNT(fs.sales_id)           AS transactions,
    SUM(fs.total_value)          AS revenue,
    ROUND(AVG(fs.total_value),2) AS avg_basket_value
FROM fact_sales fs
JOIN dim_date dd ON fs.date_key = dd.date_key
GROUP BY dd.is_weekend
ORDER BY dd.is_weekend;

-- Q6.8 : Inventory health summary — stock levels by category
SELECT
    dp.category,
    COUNT(DISTINCT fi.store_key)                AS stores_stocked,
    SUM(fi.stock_on_hand)                       AS total_stock,
    SUM(fi.reorder_point)                       AS total_reorder_threshold,
    SUM(CASE WHEN fi.stock_on_hand < fi.reorder_point THEN 1 ELSE 0 END) AS below_reorder,
    SUM(CASE WHEN fi.stock_on_hand < fi.safety_stock  THEN 1 ELSE 0 END) AS below_safety
FROM fact_inventory fi
JOIN dim_product dp ON fi.product_key = dp.product_key
GROUP BY dp.category
ORDER BY below_reorder DESC;
