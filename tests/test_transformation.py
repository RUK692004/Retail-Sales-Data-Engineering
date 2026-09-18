"""Unit tests for the transformation package."""

from pathlib import Path
import pandas as pd
import pytest

from transformation.transform import (
    run_transformation_pipeline,
    transform_customers,
    transform_inventory,
    transform_promotions,
    transform_sales,
    transform_skus,
    transform_stores,
)


@pytest.fixture()
def sample_sales_df() -> pd.DataFrame:
    """Create sample sales dataset including duplicates and null customer_id."""
    return pd.DataFrame(
        [
            {
                "date": "2025-05-14",
                "store_id": 31,
                "sku_id": 1176,
                "customer_id": None,
                "quantity": 3,
                "unit_price": 6.83,
                "total_value": 20.49,
                "channel": "MobileApp",
                "discount_pct": 0.0,
            },
            # Exact duplicate 1
            {
                "date": "2025-05-14",
                "store_id": 31,
                "sku_id": 1176,
                "customer_id": None,
                "quantity": 3,
                "unit_price": 6.83,
                "total_value": 20.49,
                "channel": "MobileApp",
                "discount_pct": 0.0,
            },
            # Record with valid customer_id
            {
                "date": "2025-05-15",
                "store_id": 1,
                "sku_id": 1001,
                "customer_id": 101.0,
                "quantity": 1,
                "unit_price": 10.00,
                "total_value": 10.00,
                "channel": "Store",
                "discount_pct": 0.0,
            },
        ]
    )


def test_exact_duplicate_removal(sample_sales_df: pd.DataFrame) -> None:
    """Verify that exact duplicate rows are removed, keeping 1 copy."""
    transformed, dups_removed = transform_sales(sample_sales_df)
    assert dups_removed == 1
    assert len(transformed) == 2


def test_null_customer_id_preservation(sample_sales_df: pd.DataFrame) -> None:
    """Verify that NULL customer_id is preserved as NA/NULL and not converted to 0 or -1."""
    transformed, _ = transform_sales(sample_sales_df)
    assert transformed["customer_id"].isna().sum() == 1
    non_null = transformed["customer_id"].dropna().iloc[0]
    assert non_null == 101


def test_date_conversion(sample_sales_df: pd.DataFrame) -> None:
    """Verify string date conversion to datetime64."""
    transformed, _ = transform_sales(sample_sales_df)
    assert pd.api.types.is_datetime64_any_dtype(transformed["date"])
    assert transformed["date"].dt.year.tolist() == [2025, 2025]


def test_numeric_validation(sample_sales_df: pd.DataFrame) -> None:
    """Verify numeric column types and total value math."""
    transformed, _ = transform_sales(sample_sales_df)
    assert (transformed["quantity"] > 0).all()
    assert (transformed["unit_price"] > 0).all()
    assert (transformed["total_value"] > 0).all()
    calculated_total = (transformed["quantity"] * transformed["unit_price"]).round(2)
    assert (transformed["total_value"].round(2) == calculated_total).all()


def test_foreign_key_validation() -> None:
    """Verify referential integrity between sales, customers, skus, and stores."""
    project_root = Path(__file__).resolve().parents[1]
    input_dir = project_root / "data" / "processed"
    if not input_dir.exists():
        pytest.skip("Processed data directory not found.")

    sales = pd.read_csv(input_dir / "sales_ingested.csv")
    customers = pd.read_csv(input_dir / "customers_ingested.csv")
    skus = pd.read_csv(input_dir / "skus_ingested.csv")
    stores = pd.read_csv(input_dir / "stores_ingested.csv")

    valid_custs = set(customers["cust_id"])
    valid_skus = set(skus["sku_id"])
    valid_stores = set(stores["store_id"])

    non_null_custs = sales["customer_id"].dropna()
    assert non_null_custs.isin(valid_custs).all()
    assert sales["sku_id"].isin(valid_skus).all()
    assert sales["store_id"].isin(valid_stores).all()


def test_output_schema_and_pipeline_execution(tmp_path: Path) -> None:
    """Verify pipeline execution: output files exist and contain rows."""
    project_root = Path(__file__).resolve().parents[1]
    input_dir = project_root / "data" / "processed"
    if not input_dir.exists():
        pytest.skip("Processed data directory not found.")

    output_dir = tmp_path / "transformed"
    # run_transformation_pipeline now returns a validation-report dict
    report = run_transformation_pipeline(
        input_dir=input_dir, output_dir=output_dir
    )

    expected_tables = ["sales", "customers", "inventory", "promotions", "skus", "stores"]
    for table_name in expected_tables:
        assert table_name in report
        # Verify the output CSV was actually written and is non-empty
        out_file = output_dir / f"{table_name}_transformed.csv"
        assert out_file.is_file(), f"Missing output file: {out_file}"
        loaded = pd.read_csv(out_file)
        assert len(loaded) > 0, f"{table_name}_transformed.csv is empty"

