"""
GET /api/sales

Same schema-gap caveat as dashboard.py: customerName is a placeholder
(dim_customer has no real name field). paymentMethod also doesn't exist
anywhere in the schema — fact_sales has `channel` (e.g. "in_store",
"online"), which is the closest real field; returned as paymentMethod
for now since the contract expects that key, but this is a mismatch
worth resolving with whoever owns the frontend contract rather than
silently treating channel and payment method as the same thing.
"""
from fastapi import APIRouter, Query
from db import query, query_one
from filters import clean_filter

router = APIRouter()

# Whitelist sortBy values -> real column expressions, so user input never
# gets interpolated directly into SQL (avoids injection via sortBy).
SORT_COLUMNS = {
    "saleDate": "d.full_date",
    "totalAmount": "fs.total_value",
    "quantity": "fs.quantity",
}


@router.get("/sales")
def list_sales(
    page: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1, le=100),
    search: str | None = None,
    storeId: str | None = None,
    category: str | None = None,
    sortBy: str = "saleDate",
    sortOrder: str = Query("desc", pattern="^(asc|desc)$"),
):
    sort_col = SORT_COLUMNS.get(sortBy, SORT_COLUMNS["saleDate"])
    offset = (page - 1) * pageSize
    storeId = clean_filter(storeId)
    category = clean_filter(category)

    where = ["1=1"]
    params: list = []

    if storeId:
        # storeId arrives as "STR-101" — pull the numeric part back out.
        numeric_store_id = storeId.replace("STR-", "")
        where.append("s.store_id = %s")
        params.append(numeric_store_id)

    if category:
        where.append("p.category = %s")
        params.append(category)

    if search:
        where.append("(p.sku_name ILIKE %s OR s.store_name ILIKE %s)")
        params.extend([f"%{search}%", f"%{search}%"])

    where_clause = " AND ".join(where)

    total_row = query_one(f"""
        SELECT COUNT(*) AS total
        FROM fact_sales fs
        JOIN dim_date d ON fs.date_key = d.date_key
        JOIN dim_product p ON fs.product_key = p.product_key
        JOIN dim_store s ON fs.store_key = s.store_key
        WHERE {where_clause}
    """, tuple(params))
    total = total_row["total"]

    rows = query(f"""
        SELECT
            'SAL-' || fs.sales_id AS "saleId",
            d.full_date AS "saleDate",
            COALESCE('CUST-' || c.cust_id, NULL) AS "customerId",
            COALESCE('Customer CUST-' || c.cust_id, 'Guest') AS "customerName",
            'SKU-' || p.sku_id AS "skuId",
            p.sku_name AS "productName",
            p.category,
            'STR-' || s.store_id AS "storeId",
            s.store_name AS "storeName",
            fs.quantity,
            fs.unit_price AS "unitPrice",
            fs.total_value AS "totalAmount",
            fs.channel AS "paymentMethod"
        FROM fact_sales fs
        JOIN dim_date d ON fs.date_key = d.date_key
        JOIN dim_product p ON fs.product_key = p.product_key
        JOIN dim_store s ON fs.store_key = s.store_key
        LEFT JOIN dim_customer c ON fs.customer_key = c.customer_key
        WHERE {where_clause}
        ORDER BY {sort_col} {sortOrder.upper()}
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


@router.get("/sales/metrics")
def sales_metrics():
    row = query_one("""
        SELECT
            COUNT(*) AS "totalSalesCount",
            COALESCE(SUM(total_value), 0) AS "totalRevenue",
            COALESCE(SUM(quantity), 0) AS "totalQuantitySold"
        FROM fact_sales
    """)
    total_count = row["totalSalesCount"]
    total_revenue = float(row["totalRevenue"])
    return {
        "data": {
            "totalSalesCount": total_count,
            "totalRevenue": total_revenue,
            "averageOrderValue": round(total_revenue / total_count, 2) if total_count else 0.0,
            "totalQuantitySold": row["totalQuantitySold"],
        }
    }
