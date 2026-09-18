"""Orchestration entry point for the retail raw-data ingestion stage."""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from .reader import (
    load_customers,
    load_inventory,
    load_promotions,
    load_sales,
    load_skus,
    load_stores,
)
from .validator import validate_dataframe


def _get_logger() -> logging.Logger:
    """Return a console logger without adding duplicate handlers."""
    logger = logging.getLogger("ingestion")
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
        )
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


def run_ingestion(data_path: str | Path = "data/raw") -> dict[str, pd.DataFrame]:
    """Load and validate every raw dataset, returning DataFrames by dataset key."""
    source_path = Path(data_path)
    logger = _get_logger()
    logger.info("Starting ingestion from %s", source_path)

    loaders = {
        "sales": load_sales,
        "customers": load_customers,
        "skus": load_skus,
        "stores": load_stores,
        "inventory": load_inventory,
        "promotions": load_promotions,
    }
    datasets: dict[str, pd.DataFrame] = {}

    for dataset_name, loader in loaders.items():
        try:
            dataframe = loader(source_path)
            logger.info(
                "Loaded %s: rows=%d columns=%d",
                dataset_name,
                len(dataframe),
                len(dataframe.columns),
            )
            validate_dataframe(dataset_name, dataframe)
        except Exception:
            logger.exception("Ingestion failed for dataset=%s", dataset_name)
            raise
        datasets[dataset_name] = dataframe

    logger.info("Ingestion completed successfully: datasets=%d", len(datasets))
    return datasets
