# Ingestion module

This package is the pipeline's raw-data boundary. `reader.py` loads each CSV unchanged, `validator.py` verifies schemas and reports data health, and `pipeline.py` combines both through `run_ingestion()`.

From the repository root:

```powershell
python -m pip install -r requirements.txt
python -c "from ingestion import run_ingestion; print(run_ingestion().keys())"
python -m pytest tests/test_ingestion.py
```

The default input folder is `data/raw`. It must contain all six `bm_*.csv` files. The runner returns a dictionary containing `sales`, `customers`, `skus`, `stores`, `inventory`, and `promotions` Pandas DataFrames. Required columns and numeric identifier types are enforced; missing values and duplicates are logged in validation reports for downstream cleansing.

## Code guide

- `__init__.py`: imports `run_ingestion` and exposes it as the package's public API.
- `reader.py` lines 1–8 import Pandas, CSV exceptions, and path/type helpers. Lines 11–12 define `DataReadError`. Lines 15–27 define `_read_csv`: it builds a path, calls `pd.read_csv`, and converts missing, empty, malformed, encoding, and operating-system errors into descriptive exceptions. Lines 30–55 are six small dataset-specific wrappers that select the correct filename.
- `validator.py` lines 1–10 create imports and the module logger. Lines 13–14 define `SchemaValidationError`. Lines 17–36 declare each dataset's required fields and numeric IDs. Lines 39–77 validate the dataset name and DataFrame, reject missing columns or nonnumeric IDs, then produce shape, null-count, duplicate-count, and dtype metrics. Lines 80–82 validate a full mapping.
- `pipeline.py` lines 1–18 import the readers and validator. Lines 21–32 create a timestamped INFO console logger only once. Lines 35–67 define `run_ingestion`: it loops through the six readers, logs row and column counts, validates each DataFrame, logs any failure with its traceback, and returns the validated dictionary.
