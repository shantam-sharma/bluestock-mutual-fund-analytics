
from pathlib import Path
import pandas as pd

DATA_DIR = Path("data/raw")

csv_files = sorted(DATA_DIR.glob("*.csv"))

print(f"Found {len(csv_files)} CSV files\n")

for file in csv_files:
    print("=" * 70)
    print(f"FILE: {file.name}")

    try:
        df = pd.read_csv(file)

        print(f"Shape: {df.shape}")
        print("\nColumns and data types:")
        print(df.dtypes)
        print("\nFirst 5 rows:")
        print(df.head())
        print("\nMissing values:")
        print(df.isnull().sum())
        print()

    except Exception as error:
        print(f"Could not read file: {error}")
