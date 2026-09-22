"""
BlueMart Retail Sales Data Engineering Pipeline
Member 4 (Kevin) — orchestration.

Status: ingest_csv, transform_data, and load_database call the real
Members 1/2/3 code. run_quality_checks is still a placeholder — no one
has written real post-load quality checks yet (row counts, null PKs,
duplicate transactions, referential integrity).

Pipeline data flow on disk (all under /opt/airflow/project, mounted
from the repo's data/ folder):
  data/raw/*.csv                    (Member 1 input, bm_*.csv)
    -> ingest_csv -> data/processed/*_ingested.csv
    -> transform_data -> data/transformed/*_transformed.csv
    -> load_database -> retail_sales_dw (warehouse-postgres service)

Star schema (database/schema/create_tables.sql, Member 3):
  dim_date, dim_customer, dim_product, dim_store, dim_promotion
  fact_sales(date_key, store_key, product_key, customer_key, channel,
             quantity, unit_price, discount_pct, total_value)
  customer_key is nullable — anonymous/walk-in sales have no customer.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta

from airflow.sdk import dag, task

log = logging.getLogger(__name__)

default_args = {
    "owner": "kevin",
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
    "email_on_failure": False,  # flip to True + set 'email' key if you wire up alerting
}


@dag(
    dag_id="retail_sales_pipeline",
    description="BlueMart retail sales ETL: ingest -> validate -> transform -> load -> quality check",
    schedule=None,  # manually triggered for now; not a recurring job
    start_date=datetime(2026, 1, 1),
    catchup=False,
    default_args=default_args,
    tags=["bluemart", "retail", "etl"],
)
def retail_sales_pipeline():

    @task
    def ingest_csv() -> dict:
        """Runs Member 1's real ingestion (ingestion/pipeline.py).
        Reads the six raw bm_*.csv files, validates them, and writes
        *_ingested.csv into data/processed. Returns row counts per dataset."""
        import sys
        sys.path.insert(0, "/opt/airflow/project")
        from ingestion import run_ingestion

        datasets = run_ingestion(
            data_path="/opt/airflow/project/data/raw",
            output_path="/opt/airflow/project/data/processed",
        )
        row_counts = {name: len(df) for name, df in datasets.items()}
        log.info(f"Ingested row counts: {row_counts}")
        return {"row_counts": row_counts, "row_count": row_counts.get("sales", 0)}

    @task
    def validate_data(ingest_result: dict) -> dict:
        """Lightweight sanity check on ingestion's own output.
        NOTE: Member 1's ingestion already runs real per-dataset validation
        internally (ingestion/validator.py) and would have raised before
        this task even runs if something was wrong. This task just confirms
        every expected dataset actually produced rows before moving on."""
        row_counts = ingest_result.get("row_counts", {})
        empty = [name for name, count in row_counts.items() if count == 0]
        if empty:
            raise ValueError(f"These datasets ingested with zero rows: {empty}")
        log.info(f"All datasets have rows: {row_counts}")
        return {"validated": True, "row_counts": row_counts}

    @task
    def transform_data(validate_result: dict) -> dict:
        """Runs Member 2's real transformation (transformation/transform.py).
        Reads data/processed/*_ingested.csv (default paths already line up
        correctly), cleans/transforms, writes *_transformed.csv into
        data/transformed. Returns the validation report it produces."""
        import sys
        sys.path.insert(0, "/opt/airflow/project")
        from transformation.transform import run_transformation_pipeline

        report = run_transformation_pipeline(
            input_dir="/opt/airflow/project/data/processed",
            output_dir="/opt/airflow/project/data/transformed",
        )
        log.info(f"Transformation validation report: {report}")
        return {"transformed": True, "report": report}

    @task
    def load_database(transform_result: dict) -> dict:
        """Runs Member 3's real warehouse loader (database/load_data.py).
        Loads dim_customer, dim_product, dim_store, dim_promotion first,
        then truncates + reloads fact_sales, then upserts fact_inventory.

        NOTE ON THE HANDOFF: load_data.py does NOT take the transformed
        DataFrame as a Python argument — it reads fixed-named CSVs
        (customers_ingested.csv, sales_ingested.csv, etc.) from
        data/processed/. So the real contract with Member 2's
        transformation step is: those exact files must exist on disk
        before this task runs, not an in-memory handoff.

        DB_HOST/DB_NAME/DB_USER/DB_PASSWORD are already set as container
        env vars (see docker-compose.yaml) and point at the
        warehouse-postgres service — a separate database from Airflow's
        own metadata Postgres."""
        import sys
        sys.path.insert(0, "/opt/airflow/project")
        from database.load_data import main as load_main

        log.info(f"Transformation report from previous task: {transform_result.get('report')}")
        log.info("Loading transformed data into the warehouse")
        try:
            load_main()
        except SystemExit as exc:
            # load_data.py calls sys.exit(1) on fatal errors (missing
            # DB_PASSWORD, missing INPUT_DIR, etc.) instead of raising a
            # normal exception. sys.exit() inside a task would otherwise
            # kill the whole Airflow worker process, not just this task —
            # converting it to a RuntimeError here makes Airflow correctly
            # mark just this task as failed.
            raise RuntimeError(f"database/load_data.py exited with code {exc.code}") from exc
        return {"loaded": True}

    @task
    def run_quality_checks(load_result: dict) -> None:
        """PLACEHOLDER for post-load data quality checks."""
        if not load_result.get("loaded"):
            raise ValueError("Load did not complete — failing quality checks")
        log.info("Placeholder: quality checks passed")
        # TODO: real checks — row counts, null PKs, duplicate transactions,
        # invalid quantities/prices, referential integrity

    # dependency chain
    ingested = ingest_csv()
    validated = validate_data(ingested)
    transformed = transform_data(validated)
    loaded = load_database(transformed)
    run_quality_checks(loaded)


retail_sales_pipeline()
