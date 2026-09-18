# Transformation Report

## Overview

This report documents the transformation pipeline implemented for the
Retail Sales Data Engineering project (Member 2 — Step 3).

The pipeline reads all six processed datasets from `data/processed/`,
applies documented cleaning rules, and writes clean CSV files to
`data/transformed/`.

---

## Input Datasets

| Dataset | File | Rows | Columns |
|:--------|:-----|-----:|--------:|
| Sales | `data/processed/sales_ingested.csv` | 641,843 | 9 |
| Customers | `data/processed/customers_ingested.csv` | 5,000 | 7 |
| Inventory | `data/processed/inventory_ingested.csv` | 8,735 | 7 |
| Promotions | `data/processed/promotions_ingested.csv` | 33 | 6 |
| SKUs | `data/processed/skus_ingested.csv` | 200 | 7 |
| Stores | `data/processed/stores_ingested.csv` | 50 | 5 |

---

## Output Datasets

| Dataset | File | Rows |
|:--------|:-----|-----:|
| Sales | `data/transformed/sales_transformed.csv` | 641,798 |
| Customers | `data/transformed/customers_transformed.csv` | 5,000 |
| Inventory | `data/transformed/inventory_transformed.csv` | 8,735 |
| Promotions | `data/transformed/promotions_transformed.csv` | 33 |
| SKUs | `data/transformed/skus_transformed.csv` | 200 |
| Stores | `data/transformed/stores_transformed.csv` | 50 |

---

## Transformations Applied

### Sales

| Rule | Action |
|:-----|:-------|
| Exact duplicate rows | Removed 45 duplicate rows; retained 1 copy of each |
| NULL `customer_id` | Preserved as-is — not replaced with 0 or -1 |
| `date` | Converted `object` → `datetime64[ns]` |
| `customer_id` | Cast to Pandas nullable `Int64` (supports NaN) |
| `store_id`, `sku_id` | Cast to `int64` |
| `quantity` | Cast to `int64` |
| `unit_price`, `total_value` | Cast to `float64` |
| `discount_pct` | Cast to `float64` |
| `channel` | String whitespace stripped |
| `total_value` | NOT recalculated — already validated (100% consistent) |
| Column order | Original order preserved |

### Customers

| Rule | Action |
|:-----|:-------|
| `cust_id` | Cast to `int64` |
| `age` | Cast to `int64` |
| `registration_date` | Converted `object` → `datetime64[ns]` |
| `gender`, `city`, `loyalty_segment`, `preferred_channel` | String whitespace stripped |
| Column order | Original order preserved |

### Inventory

| Rule | Action |
|:-----|:-------|
| `store_id`, `sku_id` | Cast to `int64` |
| `stock_on_hand`, `reorder_point`, `safety_stock` | Cast to `int64` |
| `last_restock_date`, `snapshot_date` | Converted `object` → `datetime64[ns]` |
| Column order | Original order preserved |

### Promotions

| Rule | Action |
|:-----|:-------|
| `promo_id`, `discount_pct` | Cast to `int64` |
| `start_date`, `end_date` | Converted `object` → `datetime64[ns]` |
| `promo_name`, `promo_type` | String whitespace stripped |
| Column order | Original order preserved |

### SKUs

| Rule | Action |
|:-----|:-------|
| `sku_id` | Cast to `int64` |
| `unit_price`, `cost_price` | Cast to `float64` |
| `sku_name`, `category`, `subcategory`, `brand` | String whitespace stripped |
| Column order | Original order preserved |

### Stores

| Rule | Action |
|:-----|:-------|
| `store_id` | Cast to `int64` |
| `opening_date` | Converted `object` → `datetime64[ns]` |
| `store_name`, `city`, `store_type` | String whitespace stripped |
| Column order | Original order preserved |

---

## Sales Duplicate Handling

| Metric | Value |
|:-------|------:|
| Input rows (sales_ingested.csv) | 641,843 |
| Exact duplicate rows identified | 45 |
| Duplicate rows removed | 45 |
| Output rows (sales_transformed.csv) | 641,798 |

The duplicates were exact across all 9 columns (date, store_id, sku_id, customer_id,
quantity, unit_price, total_value, channel, discount_pct). One confirmed example:

| date | store_id | sku_id | customer_id | quantity | unit_price | total_value | channel | discount_pct |
|:-----|:--------:|:------:|:-----------:|:--------:|:----------:|:-----------:|:-------:|:------------:|
| 2025-05-14 | 31 | 1176 | NULL | 3 | 6.83 | 20.49 | MobileApp | 0.0 |

---

## Null Handling

| Column | Dataset | Null Count | Action |
|:-------|:--------|----------:|:-------|
| `customer_id` | sales | 159,777 | **Preserved as NULL** — represents valid guest/anonymous purchases |

No other null values were found across any dataset.

`customer_id` NULL values were **not** replaced with 0, -1, or any placeholder.
The column uses Pandas nullable `Int64` type to distinguish real integer IDs from
genuine missing values.

---

## Data Type Standardization

### Date Columns

| Column | Dataset | Before | After |
|:-------|:--------|:-------|:------|
| `date` | sales | `object` | `datetime64[ns]` |
| `registration_date` | customers | `object` | `datetime64[ns]` |
| `last_restock_date` | inventory | `object` | `datetime64[ns]` |
| `snapshot_date` | inventory | `object` | `datetime64[ns]` |
| `start_date` | promotions | `object` | `datetime64[ns]` |
| `end_date` | promotions | `object` | `datetime64[ns]` |
| `opening_date` | stores | `object` | `datetime64[ns]` |

Dates are stored as `YYYY-MM-DD` strings in the output CSV files.

### Numeric Columns

| Column | Dataset | Type |
|:-------|:--------|:-----|
| `store_id`, `sku_id`, `quantity` | sales | `int64` |
| `customer_id` | sales | `Int64` (nullable) |
| `unit_price`, `total_value`, `discount_pct` | sales | `float64` |
| `cust_id`, `age` | customers | `int64` |
| `store_id`, `sku_id`, `stock_on_hand`, `reorder_point`, `safety_stock` | inventory | `int64` |
| `promo_id`, `discount_pct` | promotions | `int64` |
| `sku_id` | skus | `int64` |
| `unit_price`, `cost_price` | skus | `float64` |
| `store_id` | stores | `int64` |

---

## Validation Results

### Row Counts

| Dataset | Rows In | Rows Out | Difference |
|:--------|--------:|---------:|:----------:|
| sales | 641,843 | 641,798 | -45 (duplicates removed) |
| customers | 5,000 | 5,000 | 0 |
| inventory | 8,735 | 8,735 | 0 |
| promotions | 33 | 33 | 0 |
| skus | 200 | 200 | 0 |
| stores | 50 | 50 | 0 |

### Duplicate Counts (Output)

| Dataset | Exact Duplicates | Status |
|:--------|:----------------:|:------:|
| sales | **0** | PASS |
| customers | 0 | PASS |
| inventory | 0 | PASS |
| promotions | 0 | PASS |
| skus | 0 | PASS |
| stores | 0 | PASS |

### Null Counts (Output)

| Dataset | Column | Nulls | Note |
|:--------|:-------|------:|:-----|
| sales | `customer_id` | 159,777 | **Intentionally preserved** |
| All others | — | 0 | No nulls |

### Referential Integrity Results

| Check | Invalid References | Status |
|:------|:-----------------:|:------:|
| `sales.customer_id` → `customers.cust_id` (non-null only) | 0 | PASS |
| `sales.sku_id` → `skus.sku_id` | 0 | PASS |
| `sales.store_id` → `stores.store_id` | 0 | PASS |
| `inventory.store_id` → `stores.store_id` | 0 | PASS |
| `inventory.sku_id` → `skus.sku_id` | 0 | PASS |

### Numeric Validation Results (Sales)

| Check | Result | Status |
|:------|:------:|:------:|
| Negative `quantity` | 0 | PASS |
| Negative `unit_price` | 0 | PASS |
| Negative `total_value` | 0 | PASS |
| `total_value` = `quantity × unit_price` mismatches | 0 | PASS |
| Invalid `discount_pct` (outside {0,10,15,20,25,30,35}) | 0 | PASS |

---

## How to Run the Transformation

From the repository root:

```bash
python transformation/transform.py
```

To run the test suite:

```bash
python -m pytest
```

To run only transformation tests:

```bash
python -m pytest tests/test_transform.py -v
```

---

## Pipeline Architecture

```
data/processed/          transformation/
    |                        |
    |  load_data()           |
    +----------------------->|
                             |
                     transform_sales()
                     transform_customers()
                     transform_inventory()
                     transform_promotions()
                     transform_skus()
                     transform_stores()
                             |
                   validate_transformed_data()
                             |
                   save_transformed_data()
                             |
                             v
                    data/transformed/
```

The pipeline is structured as modular, importable functions suitable for
wrapping in an Apache Airflow DAG (`run_transformation_pipeline()` is the
single callable entry point).

---

## Notes and Manual Review Items

None. All data quality findings from Step 2 were addressed by the transformation
rules above. No data was deleted beyond the 45 verified exact duplicates in sales.
