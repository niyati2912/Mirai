import pandas as pd
from pathlib import Path



PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"



PROCESSED_DIR.mkdir(exist_ok=True)



datasets = {}


for file in RAW_DIR.glob("*.csv"):
    df = pd.read_csv(file)
    datasets[file.stem] = df


for name, df in datasets.items():

    print("=" * 60)
    print(name.upper())

    print(df.shape)
    print(df.columns.tolist())
    print(df.dtypes)
    print(df.isnull().sum())
    print(df.head())


for name, df in datasets.items():

    if "Unnamed: 0" in df.columns:
        df.rename(columns={"Unnamed: 0": "Date"}, inplace=True)

    elif "date" in df.columns:
        df.rename(columns={"date": "Date"}, inplace=True)



print("\nChecking standardized columns...\n")

for name, df in datasets.items():
    print(f"{name}: {df.columns.tolist()}")



def clean_yahoo_dataset(df):
    df.rename(columns={"Price": "Date"}, inplace=True)
    df = df.iloc[2:].reset_index(drop=True)

    return df

def convert_date_column(df):
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    return df

for name, df in datasets.items():

    if "Price" in df.columns:

        datasets[name] = clean_yahoo_dataset(df)


for name, df in datasets.items():

    if "Close" in df.columns:

        print("=" * 50)
        print(name.upper())
        print(df.head())

for name, df in datasets.items():

    datasets[name] = convert_date_column(df)


    print("\nChecking Date data types...\n")

for name, df in datasets.items():

    if "Date" in df.columns:

        print(f"{name}: {df['Date'].dtype}")

print("\nSample dates...\n")

for name, df in datasets.items():

    if "Date" in df.columns:

        print(f"{name}: {df['Date'].head(3).tolist()}")


def convert_numeric_columns(df):
    for col in df.columns:
        if col != "Date":
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

for name, df in datasets.items():
    datasets[name] = convert_numeric_columns(df)


print("\nChecking data types...\n")

for name, df in datasets.items():

    print("=" * 50)
    print(name)
    print(df.dtypes)


print("\nChecking missing values after numeric conversion...\n")

for name, df in datasets.items():

    missing = df.isnull().sum().sum()

    print(f"{name}: {missing}")