"""
GET /api/dashboard/summary

IMPORTANT SCHEMA GAPS — read before wiring this to the real frontend:
1. dim_customer has NO name/email field (only cust_id, age, gender, city,
   loyalty_segment, preferred_channel, registration_date). The contract's
   `recentSales[].customerName` expects a real name that doesn't exist in
   our data. This returns a placeholder ("Customer CUST-1001" / "Guest"
   for anonymous sales) instead of fabricating a fake name. Flag this to
   whoever owns the dashboard — either the contract needs to drop
   customerName, or Member 1/2's ingestion needs a name field that isn't
   currently in the raw CSVs either.
2. fact_sales has no load/created timestamp column, so "recordsProcessedToday"
   can't genuinely mean "today" — it's set to the total fact_sales row
   count instead. Same honesty note applies to pipelineStatus overall;
   it's a simplified placeholder, not derived from Airflow's real DAG
   run history (that would require querying Airflow's own metadata DB,
   not the warehouse — out of scope for this first pass).
3. "orders" in this contract is treated as one row = one order (fact_sales
   grain is actually one row per transaction line, not per order — if a
   single order has multiple line items in the real data, this overcounts
   orders). Flagging in case that distinction matters for a demo.
"""
from fastapi import APIRouter
from db import get_latest_sale_date, query, query_one

router = APIRouter()


@router.get("/dashboard/summary")
def dashboard_summary():
    # Anchored to the data's own latest date, not CURRENT_DATE — this dataset
    # is a fixed historical snapshot, and the real clock has since moved past
    # it, so CURRENT_DATE-based windows would always be empty. See
    # db.get_latest_sale_date's docstring.
    latest_date = get_latest_sale_date()

    revenue_row = query_one("""
        SELECT
            COALESCE(SUM(total_value), 0) AS total_revenue,
            COUNT(*) AS total_orders
        FROM fact_sales
    """)

    # Last 30 days vs the 30 days before that, for growth %.
    growth_row = query_one("""
        WITH anchor AS (SELECT %s::date AS latest_date),
        windows AS (
            SELECT
                SUM(CASE WHEN d.full_date > a.latest_date - 30 THEN fs.total_value ELSE 0 END) AS rev_current,
                SUM(CASE WHEN d.full_date <= a.latest_date - 30 AND d.full_date > a.latest_date - 60
                         THEN fs.total_value ELSE 0 END) AS rev_previous,
                COUNT(CASE WHEN d.full_date > a.latest_date - 30 THEN 1 END) AS orders_current,
                COUNT(CASE WHEN d.full_date <= a.latest_date - 30 AND d.full_date > a.latest_date - 60
                           THEN 1 END) AS orders_previous
            FROM fact_sales fs
            JOIN dim_date d ON fs.date_key = d.date_key
            CROSS JOIN anchor a
        )
        SELECT
            rev_current, rev_previous, orders_current, orders_previous,
            CASE WHEN rev_previous > 0
                 THEN ROUND(((rev_current - rev_previous) / rev_previous) * 100, 1)
                 ELSE 0 END AS revenue_growth_pct,
            CASE WHEN orders_previous > 0
                 THEN ROUND(((orders_current - orders_previous)::numeric / orders_previous) * 100, 1)
                 ELSE 0 END AS orders_growth_pct
        FROM windows
    """, (latest_date,))

    counts_row = query_one("""
        SELECT
            (SELECT COUNT(*) FROM dim_customer) AS total_customers,
            (SELECT COUNT(*) FROM dim_product) AS total_skus
    """)

    # Inventory: only the latest snapshot per store+product counts as "current".
    inventory_row = query_one("""
        WITH latest AS (
            SELECT store_key, product_key, stock_on_hand, reorder_point,
                   ROW_NUMBER() OVER (
                       PARTITION BY store_key, product_key
                       ORDER BY snapshot_date_key DESC
                   ) AS rn
            FROM fact_inventory
        )
        SELECT
            COALESCE(SUM(stock_on_hand), 0) AS total_inventory_units,
            COUNT(*) FILTER (WHERE stock_on_hand <= reorder_point) AS low_stock_items_count
        FROM latest WHERE rn = 1
    """)

    # Anchored to latest_date, same reason as the growth-% windows above.
    sales_trend = query("""
        WITH anchor AS (SELECT %s::date AS latest_date)
        SELECT
            TO_CHAR(d.full_date, 'Mon DD') AS date,
            SUM(fs.total_value) AS revenue,
            COUNT(*) AS orders
        FROM fact_sales fs
        JOIN dim_date d ON fs.date_key = d.date_key
        CROSS JOIN anchor a
        WHERE d.full_date > a.latest_date - 14
        GROUP BY d.full_date
        ORDER BY d.full_date
    """, (latest_date,))

    sales_by_store = query("""
        SELECT
            'STR-' || s.store_id AS "storeId",
            s.store_name AS "storeName",
            SUM(fs.total_value) AS revenue,
            COUNT(*) AS orders
        FROM fact_sales fs
        JOIN dim_store s ON fs.store_key = s.store_key
        GROUP BY s.store_id, s.store_name
        ORDER BY revenue DESC
        LIMIT 10
    """)

    top_products = query("""
        SELECT
            'SKU-' || p.sku_id AS "skuId",
            p.sku_name AS "productName",
            p.category,
            SUM(fs.quantity) AS "unitsSold",
            SUM(fs.total_value) AS "totalRevenue"
        FROM fact_sales fs
        JOIN dim_product p ON fs.product_key = p.product_key
        GROUP BY p.sku_id, p.sku_name, p.category
        ORDER BY "totalRevenue" DESC
        LIMIT 10
    """)

    total_rev = float(revenue_row["total_revenue"]) or 1  # guard divide-by-zero below
    sales_by_category_raw = query("""
        SELECT p.category, SUM(fs.total_value) AS revenue
        FROM fact_sales fs
        JOIN dim_product p ON fs.product_key = p.product_key
        GROUP BY p.category
        ORDER BY revenue DESC
    """)
    sales_by_category = [
        {**row, "percentage": round(float(row["revenue"]) / total_rev * 100, 1)}
        for row in sales_by_category_raw
    ]

    recent_sales = query("""
        SELECT
            'SAL-' || fs.sales_id AS "saleId",
            d.full_date || ' ' || TO_CHAR(NOW(), 'HH24:MI') AS date,
            COALESCE('Customer CUST-' || c.cust_id, 'Guest') AS "customerName",
            p.sku_name AS "productName",
            s.store_name AS "storeName",
            fs.total_value AS "totalAmount"
        FROM fact_sales fs
        JOIN dim_date d ON fs.date_key = d.date_key
        JOIN dim_product p ON fs.product_key = p.product_key
        JOIN dim_store s ON fs.store_key = s.store_key
        LEFT JOIN dim_customer c ON fs.customer_key = c.customer_key
        ORDER BY fs.sales_id DESC
        LIMIT 10
    """)

    low_stock_alerts = query("""
        WITH latest AS (
            SELECT store_key, product_key, stock_on_hand, reorder_point,
                   ROW_NUMBER() OVER (
                       PARTITION BY store_key, product_key
                       ORDER BY snapshot_date_key DESC
                   ) AS rn
            FROM fact_inventory
        )
        SELECT
            'SKU-' || p.sku_id AS "skuId",
            p.sku_name AS "productName",
            s.store_name AS "storeName",
            l.stock_on_hand AS "stockOnHand",
            l.reorder_point AS "reorderPoint"
        FROM latest l
        JOIN dim_product p ON l.product_key = p.product_key
        JOIN dim_store s ON l.store_key = s.store_key
        WHERE l.rn = 1 AND l.stock_on_hand <= l.reorder_point
        ORDER BY l.stock_on_hand ASC
        LIMIT 10
    """)

    return {
        "data": {
            "totalRevenue": float(revenue_row["total_revenue"]),
            "revenueGrowthPercentage": float(growth_row["revenue_growth_pct"]),
            "totalOrders": revenue_row["total_orders"],
            "ordersGrowthPercentage": float(growth_row["orders_growth_pct"]),
            "totalCustomers": counts_row["total_customers"],
            "totalSkus": counts_row["total_skus"],
            "totalInventoryUnits": inventory_row["total_inventory_units"],
            "lowStockItemsCount": inventory_row["low_stock_items_count"],
            "salesTrend": sales_trend,
            "salesByStore": sales_by_store,
            "topProducts": top_products,
            "salesByCategory": sales_by_category,
            "recentSales": recent_sales,
            "lowStockAlerts": low_stock_alerts,
            "pipelineStatus": {
                "status": "HEALTHY",
                "lastRunAt": None,  # TODO: wire to Airflow's metadata DB if needed later
                "recordsProcessedToday": revenue_row["total_orders"],  # see docstring note 2
                "errorRatePercentage": 0.0,
            },
        }
    }
