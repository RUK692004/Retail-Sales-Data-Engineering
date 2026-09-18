-- =============================================================================
-- Retail Sales Data Warehouse - Star Schema DDL
-- Database : retail_sales_dw
-- Author   : Member 3 (Database / DW Layer)
-- Created  : 2026-09-18
-- Safe to re-run: yes (uses IF NOT EXISTS guards)
-- =============================================================================

-- =============================================================================
-- DIMENSION TABLES
-- =============================================================================

-- ---------------------------------------------------------------------------
-- 1. dim_date
--    Populated by seed_data.sql (date-spine from 2021-01-01 to 2025-12-31).
--    date_key is an integer in YYYYMMDD format (e.g. 20210101).
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dim_date (
    date_key        INTEGER         NOT NULL,
    full_date       DATE            NOT NULL,
    day             SMALLINT        NOT NULL,
    month           SMALLINT        NOT NULL,
    month_name      VARCHAR(12)     NOT NULL,
    quarter         SMALLINT        NOT NULL,
    year            SMALLINT        NOT NULL,
    day_of_week     SMALLINT        NOT NULL,
    day_name        VARCHAR(12)     NOT NULL,
    is_weekend      BOOLEAN         NOT NULL DEFAULT FALSE,
    is_month_start  BOOLEAN         NOT NULL DEFAULT FALSE,
    is_month_end    BOOLEAN         NOT NULL DEFAULT FALSE,

    CONSTRAINT pk_dim_date          PRIMARY KEY (date_key),
    CONSTRAINT uq_dim_date_fulldate UNIQUE (full_date),
    CONSTRAINT chk_dim_date_month   CHECK (month BETWEEN 1 AND 12),
    CONSTRAINT chk_dim_date_quarter CHECK (quarter BETWEEN 1 AND 4),
    CONSTRAINT chk_dim_date_dow     CHECK (day_of_week BETWEEN 1 AND 7)
);

COMMENT ON TABLE  dim_date             IS 'Date dimension — one row per calendar day';
COMMENT ON COLUMN dim_date.date_key    IS 'Surrogate PK in YYYYMMDD integer format';
COMMENT ON COLUMN dim_date.day_of_week IS '1=Monday 7=Sunday (ISO 8601)';


-- ---------------------------------------------------------------------------
-- 2. dim_customer
--    Business key : cust_id (integer)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dim_customer (
    customer_key        SERIAL          NOT NULL,
    cust_id             INTEGER         NOT NULL,
    age                 SMALLINT,
    gender              VARCHAR(20),
    city                VARCHAR(100),
    loyalty_segment     VARCHAR(50),
    preferred_channel   VARCHAR(50),
    registration_date   DATE,

    CONSTRAINT pk_dim_customer      PRIMARY KEY (customer_key),
    CONSTRAINT uq_dim_customer_bk   UNIQUE (cust_id),
    CONSTRAINT chk_dim_customer_age CHECK (age IS NULL OR age BETWEEN 0 AND 150)
);

COMMENT ON TABLE  dim_customer          IS 'Customer dimension — one row per unique customer';
COMMENT ON COLUMN dim_customer.cust_id  IS 'Business key from customers_ingested.csv';


-- ---------------------------------------------------------------------------
-- 3. dim_product  (sourced from skus_ingested.csv)
--    Business key : sku_id
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dim_product (
    product_key     SERIAL          NOT NULL,
    sku_id          INTEGER         NOT NULL,
    sku_name        VARCHAR(200)    NOT NULL,
    category        VARCHAR(100)    NOT NULL,
    subcategory     VARCHAR(100),
    unit_price      NUMERIC(10,2)   NOT NULL,
    cost_price      NUMERIC(10,2),
    brand           VARCHAR(100),

    CONSTRAINT pk_dim_product       PRIMARY KEY (product_key),
    CONSTRAINT uq_dim_product_bk    UNIQUE (sku_id),
    CONSTRAINT chk_dim_product_price
        CHECK (unit_price >= 0 AND (cost_price IS NULL OR cost_price >= 0))
);

COMMENT ON TABLE  dim_product          IS 'Product (SKU) dimension — one row per unique SKU';
COMMENT ON COLUMN dim_product.sku_id   IS 'Business key from skus_ingested.csv';


-- ---------------------------------------------------------------------------
-- 4. dim_store  (sourced from stores_ingested.csv)
--    Business key : store_id
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dim_store (
    store_key       SERIAL          NOT NULL,
    store_id        INTEGER         NOT NULL,
    store_name      VARCHAR(200)    NOT NULL,
    city            VARCHAR(100)    NOT NULL,
    store_type      VARCHAR(50),
    opening_date    DATE,

    CONSTRAINT pk_dim_store         PRIMARY KEY (store_key),
    CONSTRAINT uq_dim_store_bk      UNIQUE (store_id)
);

COMMENT ON TABLE  dim_store          IS 'Store dimension — one row per unique store';
COMMENT ON COLUMN dim_store.store_id IS 'Business key from stores_ingested.csv';


-- ---------------------------------------------------------------------------
-- 5. dim_promotion  (sourced from promotions_ingested.csv)
--    NOTE: No FK from fact_sales — promo_id absent from sales_ingested.csv.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dim_promotion (
    promo_id        INTEGER         NOT NULL,
    promo_name      VARCHAR(200)    NOT NULL,
    promo_type      VARCHAR(100),
    start_date      DATE            NOT NULL,
    end_date        DATE            NOT NULL,
    discount_pct    NUMERIC(5,2)    NOT NULL,

    CONSTRAINT pk_dim_promotion     PRIMARY KEY (promo_id),
    CONSTRAINT chk_dim_promo_dates  CHECK (end_date >= start_date),
    CONSTRAINT chk_dim_promo_disc   CHECK (discount_pct BETWEEN 0 AND 100)
);

COMMENT ON TABLE  dim_promotion          IS 'Promotion dimension — one row per promotion campaign';
COMMENT ON COLUMN dim_promotion.promo_id IS 'Natural PK; NOT referenced from fact_sales (unreliable join key)';


-- =============================================================================
-- FACT TABLES
-- =============================================================================

-- ---------------------------------------------------------------------------
-- 6. fact_sales
--    Grain    : one row per individual sales transaction line
--    Surrogate PK : sales_id (BIGSERIAL — warehouse-generated)
--    No FK to dim_promotion — promo_id absent from sales_ingested.csv.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS fact_sales (
    sales_id        BIGSERIAL       NOT NULL,
    date_key        INTEGER         NOT NULL,
    store_key       INTEGER         NOT NULL,
    product_key     INTEGER         NOT NULL,
    customer_key    INTEGER,

    channel         VARCHAR(50)     NOT NULL,
    quantity        INTEGER         NOT NULL,
    unit_price      NUMERIC(10,2)   NOT NULL,
    discount_pct    NUMERIC(5,2)    NOT NULL DEFAULT 0,
    total_value     NUMERIC(14,2)   NOT NULL,

    CONSTRAINT pk_fact_sales            PRIMARY KEY (sales_id),
    CONSTRAINT fk_fact_sales_date       FOREIGN KEY (date_key)
                                            REFERENCES dim_date (date_key),
    CONSTRAINT fk_fact_sales_store      FOREIGN KEY (store_key)
                                            REFERENCES dim_store (store_key),
    CONSTRAINT fk_fact_sales_product    FOREIGN KEY (product_key)
                                            REFERENCES dim_product (product_key),
    CONSTRAINT fk_fact_sales_customer   FOREIGN KEY (customer_key)
                                            REFERENCES dim_customer (customer_key),
    CONSTRAINT chk_fact_sales_qty       CHECK (quantity > 0),
    CONSTRAINT chk_fact_sales_price     CHECK (unit_price >= 0),
    CONSTRAINT chk_fact_sales_total     CHECK (total_value >= 0),
    CONSTRAINT chk_fact_sales_disc      CHECK (discount_pct BETWEEN 0 AND 100)
);

COMMENT ON TABLE  fact_sales               IS 'Sales fact — one row per transaction line';
COMMENT ON COLUMN fact_sales.sales_id      IS 'Warehouse-generated surrogate PK (BIGSERIAL)';
COMMENT ON COLUMN fact_sales.customer_key  IS 'Nullable — anonymous/walk-in sales have no customer';
COMMENT ON COLUMN fact_sales.unit_price    IS 'Price per unit at time of sale';
COMMENT ON COLUMN fact_sales.total_value   IS 'Source-recorded total sales value (quantity * unit_price as captured in the source system); discount_pct is stored separately';


-- ---------------------------------------------------------------------------
-- 7. fact_inventory
--    Grain    : one row per store + SKU + snapshot_date
--    Surrogate PK : inventory_id (BIGSERIAL)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS fact_inventory (
    inventory_id        BIGSERIAL       NOT NULL,
    store_key           INTEGER         NOT NULL,
    product_key         INTEGER         NOT NULL,
    snapshot_date_key   INTEGER         NOT NULL,
    last_restock_date   DATE,
    stock_on_hand       INTEGER         NOT NULL,
    reorder_point       INTEGER         NOT NULL,
    safety_stock        INTEGER         NOT NULL,

    CONSTRAINT pk_fact_inventory            PRIMARY KEY (inventory_id),
    CONSTRAINT uq_fact_inventory_grain      UNIQUE (store_key, product_key, snapshot_date_key),
    CONSTRAINT fk_fact_inv_store            FOREIGN KEY (store_key)
                                                REFERENCES dim_store (store_key),
    CONSTRAINT fk_fact_inv_product          FOREIGN KEY (product_key)
                                                REFERENCES dim_product (product_key),
    CONSTRAINT fk_fact_inv_snapshot_date    FOREIGN KEY (snapshot_date_key)
                                                REFERENCES dim_date (date_key),
    CONSTRAINT chk_fact_inv_stock           CHECK (stock_on_hand >= 0),
    CONSTRAINT chk_fact_inv_reorder         CHECK (reorder_point >= 0),
    CONSTRAINT chk_fact_inv_safety          CHECK (safety_stock >= 0)
);

COMMENT ON TABLE  fact_inventory                   IS 'Inventory snapshot fact — one row per store/SKU/snapshot date';
COMMENT ON COLUMN fact_inventory.inventory_id      IS 'Warehouse-generated surrogate PK (BIGSERIAL)';
COMMENT ON COLUMN fact_inventory.snapshot_date_key IS 'FK to dim_date; date of the inventory snapshot';


-- =============================================================================
-- INDEXES
-- =============================================================================

-- dim_date
CREATE INDEX IF NOT EXISTS idx_dim_date_year_month  ON dim_date (year, month);
CREATE INDEX IF NOT EXISTS idx_dim_date_full_date   ON dim_date (full_date);

-- dim_customer
CREATE INDEX IF NOT EXISTS idx_dim_customer_city    ON dim_customer (city);
CREATE INDEX IF NOT EXISTS idx_dim_customer_loyalty ON dim_customer (loyalty_segment);

-- dim_product
CREATE INDEX IF NOT EXISTS idx_dim_product_category ON dim_product (category);
CREATE INDEX IF NOT EXISTS idx_dim_product_brand    ON dim_product (brand);

-- dim_store
CREATE INDEX IF NOT EXISTS idx_dim_store_city       ON dim_store (city);
CREATE INDEX IF NOT EXISTS idx_dim_store_type       ON dim_store (store_type);

-- fact_sales
CREATE INDEX IF NOT EXISTS idx_fact_sales_date_key      ON fact_sales (date_key);
CREATE INDEX IF NOT EXISTS idx_fact_sales_store_key     ON fact_sales (store_key);
CREATE INDEX IF NOT EXISTS idx_fact_sales_product_key   ON fact_sales (product_key);
CREATE INDEX IF NOT EXISTS idx_fact_sales_customer_key  ON fact_sales (customer_key);
CREATE INDEX IF NOT EXISTS idx_fact_sales_channel       ON fact_sales (channel);
CREATE INDEX IF NOT EXISTS idx_fact_sales_date_store    ON fact_sales (date_key, store_key);

-- fact_inventory
CREATE INDEX IF NOT EXISTS idx_fact_inv_store_key       ON fact_inventory (store_key);
CREATE INDEX IF NOT EXISTS idx_fact_inv_product_key     ON fact_inventory (product_key);
CREATE INDEX IF NOT EXISTS idx_fact_inv_snapshot_date   ON fact_inventory (snapshot_date_key);
CREATE INDEX IF NOT EXISTS idx_fact_inv_store_product   ON fact_inventory (store_key, product_key);
