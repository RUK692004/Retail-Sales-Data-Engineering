# Member 2 handoff: validated ingestion data

## Architecture

```text
Raw CSV files
    -> Member 1 ingestion and validation
    -> data/processed/ safe CSV copies OR in-memory dictionary
    -> Member 2 transformation functions
```

`run_ingestion()` reads the six files in `data/raw/`, validates their schema and
basic health, saves safe intermediate copies to `data/processed/`, and returns
the same validated Pandas DataFrames. It does not change business values, fill
missing values, or remove duplicates.

## How to run ingestion

Run all commands from the repository root (`Retail-Sales-Data-Engineering`).

1. Install project dependencies once:

   ```powershell
   python -m pip install -r requirements.txt
   ```

2. Confirm that `data/raw/` contains these six files:

   ```text
   bm_sales.csv
   bm_customers.csv
   bm_skus.csv
   bm_stores.csv
   bm_inventory.csv
   bm_promotions.csv
   ```

3. Run the pipeline:

   ```powershell
   python -c "from ingestion import run_ingestion; datasets = run_ingestion(); print(datasets.keys())"
   ```

   The default reads `data/raw/`. To explicitly use a different raw folder,
   pass that folder path. Passing a project root that contains `data/raw/` also
   works:

   ```python
   from ingestion import run_ingestion

   datasets = run_ingestion("data/raw")     # raw directory
   datasets = run_ingestion(".")            # project root containing data/raw/
   ```

4. Run the ingestion tests when changing ingestion code:

   ```powershell
   python -m pytest tests/test_ingestion.py
   ```

Successful execution creates `data/processed/` automatically and writes the
complete validated DataFrame—not a sample or dummy row—to every
`*_ingested.csv` file. The console logs identify every loaded, validated, and
saved dataset, including the number of rows written. For example:

```text
INFO ingestion Saved ingested sales: rows=641843 to data/processed/sales_ingested.csv
```

## Data available to Member 2

| Dictionary key | In-memory DataFrame | Safe intermediate CSV |
| --- | --- | --- |
| `sales` | `datasets["sales"]` | `data/processed/sales_ingested.csv` |
| `customers` | `datasets["customers"]` | `data/processed/customers_ingested.csv` |
| `skus` | `datasets["skus"]` | `data/processed/skus_ingested.csv` |
| `stores` | `datasets["stores"]` | `data/processed/stores_ingested.csv` |
| `inventory` | `datasets["inventory"]` | `data/processed/inventory_ingested.csv` |
| `promotions` | `datasets["promotions"]` | `data/processed/promotions_ingested.csv` |

## Option A: transform in memory

This avoids reading the CSVs twice and is the preferred path when ingestion and
transformation run in the same process.

```python
from ingestion import run_ingestion
from transformation.pipeline import transform_sales, transform_customers

datasets = run_ingestion()
sales_clean = transform_sales(datasets["sales"])
customers_clean = transform_customers(datasets["customers"])
```

Member 2 should add transformation functions in the `transformation/` package;
for example, `transformation/transformers.py` may define
`transform_sales(sales: pd.DataFrame)` and
`transform_customers(customers: pd.DataFrame)`. The ingestion files should not
be modified for ordinary cleaning rules.

## Option B: transform from safe CSV copies

Use this when Member 2's code runs separately from ingestion, or to restart a
transformation job without rereading raw source files.

```python
import pandas as pd

sales = pd.read_csv("data/processed/sales_ingested.csv")
customers = pd.read_csv("data/processed/customers_ingested.csv")
```

To load every persisted input at once, Member 2 can use:

```python
from pathlib import Path
import pandas as pd

processed_path = Path("data/processed")
datasets = {
    "sales": pd.read_csv(processed_path / "sales_ingested.csv"),
    "customers": pd.read_csv(processed_path / "customers_ingested.csv"),
    "skus": pd.read_csv(processed_path / "skus_ingested.csv"),
    "stores": pd.read_csv(processed_path / "stores_ingested.csv"),
    "inventory": pd.read_csv(processed_path / "inventory_ingested.csv"),
    "promotions": pd.read_csv(processed_path / "promotions_ingested.csv"),
}
```

## Member 2 update rules

- Use the dictionary keys and processed filenames exactly as listed above.
- Write cleaned outputs to a transformation-owned location, such as
  `data/processed/sales_transformed.csv`; do not overwrite `*_ingested.csv`.
- Add new business transformations in `transformation/`, not in `ingestion/`.
- Re-run ingestion whenever raw files change. This safely refreshes the
  `*_ingested.csv` copies before transformation begins.

The runner logs each dataset's load, validation, and save operation. A read,
validation, or save failure is logged as an error and stops the run, preventing
a partially validated result from being returned to Member 2.
