# Transformation Output Validation Report

## Execution Summary
- **Execution Date:** 2026-09-18
- **Pipeline Module:** `transformation.transform`
- **Input Directory:** `data/processed/`
- **Output Directory:** `data/transformed/`
- **Validation Status:** **PASSED ALL CHECKS**

---

## Output Datasets Overview

| Transformed Dataset | File Path | Row Count | Column Count | Exact Duplicates | Missing Values | Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Sales** | `data/transformed/sales_transformed.csv` | 641,798 | 9 | 0 | 159,777 (`customer_id`) | PASS |
| **Customers** | `data/transformed/customers_transformed.csv` | 5,000 | 7 | 0 | 0 | PASS |
| **Inventory** | `data/transformed/inventory_transformed.csv` | 8,735 | 7 | 0 | 0 | PASS |
| **Promotions** | `data/transformed/promotions_transformed.csv` | 33 | 6 | 0 | 0 | PASS |
| **SKUs** | `data/transformed/skus_transformed.csv` | 200 | 7 | 0 | 0 | PASS |
| **Stores** | `data/transformed/stores_transformed.csv` | 50 | 5 | 0 | 0 | PASS |

---

## Referential Integrity Validation

| Reference Link | Parent Dataset | Primary Key | Foreign Key in Sales/Inventory | Invalid References | Status |
| :--- | :--- | :--- | :--- | :---: | :---: |
| Sales -> Customers | `customers_transformed.csv` | `cust_id` | `sales.customer_id` | **0** | PASS |
| Sales -> SKUs | `skus_transformed.csv` | `sku_id` | `sales.sku_id` | **0** | PASS |
| Sales -> Stores | `stores_transformed.csv` | `store_id` | `sales.store_id` | **0** | PASS |
| Inventory -> Stores | `stores_transformed.csv` | `store_id` | `inventory.store_id` | **0** | PASS |
| Inventory -> SKUs | `skus_transformed.csv` | `sku_id` | `inventory.sku_id` | **0** | PASS |

---

## Key Data Quality Verification Results

1. **Sales Duplicate Removal:**
   - Pre-transformation sales rows: `641,843`
   - Exact duplicate rows identified & removed: `45`
   - Transformed sales rows: `641,798`

2. **Preservation of Guest Purchases:**
   - 159,777 transactions have `NULL` `customer_id` (~24.90%).
   - All nulls are preserved as standard `NaN`/`NULL` without substitution.

3. **Numeric & Financial Integrity:**
   - `total_value == quantity * unit_price`: 100% match across 641,798 rows.
   - `unit_price == sku.unit_price * (1 - discount_pct / 100)`: 100% match across 641,798 rows.
   - `cost_price <= unit_price`: 100% match across 200 SKUs.

4. **Date Format Standardization:**
   - All dates converted to standard ISO `YYYY-MM-DD` format on persistence.

5. **Automated Unit Tests:**
   - Pytest execution: **15 passed out of 15 tests (100%)**.
