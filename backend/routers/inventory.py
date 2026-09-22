"""
GET /api/inventory
Only the latest snapshot per store+product counts as "current" stock —
fact_inventory's grain is one row per store/SKU/snapshot date, so we
pick the most recent snapshot_date_key for each combination.
"""
from fastapi import APIRouter, Query
from db import query, query_one

router = APIRouter()


@router.get("/inventory")
def list_inventory(
    page: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1, le=100),
    search: str | None = None,
    storeId: str | None = None,
    status: str | None = Query(None, pattern="^(IN_STOCK|LOW_STOCK|OUT_OF_STOCK)$"),
):
    offset = (page - 1) * pageSize

    where = ["l.rn = 1"]
    params: list = []

    if storeId:
        numeric_store_id = storeId.replace("STR-", "")
        where.append("s.store_id = %s")
        params.append(numeric_store_id)

    if search:
        where.append("(p.sku_name ILIKE %s OR s.store_name ILIKE %s)")
        params.extend([f"%{search}%", f"%{search}%"])

    if status == "OUT_OF_STOCK":
        where.append("l.stock_on_hand = 0")
    elif status == "LOW_STOCK":
        where.append("l.stock_on_hand > 0 AND l.stock_on_hand <= l.reorder_point")
    elif status == "IN_STOCK":
        where.append("l.stock_on_hand > l.reorder_point")

    where_clause = " AND ".join(where)

    latest_cte = """
        WITH latest AS (
            SELECT inventory_id, store_key, product_key, stock_on_hand,
                   reorder_point, last_restock_date,
                   ROW_NUMBER() OVER (
                       PARTITION BY store_key, product_key
                       ORDER BY snapshot_date_key DESC
                   ) AS rn
            FROM fact_inventory
        )
    """

    total_row = query_one(f"""
        {latest_cte}
        SELECT COUNT(*) AS total
        FROM latest l
        JOIN dim_product p ON l.product_key = p.product_key
        JOIN dim_store s ON l.store_key = s.store_key
        WHERE {where_clause}
    """, tuple(params))
    total = total_row["total"]

    rows = query(f"""
        {latest_cte}
        SELECT
            'INV-' || l.inventory_id AS id,
            'STR-' || s.store_id AS "storeId",
            s.store_name AS "storeName",
            'SKU-' || p.sku_id AS "skuId",
            p.sku_name AS "productName",
            p.category,
            l.stock_on_hand AS "stockOnHand",
            l.reorder_point AS "reorderPoint",
            CASE
                WHEN l.stock_on_hand = 0 THEN 'OUT_OF_STOCK'
                WHEN l.stock_on_hand <= l.reorder_point THEN 'LOW_STOCK'
                ELSE 'IN_STOCK'
            END AS status,
            l.last_restock_date AS "lastRestocked"
        FROM latest l
        JOIN dim_product p ON l.product_key = p.product_key
        JOIN dim_store s ON l.store_key = s.store_key
        WHERE {where_clause}
        ORDER BY l.stock_on_hand ASC
        LIMIT %s OFFSET %s
    """, tuple(params) + (pageSize, offset))

    return {
        "data": rows,
        "meta": {
            "total": total,
            "page": page,
            "pageSize": pageSize,
            "totalPages": (total + pageSize - 1) // pageSize,
        },
    }
