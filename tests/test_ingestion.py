"""Tests for the ingestion package."""

from pathlib import Path

import pandas as pd
import pytest

from ingestion.pipeline import run_ingestion
from ingestion.reader import DataReadError, load_sales
from ingestion.validator import REQUIRED_COLUMNS, SchemaValidationError, validate_dataframe


@pytest.fixture()
def raw_directory(tmp_path: Path) -> Path:
    """Create a small complete raw-source directory for isolated tests."""
    datasets = {
        "bm_sales.csv": pd.DataFrame([{
            "date": "2025-01-01", "store_id": 1, "sku_id": 100,
            "customer_id": 10, "quantity": 2, "unit_price": 5.0,
            "total_value": 10.0,
        }]),
        "bm_customers.csv": pd.DataFrame([{
            "cust_id": 10, "age": 30, "gender": "Female", "city": "Dubai",
            "loyalty_segment": "Gold",
        }]),
        "bm_skus.csv": pd.DataFrame([{
            "sku_id": 100, "sku_name": "Tea", "category": "Grocery",
            "unit_price": 5.0, "cost_price": 3.0,
        }]),
        "bm_stores.csv": pd.DataFrame([{
            "store_id": 1, "store_name": "Central", "city": "Dubai",
            "store_type": "Mall",
        }]),
        "bm_inventory.csv": pd.DataFrame([{
            "store_id": 1, "sku_id": 100, "stock_on_hand": 20,
            "reorder_point": 5, "safety_stock": 2,
        }]),
        "bm_promotions.csv": pd.DataFrame([{
            "promo_id": 1, "promo_name": "Launch", "start_date": "2025-01-01",
            "end_date": "2025-01-02", "discount_pct": 10, "promo_type": "Seasonal",
        }]),
    }
    for filename, dataframe in datasets.items():
        dataframe.to_csv(tmp_path / filename, index=False)
    return tmp_path


def test_pipeline_loads_non_empty_dataframes(raw_directory: Path) -> None:
    datasets = run_ingestion(raw_directory)
    assert set(datasets) == set(REQUIRED_COLUMNS)
    assert all(not dataframe.empty for dataframe in datasets.values())


def test_all_required_columns_are_present(raw_directory: Path) -> None:
    datasets = run_ingestion(raw_directory)
    for name, required_columns in REQUIRED_COLUMNS.items():
        assert required_columns.issubset(datasets[name].columns)


def test_identifier_columns_are_numeric(raw_directory: Path) -> None:
    datasets = run_ingestion(raw_directory)
    assert pd.api.types.is_numeric_dtype(datasets["sales"]["store_id"])
    assert pd.api.types.is_numeric_dtype(datasets["sales"]["sku_id"])
    assert pd.api.types.is_numeric_dtype(datasets["customers"]["cust_id"])
    assert pd.api.types.is_numeric_dtype(datasets["promotions"]["promo_id"])


def test_missing_file_raises_file_not_found(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="bm_sales.csv"):
        load_sales(tmp_path)


def test_empty_file_raises_clear_read_error(tmp_path: Path) -> None:
    (tmp_path / "bm_sales.csv").write_text("", encoding="utf-8")
    with pytest.raises(DataReadError, match="Source file is empty"):
        load_sales(tmp_path)


def test_missing_required_column_raises_schema_error() -> None:
    incomplete = pd.DataFrame({"store_id": [1], "sku_id": [100]})
    with pytest.raises(SchemaValidationError, match="customer_id"):
        validate_dataframe("sales", incomplete)


def test_non_numeric_identifier_raises_schema_error() -> None:
    invalid_identifier = pd.DataFrame({
        "date": ["2025-01-01"],
        "store_id": ["one"],
        "sku_id": [100],
        "customer_id": [10],
        "quantity": [1],
        "unit_price": [5.0],
        "total_value": [5.0],
    })
    with pytest.raises(SchemaValidationError, match="non-numeric"):
        validate_dataframe("sales", invalid_identifier)
