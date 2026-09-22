"""
Retail Sales Data Engineering — Member 2: Transformation Pipeline
=================================================================

Reads all six processed datasets from  data/processed/,
applies documented cleaning rules, and writes transformed CSVs to
data/transformed/.

Usage (from repository root):
    python transformation/transform.py

All transformation rules were established during Step 2 data-quality
investigation and are documented in docs/transformation_report.md.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_DIR = PROJECT_ROOT / "data" / "transformed"

# Expected input filenames
INPUT_FILES: dict[str, str] = {
    "sales":      "sales_ingested.csv",
    "customers":  "customers_ingested.csv",
    "inventory":  "inventory_ingested.csv",
    "promotions": "promotions_ingested.csv",
    "skus":       "skus_ingested.csv",
    "stores":     "stores_ingested.csv",
}

# Output filenames (matches INPUT_FILES keys)
OUTPUT_FILES: dict[str, str] = {
    "sales":      "sales_transformed.csv",
    "customers":  "customers_transformed.csv",
    "inventory":  "inventory_transformed.csv",
    "promotions": "promotions_transformed.csv",
    "skus":       "skus_transformed.csv",
    "stores":     "stores_transformed.csv",
}

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------


def _get_logger() -> logging.Logger:
    """Return a module-level logger, configuring it only once."""
    logger = logging.getLogger("transformation")
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter("%(asctime)s  %(levelname)-8s  %(message)s",
                              datefmt="%Y-%m-%d %H:%M:%S")
        )
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
    return logger


logger = _get_logger()

# ---------------------------------------------------------------------------
# Step 3.3 — Load processed data
# ---------------------------------------------------------------------------


def load_data(input_dir: Path = INPUT_DIR) -> dict[str, pd.DataFrame]:
    """Load all six processed CSV datasets.

    Parameters
    ----------
    input_dir : Path
        Directory containing the *_ingested.csv files.

    Returns
    -------
    dict[str, pd.DataFrame]
        Keyed by dataset name (e.g. "sales", "customers", …).

    Raises
    ------
    FileNotFoundError
        If the input directory or any expected file is missing.
    ValueError
        If a CSV file cannot be parsed or is empty.
    """
    if not input_dir.is_dir():
        raise FileNotFoundError(
            f"Input directory not found: {input_dir}\n"
            "Run the ingestion pipeline first."
        )

    datasets: dict[str, pd.DataFrame] = {}
    for name, filename in INPUT_FILES.items():
        file_path = input_dir / filename
        if not file_path.is_file():
            raise FileNotFoundError(
                f"Expected input file missing: {file_path}"
            )
        try:
            df = pd.read_csv(file_path)
        except pd.errors.EmptyDataError as exc:
            raise ValueError(f"Input file is empty: {file_path}") from exc
        except pd.errors.ParserError as exc:
            raise ValueError(
                f"Could not parse CSV: {file_path}\n{exc}"
            ) from exc

        logger.info("Loaded %-12s — %d rows, %d columns",
                    name, len(df), len(df.columns))
        datasets[name] = df

    return datasets


# ---------------------------------------------------------------------------
# Step 3.4 — Sales transformation
# ---------------------------------------------------------------------------


def transform_sales(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Clean and type-cast the sales dataset.

    Rules applied (all verified during Step 2 investigation):
    1.  Remove exact duplicate rows; keep one copy.
    2.  Preserve NULL customer_id — do NOT replace with 0 / -1.
    3.  Convert ``date``        → datetime64[ns].
    4.  Cast ``customer_id``   → Int64 (pandas nullable integer).
    5.  Cast ``store_id``      → int64.
    6.  Cast ``sku_id``        → int64.
    7.  Cast ``quantity``      → int64.
    8.  Cast ``unit_price``    → float64.
    9.  Cast ``total_value``   → float64.
    10. Cast ``discount_pct``  → float64.
    11. Strip whitespace from ``channel``.
    12. Original column order is preserved.
    13. ``total_value`` is NOT recalculated (already validated).

    Returns
    -------
    tuple[pd.DataFrame, int]
        (transformed DataFrame, number of duplicate rows removed)
    """
    logger.info("Transforming sales ...")
    original_cols = list(df.columns)
    df = df.copy()

    # 1. Exact duplicate removal
    initial_rows = len(df)
    df = df.drop_duplicates()
    duplicates_removed = initial_rows - len(df)
    logger.info("  Duplicate rows removed: %d  (rows remaining: %d)",
                duplicates_removed, len(df))

    # 2. Date conversion
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # 3. Numeric type casts
    df["store_id"]    = df["store_id"].astype("int64")
    df["sku_id"]      = df["sku_id"].astype("int64")
    df["quantity"]    = df["quantity"].astype("int64")
    df["unit_price"]  = df["unit_price"].astype("float64")
    df["total_value"] = df["total_value"].astype("float64")

    if "discount_pct" in df.columns:
        df["discount_pct"] = df["discount_pct"].astype("float64")

    # 4. Nullable integer for customer_id (preserves NaN as <NA>)
    df["customer_id"] = df["customer_id"].astype("Int64")

    # 5. String normalisation
    if "channel" in df.columns:
        df["channel"] = df["channel"].astype(str).str.strip()

    # 6. Restore original column order
    df = df[original_cols]

    null_cust = df["customer_id"].isna().sum()
    logger.info("  NULL customer_id preserved: %d", null_cust)

    return df, duplicates_removed


# ---------------------------------------------------------------------------
# Step 3.5 — Customer transformation
# ---------------------------------------------------------------------------


def transform_customers(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and type-cast the customers dataset.

    Rules applied:
    1. Cast ``cust_id``            → int64.
    2. Cast ``age``                → int64.
    3. Convert ``registration_date`` → datetime64[ns].
    4. Strip whitespace from text columns.
    5. Original column order preserved.
    """
    logger.info("Transforming customers ...")
    original_cols = list(df.columns)
    df = df.copy()

    df["cust_id"] = df["cust_id"].astype("int64")
    df["age"]     = df["age"].astype("int64")

    if "registration_date" in df.columns:
        df["registration_date"] = pd.to_datetime(
            df["registration_date"], errors="coerce"
        )

    for col in ["gender", "city", "loyalty_segment", "preferred_channel"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    df = df[original_cols]
    return df


# ---------------------------------------------------------------------------
# Step 3.6 — Inventory transformation
# ---------------------------------------------------------------------------


def transform_inventory(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and type-cast the inventory dataset.

    Rules applied:
    1. Cast ``store_id``, ``sku_id``, ``stock_on_hand``,
       ``reorder_point``, ``safety_stock`` → int64.
    2. Convert ``last_restock_date`` and ``snapshot_date`` → datetime64[ns].
    3. Original column order preserved.
    """
    logger.info("Transforming inventory ...")
    original_cols = list(df.columns)
    df = df.copy()

    for col in ["store_id", "sku_id", "stock_on_hand",
                "reorder_point", "safety_stock"]:
        if col in df.columns:
            df[col] = df[col].astype("int64")

    for col in ["last_restock_date", "snapshot_date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    df = df[original_cols]
    return df


# ---------------------------------------------------------------------------
# Step 3.7 — Promotion transformation
# ---------------------------------------------------------------------------


def transform_promotions(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and type-cast the promotions dataset.

    Rules applied:
    1. Cast ``promo_id``     → int64.
    2. Cast ``discount_pct`` → int64.
    3. Convert ``start_date`` and ``end_date`` → datetime64[ns].
    4. Strip whitespace from text columns.
    5. Original column order preserved.
    """
    logger.info("Transforming promotions ...")
    original_cols = list(df.columns)
    df = df.copy()

    df["promo_id"]     = df["promo_id"].astype("int64")
    df["discount_pct"] = df["discount_pct"].astype("int64")

    for col in ["start_date", "end_date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    for col in ["promo_name", "promo_type"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    df = df[original_cols]
    return df


# ---------------------------------------------------------------------------
# Step 3.8 — SKU transformation
# ---------------------------------------------------------------------------


def transform_skus(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and type-cast the SKUs dataset.

    Rules applied:
    1. Cast ``sku_id``      → int64.
    2. Cast ``unit_price``  → float64.
    3. Cast ``cost_price``  → float64.
    4. Strip whitespace from text columns.
    5. Original column order preserved.
    """
    logger.info("Transforming SKUs ...")
    original_cols = list(df.columns)
    df = df.copy()

    df["sku_id"]     = df["sku_id"].astype("int64")
    df["unit_price"] = df["unit_price"].astype("float64")
    df["cost_price"] = df["cost_price"].astype("float64")

    for col in ["sku_name", "category", "subcategory", "brand"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    df = df[original_cols]
    return df


# ---------------------------------------------------------------------------
# Step 3.9 — Store transformation
# ---------------------------------------------------------------------------


def transform_stores(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and type-cast the stores dataset.

    Rules applied:
    1. Cast ``store_id``    → int64.
    2. Convert ``opening_date`` → datetime64[ns].
    3. Strip whitespace from text columns.
    4. Original column order preserved.
    """
    logger.info("Transforming stores ...")
    original_cols = list(df.columns)
    df = df.copy()

    df["store_id"] = df["store_id"].astype("int64")

    if "opening_date" in df.columns:
        df["opening_date"] = pd.to_datetime(df["opening_date"], errors="coerce")

    for col in ["store_name", "city", "store_type"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    df = df[original_cols]
    return df


# ---------------------------------------------------------------------------
# Step 3.11 — Save outputs
# ---------------------------------------------------------------------------


def save_transformed_data(
    datasets: dict[str, pd.DataFrame],
    output_dir: Path = OUTPUT_DIR,
) -> None:
    """Persist all transformed DataFrames to CSV.

    Dates are serialised as ``YYYY-MM-DD``.
    Int64 nullable integers are serialised naturally (NaN becomes empty cell).
    Output directory is created if it does not exist.

    Parameters
    ----------
    datasets : dict[str, pd.DataFrame]
        Keyed by dataset name matching OUTPUT_FILES.
    output_dir : Path
        Directory to write the *_transformed.csv files.

    Raises
    ------
    OSError
        If any file cannot be written.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    for name, df in datasets.items():
        out_path = output_dir / OUTPUT_FILES[name]

        # Convert datetime columns to ISO date strings for plain CSV storage
        df_save = df.copy()
        for col in df_save.columns:
            if pd.api.types.is_datetime64_any_dtype(df_save[col]):
                df_save[col] = df_save[col].dt.strftime("%Y-%m-%d")

        try:
            df_save.to_csv(out_path, index=False)
        except OSError as exc:
            raise OSError(
                f"Failed to write transformed {name} to {out_path}"
            ) from exc

        logger.info("Saved %-12s -> %s  (%d rows)", name, out_path, len(df_save))


# ---------------------------------------------------------------------------
# Step 3.12 — Output validation
# ---------------------------------------------------------------------------


def validate_transformed_data(
    datasets: dict[str, pd.DataFrame],
    raw_datasets: dict[str, pd.DataFrame],
) -> dict[str, dict]:
    """Validate every transformed dataset and return a structured report.

    Checks performed for all datasets
    -----------------------------------
    - Row count.
    - Column names.
    - Exact duplicate count.
    - Null counts per column.

    Additional checks for sales
    ----------------------------
    - Exact duplicates == 0.
    - NULL customer_id values still present.
    - total_value == quantity × unit_price (within floating-point tolerance).
    - All non-null customer_id values remain valid references.
    - All sku_id values remain valid references.
    - All store_id values remain valid references.
    - No negative quantity / unit_price / total_value.
    - discount_pct in {0, 10, 15, 20, 25, 30, 35}.

    Returns
    -------
    dict[str, dict]
        Nested dict: { dataset_name: { check_name: result } }
    """
    logger.info("Validating transformed outputs ...")
    report: dict[str, dict] = {}

    valid_cust_ids  = set(datasets["customers"]["cust_id"])
    valid_sku_ids   = set(datasets["skus"]["sku_id"])
    valid_store_ids = set(datasets["stores"]["store_id"])

    for name, df in datasets.items():
        raw_df = raw_datasets[name]
        checks: dict = {}

        checks["rows_in"]     = len(raw_df)
        checks["rows_out"]    = len(df)
        checks["columns"]     = list(df.columns)
        checks["duplicates"]  = int(df.duplicated().sum())
        checks["null_counts"] = df.isnull().sum().to_dict()

        if name == "sales":
            # Duplicate check
            checks["sales_duplicates_zero"] = checks["duplicates"] == 0

            # NULL customer preservation
            null_cust = int(df["customer_id"].isna().sum())
            checks["null_customer_id_count"] = null_cust
            checks["null_customer_id_preserved"] = null_cust > 0

            # total_value consistency
            calculated = (df["quantity"] * df["unit_price"]).round(2)
            mismatched  = int((df["total_value"].round(2) != calculated).sum())
            checks["total_value_mismatches"] = mismatched
            checks["total_value_consistent"] = mismatched == 0

            # Referential integrity
            non_null_cust_ids = df["customer_id"].dropna()
            invalid_cust  = int((~non_null_cust_ids.isin(valid_cust_ids)).sum())
            invalid_sku   = int((~df["sku_id"].isin(valid_sku_ids)).sum())
            invalid_store = int((~df["store_id"].isin(valid_store_ids)).sum())
            checks["invalid_customer_ids"] = invalid_cust
            checks["invalid_sku_ids"]      = invalid_sku
            checks["invalid_store_ids"]    = invalid_store
            checks["referential_integrity_ok"] = (
                invalid_cust == 0 and invalid_sku == 0 and invalid_store == 0
            )

            # Numeric validity
            checks["negative_quantity"]    = int((df["quantity"]    < 0).sum())
            checks["negative_unit_price"]  = int((df["unit_price"]  < 0).sum())
            checks["negative_total_value"] = int((df["total_value"] < 0).sum())
            valid_discounts = {0, 10, 15, 20, 25, 30, 35}
            checks["invalid_discount_pct"] = int(
                (~df["discount_pct"].isin(valid_discounts)).sum()
            )

        report[name] = checks

    return report


def _log_validation_report(report: dict[str, dict]) -> None:
    """Log a human-readable summary of the validation report."""
    logger.info("=" * 60)
    logger.info("VALIDATION SUMMARY")
    logger.info("=" * 60)
    for name, checks in report.items():
        logger.info("  %s:", name.upper())
        logger.info("    Rows in / out : %d / %d",
                    checks["rows_in"], checks["rows_out"])
        logger.info("    Duplicates    : %d", checks["duplicates"])
        nulls = {k: v for k, v in checks["null_counts"].items() if v > 0}
        if nulls:
            logger.info("    Nulls present : %s", nulls)
        else:
            logger.info("    Nulls present : none")
        if name == "sales":
            logger.info("    NULL customer_id preserved  : %s  (%d rows)",
                        checks["null_customer_id_preserved"],
                        checks["null_customer_id_count"])
            logger.info("    total_value consistent      : %s",
                        checks["total_value_consistent"])
            logger.info("    Referential integrity OK    : %s",
                        checks["referential_integrity_ok"])
            logger.info("    Negative quantity           : %d",
                        checks["negative_quantity"])
            logger.info("    Invalid discount_pct        : %d",
                        checks["invalid_discount_pct"])
    logger.info("=" * 60)


# ---------------------------------------------------------------------------
# Public pipeline runner (importable for tests & Airflow)
# ---------------------------------------------------------------------------


def run_transformation_pipeline(
    input_dir:  Path | None = None,
    output_dir: Path | None = None,
) -> dict[str, dict]:
    """Load → transform → save → validate all six retail datasets.

    Parameters
    ----------
    input_dir : Path, optional
        Override for the default INPUT_DIR.
    output_dir : Path, optional
        Override for the default OUTPUT_DIR.

    Returns
    -------
    dict[str, dict]
        Validation report keyed by dataset name.
    """
    in_dir  = Path(input_dir)  if input_dir  else INPUT_DIR
    out_dir = Path(output_dir) if output_dir else OUTPUT_DIR

    logger.info("Retail Sales Transformation Pipeline — starting")
    logger.info("Input  : %s", in_dir)
    logger.info("Output : %s", out_dir)

    # Load
    raw_datasets = load_data(in_dir)

    # Transform
    sales_df, dups_removed = transform_sales(raw_datasets["sales"])

    transformed: dict[str, pd.DataFrame] = {
        "sales":      sales_df,
        "customers":  transform_customers(raw_datasets["customers"]),
        "inventory":  transform_inventory(raw_datasets["inventory"]),
        "promotions": transform_promotions(raw_datasets["promotions"]),
        "skus":       transform_skus(raw_datasets["skus"]),
        "stores":     transform_stores(raw_datasets["stores"]),
    }

    logger.info("Sales duplicate rows removed: %d", dups_removed)

    # Save
    save_transformed_data(transformed, out_dir)

    # Validate
    report = validate_transformed_data(transformed, raw_datasets)
    _log_validation_report(report)

    logger.info("Transformation pipeline completed successfully.")
    return report


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main() -> None:
    """Entry point when executed as a script."""
    run_transformation_pipeline()


if __name__ == "__main__":
    main()
