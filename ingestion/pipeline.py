"""Orchestration entry point for the retail raw-data ingestion stage."""

from __future__ import annotations

import logging
import os
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
        logger.propagate = False
    return logger


def _persist_datasets(
    datasets: dict[str, pd.DataFrame], logger: logging.Logger, output_path: str | Path = "data/processed"
) -> None:
    """Write validated datasets to the durable intermediate-data location."""
    processed_path = Path(output_path)
    processed_path.mkdir(parents=True, exist_ok=True)

    for dataset_name, dataframe in datasets.items():
        file_output_path = processed_path / f"{dataset_name}_ingested.csv"
        try:
            dataframe.to_csv(file_output_path, index=False)
        except OSError:
            logger.exception("Failed to save ingested %s to %s", dataset_name, file_output_path)
            raise
        logger.info(
            "Saved ingested %s: rows=%d to %s",
            dataset_name,
            len(dataframe),
            file_output_path,
        )


def _resolve_source_path(data_path: str | Path) -> Path:
    """Accept either a raw-data directory or a project root containing data/raw."""
    requested_path = Path(data_path)
    if (requested_path / "bm_sales.csv").is_file():
        return requested_path

    nested_raw_path = requested_path / "data" / "raw"
    if (nested_raw_path / "bm_sales.csv").is_file():
        return nested_raw_path

    # Preserve the requested path so the reader raises a clear missing-file error.
    return requested_path


def run_ingestion(
    data_path: str | Path = "data/raw",
    output_path: str | Path = "data/processed",
) -> dict[str, pd.DataFrame]:
    """Load, validate, persist, and return every raw dataset by dataset key.

    ``data_path`` may point directly to the raw CSV directory or to a project
    root containing ``data/raw``.
    ``output_path`` specifies where validated ingested CSVs are saved.
    """
    source_path = _resolve_source_path(data_path)
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

    _persist_datasets(datasets, logger, output_path=output_path)
    logger.info("Ingestion completed successfully: datasets=%d", len(datasets))
    return datasets