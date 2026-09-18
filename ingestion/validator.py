"""Schema and basic data-health validation for raw datasets."""

from __future__ import annotations

import logging
from typing import Any, Mapping

import pandas as pd
from pandas.api.types import is_numeric_dtype

LOGGER = logging.getLogger(__name__)


class SchemaValidationError(ValueError):
    """Raised when a raw dataset does not meet its required schema."""


REQUIRED_COLUMNS: Mapping[str, set[str]] = {
    "sales": {
        "date", "store_id", "sku_id", "customer_id", "quantity",
        "unit_price", "total_value",
    },
    "customers": {"cust_id", "age", "gender", "city", "loyalty_segment"},
    "skus": {"sku_id", "sku_name", "category", "unit_price", "cost_price"},
    "stores": {"store_id", "store_name", "city", "store_type"},
    "inventory": {
        "store_id", "sku_id", "stock_on_hand", "reorder_point", "safety_stock",
    },
    "promotions": {
        "promo_id", "promo_name", "start_date", "end_date", "discount_pct", "promo_type",
    },
}

IDENTIFIER_COLUMNS: Mapping[str, tuple[str, ...]] = {
    "sales": ("store_id", "sku_id", "customer_id"),
    "customers": ("cust_id",),
    "skus": ("sku_id",),
    "stores": ("store_id",),
    "inventory": ("store_id", "sku_id"),
    "promotions": ("promo_id",),
}


def validate_dataframe(name: str, dataframe: pd.DataFrame) -> dict[str, Any]:
    """Validate one DataFrame and return a basic health report.

    Missing values and duplicate rows are reported, not changed or rejected;
    those business-quality decisions belong to the transformation stage.
    """
    if name not in REQUIRED_COLUMNS:
        raise ValueError(f"Unknown dataset {name!r}. Expected: {sorted(REQUIRED_COLUMNS)}")
    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError(f"{name} must be a pandas DataFrame")

    missing_columns = REQUIRED_COLUMNS[name].difference(dataframe.columns)
    if missing_columns:
        message = f"{name} is missing required columns: {sorted(missing_columns)}"
        LOGGER.error(message)
        raise SchemaValidationError(message)

    invalid_identifiers = [
        column
        for column in IDENTIFIER_COLUMNS[name]
        if not is_numeric_dtype(dataframe[column])
    ]
    if invalid_identifiers:
        message = f"{name} has non-numeric identifier columns: {invalid_identifiers}"
        LOGGER.error(message)
        raise SchemaValidationError(message)

    report: dict[str, Any] = {
        "dataset": name,
        "shape": dataframe.shape,
        "row_count": len(dataframe),
        "column_count": len(dataframe.columns),
        "missing_values": dataframe.isna().sum().astype(int).to_dict(),
        "duplicate_rows": int(dataframe.duplicated().sum()),
        "data_types": {column: str(dtype) for column, dtype in dataframe.dtypes.items()},
    }
    LOGGER.info(
        "Validation passed for %s: rows=%d duplicates=%d",
        name,
        report["row_count"],
        report["duplicate_rows"],
    )
    return report


def validate_all(datasets: Mapping[str, pd.DataFrame]) -> dict[str, dict[str, Any]]:
    """Validate every named dataset and return reports keyed by dataset name."""
    return {name: validate_dataframe(name, frame) for name, frame in datasets.items()}
