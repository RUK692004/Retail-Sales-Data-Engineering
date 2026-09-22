"""
GET /api/products
GET /api/products/{skuId}

SCHEMA GAPS — dim_product only has sku_id, sku_name, category, subcategory,
unit_price, cost_price, brand. The contract also wants unit, status,
createdAt, and description, none of which exist in our data:
  - unit: hardcoded "piece" (no per-SKU unit-of-measure is tracked).
  - status: hardcoded "ACTIVE" (no product lifecycle state is tracked, so
    every SKU is reported active; the status filter still works, it just
    never matches DISCONTINUED/DRAFT since no row can have those values).
  - createdAt / description: returned as null rather than fabricated —
    there's no real date or descriptive text to draw from.
"""
from fastapi import APIRouter, HTTPException, Query
from db import query, query_one
from filters import clean_filter

router = APIRouter()

PRODUCT_COLUMNS = """
    'SKU-' || sku_id AS "skuId",
    sku_name AS "productName",
    category,
    brand,
    unit_price AS price,
    cost_price AS "costPrice",
    'piece' AS unit,
    'ACTIVE' AS status,
    NULL AS "createdAt",
    NULL AS description
"""


@router.get("/products")
def list_products(
    page: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1, le=100),
    search: str | None = None,
    category: str | None = None,
    status: str | None = None,
):
    offset = (page - 1) * pageSize
    category = clean_filter(category)
    status = clean_filter(status)

    where = ["1=1"]
    params: list = []

    if search:
        where.append("(sku_name ILIKE %s OR brand ILIKE %s)")
        params.extend([f"%{search}%", f"%{search}%"])

    if category:
        where.append("category = %s")
        params.append(category)

    if status and status != "ACTIVE":
        # No product can ever be DISCONTINUED/DRAFT — see docstring.
        where.append("1=0")

    where_clause = " AND ".join(where)

    total_row = query_one(f"SELECT COUNT(*) AS total FROM dim_product WHERE {where_clause}", tuple(params))
    total = total_row["total"]

    rows = query(f"""
        SELECT {PRODUCT_COLUMNS}
        FROM dim_product
        WHERE {where_clause}
        ORDER BY sku_name
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


@router.get("/products/{skuId}")
def get_product(skuId: str):
    numeric_sku_id = skuId.replace("SKU-", "")
    row = query_one(f"""
        SELECT {PRODUCT_COLUMNS}
        FROM dim_product
        WHERE sku_id = %s
    """, (numeric_sku_id,))
    if row is None:
        raise HTTPException(status_code=404, detail={
            "message": f"Product {skuId} not found",
            "code": "ERR_404",
            "details": {"field": "skuId", "issue": "No matching sku_id in dim_product"},
        })
    return {"data": row}
