
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def clean_nav_history(df):
    """Validate NAV records and fill weekends and holidays per scheme."""
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d", errors="coerce")
    df["nav"] = pd.to_numeric(df["nav"], errors="coerce")
    df["amfi_code"] = pd.to_numeric(df["amfi_code"], errors="coerce")

    df = df.dropna(subset=["amfi_code", "date", "nav"])
    df = df[df["nav"] > 0]
    df["amfi_code"] = df["amfi_code"].astype("int64")
    df = df.drop_duplicates(subset=["amfi_code", "date"], keep="last")
    df = df.sort_values(["amfi_code", "date"])

    filled_groups = []

    for code, group in df.groupby("amfi_code"):
        group = group.set_index("date").sort_index()
        full_dates = pd.date_range(
            group.index.min(), group.index.max(), freq="D"
        )
        group = group.reindex(full_dates)
        group["amfi_code"] = code
        group["nav"] = group["nav"].ffill()
        group.index.name = "date"
        filled_groups.append(group.reset_index())

    if not filled_groups:
        return pd.DataFrame(columns=["amfi_code", "date", "nav"])

    result = pd.concat(filled_groups, ignore_index=True)
    return result[["amfi_code", "date", "nav"]].sort_values(
        ["amfi_code", "date"]
    )


def clean_investor_transactions(df):
    """Standardize transaction fields and validate amounts and dates."""
    df = df.copy()

    df["transaction_date"] = pd.to_datetime(
        df["transaction_date"], format="%Y-%m-%d", errors="coerce"
    )
    df["amount_inr"] = pd.to_numeric(df["amount_inr"], errors="coerce")

    # Invalid dates and non-positive amounts cannot be used reliably.
    df = df.dropna(subset=["transaction_date", "amount_inr", "amfi_code"])
    df = df[df["amount_inr"] > 0]

    df["transaction_type"] = (
        df["transaction_type"].astype("string").str.strip().str.upper()
    )
    df["transaction_type"] = df["transaction_type"].replace({
        "SYSTEMATIC INVESTMENT PLAN": "SIP",
        "LUMP SUM": "LUMPSUM",
        "LUMP-SUM": "LUMPSUM",
        "LUMPSUM INVESTMENT": "LUMPSUM",
    })

    df["kyc_status"] = (
        df["kyc_status"].astype("string").str.strip().str.upper()
    )

    return df.drop_duplicates()


def clean_scheme_performance(df):
    """Convert performance metrics and flag unusual expense ratios."""
    df = df.copy()

    numeric_columns = [
        "return_1yr_pct",
        "return_3yr_pct",
        "return_5yr_pct",
        "benchmark_3yr_pct",
        "alpha",
        "beta",
        "sharpe_ratio",
        "sortino_ratio",
        "std_dev_ann_pct",
        "max_drawdown_pct",
        "aum_crore",
        "expense_ratio_pct",
        "morningstar_rating",
    ]

    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    # Keep suspicious values for investigation rather than deleting funds.
    if "expense_ratio_pct" in df.columns:
        df["expense_ratio_out_of_range"] = ~df[
            "expense_ratio_pct"
        ].between(0.1, 2.5, inclusive="both")

    return df.drop_duplicates()


def main():
    csv_files = [
        RAW_DIR / f"{i:02d}_{name}.csv"
        for i, name in [
            (1, "fund_master"),
            (2, "nav_history"),
            (3, "aum_by_fund_house"),
            (4, "monthly_sip_inflows"),
            (5, "category_inflows"),
            (6, "industry_folio_count"),
            (7, "scheme_performance"),
            (8, "investor_transactions"),
            (9, "portfolio_holdings"),
            (10, "benchmark_indices"),
        ]
    ]
    missing_files = [path.name for path in csv_files if not path.exists()]
    if missing_files:
        raise FileNotFoundError(f"Missing original datasets: {missing_files}")

    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {RAW_DIR}")

    if len(csv_files) != 10:
        print(f"WARNING: Expected 10 CSV files; found {len(csv_files)}.")

    summary = []

    for file_path in csv_files:
        try:
            df = pd.read_csv(file_path)
            original_rows = len(df)

            if file_path.name == "02_nav_history.csv":
                df = clean_nav_history(df)
            elif file_path.name == "08_investor_transactions.csv":
                df = clean_investor_transactions(df)
            elif file_path.name == "07_scheme_performance.csv":
                df = clean_scheme_performance(df)
            else:
                df = df.drop_duplicates()

            output_name = file_path.stem + "_cleaned.csv"
            output_path = PROCESSED_DIR / output_name
            df.to_csv(output_path, index=False, date_format="%Y-%m-%d")

            summary.append({
                "file": file_path.name,
                "source_rows": original_rows,
                "cleaned_rows": len(df),
                "row_count_change": len(df) - original_rows,
                "missing_cells": int(df.isna().sum().sum()),
                "output": str(output_path.relative_to(BASE_DIR)),
            })

            print(
                f"OK: {file_path.name}: {original_rows:,} -> "
                f"{len(df):,} rows; saved {output_name}"
            )

        except Exception as error:
            print(f"ERROR processing {file_path.name}: {error}")

    if summary:
        report_path = PROCESSED_DIR / "cleaning_summary.csv"
        pd.DataFrame(summary).to_csv(report_path, index=False)
        print(f"\nSummary saved to {report_path}")

    if len(summary) != len(csv_files):
        raise RuntimeError(
            "One or more datasets failed. Review the errors above."
        )


if __name__ == "__main__":
    main()
