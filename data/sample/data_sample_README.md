# Retail Sales Data Engineering Pipeline - Member 2 Transformation Sample Dataset

## Overview
This directory (`data/sample/`) contains a small, realistic sample dataset specifically curated for **Member 2 (Transformation)**. The purpose of this dataset is to allow Member 2 to load these files into Pandas DataFrames and develop, test, and refine transformation functions independently before working with the full-scale production datasets.

---

## Pipeline Workflow
```
Original CSV files
        ↓
Sample transformation-input CSVs (data/sample/)
        ↓
Pandas DataFrames
        ↓
Member 2 transformation functions (transform_sales, transform_customers, etc.)
        ↓
Processed DataFrames
        ↓
Member 3 PostgreSQL loading
```

---

## Source Files Used & Selection Methodology
1. **`sales_transform_input.csv`**:
   - **Source**: `bm_sales.csv` (641,843 total rows)
   - **Method**: Randomly sampled **5,000 records** using `random_state=42`.
   - **Fields Kept**: `date`, `store_id`, `sku_id`, `customer_id`, `quantity`, `unit_price`, `total_value`, `channel`, `discount_pct`.
   - **Notes**: Uncleaned raw data. Preserves missing `customer_id` values (1,287 missing values in sample) and any natural duplicates. No business transformations or calculations applied.

2. **`customers_transform_input.csv`**:
   - **Source**: `bm_customers.csv` (5,000 total rows)
   - **Method**: Filtered to include all customer records referenced by non-null `customer_id` values in the sales sample.
   - **Fields Kept**: `cust_id`, `age`, `gender`, `city`, `loyalty_segment`, `preferred_channel`, `registration_date`.
   - **Row Count**: 2,595 records.

3. **`skus_transform_input.csv`**:
   - **Source**: `bm_skus.csv` (200 total rows)
   - **Method**: Filtered to include all SKUs referenced by the sales sample.
   - **Fields Kept**: `sku_id`, `sku_name`, `category`, `subcategory`, `unit_price`, `cost_price`, `brand`.
   - **Row Count**: 200 records (all SKUs were referenced in the 5,000 sales sample).

4. **`stores_transform_input.csv`**:
   - **Source**: `bm_stores.csv` (50 total rows)
   - **Method**: Filtered to include all stores referenced by the sales sample.
   - **Fields Kept**: `store_id`, `store_name`, `city`, `store_type`, `opening_date`.
   - **Column Mapping**: Source columns match expected names directly (`store_id`, `store_name`, `city`, `store_type`, `opening_date`). No column renaming needed.
   - **Row Count**: 50 records.

5. **`inventory_transform_input.csv`**:
   - **Source**: `bm_inventory.csv` (8,735 total rows)
   - **Method**: Filtered for inventory records matching the stores and SKUs present in the sales sample.
   - **Fields Kept**: `store_id`, `sku_id`, `stock_on_hand`, `reorder_point`, `safety_stock`, `last_restock_date`, `snapshot_date`.
   - **Row Count**: 8,735 records (snapshot date: `2025-10-31`).

6. **`promotions_transform_input.csv`**:
   - **Source**: `bm_promotions.csv` (33 total rows)
   - **Method**: Preserved all available promotion records. Note: Sales records do not have a reliable `promo_id`; no artificial relationship or assignment has been created.
   - **Fields Kept**: `promo_id`, `promo_name`, `start_date`, `end_date`, `discount_pct`, `promo_type`.
   - **Row Count**: 33 records.

---

## Dataset Summary & File Row Counts
| File Name | Description | Row Count | Key Identifier |
| :--- | :--- | :--- | :--- |
| `sales_transform_input.csv` | Driving sales transaction sample | 5,000 | `date`, `store_id`, `sku_id` |
| `customers_transform_input.csv` | Customer dimension sample | 2,595 | `cust_id` |
| `skus_transform_input.csv` | SKU/Product dimension sample | 200 | `sku_id` |
| `stores_transform_input.csv` | Store dimension sample | 50 | `store_id` |
| `inventory_transform_input.csv` | Store-SKU inventory levels | 8,735 | `store_id`, `sku_id` |
| `promotions_transform_input.csv` | Promotion reference table | 33 | `promo_id` |

---

## Referential Integrity & Validation
- **Sales → Customers**: PASS (Every non-null `sales.customer_id` exists in `customers_transform_input.cust_id`).
- **Sales → SKUs**: PASS (Every `sales.sku_id` exists in `skus_transform_input.sku_id`).
- **Sales → Stores**: PASS (Every `sales.store_id` exists in `stores_transform_input.store_id`).
- **Inventory Relationships**: PASS/INFO (Inventory records correspond exactly to the sampled stores and SKUs).

---

## Usage Guide for Member 2
Member 2 can load these files into Pandas DataFrames for transformation development:

```python
import pandas as pd

# Load input samples
sales_df = pd.read_csv("data/sample/sales_transform_input.csv")
customers_df = pd.read_csv("data/sample/customers_transform_input.csv")
skus_df = pd.read_csv("data/sample/skus_transform_input.csv")
stores_df = pd.read_csv("data/sample/stores_transform_input.csv")
inventory_df = pd.read_csv("data/sample/inventory_transform_input.csv")
promotions_df = pd.read_csv("data/sample/promotions_transform_input.csv")

# Example transformation function stubs to implement:
# processed_sales = transform_sales(sales_df)
# processed_customers = transform_customers(customers_df)
# processed_skus = transform_skus(skus_df)
# processed_stores = transform_stores(stores_df)
# processed_inventory = transform_inventory(inventory_df)
# processed_promotions = transform_promotions(promotions_df)
```
