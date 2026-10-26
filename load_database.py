
from pathlib import Path
import sqlite3
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
DB_DIR = BASE_DIR / "data" / "db"
DB_PATH = DB_DIR / "database.db"
SCHEMA_PATH = BASE_DIR / "sql" / "schema.sql"

DATASETS = {
    "fund_master": "01_fund_master_cleaned.csv",
    "nav_history": "02_nav_history_cleaned.csv",
    "aum_by_fund_house": "03_aum_by_fund_house_cleaned.csv",
    "monthly_sip_inflows": "04_monthly_sip_inflows_cleaned.csv",
    "category_inflows": "05_category_inflows_cleaned.csv",
    "industry_folio_count": "06_industry_folio_count_cleaned.csv",
    "scheme_performance": "07_scheme_performance_cleaned.csv",
    "investor_transactions": "08_investor_transactions_cleaned.csv",
    "portfolio_holdings": "09_portfolio_holdings_cleaned.csv",
    "benchmark_indices": "10_benchmark_indices_cleaned.csv",
}


def main():
    DB_DIR.mkdir(parents=True, exist_ok=True)

    missing = [
        filename
        for filename in DATASETS.values()
        if not (PROCESSED_DIR / filename).exists()
    ]
    if missing:
        raise FileNotFoundError(f"Missing cleaned datasets: {missing}")

    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(f"Schema not found: {SCHEMA_PATH}")

    schema = SCHEMA_PATH.read_text(encoding="utf-8")

    with sqlite3.connect(DB_PATH) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.executescript(schema)

        for table, filename in DATASETS.items():
            path = PROCESSED_DIR / filename
            df = pd.read_csv(path)

            # SQLite should store missing numeric values as NULL.
            df = df.astype(object).where(pd.notna(df), None)

            # Replace table contents on each run to avoid duplicate rows.
            connection.execute(f'DELETE FROM "{table}"')
            df.to_sql(table, connection, if_exists="append", index=False)

            count = connection.execute(
                f'SELECT COUNT(*) FROM "{table}"'
            ).fetchone()[0]

            print(f"Loaded {table}: {count:,} rows")

        violations = connection.execute(
            "PRAGMA foreign_key_check"
        ).fetchall()

        if violations:
            print("\nForeign key violations found:")
            for violation in violations[:10]:
                print(violation)
            raise RuntimeError("Database foreign key validation failed.")

        print("\nForeign key check: PASS")

    print(f"Database saved to: {DB_PATH}")


if __name__ == "__main__":
    main()
