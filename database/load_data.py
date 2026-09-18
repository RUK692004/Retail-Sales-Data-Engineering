#!/usr/bin/env python3
"""
load_data.py -- Retail Sales Data Warehouse Loader
====================================================
Loads all six processed CSV files into the retail_sales_dw PostgreSQL
warehouse.

Author  : Member 3 (Database / DW Layer)
Created : 2026-09-18

Usage
-----
    python database/load_data.py

Environment variables (required -- do NOT hardcode passwords)
-------------------------------------------------------------
    DB_HOST      PostgreSQL host        (default: localhost)
    DB_PORT      PostgreSQL port        (default: 5432)
    DB_NAME      Database name          (default: retail_sales_dw)
    DB_USER      Database user          (default: postgres)
    DB_PASSWORD  Database password      (REQUIRED -- no default)

Optional overrides
------------------
    INPUT_DIR    Directory containing the processed CSV files
                 (default: data/processed relative to project root)
                 Change this to Member 2s transformed-output directory
                 when the transformation pipeline is ready.

    BATCH_SIZE   Number of rows per INSERT batch for fact tables
                 (default: 5000)

CSV files loaded
----------------
    customers_ingested.csv   -> dim_customer    (upsert on cust_id)
    skus_ingested.csv        -> dim_product     (upsert on sku_id)
    stores_ingested.csv      -> dim_store       (upsert on store_id)
    promotions_ingested.csv  -> dim_promotion   (upsert on promo_id)
    sales_ingested.csv       -> fact_sales      (full-refresh -- see below)
    inventory_ingested.csv   -> fact_inventory  (upsert on grain key)

Repeated-load / reload behavior
--------------------------------
Dimension tables (dim_customer, dim_product, dim_store, dim_promotion)
    Use INSERT ... ON CONFLICT (business_key) DO UPDATE.
    Safe to run multiple times; existing rows are refreshed in-place.

fact_inventory
    Uses INSERT ... ON CONFLICT (store_key, product_key, snapshot_date_key)
    DO UPDATE.  The grain uniqueness constraint makes this naturally
    idempotent.

fact_sales -- FULL REFRESH
    sales_ingested.csv has no reliable transaction identifier, so no
    natural conflict key exists.  To avoid duplicate rows on re-runs the
    loader truncates fact_sales before each load (TRUNCATE ... CASCADE is
    NOT used -- referential integrity flows one way into fact_sales, not
    out of it, so a plain TRUNCATE is safe).  Dimension tables are never
    touched by the truncation.  If only incremental loads are needed in
    the future, introduce a pipeline-run-id or source transaction_id
    column as the conflict key and switch to INSERT ... ON CONFLICT.

Order of loading
----------------
1. dim_date      -- seeded by seed_data.sql (not handled here)
2. dim_customer  -- customers_ingested.csv
3. dim_product   -- skus_ingested.csv
4. dim_store     -- stores_ingested.csv
5. dim_promotion -- promotions_ingested.csv
6. fact_sales    -- sales_ingested.csv      (full-refresh)
7. fact_inventory-- inventory_ingested.csv  (upsert)
"""

import csv
import logging
import os
import sys
import time
from datetime import date, datetime
from pathlib import Path

import psycopg2
import psycopg2.extras

# ---------------------------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration -- read exclusively from environment variables
# ---------------------------------------------------------------------------
DB_CONFIG = {
    "host":     os.getenv("DB_HOST",     "localhost"),
    "port":     int(os.getenv("DB_PORT", "5432")),
    "dbname":   os.getenv("DB_NAME",     "retail_sales_dw"),
    "user":     os.getenv("DB_USER",     "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),   # REQUIRED
}

# Directory containing processed CSVs (overridable for Member 2 output)
_script_dir   = Path(__file__).resolve().parent          # database/
_project_root = _script_dir.parent                       # project root
INPUT_DIR = Path(os.getenv("INPUT_DIR", str(_project_root / "data" / "processed")))

BATCH_SIZE = int(os.getenv("BATCH_SIZE", "5000"))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_connection():
    """Create and return a psycopg2 connection using DB_CONFIG."""
    if not DB_CONFIG["password"]:
        log.error(
            "DB_PASSWORD environment variable is not set. "
            "Set it before running this script."
        )
        sys.exit(1)
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = False
        return conn
    except psycopg2.OperationalError as exc:
        log.error("Could not connect to PostgreSQL: %s", exc)
        sys.exit(1)


def read_csv(filepath: Path) -> list:
    """Read a CSV file and return a list of row dicts."""
    if not filepath.exists():
        raise FileNotFoundError(f"CSV not found: {filepath}")
    with open(filepath, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        return list(reader)


def _nullable_int(value):
    """Convert a string to int, returning None for empty/float-formatted blanks."""
    if value is None or str(value).strip() == "":
        return None
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return None


def _nullable_float(value):
    """Convert a string to float, returning None for empty strings."""
    if value is None or str(value).strip() == "":
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def _nullable_date(value):
    """Parse a date string, handling common formats including timestamps."""
    if value is None or str(value).strip() == "":
        return None
    # Strip timestamp portion (e.g. '2017-01-01 00:00:00.000000000')
    raw = str(value).strip().split(" ")[0]
    try:
        return datetime.strptime(raw, "%Y-%m-%d").date()
    except ValueError:
        log.warning("Could not parse date: %r", value)
        return None


def _date_to_key(d):
    """Convert a date to the YYYYMMDD integer key used in dim_date."""
    if d is None:
        return None
    return int(d.strftime("%Y%m%d"))


def batch_insert(cursor, sql, rows, batch_size=None):
    """Execute a batch INSERT using execute_values for efficiency."""
    if batch_size is None:
        batch_size = BATCH_SIZE
    total = len(rows)
    for start in range(0, total, batch_size):
        chunk = rows[start : start + batch_size]
        psycopg2.extras.execute_values(cursor, sql, chunk, page_size=batch_size)
    return total


# ---------------------------------------------------------------------------
# Dimension loader functions
# ---------------------------------------------------------------------------

def load_dim_customer(conn, filepath: Path):
    """Load dim_customer from customers_ingested.csv (upsert on cust_id)."""
    log.info("Loading dim_customer from %s ...", filepath.name)
    rows = read_csv(filepath)

    sql = """
        INSERT INTO dim_customer
            (cust_id, age, gender, city, loyalty_segment,
             preferred_channel, registration_date)
        VALUES %s
        ON CONFLICT (cust_id) DO UPDATE SET
            age               = EXCLUDED.age,
            gender            = EXCLUDED.gender,
            city              = EXCLUDED.city,
            loyalty_segment   = EXCLUDED.loyalty_segment,
            preferred_channel = EXCLUDED.preferred_channel,
            registration_date = EXCLUDED.registration_date
    """
    data = []
    for r in rows:
        data.append((
            int(r["cust_id"]),
            _nullable_int(r.get("age")),
            r.get("gender") or None,
            r.get("city") or None,
            r.get("loyalty_segment") or None,
            r.get("preferred_channel") or None,
            _nullable_date(r.get("registration_date")),
        ))

    with conn.cursor() as cur:
        batch_insert(cur, sql, data)
    conn.commit()
    log.info("  -> %d customers loaded.", len(data))


def load_dim_product(conn, filepath: Path):
    """Load dim_product from skus_ingested.csv (upsert on sku_id)."""
    log.info("Loading dim_product from %s ...", filepath.name)
    rows = read_csv(filepath)

    sql = """
        INSERT INTO dim_product
            (sku_id, sku_name, category, subcategory,
             unit_price, cost_price, brand)
        VALUES %s
        ON CONFLICT (sku_id) DO UPDATE SET
            sku_name    = EXCLUDED.sku_name,
            category    = EXCLUDED.category,
            subcategory = EXCLUDED.subcategory,
            unit_price  = EXCLUDED.unit_price,
            cost_price  = EXCLUDED.cost_price,
            brand       = EXCLUDED.brand
    """
    data = []
    for r in rows:
        data.append((
            int(r["sku_id"]),
            r["sku_name"],
            r["category"],
            r.get("subcategory") or None,
            float(r["unit_price"]),
            _nullable_float(r.get("cost_price")),
            r.get("brand") or None,
        ))

    with conn.cursor() as cur:
        batch_insert(cur, sql, data)
    conn.commit()
    log.info("  -> %d products loaded.", len(data))


def load_dim_store(conn, filepath: Path):
    """Load dim_store from stores_ingested.csv (upsert on store_id)."""
    log.info("Loading dim_store from %s ...", filepath.name)
    rows = read_csv(filepath)

    sql = """
        INSERT INTO dim_store
            (store_id, store_name, city, store_type, opening_date)
        VALUES %s
        ON CONFLICT (store_id) DO UPDATE SET
            store_name   = EXCLUDED.store_name,
            city         = EXCLUDED.city,
            store_type   = EXCLUDED.store_type,
            opening_date = EXCLUDED.opening_date
    """
    data = []
    for r in rows:
        data.append((
            int(r["store_id"]),
            r["store_name"],
            r["city"],
            r.get("store_type") or None,
            _nullable_date(r.get("opening_date")),
        ))

    with conn.cursor() as cur:
        batch_insert(cur, sql, data)
    conn.commit()
    log.info("  -> %d stores loaded.", len(data))


def load_dim_promotion(conn, filepath: Path):
    """
    Load dim_promotion from promotions_ingested.csv (upsert on promo_id).

    promotions_ingested.csv columns:
        promo_name, start_date, end_date, discount_pct, promo_type, promo_id

    This is the single source of truth for promotions -- there is no
    hardcoded list in seed_data.sql.  Safe to re-run: existing rows are
    updated if the source data changes.
    """
    log.info("Loading dim_promotion from %s ...", filepath.name)
    rows = read_csv(filepath)

    sql = """
        INSERT INTO dim_promotion
            (promo_id, promo_name, promo_type, start_date, end_date, discount_pct)
        VALUES %s
        ON CONFLICT (promo_id) DO UPDATE SET
            promo_name   = EXCLUDED.promo_name,
            promo_type   = EXCLUDED.promo_type,
            start_date   = EXCLUDED.start_date,
            end_date     = EXCLUDED.end_date,
            discount_pct = EXCLUDED.discount_pct
    """
    data = []
    skipped = 0
    for i, r in enumerate(rows):
        promo_id = _nullable_int(r.get("promo_id"))
        if promo_id is None:
            log.warning("Row %d: missing promo_id -- skipping", i)
            skipped += 1
            continue

        promo_name = r.get("promo_name", "").strip()
        if not promo_name:
            log.warning("Row %d: missing promo_name -- skipping", i)
            skipped += 1
            continue

        start_date = _nullable_date(r.get("start_date"))
        end_date   = _nullable_date(r.get("end_date"))
        if start_date is None or end_date is None:
            log.warning("Row %d: missing start_date or end_date -- skipping", i)
            skipped += 1
            continue

        discount_pct = _nullable_float(r.get("discount_pct"))
        if discount_pct is None:
            log.warning("Row %d: missing discount_pct -- skipping", i)
            skipped += 1
            continue

        data.append((
            promo_id,
            promo_name,
            r.get("promo_type") or None,
            start_date,
            end_date,
            discount_pct,
        ))

    with conn.cursor() as cur:
        batch_insert(cur, sql, data)
    conn.commit()
    log.info("  -> %d promotions loaded, %d rows skipped.", len(data), skipped)


# ---------------------------------------------------------------------------
# Fact loader functions
# ---------------------------------------------------------------------------

def truncate_fact_sales(conn):
    """
    Truncate fact_sales before a full reload.

    WHY TRUNCATE (not upsert):
        sales_ingested.csv contains no reliable transaction identifier that
        could serve as a natural conflict key.  Using TRUNCATE + INSERT is
        the correct full-refresh strategy: it avoids duplicates on re-runs
        without requiring an invented key.

    SAFETY:
        - Only fact_sales is truncated; all dimension tables are untouched.
        - fact_sales has no child tables with FK references pointing INTO it,
          so a plain TRUNCATE (without CASCADE) is safe.
        - The truncation and the subsequent inserts run in the same
          connection so a crash mid-load leaves an empty (not partial)
          table until the next successful run.

    FUTURE INCREMENTAL LOADS:
        If the upstream pipeline provides a stable transaction_id column,
        remove this function and switch load_fact_sales() to use
        INSERT ... ON CONFLICT (transaction_id) DO UPDATE.
    """
    log.info("Truncating fact_sales for full refresh ...")
    with conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE fact_sales;")
    conn.commit()
    log.info("  -> fact_sales truncated.")


def load_fact_sales(conn, filepath: Path):
    """
    Load fact_sales from sales_ingested.csv.

    Call truncate_fact_sales() before this function to ensure a clean
    full-refresh load with no duplicate rows.

    Resolves business-key columns (store_id, sku_id, customer_id, date)
    to surrogate keys using lookup maps fetched once from the DB.
    customer_key remains NULL for anonymous transactions.
    """
    log.info("Loading fact_sales from %s ...", filepath.name)
    log.info("  (this is the largest table -- ~641k rows, may take a minute)")

    # Build lookup maps from the DB (dimensions already loaded above)
    with conn.cursor() as cur:
        cur.execute("SELECT store_id,  store_key   FROM dim_store")
        store_map = dict(cur.fetchall())

        cur.execute("SELECT sku_id,    product_key FROM dim_product")
        product_map = dict(cur.fetchall())

        cur.execute("SELECT cust_id,   customer_key FROM dim_customer")
        customer_map = dict(cur.fetchall())

        cur.execute("SELECT full_date, date_key    FROM dim_date")
        date_map = {str(row[0]): row[1] for row in cur.fetchall()}

    sql = """
        INSERT INTO fact_sales
            (date_key, store_key, product_key, customer_key,
             channel, quantity, unit_price, discount_pct, total_value)
        VALUES %s
    """

    rows    = read_csv(filepath)
    total   = len(rows)
    skipped = 0
    data    = []

    for i, r in enumerate(rows):
        # Resolve surrogate keys
        raw_date = r.get("date", "").strip()
        date_key = date_map.get(raw_date)
        if date_key is None:
            log.warning("Row %d: unresolvable date %r -- skipping", i, raw_date)
            skipped += 1
            continue

        store_id  = _nullable_int(r.get("store_id"))
        store_key = store_map.get(store_id) if store_id else None
        if store_key is None:
            log.warning("Row %d: unresolvable store_id %r -- skipping", i, store_id)
            skipped += 1
            continue

        sku_id      = _nullable_int(r.get("sku_id"))
        product_key = product_map.get(sku_id) if sku_id else None
        if product_key is None:
            log.warning("Row %d: unresolvable sku_id %r -- skipping", i, sku_id)
            skipped += 1
            continue

        # customer_id is nullable -- anonymous sales are valid
        raw_cust     = r.get("customer_id", "").strip()
        cust_id      = _nullable_int(raw_cust)
        customer_key = customer_map.get(cust_id) if cust_id is not None else None

        quantity     = _nullable_int(r.get("quantity"))
        unit_price   = _nullable_float(r.get("unit_price"))
        total_value  = _nullable_float(r.get("total_value"))
        discount_pct = _nullable_float(r.get("discount_pct")) or 0.0
        channel      = r.get("channel", "").strip() or "Unknown"

        if quantity is None or unit_price is None or total_value is None:
            log.warning("Row %d: missing numeric field -- skipping", i)
            skipped += 1
            continue

        data.append((
            date_key, store_key, product_key, customer_key,
            channel, quantity, unit_price, discount_pct, total_value,
        ))

        # Flush batch
        if len(data) >= BATCH_SIZE:
            with conn.cursor() as cur:
                batch_insert(cur, sql, data, batch_size=BATCH_SIZE)
            conn.commit()
            data = []
            if (i + 1) % 50000 == 0:
                log.info("  ... %d / %d rows processed", i + 1, total)

    # Flush remainder
    if data:
        with conn.cursor() as cur:
            batch_insert(cur, sql, data, batch_size=BATCH_SIZE)
        conn.commit()

    loaded = total - skipped
    log.info("  -> %d sales loaded, %d rows skipped.", loaded, skipped)


def load_fact_inventory(conn, filepath: Path):
    """
    Load fact_inventory from inventory_ingested.csv.
    Grain: store + SKU + snapshot_date.
    Uses upsert on the grain UNIQUE constraint -- naturally idempotent.
    """
    log.info("Loading fact_inventory from %s ...", filepath.name)

    # Build lookup maps
    with conn.cursor() as cur:
        cur.execute("SELECT store_id,  store_key   FROM dim_store")
        store_map = dict(cur.fetchall())

        cur.execute("SELECT sku_id,    product_key FROM dim_product")
        product_map = dict(cur.fetchall())

        cur.execute("SELECT full_date, date_key    FROM dim_date")
        date_map = {str(row[0]): row[1] for row in cur.fetchall()}

    sql = """
        INSERT INTO fact_inventory
            (store_key, product_key, snapshot_date_key,
             last_restock_date, stock_on_hand, reorder_point, safety_stock)
        VALUES %s
        ON CONFLICT (store_key, product_key, snapshot_date_key) DO UPDATE SET
            last_restock_date = EXCLUDED.last_restock_date,
            stock_on_hand     = EXCLUDED.stock_on_hand,
            reorder_point     = EXCLUDED.reorder_point,
            safety_stock      = EXCLUDED.safety_stock
    """

    rows    = read_csv(filepath)
    total   = len(rows)
    skipped = 0
    data    = []

    for i, r in enumerate(rows):
        store_id  = _nullable_int(r.get("store_id"))
        store_key = store_map.get(store_id) if store_id else None
        if store_key is None:
            log.warning("Row %d: unresolvable store_id %r -- skipping", i, store_id)
            skipped += 1
            continue

        sku_id      = _nullable_int(r.get("sku_id"))
        product_key = product_map.get(sku_id) if sku_id else None
        if product_key is None:
            log.warning("Row %d: unresolvable sku_id %r -- skipping", i, sku_id)
            skipped += 1
            continue

        raw_snap          = r.get("snapshot_date", "").strip()
        snapshot_date_key = date_map.get(raw_snap)
        if snapshot_date_key is None:
            log.warning("Row %d: unresolvable snapshot_date %r -- skipping", i, raw_snap)
            skipped += 1
            continue

        stock_on_hand = _nullable_int(r.get("stock_on_hand"))
        reorder_point = _nullable_int(r.get("reorder_point"))
        safety_stock  = _nullable_int(r.get("safety_stock"))
        last_restock  = _nullable_date(r.get("last_restock_date"))

        if stock_on_hand is None or reorder_point is None or safety_stock is None:
            log.warning("Row %d: missing stock field -- skipping", i)
            skipped += 1
            continue

        data.append((
            store_key, product_key, snapshot_date_key,
            last_restock, stock_on_hand, reorder_point, safety_stock,
        ))

        if len(data) >= BATCH_SIZE:
            with conn.cursor() as cur:
                batch_insert(cur, sql, data, batch_size=BATCH_SIZE)
            conn.commit()
            data = []

    if data:
        with conn.cursor() as cur:
            batch_insert(cur, sql, data, batch_size=BATCH_SIZE)
        conn.commit()

    loaded = total - skipped
    log.info("  -> %d inventory rows loaded, %d rows skipped.", loaded, skipped)


# ---------------------------------------------------------------------------
# Main entrypoint
# ---------------------------------------------------------------------------

def main():
    log.info("=== Retail Sales DW -- Data Loader ===")
    log.info("Database : %(dbname)s @ %(host)s:%(port)s", DB_CONFIG)
    log.info("Input dir: %s", INPUT_DIR)

    if not INPUT_DIR.exists():
        log.error("INPUT_DIR does not exist: %s", INPUT_DIR)
        sys.exit(1)

    conn = get_connection()
    log.info("Connected to PostgreSQL successfully.")

    start_time = time.time()

    try:
        # --- Dimensions (upsert -- safe to re-run in any order after dim_date) ---
        load_dim_customer(conn,  INPUT_DIR / "customers_ingested.csv")
        load_dim_product(conn,   INPUT_DIR / "skus_ingested.csv")
        load_dim_store(conn,     INPUT_DIR / "stores_ingested.csv")
        load_dim_promotion(conn, INPUT_DIR / "promotions_ingested.csv")

        # --- Facts ---
        # fact_sales: full-refresh (truncate then insert)
        truncate_fact_sales(conn)
        load_fact_sales(conn,    INPUT_DIR / "sales_ingested.csv")

        # fact_inventory: upsert on grain key
        load_fact_inventory(conn, INPUT_DIR / "inventory_ingested.csv")

    except Exception as exc:
        conn.rollback()
        log.error("Fatal error during load -- transaction rolled back: %s", exc)
        raise
    finally:
        conn.close()

    elapsed = time.time() - start_time
    log.info("=== Load complete in %.1f seconds ===", elapsed)


if __name__ == "__main__":
    main()