# retail_sales_dw -- PostgreSQL Data Warehouse

**Member 3 -- Database / Warehouse Layer**

This directory contains the complete PostgreSQL star-schema data warehouse for
the Retail Sales Data Engineering project.

---

## Directory structure

```
database/
├── schema/
│   └── create_tables.sql    # DDL: all 7 tables, constraints, indexes
├── seeds/
│   └── seed_data.sql        # Seed: dim_date spine only
├── queries/
│   └── test_queries.sql     # Validation + business analytics queries
├── load_data.py             # Python loader: all 6 CSVs -> PostgreSQL
└── README.md                # This file
```

---

## Star schema

```
                       dim_date
                          |
          +---------------+---------------+
          |               |               |
      fact_sales    fact_inventory        |
          |               |               |
   +------+------+    +---+---+           |
   |      |      |    |       |           |
dim_store  dim_product  dim_store  dim_product
   |
dim_customer

dim_promotion  (standalone -- no FK from fact_sales)
```

### Tables

| Table | Type | Grain / Notes |
|---|---|---|
| `dim_date` | Dimension | One row per calendar day (2021-01-01 to 2025-12-31) |
| `dim_customer` | Dimension | One row per customer; business key `cust_id` |
| `dim_product` | Dimension | One row per SKU; business key `sku_id` |
| `dim_store` | Dimension | One row per store; business key `store_id` |
| `dim_promotion` | Dimension | One row per promotion; no FK from fact tables |
| `fact_sales` | Fact | One row per sales transaction line; surrogate PK `sales_id` |
| `fact_inventory` | Fact | One row per store x SKU x snapshot_date; surrogate PK `inventory_id` |

---

## Primary keys, foreign keys & indexes

### dim_date
- PK: `date_key` (YYYYMMDD integer)
- Unique: `full_date`
- Indexes: `(year, month)`, `full_date`

### dim_customer
- PK: `customer_key` (surrogate, SERIAL)
- Unique: `cust_id` (business key)
- Indexes: `city`, `loyalty_segment`

### dim_product
- PK: `product_key` (surrogate, SERIAL)
- Unique: `sku_id` (business key)
- Indexes: `category`, `brand`

### dim_store
- PK: `store_key` (surrogate, SERIAL)
- Unique: `store_id` (business key)
- Indexes: `city`, `store_type`

### dim_promotion
- PK: `promo_id` (natural key from source)
- No FK to or from any fact table
- Loaded from `promotions_ingested.csv` by `load_data.py` (single source of truth)

### fact_sales
- PK: `sales_id` (BIGSERIAL -- warehouse-generated)
- FKs: `date_key -> dim_date`, `store_key -> dim_store`,
  `product_key -> dim_product`, `customer_key -> dim_customer` (nullable)
- **No FK to `dim_promotion`** -- `promo_id` is absent from `sales_ingested.csv`
- Indexes: `date_key`, `store_key`, `product_key`, `customer_key`,
  `channel`, `(date_key, store_key)`

### fact_inventory
- PK: `inventory_id` (BIGSERIAL -- warehouse-generated)
- Unique: `(store_key, product_key, snapshot_date_key)` -- enforces grain
- FKs: `store_key -> dim_store`, `product_key -> dim_product`,
  `snapshot_date_key -> dim_date`
- Indexes: `store_key`, `product_key`, `snapshot_date_key`,
  `(store_key, product_key)`

---

## Prerequisites

```bash
# Python dependencies
pip install psycopg2-binary

# PostgreSQL: create the target database
createdb retail_sales_dw
# or via psql:
# CREATE DATABASE retail_sales_dw;
```

---

## Environment variables

Never hardcode passwords. Set these before running any load command.

**Windows (PowerShell)**:
```powershell
$env:DB_HOST     = "localhost"
$env:DB_PORT     = "5432"
$env:DB_NAME     = "retail_sales_dw"
$env:DB_USER     = "postgres"
$env:DB_PASSWORD = "your_password_here"
```

**Linux / macOS / WSL**:
```bash
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=retail_sales_dw
export DB_USER=postgres
export DB_PASSWORD=your_password_here
```

Optional overrides:
```powershell
$env:INPUT_DIR  = "path\to\csv_directory"   # default: data/processed
$env:BATCH_SIZE = "10000"                   # default: 5000
```

---

## Full run order

```
Step 1  Create schema        psql ... -f database/schema/create_tables.sql
Step 2  Seed dim_date        psql ... -f database/seeds/seed_data.sql
Step 3  Load all 6 CSVs      python database/load_data.py
Step 4  Run validation       psql ... -f database/queries/test_queries.sql
```

---

## Step 1 -- Create the schema

```bash
psql -h localhost -U postgres -d retail_sales_dw \
     -f database/schema/create_tables.sql
```

The script is **safe to re-run** -- all objects use `CREATE TABLE IF NOT EXISTS`
and `CREATE INDEX IF NOT EXISTS`.

---

## Step 2 -- Seed dim_date

```bash
psql -h localhost -U postgres -d retail_sales_dw \
     -f database/seeds/seed_data.sql
```

Generates a continuous date spine from 2021-01-01 to 2025-12-31 using
`generate_series`.  Uses `INSERT ... ON CONFLICT DO NOTHING` so it is
**idempotent**.

`dim_promotion` is **not** seeded here.  It is loaded entirely from
`promotions_ingested.csv` by `load_data.py` (see Step 3).

---

## Step 3 -- Load all six CSV datasets

```powershell
# Set env vars first (see Environment variables section above)
python database/load_data.py
```

### CSV files loaded

| CSV file | Target table | Strategy |
|---|---|---|
| `customers_ingested.csv` | `dim_customer` | Upsert on `cust_id` |
| `skus_ingested.csv` | `dim_product` | Upsert on `sku_id` |
| `stores_ingested.csv` | `dim_store` | Upsert on `store_id` |
| `promotions_ingested.csv` | `dim_promotion` | Upsert on `promo_id` |
| `sales_ingested.csv` | `fact_sales` | **Full refresh** (see below) |
| `inventory_ingested.csv` | `fact_inventory` | Upsert on grain key |

### Repeated-load / reload behavior

**Dimension tables** (`dim_customer`, `dim_product`, `dim_store`, `dim_promotion`)
Use `INSERT ... ON CONFLICT (business_key) DO UPDATE`.  Running the loader
multiple times updates existing rows in-place and inserts any new ones.

**`fact_inventory`**
Uses `INSERT ... ON CONFLICT (store_key, product_key, snapshot_date_key) DO UPDATE`.
The grain UNIQUE constraint makes this naturally idempotent.

**`fact_sales` -- FULL REFRESH**
`sales_ingested.csv` contains no reliable transaction identifier that could
serve as a natural conflict key.  To prevent duplicate rows on re-runs, the
loader **truncates `fact_sales` before each load** and then re-inserts all
rows from the CSV.

- Only `fact_sales` is truncated; all dimension tables are unaffected.
- `fact_sales` has no child FK references pointing out of it, so a plain
  `TRUNCATE` (without `CASCADE`) is safe.
- If the upstream pipeline later provides a stable `transaction_id` column,
  remove the truncation step and switch to `INSERT ... ON CONFLICT (transaction_id)
  DO UPDATE` for true incremental loads.

---

## Step 4 -- Run validation queries

```bash
psql -h localhost -U postgres -d retail_sales_dw \
     -f database/queries/test_queries.sql
```

Or run individual sections in psql / pgAdmin / DBeaver.

### Query sections in test_queries.sql

| Section | Queries | Purpose |
|---|---|---|
| 1 | Q1.1 | Row counts for all tables |
| 2 | Q2.1-Q2.3 | dim_date integrity (no gaps, weekend flag, sample) |
| 3 | Q3.1-Q3.4 | Dimension cardinality checks |
| 4 | Q4.1-Q4.8 | fact_sales nullability, range, orphaned-FK checks |
| 5 | Q5.1-Q5.2 | fact_inventory grain uniqueness + below-reorder SKUs |
| 6 | Q6.1-Q6.8 | Business analytics (revenue trends, top SKUs, inventory health) |

---

## Switching to Member 2 transformed output

When Member 2 transformation pipeline is complete, set `INPUT_DIR`:

```powershell
$env:INPUT_DIR = "transformation\output"   # adjust path as needed
python database/load_data.py
```

No code changes are required -- the loader is fully path-configurable.

---

## Data contract notes

| Constraint | Detail |
|---|---|
| `customer_id` in sales | May be NULL (walk-in / anonymous transactions) |
| No promo FK in fact_sales | `sales_ingested.csv` has no `promo_id` column |
| Sales PK | Warehouse-generated `sales_id` (BIGSERIAL) |
| `total_value` in fact_sales | Source-recorded value (quantity * unit_price as in the source system); `discount_pct` is stored as a separate column |
| Inventory grain | Enforced via UNIQUE `(store_key, product_key, snapshot_date_key)` |
| Passwords | Never hardcoded -- always read from `DB_PASSWORD` env var |
| dim_promotion source | Loaded from `promotions_ingested.csv` only; no hardcoded fallback |