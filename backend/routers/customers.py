"""
GET /api/customers

SCHEMA GAPS — dim_customer has cust_id, age, gender, city, loyalty_segment,
preferred_channel, registration_date. No name, email, state, or country:
  - fullName: same placeholder pattern as dashboard.py's recentSales
    ("Customer CUST-1001"), not a fabricated real name.
  - email / state / country: returned as null, nothing to draw from.
  - loyaltyTier: dim_customer's loyalty_segment values (Silver/Gold/
    Platinum) uppercased to match the contract's PLATINUM/GOLD/SILVER/
    BRONZE. No customer is currently tagged BRONZE in the data — that's
    a real filter value that just won't match anything right now, not a
    bug here.

totalPurchases/totalOrders/firstPurchasedAt/lastPurchasedAt are real
aggregates from fact_sales, joined on customer_key.
"""
from fastapi import APIRouter, Query
from db import query, query_one

router = APIRouter()


@router.get("/customers")
def list_customers(
    page: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1, le=100),
    search: str | None = None,
    loyaltyTier: str | None = Query(None, pattern="^(PLATINUM|GOLD|SILVER|BRONZE)$"),
):
    offset = (page - 1) * pageSize

    where = ["1=1"]
    params: list = []

    if search:
        # No name field to search — match on city or the business-key id.
        where.append("(c.city ILIKE %s OR c.cust_id::text ILIKE %s)")
        params.extend([f"%{search}%", f"%{search}%"])

    if loyaltyTier:
        where.append("UPPER(c.loyalty_segment) = %s")
        params.append(loyaltyTier)

    where_clause = " AND ".join(where)

    total_row = query_one(f"SELECT COUNT(*) AS total FROM dim_customer c WHERE {where_clause}", tuple(params))
    total = total_row["total"]

    rows = query(f"""
        SELECT
            'CUST-' || c.cust_id AS "customerId",
            'Customer CUST-' || c.cust_id AS "fullName",
            NULL AS email,
            c.city,
            NULL AS state,
            NULL AS country,
            COALESCE(SUM(fs.total_value), 0) AS "totalPurchases",
            COUNT(fs.sales_id) AS "totalOrders",
            UPPER(c.loyalty_segment) AS "loyaltyTier",
            MIN(d.full_date) AS "firstPurchasedAt",
            MAX(d.full_date) AS "lastPurchasedAt"
        FROM dim_customer c
        LEFT JOIN fact_sales fs ON fs.customer_key = c.customer_key
        LEFT JOIN dim_date d ON fs.date_key = d.date_key
        WHERE {where_clause}
        GROUP BY c.cust_id, c.city, c.loyalty_segment
        ORDER BY "totalPurchases" DESC
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
