-- =============================================================================
-- Retail Sales Data Warehouse - Seed Data
-- Database : retail_sales_dw
-- Author   : Member 3 (Database / DW Layer)
-- Created  : 2026-09-18
--
-- This script seeds dim_date with a continuous date spine (2021-01-01 to
-- 2025-12-31).  All other dimension data, including dim_promotion, is loaded
-- by load_data.py from the processed CSV files — there is no second hardcoded
-- source of truth for promotions here.
--
-- Safe to re-run: yes (uses INSERT ... ON CONFLICT DO NOTHING)
-- =============================================================================

-- ---------------------------------------------------------------------------
-- 1. dim_date  - date spine from 2021-01-01 to 2025-12-31
--    Uses a PostgreSQL generate_series to build the spine in a single
--    set-based statement; no row-by-row loops required.
-- ---------------------------------------------------------------------------
INSERT INTO dim_date (
    date_key,
    full_date,
    day,
    month,
    month_name,
    quarter,
    year,
    day_of_week,
    day_name,
    is_weekend,
    is_month_start,
    is_month_end
)
SELECT
    TO_CHAR(d, 'YYYYMMDD')::INTEGER                                            AS date_key,
    d::DATE                                                                    AS full_date,
    EXTRACT(DAY   FROM d)::SMALLINT                                            AS day,
    EXTRACT(MONTH FROM d)::SMALLINT                                            AS month,
    TO_CHAR(d, 'Month')                                                        AS month_name,
    EXTRACT(QUARTER FROM d)::SMALLINT                                          AS quarter,
    EXTRACT(YEAR  FROM d)::SMALLINT                                            AS year,
    EXTRACT(ISODOW FROM d)::SMALLINT                                           AS day_of_week,
    TO_CHAR(d, 'Day')                                                          AS day_name,
    EXTRACT(ISODOW FROM d) IN (6,7)                                            AS is_weekend,
    (d = DATE_TRUNC('month', d))                                               AS is_month_start,
    (d = (DATE_TRUNC('month', d) + INTERVAL '1 month - 1 day')::DATE)         AS is_month_end
FROM generate_series(
    '2021-01-01'::DATE,
    '2025-12-31'::DATE,
    '1 day'::INTERVAL
) AS gs(d)
ON CONFLICT (date_key) DO NOTHING;