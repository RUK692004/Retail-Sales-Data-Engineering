# Data Transformation Rules & Specifications

## Overview
This document specifies the transformation and data cleaning rules applied to the ingested retail sales datasets for **Task 2 (Transformation Layer)** in the `Retail-Sales-Data-Engineering` project.

All transformations are implemented in Pandas within the modular `transformation` package and output clean CSV files to `data/transformed/`.

---

## Transformation Summary Table

| Dataset | Ingested Rows | Transformed Rows | Key Changes / Rules Applied |
| :--- | :---: | :---: | :--- |
| **sales** | 641,843 | 641,798 | Removed 45 exact duplicate rows (retained 1 copy). Standardized `date` to `datetime64`, `customer_id` to nullable integer (`Int64`), preserved 159,777 NULL customer IDs. |
| **customers** | 5,000 | 5,000 | Converted `registration_date` to `datetime64`. Standardized string whitespace across categorical attributes. |
| **inventory** | 8,735 | 8,735 | Converted `last_restock_date` and `snapshot_date` to `datetime64`. Verified `stock_on_hand`, `reorder_point`, and `safety_stock`. |
| **promotions** | 33 | 33 | Converted `start_date` and `end_date` to `datetime64`. Validated `start_date <= end_date` and discount percentages. |
| **skus** | 200 | 200 | Standardized numerical types (`unit_price`, `cost_price`). Verified `cost_price <= unit_price`. |
| **stores** | 50 | 50 | Converted `opening_date` to `datetime64`. Standardized string categories (`city`, `store_type`). |

---

## Detailed Transformation Decisions & Rules

### 1. Sales Dataset (`sales_ingested.csv` -> `sales_transformed.csv`)
- **Duplicate Handling:** Removed 45 exact duplicate rows where all column values matched identical transaction timestamps, store IDs, SKU IDs, quantities, prices, channels, and discounts. Retained exactly one copy.
- **NULL Customer IDs:** Preserved 159,777 NULL `customer_id` values (~24.90% of transactions). These represent guest / non-loyalty purchases. They are **not** replaced with `0`, `-1`, or placeholder IDs to avoid corrupting analytics.
- **Referential Integrity:** 100% of non-null `customer_id` values match `customers.cust_id`. 100% of `sku_id` match `skus.sku_id`. 100% of `store_id` match `stores.store_id`.
- **Value Validation:**
  - `total_value` equals `quantity * unit_price` across all 641,798 rows.
  - `unit_price` equals `sku.unit_price * (1 - discount_pct / 100)` across all rows.
  - Dates range from `2021-01-01` to `2025-10-31`. No invalid date strings found.
- **Data Types:**
  - `date`: `datetime64[ns]`
  - `store_id`: `int64`
  - `sku_id`: `int64`
  - `customer_id`: `Int64` (Pandas nullable integer)
  - `quantity`: `int64`
  - `unit_price`: `float64`
  - `total_value`: `float64`
  - `channel`: `string` (whitespace trimmed)
  - `discount_pct`: `float64`

### 2. Customers Dataset (`customers_ingested.csv` -> `customers_transformed.csv`)
- **Uniqueness & Integrity:** 5,000 unique customer IDs. 0 duplicates. 0 missing values.
- **Validations:** Ages range from 18 to 60 (all valid adults). Genders are restricted to `['Male', 'Female']`. Loyalty segments are restricted to `['Silver', 'Gold', 'Platinum']`.
- **Data Types:**
  - `cust_id`: `int64`
  - `age`: `int64`
  - `gender`, `city`, `loyalty_segment`, `preferred_channel`: `string` (whitespace trimmed)
  - `registration_date`: `datetime64[ns]`

### 3. Inventory Dataset (`inventory_ingested.csv` -> `inventory_transformed.csv`)
- **Integrity & Bounds:** 8,735 inventory snapshot records. All `store_id` and `sku_id` references exist in dimension tables. `stock_on_hand` (min 35, max 449), `reorder_point` (min 10, max 217), and `safety_stock` (min 5, max 108) are strictly non-negative.
- **Data Types:**
  - `store_id`, `sku_id`, `stock_on_hand`, `reorder_point`, `safety_stock`: `int64`
  - `last_restock_date`, `snapshot_date`: `datetime64[ns]`

### 4. Promotions Dataset (`promotions_ingested.csv` -> `promotions_transformed.csv`)
- **Validations:** 33 promo IDs, 0 duplicates. `start_date <= end_date` for all promotions. `discount_pct` ranges between 10% and 35%.
- **Data Types:**
  - `promo_id`, `discount_pct`: `int64`
  - `start_date`, `end_date`: `datetime64[ns]`
  - `promo_name`, `promo_type`: `string` (whitespace trimmed)

### 5. SKUs Dataset (`skus_ingested.csv` -> `skus_transformed.csv`)
- **Validations:** 200 unique SKUs. `cost_price <= unit_price` across all products. No missing values.
- **Data Types:**
  - `sku_id`: `int64`
  - `unit_price`, `cost_price`: `float64`
  - `sku_name`, `category`, `subcategory`, `brand`: `string` (whitespace trimmed)

### 6. Stores Dataset (`stores_ingested.csv` -> `stores_transformed.csv`)
- **Validations:** 50 stores in UAE (Abu Dhabi, Dubai, Sharjah).
- **Data Types:**
  - `store_id`: `int64`
  - `opening_date`: `datetime64[ns]`
  - `store_name`, `city`, `store_type`: `string` (whitespace trimmed)

---

## File Storage & Pipeline Execution

- **Input Location:** `data/processed/`
- **Output Location:** `data/transformed/`
- **Execution Command:**
  ```bash
  python -m transformation.transform
  ```
- **Test Command:**
  ```bash
  python -m pytest
  ```
