"""Profile processed retail datasets and generate a Markdown report."""

from pathlib import Path

import pandas as pd


# Project directories
PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
DOCS_DIR = PROJECT_ROOT / "docs"
REPORT_FILE = DOCS_DIR / "data_profiling.md"


def profile_dataset(file_path: Path) -> str:
    """Generate a Markdown data-quality profile for one CSV dataset."""

    try:
        df = pd.read_csv(file_path)
    except (pd.errors.EmptyDataError, pd.errors.ParserError, OSError) as exc:
        return (
            f"## {file_path.name}\n\n"
            f"**ERROR:** Could not read dataset: `{exc}`\n"
        )

    report = []

    report.append(f"## {file_path.name}\n")

    # Basic information
    report.append("### Dataset Overview\n")
    report.append(f"- **Rows:** {len(df)}")
    report.append(f"- **Columns:** {len(df.columns)}")
    report.append(f"- **Duplicate rows:** {df.duplicated().sum()}\n")

    # Column information
    report.append("### Column Information\n")

    column_info = pd.DataFrame(
        {
            "Column": df.columns,
            "Data Type": df.dtypes.astype(str).values,
            "Null Count": df.isnull().sum().values,
            "Null %": (df.isnull().mean() * 100).round(2).values,
            "Unique Values": df.nunique(dropna=True).values,
        }
    )

    report.append(
        column_info.to_markdown(index=False)
    )
    report.append("")

    # Numeric summary
    numeric_columns = df.select_dtypes(include="number").columns

    if len(numeric_columns) > 0:
        report.append("### Numeric Summary\n")

        numeric_summary = (
            df[numeric_columns]
            .describe()
            .transpose()
            .round(2)
        )

        report.append(
            numeric_summary.to_markdown()
        )
        report.append("")

    # Missing values
    report.append("### Missing Values\n")

    missing_columns = df.columns[df.isnull().any()]

    if len(missing_columns) == 0:
        report.append("No missing values found.\n")
    else:
        report.append("| Column | Missing Count | Missing % |")
        report.append("|---|---:|---:|")

        for column in missing_columns:
            count = df[column].isnull().sum()
            percentage = (count / len(df)) * 100

            report.append(
                f"| {column} | {count} | {percentage:.2f}% |"
            )

        report.append("")

    # Sample records
    report.append("### Sample Records\n")

    sample = df.head(5)

    report.append(
        sample.to_markdown(index=False)
    )
    report.append("")

    return "\n".join(report)


def main() -> None:
    """Profile all processed CSV datasets and save a Markdown report."""

    if not PROCESSED_DATA_DIR.exists():
        print(
            f"Processed data directory not found: "
            f"{PROCESSED_DATA_DIR}"
        )
        return

    csv_files = sorted(PROCESSED_DATA_DIR.glob("*.csv"))

    if not csv_files:
        print(
            f"No CSV files found in: "
            f"{PROCESSED_DATA_DIR}"
        )
        return

    # Create docs directory if it doesn't exist
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    report = []

    report.append("# Processed Data Profiling Report\n")
    report.append(
        "This report summarizes the structure and data quality "
        "of the processed retail datasets before transformation.\n"
    )

    report.append(
        f"**Datasets profiled:** {len(csv_files)}\n"
    )

    # Profile each dataset
    for file_path in csv_files:
        print(f"Profiling: {file_path.name}")

        dataset_report = profile_dataset(file_path)

        report.append(dataset_report)

    # Save Markdown report
    REPORT_FILE.write_text(
        "\n".join(report),
        encoding="utf-8",
    )

    print("\nProfiling completed successfully.")
    print(f"Report saved to: {REPORT_FILE}")


if __name__ == "__main__":
    main()