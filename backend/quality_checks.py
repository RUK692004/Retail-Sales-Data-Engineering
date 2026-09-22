"""
Live data-quality checks for /api/data-quality/*.

These are NOT read from a persisted pipeline run — dags/retail_sales_pipeline.py's
run_quality_checks task doesn't write structured results anywhere queryable yet
(just Airflow logs). Rather than block these endpoints on that, or fake results
from data that doesn't exist, the checks below run live against warehouse-postgres
(and the transformed sales CSV, mounted read-only into this container) on every
request. Same 4 checks originally scoped for the DAG task:
  1. Row count: fact_sales vs. the transformed sales CSV it was loaded from.
  2. Null customer_key rate (>50% is suspicious — see NULL_CHECK below).
  3. Exact-duplicate transactions in fact_sales.
  4. Dimension referential sanity: dim_customer/dim_product/dim_store each have
     at least as many rows as the distinct business keys seen in the sales CSV.

SCHEMA / DATA_TYPE categories from the contract's sample are intentionally not
implemented — ingestion/validator.py already enforces those upstream of this
warehouse, and Postgres CHECK/NOT NULL constraints enforce them again at load
time. There's nothing left to check post-load for those two categories.

Severity is binary CRITICAL per finding — these are real integrity checks with
a pass/fail outcome, not scored on a WARNING/INFO scale.
"""
import csv
import os

from db import query, query_one

SALES_CSV_PATH = os.getenv("SALES_TRANSFORMED_CSV", "/app/data/transformed/sales_transformed.csv")

NULL_CUSTOMER_KEY_THRESHOLD_PCT = 50.0
ROW_COUNT_TOLERANCE_PCT = 1.0


def _load_source_sales_keys() -> dict:
    """One pass over the transformed sales CSV: row count + distinct business keys."""
    cust_ids, sku_ids, store_ids = set(), set(), set()
    row_count = 0
    with open(SALES_CSV_PATH, newline="") as f:
        for row in csv.DictReader(f):
            row_count += 1
            if row["customer_id"]:
                cust_ids.add(row["customer_id"])
            sku_ids.add(row["sku_id"])
            store_ids.add(row["store_id"])
    return {"row_count": row_count, "cust_ids": cust_ids, "sku_ids": sku_ids, "store_ids": store_ids}


def check_row_count(source: dict) -> dict:
    fact_count = query_one("SELECT COUNT(*) AS n FROM fact_sales")["n"]
    source_count = source["row_count"]
    diff_pct = abs(fact_count - source_count) / source_count * 100 if source_count else 0.0
    passed = diff_pct <= ROW_COUNT_TOLERANCE_PCT
    return {
        "category": "ROW_COUNT",
        "name": "Row Count Reconciliation",
        "description": "fact_sales row count vs. the transformed sales CSV it was loaded from.",
        "totalEvaluated": 1,
        "passedCount": 1 if passed else 0,
        "failedCount": 0 if passed else 1,
        "passRatePercentage": 100.0 if passed else 0.0,
        "status": "PASSED" if passed else "FAILED",
        "detail": f"fact_sales={fact_count}, source={source_count}, diff={diff_pct:.2f}% (tolerance {ROW_COUNT_TOLERANCE_PCT}%)",
        "issues": [] if passed else [{
            "category": "ROW_COUNT",
            "ruleViolated": "ROW_COUNT_WITHIN_TOLERANCE",
            "targetTable": "fact_sales",
            "targetColumn": None,
            "recordIdentifier": "AGGREGATE",
            "severity": "CRITICAL",
            "invalidValue": f"{diff_pct:.2f}% diff",
            "recommendation": "fact_sales row count diverges from the source CSV by more than "
                               f"{ROW_COUNT_TOLERANCE_PCT}% — rows were likely silently dropped "
                               "during load_database. Check load_data.py's insert/lookup logic.",
        }],
    }


def check_null_customer_key() -> dict:
    row = query_one("""
        SELECT COUNT(*) AS total,
               COUNT(*) FILTER (WHERE customer_key IS NULL) AS null_count
        FROM fact_sales
    """)
    total, null_count = row["total"], row["null_count"]
    rate = (null_count / total * 100) if total else 0.0
    passed = rate <= NULL_CUSTOMER_KEY_THRESHOLD_PCT
    return {
        "category": "NULL_CHECK",
        "name": "Null customer_key Rate",
        "description": "customer_key is nullable for anonymous/walk-in sales, but a rate above "
                        f"{NULL_CUSTOMER_KEY_THRESHOLD_PCT:.0f}% likely means the customer lookup "
                        "in load_database is failing rather than sales genuinely being anonymous.",
        "totalEvaluated": total,
        "passedCount": total - null_count,
        "failedCount": 0 if passed else null_count,
        "passRatePercentage": round(100 - rate, 2),
        "status": "PASSED" if passed else "FAILED",
        "detail": f"{null_count}/{total} rows ({rate:.2f}%) have a null customer_key "
                  f"(threshold {NULL_CUSTOMER_KEY_THRESHOLD_PCT:.0f}%)",
        "issues": [] if passed else [{
            "category": "NULL_CHECK",
            "ruleViolated": "NULL_CUSTOMER_KEY_RATE_BELOW_THRESHOLD",
            "targetTable": "fact_sales",
            "targetColumn": "customer_key",
            "recordIdentifier": "AGGREGATE",
            "severity": "CRITICAL",
            "invalidValue": f"{rate:.2f}% null",
            "recommendation": "Null customer_key rate exceeds the anonymous-sale threshold — "
                               "check the cust_id-to-customer_key lookup in load_database.",
        }],
    }


def check_duplicates() -> dict:
    total = query_one("SELECT COUNT(*) AS n FROM fact_sales WHERE customer_key IS NOT NULL")["n"]
    groups = query("""
        SELECT
            ARRAY_AGG(sales_id ORDER BY sales_id) AS sales_ids,
            date_key, store_key, product_key, customer_key, quantity, unit_price,
            COUNT(*) AS n
        FROM fact_sales
        WHERE customer_key IS NOT NULL
        GROUP BY date_key, store_key, product_key, customer_key, quantity, unit_price
        HAVING COUNT(*) > 1
        ORDER BY n DESC
    """)
    extra_rows = sum(g["n"] - 1 for g in groups)
    passed = len(groups) == 0
    issues = [{
        "category": "DUPLICATE",
        "ruleViolated": "EXACT_DUPLICATE_TRANSACTION",
        "targetTable": "fact_sales",
        "targetColumn": None,
        "recordIdentifier": ",".join(f"SAL-{sid}" for sid in g["sales_ids"]),
        "severity": "CRITICAL",
        "invalidValue": f"{g['n']} identical rows (date_key={g['date_key']}, store_key={g['store_key']}, "
                         f"product_key={g['product_key']}, customer_key={g['customer_key']}, "
                         f"qty={g['quantity']}, price={g['unit_price']})",
        "recommendation": "Same customer/product/store/date/quantity/price appears more than once — "
                           "likely a duplicate insert from load_database. Verify truncate-before-reload "
                           "actually ran, and consider deleting the extra row(s).",
    } for g in groups]
    return {
        "category": "DUPLICATE",
        "name": "Duplicate Transaction Check",
        "description": "Exact-duplicate (store, product, customer, date, quantity, price) rows in "
                        "fact_sales, among rows with a known customer_key. Anonymous (null "
                        "customer_key) rows are excluded — SQL GROUP BY treats NULLs as equal, so "
                        "two different walk-in sales with the same SKU/qty/price/day would otherwise "
                        "false-positive as duplicates.",
        "totalEvaluated": total,
        "passedCount": total - extra_rows,
        "failedCount": extra_rows,
        "passRatePercentage": round((total - extra_rows) / total * 100, 2) if total else 100.0,
        "status": "PASSED" if passed else "FAILED",
        "detail": f"{len(groups)} duplicate group(s), {extra_rows} extra row(s)",
        "issues": issues,
    }


def _referential_check(category: str, name: str, dim_table: str, dim_business_key_col: str,
                        source_ids: set, id_prefix: str) -> dict:
    dim_count = query_one(f"SELECT COUNT(*) AS n FROM {dim_table}")["n"]
    dim_rows = query(f"SELECT {dim_business_key_col} AS bk FROM {dim_table}")
    dim_keys = {str(r["bk"]) for r in dim_rows}
    missing = sorted(source_ids - dim_keys, key=lambda x: (len(x), x))
    passed = len(missing) == 0
    total_evaluated = len(source_ids)
    issues = [{
        "category": category,
        "ruleViolated": "FOREIGN_KEY_EXISTS",
        "targetTable": dim_table,
        "targetColumn": dim_business_key_col,
        "recordIdentifier": f"{id_prefix}-{bk}",
        "severity": "CRITICAL",
        "invalidValue": bk,
        "recommendation": f"{id_prefix}-{bk} appears in sales_transformed.csv but has no matching row "
                           f"in {dim_table} — check load_database's dimension-load step for this key.",
    } for bk in missing]
    return {
        "category": category,
        "name": name,
        "description": f"{dim_table} should have at least one row for every distinct business key "
                        "seen in the transformed sales CSV — a missing one means load_database "
                        "silently skipped inserting that dimension row.",
        "totalEvaluated": total_evaluated,
        "passedCount": total_evaluated - len(missing),
        "failedCount": len(missing),
        "passRatePercentage": round((total_evaluated - len(missing)) / total_evaluated * 100, 2) if total_evaluated else 100.0,
        "status": "PASSED" if passed else "FAILED",
        "detail": f"{dim_table}: {dim_count} rows in dimension, {total_evaluated} distinct keys "
                  f"in source, {len(missing)} missing",
        "issues": issues,
    }


def run_all_checks() -> list[dict]:
    source = _load_source_sales_keys()
    return [
        check_row_count(source),
        check_null_customer_key(),
        check_duplicates(),
        _referential_check("CUSTOMER_FK", "Customer Referential Sanity", "dim_customer", "cust_id",
                            source["cust_ids"], "CUST"),
        _referential_check("SKU_FK", "Product Referential Sanity", "dim_product", "sku_id",
                            source["sku_ids"], "SKU"),
        _referential_check("STORE_FK", "Store Referential Sanity", "dim_store", "store_id",
                            source["store_ids"], "STORE"),
    ]
