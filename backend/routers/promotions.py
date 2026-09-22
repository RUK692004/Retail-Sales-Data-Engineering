"""
GET /api/promotions

SCHEMA GAP — dim_promotion has no FK from fact_sales (promo_id is absent
from sales_ingested.csv entirely, see create_tables.sql's comment on
dim_promotion), so "redemption statistics" mentioned in the contract's
endpoint description can't be computed from this data. Returning promo
metadata + a derived status only; no redemption/usage counts.

status (ACTIVE/UPCOMING/EXPIRED) is derived from start_date/end_date vs.
the latest date the sales data actually has (db.get_latest_sale_date),
not the real wall clock — this dataset's promotions all fall in
2021-2025, and the real clock has since moved past all of them, which
would make every promotion read EXPIRED regardless of how it actually
sits relative to the data's own timeline.
"""
from fastapi import APIRouter, Query
from db import get_latest_sale_date, query, query_one
from filters import clean_filter

router = APIRouter()

# References anchor.latest_date (from the CTE below), not CURRENT_DATE —
# see docstring above.
STATUS_CASE = """
    CASE
        WHEN a.latest_date < start_date THEN 'UPCOMING'
        WHEN a.latest_date > end_date THEN 'EXPIRED'
        ELSE 'ACTIVE'
    END
"""


@router.get("/promotions")
def list_promotions(
    page: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1, le=100),
    status: str | None = None,
):
    offset = (page - 1) * pageSize
    status = clean_filter(status)
    latest_date = get_latest_sale_date()

    where = ["1=1"]
    params: list = []

    if status:
        where.append(f"({STATUS_CASE}) = %s")
        params.append(status)

    where_clause = " AND ".join(where)

    total_row = query_one(
        f"WITH anchor AS (SELECT %s::date AS latest_date) SELECT COUNT(*) AS total FROM dim_promotion, anchor a WHERE {where_clause}",
        (latest_date,) + tuple(params),
    )
    total = total_row["total"]

    rows = query(f"""
        WITH anchor AS (SELECT %s::date AS latest_date)
        SELECT
            promo_id AS "promoId",
            promo_name AS "promoName",
            promo_type AS "promoType",
            start_date AS "startDate",
            end_date AS "endDate",
            discount_pct AS "discountPct",
            ({STATUS_CASE}) AS status
        FROM dim_promotion, anchor a
        WHERE {where_clause}
        ORDER BY start_date DESC
        LIMIT %s OFFSET %s
    """, (latest_date,) + tuple(params) + (pageSize, offset))

    return {
        "data": rows,
        "meta": {
            "total": total,
            "page": page,
            "pageSize": pageSize,
            "totalPages": (total + pageSize - 1) // pageSize,
        },
    }
