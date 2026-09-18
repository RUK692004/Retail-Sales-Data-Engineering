"""Utility functions for data transformation, logging, and path resolution."""

import logging
from pathlib import Path


def get_logger(name: str = "transformation") -> logging.Logger:
    """Configure and return a standardized logger."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


def resolve_paths(project_root: Path | None = None) -> tuple[Path, Path, Path]:
    """Resolve project root, input processed data dir, and output transformed data dir."""
    if project_root is None:
        project_root = Path(__file__).resolve().parents[1]
    input_dir = project_root / "data" / "processed"
    output_dir = project_root / "data" / "transformed"
    return project_root, input_dir, output_dir
