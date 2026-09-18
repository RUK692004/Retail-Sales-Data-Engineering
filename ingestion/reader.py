"""Pandas readers for raw retail CSV files."""

from pathlib import Path
from typing import Union

import pandas as pd
from pandas.errors import EmptyDataError, ParserError

PathLike = Union[str, Path]


class DataReadError(RuntimeError):
    """Raised when a source CSV exists but cannot be read."""


def _read_csv(data_path: PathLike, filename: str) -> pd.DataFrame:
    """Read *filename* from *data_path* without changing source values."""
    file_path = Path(data_path) / filename
    try:
        return pd.read_csv(file_path)
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Required source file was not found: {file_path}") from exc
    except EmptyDataError as exc:
        raise DataReadError(f"Source file is empty: {file_path}") from exc
    except (ParserError, UnicodeDecodeError, OSError) as exc:
        raise DataReadError(f"Could not read source file {file_path}: {exc}") from exc


def load_sales(data_path: PathLike = "data/raw") -> pd.DataFrame:
    """Load `bm_sales.csv`."""
    return _read_csv(data_path, "bm_sales.csv")


def load_customers(data_path: PathLike = "data/raw") -> pd.DataFrame:
    """Load `bm_customers.csv`."""
    return _read_csv(data_path, "bm_customers.csv")


def load_skus(data_path: PathLike = "data/raw") -> pd.DataFrame:
    """Load `bm_skus.csv`."""
    return _read_csv(data_path, "bm_skus.csv")


def load_stores(data_path: PathLike = "data/raw") -> pd.DataFrame:
    """Load `bm_stores.csv`."""
    return _read_csv(data_path, "bm_stores.csv")


def load_inventory(data_path: PathLike = "data/raw") -> pd.DataFrame:
    """Load `bm_inventory.csv`."""
    return _read_csv(data_path, "bm_inventory.csv")


def load_promotions(data_path: PathLike = "data/raw") -> pd.DataFrame:
    """Load `bm_promotions.csv`."""
    return _read_csv(data_path, "bm_promotions.csv")
