"""
tests/test_transform.py
-----------------------
Pytest test suite for the Member 2 transformation pipeline.

Tests cover:
  1.  Exact duplicate sales removal.
  2.  NULL customer_id preservation.
  3.  Sales total_value consistency.
  4.  Date conversion (sales, customers, inventory, promotions, stores).
  5.  Numeric validation (no negative values, valid discount_pct).
  6.  Output column preservation (original column order maintained).
  7.  Referential integrity checks against real processed data.
  8.  Pipeline smoke test (load → transform → save → validate).
  9.  load_data() raises FileNotFoundError for missing files.
  10. validate_transformed_data() detects issues correctly.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from transformation.transform import (
    INPUT_DIR,
    load_data,
    run_transformation_pipeline,
    transform_customers,
    transform_inventory,
    transform_promotions,
    transform_sales,
    transform_skus,
    transform_stores,
    validate_transformed_data,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SALES_COLS = [
    "date", "store_id", "sku_id", "customer_id",
    "quantity", "unit_price", "total_value", "channel", "discount_pct",
]


def _make_sales(*rows: dict) -> pd.DataFrame:
    """Build a minimal sales DataFrame with proper column order."""
    defaults = {
        "date": "2025-01-01",
        "store_id": 1,
        "sku_id": 1001,
        "customer_id": 100.0,
        "quantity": 2,
        "unit_price": 10.0,
        "total_value": 20.0,
        "channel": "Store",
        "discount_pct": 0.0,
    }
    records = [{**defaults, **r} for r in rows]
    return pd.DataFrame(records, columns=SALES_COLS)


@pytest.fixture()
def sales_with_duplicates() -> pd.DataFrame:
    """Three rows: one unique + two identical duplicates."""
    return _make_sales(
        # unique record
        {"date": "2025-05-15", "customer_id": 200.0},
        # duplicate pair
        {"date": "2025-05-14", "store_id": 31, "sku_id": 1176,
         "customer_id": None, "quantity": 3,
         "unit_price": 6.83, "total_value": 20.49,
         "channel": "MobileApp", "discount_pct": 0.0},
        {"date": "2025-05-14", "store_id": 31, "sku_id": 1176,
         "customer_id": None, "quantity": 3,
         "unit_price": 6.83, "total_value": 20.49,
         "channel": "MobileApp", "discount_pct": 0.0},
    )


@pytest.fixture()
def sales_with_null_customer() -> pd.DataFrame:
    return _make_sales(
        {"customer_id": None},
        {"customer_id": 42.0},
    )


@pytest.fixture()
def simple_customers() -> pd.DataFrame:
    return pd.DataFrame([
        {"cust_id": 1, "age": 30, "gender": "Female", "city": "Dubai",
         "loyalty_segment": "Gold", "preferred_channel": "Store",
         "registration_date": "2023-06-01"},
    ])


@pytest.fixture()
def simple_inventory() -> pd.DataFrame:
    return pd.DataFrame([
        {"store_id": 1, "sku_id": 1001, "stock_on_hand": 100,
         "reorder_point": 20, "safety_stock": 10,
         "last_restock_date": "2025-09-01", "snapshot_date": "2025-10-31"},
    ])


@pytest.fixture()
def simple_promotions() -> pd.DataFrame:
    return pd.DataFrame([
        {"promo_id": 1, "promo_name": "DSF Sale", "start_date": "2025-01-01",
         "end_date": "2025-01-31", "discount_pct": 15, "promo_type": "DSF"},
    ])


@pytest.fixture()
def simple_skus() -> pd.DataFrame:
    return pd.DataFrame([
        {"sku_id": 1001, "sku_name": "Tea Box", "category": "Grocery",
         "subcategory": "Tea", "unit_price": 10.00, "cost_price": 6.00,
         "brand": "Local"},
    ])


@pytest.fixture()
def simple_stores() -> pd.DataFrame:
    return pd.DataFrame([
        {"store_id": 1, "store_name": "BlueMart 01", "city": "Dubai",
         "store_type": "Mall", "opening_date": "2017-01-01 00:00:00"},
    ])


# ---------------------------------------------------------------------------
# Test 1 — Exact duplicate removal
# ---------------------------------------------------------------------------

class TestExactDuplicateRemoval:
    def test_duplicates_removed(self, sales_with_duplicates):
        df, dups = transform_sales(sales_with_duplicates)
        assert dups == 1, "Expected exactly 1 duplicate to be removed"

    def test_one_copy_retained(self, sales_with_duplicates):
        df, _ = transform_sales(sales_with_duplicates)
        assert len(df) == 2, "Expected 2 rows after deduplication (1 unique + 1 retained)"

    def test_no_duplicates_remain(self, sales_with_duplicates):
        df, _ = transform_sales(sales_with_duplicates)
        assert df.duplicated().sum() == 0


# ---------------------------------------------------------------------------
# Test 2 — NULL customer_id preservation
# ---------------------------------------------------------------------------

class TestNullCustomerIdPreservation:
    def test_null_count_preserved(self, sales_with_null_customer):
        df, _ = transform_sales(sales_with_null_customer)
        assert df["customer_id"].isna().sum() == 1

    def test_null_not_replaced_with_zero(self, sales_with_null_customer):
        df, _ = transform_sales(sales_with_null_customer)
        assert 0 not in df["customer_id"].dropna().tolist()

    def test_null_not_replaced_with_negative_one(self, sales_with_null_customer):
        df, _ = transform_sales(sales_with_null_customer)
        assert -1 not in df["customer_id"].dropna().tolist()

    def test_customer_id_type_is_nullable_integer(self, sales_with_null_customer):
        df, _ = transform_sales(sales_with_null_customer)
        assert str(df["customer_id"].dtype) == "Int64"


# ---------------------------------------------------------------------------
# Test 3 — Sales total_value consistency
# ---------------------------------------------------------------------------

class TestTotalValueConsistency:
    def test_total_value_not_altered(self):
        """transform_sales must NOT recalculate total_value."""
        df = _make_sales(
            {"quantity": 3, "unit_price": 6.83, "total_value": 20.49},
        )
        result, _ = transform_sales(df)
        assert result["total_value"].iloc[0] == pytest.approx(20.49)

    def test_total_value_consistency_on_dataset(self, sales_with_duplicates):
        df, _ = transform_sales(sales_with_duplicates)
        calc = (df["quantity"] * df["unit_price"]).round(2)
        assert (df["total_value"].round(2) == calc).all()


# ---------------------------------------------------------------------------
# Test 4 — Date conversion
# ---------------------------------------------------------------------------

class TestDateConversion:
    def test_sales_date_is_datetime(self, sales_with_null_customer):
        df, _ = transform_sales(sales_with_null_customer)
        assert pd.api.types.is_datetime64_any_dtype(df["date"])

    def test_customers_registration_date_is_datetime(self, simple_customers):
        df = transform_customers(simple_customers)
        assert pd.api.types.is_datetime64_any_dtype(df["registration_date"])

    def test_inventory_dates_are_datetime(self, simple_inventory):
        df = transform_inventory(simple_inventory)
        assert pd.api.types.is_datetime64_any_dtype(df["last_restock_date"])
        assert pd.api.types.is_datetime64_any_dtype(df["snapshot_date"])

    def test_promotions_dates_are_datetime(self, simple_promotions):
        df = transform_promotions(simple_promotions)
        assert pd.api.types.is_datetime64_any_dtype(df["start_date"])
        assert pd.api.types.is_datetime64_any_dtype(df["end_date"])

    def test_stores_opening_date_is_datetime(self, simple_stores):
        df = transform_stores(simple_stores)
        assert pd.api.types.is_datetime64_any_dtype(df["opening_date"])


# ---------------------------------------------------------------------------
# Test 5 — Numeric validation
# ---------------------------------------------------------------------------

class TestNumericValidation:
    def test_no_negative_quantity(self, sales_with_null_customer):
        df, _ = transform_sales(sales_with_null_customer)
        assert (df["quantity"] >= 0).all()

    def test_no_negative_unit_price(self, sales_with_null_customer):
        df, _ = transform_sales(sales_with_null_customer)
        assert (df["unit_price"] >= 0).all()

    def test_no_negative_total_value(self, sales_with_null_customer):
        df, _ = transform_sales(sales_with_null_customer)
        assert (df["total_value"] >= 0).all()

    def test_quantity_is_int64(self, sales_with_null_customer):
        df, _ = transform_sales(sales_with_null_customer)
        assert df["quantity"].dtype == "int64"

    def test_unit_price_is_float64(self, sales_with_null_customer):
        df, _ = transform_sales(sales_with_null_customer)
        assert df["unit_price"].dtype == "float64"

    def test_sku_cost_price_not_exceeds_unit_price(self, simple_skus):
        df = transform_skus(simple_skus)
        assert (df["cost_price"] <= df["unit_price"]).all()


# ---------------------------------------------------------------------------
# Test 6 — Output column preservation
# ---------------------------------------------------------------------------

class TestColumnPreservation:
    def test_sales_column_order(self, sales_with_null_customer):
        df, _ = transform_sales(sales_with_null_customer)
        assert list(df.columns) == SALES_COLS

    def test_customers_columns_preserved(self, simple_customers):
        original_cols = list(simple_customers.columns)
        df = transform_customers(simple_customers)
        assert list(df.columns) == original_cols

    def test_inventory_columns_preserved(self, simple_inventory):
        original_cols = list(simple_inventory.columns)
        df = transform_inventory(simple_inventory)
        assert list(df.columns) == original_cols

    def test_promotions_columns_preserved(self, simple_promotions):
        original_cols = list(simple_promotions.columns)
        df = transform_promotions(simple_promotions)
        assert list(df.columns) == original_cols

    def test_skus_columns_preserved(self, simple_skus):
        original_cols = list(simple_skus.columns)
        df = transform_skus(simple_skus)
        assert list(df.columns) == original_cols

    def test_stores_columns_preserved(self, simple_stores):
        original_cols = list(simple_stores.columns)
        df = transform_stores(simple_stores)
        assert list(df.columns) == original_cols


# ---------------------------------------------------------------------------
# Test 7 — Referential integrity against real processed data
# ---------------------------------------------------------------------------

class TestReferentialIntegrity:
    @pytest.fixture(autouse=True)
    def skip_if_no_data(self):
        if not INPUT_DIR.is_dir():
            pytest.skip("data/processed not found — run ingestion first")

    def test_sales_customer_ids_all_valid(self):
        sales     = pd.read_csv(INPUT_DIR / "sales_ingested.csv")
        customers = pd.read_csv(INPUT_DIR / "customers_ingested.csv")
        valid_ids = set(customers["cust_id"])
        non_null  = sales["customer_id"].dropna()
        assert non_null.isin(valid_ids).all()

    def test_sales_sku_ids_all_valid(self):
        sales = pd.read_csv(INPUT_DIR / "sales_ingested.csv")
        skus  = pd.read_csv(INPUT_DIR / "skus_ingested.csv")
        assert sales["sku_id"].isin(set(skus["sku_id"])).all()

    def test_sales_store_ids_all_valid(self):
        sales  = pd.read_csv(INPUT_DIR / "sales_ingested.csv")
        stores = pd.read_csv(INPUT_DIR / "stores_ingested.csv")
        assert sales["store_id"].isin(set(stores["store_id"])).all()

    def test_inventory_store_ids_all_valid(self):
        inventory = pd.read_csv(INPUT_DIR / "inventory_ingested.csv")
        stores    = pd.read_csv(INPUT_DIR / "stores_ingested.csv")
        assert inventory["store_id"].isin(set(stores["store_id"])).all()

    def test_inventory_sku_ids_all_valid(self):
        inventory = pd.read_csv(INPUT_DIR / "inventory_ingested.csv")
        skus      = pd.read_csv(INPUT_DIR / "skus_ingested.csv")
        assert inventory["sku_id"].isin(set(skus["sku_id"])).all()


# ---------------------------------------------------------------------------
# Test 8 — Pipeline smoke test
# ---------------------------------------------------------------------------

class TestPipelineSmoke:
    @pytest.fixture(autouse=True)
    def skip_if_no_data(self):
        if not INPUT_DIR.is_dir():
            pytest.skip("data/processed not found — run ingestion first")

    def test_pipeline_runs_and_writes_files(self, tmp_path):
        report = run_transformation_pipeline(
            input_dir=INPUT_DIR, output_dir=tmp_path
        )
        expected = ["sales", "customers", "inventory",
                    "promotions", "skus", "stores"]
        for name in expected:
            assert name in report
            out = tmp_path / f"{name}_transformed.csv"
            assert out.is_file(), f"Expected output file missing: {out}"
            loaded = pd.read_csv(out)
            assert len(loaded) > 0

    def test_sales_duplicates_removed_in_pipeline(self, tmp_path):
        report = run_transformation_pipeline(
            input_dir=INPUT_DIR, output_dir=tmp_path
        )
        assert report["sales"]["duplicates"] == 0

    def test_null_customer_preserved_in_pipeline(self, tmp_path):
        report = run_transformation_pipeline(
            input_dir=INPUT_DIR, output_dir=tmp_path
        )
        assert report["sales"]["null_customer_id_preserved"] is True

    def test_total_value_consistent_in_pipeline(self, tmp_path):
        report = run_transformation_pipeline(
            input_dir=INPUT_DIR, output_dir=tmp_path
        )
        assert report["sales"]["total_value_consistent"] is True

    def test_referential_integrity_in_pipeline(self, tmp_path):
        report = run_transformation_pipeline(
            input_dir=INPUT_DIR, output_dir=tmp_path
        )
        assert report["sales"]["referential_integrity_ok"] is True


# ---------------------------------------------------------------------------
# Test 9 — load_data() error handling
# ---------------------------------------------------------------------------

class TestLoadDataErrorHandling:
    def test_missing_directory_raises_file_not_found(self, tmp_path):
        missing = tmp_path / "does_not_exist"
        with pytest.raises(FileNotFoundError, match="Input directory not found"):
            load_data(missing)

    def test_missing_file_raises_file_not_found(self, tmp_path):
        # Create dir but omit sales file
        with pytest.raises(FileNotFoundError):
            load_data(tmp_path)


# ---------------------------------------------------------------------------
# Test 10 — validate_transformed_data() detects issues
# ---------------------------------------------------------------------------

class TestValidationDetectsIssues:
    def _make_datasets(self, sales_override=None):
        """Return a minimal set of transformed datasets for validation tests."""
        customers = pd.DataFrame({"cust_id": [1, 2]})
        skus      = pd.DataFrame({"sku_id":  [1001]})
        stores    = pd.DataFrame({"store_id": [1]})
        inventory = pd.DataFrame({"store_id": [1], "sku_id": [1001],
                                  "stock_on_hand": [50], "reorder_point": [10],
                                  "safety_stock": [5]})
        promotions = pd.DataFrame({"promo_id": [1], "discount_pct": [15]})
        sales = sales_override if sales_override is not None else pd.DataFrame({
            "date": pd.to_datetime(["2025-01-01"]),
            "store_id": pd.array([1], dtype="int64"),
            "sku_id": pd.array([1001], dtype="int64"),
            "customer_id": pd.array([1], dtype="Int64"),
            "quantity": pd.array([2], dtype="int64"),
            "unit_price": [10.0],
            "total_value": [20.0],
            "channel": ["Store"],
            "discount_pct": [0.0],
        })
        raw = {
            "sales": sales.copy(), "customers": customers.copy(),
            "inventory": inventory.copy(), "promotions": promotions.copy(),
            "skus": skus.copy(), "stores": stores.copy(),
        }
        transformed = {
            "sales": sales, "customers": customers,
            "inventory": inventory, "promotions": promotions,
            "skus": skus, "stores": stores,
        }
        return transformed, raw

    def test_valid_data_passes(self):
        transformed, raw = self._make_datasets()
        report = validate_transformed_data(transformed, raw)
        assert report["sales"]["duplicates"] == 0
        assert report["sales"]["total_value_consistent"] is True
        assert report["sales"]["referential_integrity_ok"] is True

    def test_detects_duplicate_sales(self):
        row = {"date": pd.to_datetime("2025-01-01"),
               "store_id": 1, "sku_id": 1001,
               "customer_id": pd.NA, "quantity": 2,
               "unit_price": 10.0, "total_value": 20.0,
               "channel": "Store", "discount_pct": 0.0}
        sales = pd.DataFrame([row, row])
        sales = sales.astype({
            "store_id": "int64", "sku_id": "int64",
            "quantity": "int64", "customer_id": "Int64",
        })
        transformed, raw = self._make_datasets(sales_override=sales)
        report = validate_transformed_data(transformed, raw)
        assert report["sales"]["duplicates"] == 1

    def test_detects_invalid_total_value(self):
        sales = pd.DataFrame({
            "date": pd.to_datetime(["2025-01-01"]),
            "store_id": pd.array([1], dtype="int64"),
            "sku_id": pd.array([1001], dtype="int64"),
            "customer_id": pd.array([1], dtype="Int64"),
            "quantity": pd.array([2], dtype="int64"),
            "unit_price": [10.0],
            "total_value": [999.0],   # deliberately wrong
            "channel": ["Store"],
            "discount_pct": [0.0],
        })
        transformed, raw = self._make_datasets(sales_override=sales)
        report = validate_transformed_data(transformed, raw)
        assert report["sales"]["total_value_consistent"] is False
