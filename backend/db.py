"""
Database connection helper for the retail sales dashboard API.
Reads the same env vars database/load_data.py already uses
(DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD), so this backend
works with zero extra config when run as another container on the
same Docker network as warehouse-postgres.
"""
import os
import psycopg2
import psycopg2.extras


def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "warehouse-postgres"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "retail_sales_dw"),
        user=os.getenv("DB_USER", "warehouse"),
        password=os.environ["DB_PASSWORD"],  # no default — fail loudly if missing
    )


def query(sql: str, params: tuple = ()) -> list[dict]:
    """Run a SELECT, return rows as a list of plain dicts (JSON-serializable)."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params)
            return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()


def query_one(sql: str, params: tuple = ()) -> dict | None:
    rows = query(sql, params)
    return rows[0] if rows else None


_latest_sale_date_cache = None


def get_latest_sale_date():
    """Latest full_date that actually has sales data. This dataset is a fixed
    historical snapshot (ends 2025-10-31) — any "last N days" or ACTIVE/EXPIRED
    logic anchored to the real wall-clock CURRENT_DATE instead of this would
    always land after the data ends. Cached in memory: it can't change without
    a fresh load, so there's no reason to hit the DB for it on every request.
    """
    global _latest_sale_date_cache
    if _latest_sale_date_cache is None:
        row = query_one("""
            SELECT MAX(d.full_date) AS latest_date
            FROM fact_sales fs
            JOIN dim_date d ON fs.date_key = d.date_key
        """)
        _latest_sale_date_cache = row["latest_date"]
    return _latest_sale_date_cache
