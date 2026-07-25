import pandas as pd
from pathlib import Path



PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

# Create processed folder if it doesn't exist
PROCESSED_DIR.mkdir(exist_ok=True)


# Dictionary to store all datasets
datasets = {}


for file in RAW_DIR.glob("*.csv"):

    print(f"Reading {file.name}...")

    df = pd.read_csv(file)

    datasets[file.stem] = df

print("\nInspecting datasets...\n")

for name, df in datasets.items():

    print("=" * 60)
    print(f"DATASET: {name.upper()}")

    print("\nShape:")
    print(df.shape)

    print("\nColumns:")
    print(df.columns.tolist())

    print("\nData Types:")
    print(df.dtypes)

    print("\nMissing Values:")
    print(df.isnull().sum())

    print("\nFirst 5 Rows:")
    print(df.head())

    print("\n")