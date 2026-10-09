
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent
RAW_DIR = ROOT / "data" / "raw"
REPORT_DIR = ROOT / "reports"

def inspect_dataset(file_path):
    """Load and inspect a CSV dataset."""
    df = pd.read_csv(file_path)

    print(f"\n{'=' * 70}")
    print(f"Dataset: {file_path.name}")
    print(f"Shape: {df.shape}")

    print("\nData types:")
    print(df.dtypes.to_string())

    print("\nFirst 5 rows:")
    print(df.head().to_string(index=False))

    missing = df.isnull().sum()
    missing = missing[missing > 0]

    print("\nMissing values:")
    if missing.empty:
        print("None")
    else:
        print(missing.to_string())

    return df


def validate_amfi_codes(dataframes):
    """Check whether fund-master AMFI codes exist in NAV history."""

    fund_master = dataframes["01_fund_master"]
    nav_history = dataframes["02_nav_history"]

    master_codes = set(fund_master["amfi_code"].dropna())
    nav_codes = set(nav_history["amfi_code"].dropna())

    missing_from_nav = master_codes - nav_codes
    unknown_in_master = nav_codes - master_codes

    print("\n" + "=" * 70)
    print("AMFI CODE VALIDATION")
    print(f"Unique codes in fund master: {len(master_codes)}")
    print(f"Unique codes in NAV history: {len(nav_codes)}")

    if not missing_from_nav:
        print("PASS: Every fund-master code exists in NAV history.")
    else:
        print("FAIL: Fund-master codes missing from NAV history:")
        print(sorted(missing_from_nav))

    if not unknown_in_master:
        print("PASS: Every NAV-history code exists in fund master.")
    else:
        print("WARNING: NAV codes absent from fund master:")
        print(sorted(unknown_in_master))

    return {
        "master_codes_missing_from_nav": sorted(missing_from_nav),
        "nav_codes_missing_from_master": sorted(unknown_in_master),
    }


def main():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    csv_files = sorted(RAW_DIR.glob("*.csv"))

    expected_datasets = [
        f"{i:02d}_" for i in range(1, 11)
    ]

    csv_files = sorted(
        file for file in RAW_DIR.glob("*.csv")
        if any(file.name.startswith(prefix) for prefix in expected_datasets)
    )

    if len(csv_files) != 10:
        raise ValueError(
            f"Expected 10 original datasets, found {len(csv_files)} in {RAW_DIR}"
        )

    dataframes = {}

    for file_path in csv_files:
        dataframes[file_path.stem] = inspect_dataset(file_path)

    validation_results = validate_amfi_codes(dataframes)


    # Save a concise data-quality summary.
    report_path = REPORT_DIR / "data_quality_summary.txt"

    with report_path.open("w", encoding="utf-8") as report:
        report.write("BLUESTOCK DATA INGESTION SUMMARY\n")
        report.write("=" * 50 + "\n")

        for name, df in dataframes.items():
            report.write(f"\nDataset: {name}.csv\n")
            report.write(f"Rows: {len(df)}\n")
            report.write(f"Columns: {len(df.columns)}\n")

            missing = df.isnull().sum()
            missing = missing[missing > 0]

            if missing.empty:
                report.write("Missing values: None\n")
            else:
                report.write("Missing values:\n")
                report.write(missing.to_string() + "\n")




        report.write("\n\nAMFI CODE VALIDATION\n")
        report.write("=" * 50 + "\n")

        report.write(
            f"Unique codes in fund master: "
            f"{len(dataframes['01_fund_master']['amfi_code'].unique())}\n"
        )
        report.write(
            f"Unique codes in NAV history: "
            f"{len(dataframes['02_nav_history']['amfi_code'].unique())}\n"
        )

        missing_nav = validation_results[
            "master_codes_missing_from_nav"
        ]

        unknown_master = validation_results[
            "nav_codes_missing_from_master"
        ]

        report.write(
            f"Fund-master codes missing from NAV history: "
            f"{len(missing_nav)}\n"
        )
        report.write(f"Codes: {missing_nav}\n")

        report.write(
            f"NAV codes missing from fund master: "
            f"{len(unknown_master)}\n"
        )
        report.write(f"Codes: {unknown_master}\n")

        report.write(
            "Result: "
            + (
                "PASS"
                if not missing_nav and not unknown_master
                else "REVIEW REQUIRED"
            )
            + "\n"
        )
    print(f"\nIngestion complete: {len(dataframes)} datasets loaded.")
    print(f"Quality summary saved to: {report_path}")


if __name__ == "__main__":
    main()
