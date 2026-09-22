"""Public interface for raw retail-data ingestion."""

from .pipeline import run_ingestion

__all__ = ["run_ingestion"]
