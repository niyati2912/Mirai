# ETL Pipeline

## Overview

The ETL (Extract, Transform, Load) pipeline is responsible for collecting, organizing, cleaning, and preparing economic data before it is used for feature engineering and machine learning.

**Current Status**

- Completed: Extract
- In Progress: Transform
- Pending: Load

---

# ETL Architecture

```text
                Data Sources
       ┌──────────┬──────────┬────────────┐
       │          │          │            │
    FRED API  Yahoo Finance  World Bank API
       │          │          │
       └──────────┴──────────┴────────────┘
                     │
                     ▼
                data/raw/*.csv
                     │
                     ▼
               ETL Pipeline
                     │
      ┌──────────────┼──────────────┐
      │              │              │
 Load Datasets  Profile Data  Validate Schema
      │              │              │
      └──────────────┴──────────────┘
                     │
                     ▼
         Data Cleaning & Transformation
                     │
                     ▼
      data/processed/master_dataset.csv
```

---

# Phase 1 — Extract

## Objective

Collect economic and financial data from multiple trusted sources and store them in a common raw data repository.

## Data Sources

### FRED

Macroeconomic indicators:

- Consumer Price Index (CPI)
- Unemployment Rate
- Federal Funds Rate
- Industrial Production
- Consumer Sentiment
- India CPI
- India GDP
- USD/INR Exchange Rate

### Yahoo Finance

Financial market indicators:

- S&P 500
- NASDAQ
- Gold
- Silver
- Crude Oil
- Brent Oil
- Dollar Index
- NIFTY 50
- Sensex

### World Bank

India economic indicators:

- GDP Growth
- Inflation
- Imports
- Exports
- Unemployment

---

# Current Folder Structure

```text
data/
├── raw/
│   ├── cpi.csv
│   ├── unemployment.csv
│   ├── interest_rate.csv
│   ├── industrial_production.csv
│   ├── consumer_sentiment.csv
│   ├── sp500.csv
│   ├── nasdaq.csv
│   ├── gold.csv
│   ├── silver.csv
│   ├── oil.csv
│   ├── brent_oil.csv
│   ├── dollar_index.csv
│   ├── nifty50.csv
│   ├── sensex.csv
│   ├── india_cpi.csv
│   ├── india_gdp.csv
│   ├── inflation_india.csv
│   ├── imports_india.csv
│   ├── exports_india.csv
│   └── unemployment_india.csv

└── processed/
```

---

# Phase 2 — Transform (Current)

The current ETL implementation focuses on automatically discovering datasets and inspecting their structure before cleaning.

## Automatic Dataset Discovery

Instead of manually loading each CSV,

```python
pd.read_csv("cpi.csv")
pd.read_csv("gold.csv")
pd.read_csv("oil.csv")
```

the pipeline scans the entire directory automatically.

```python
for file in RAW_DIR.glob("*.csv"):
```

### Benefits

- Automatically detects newly added datasets.
- Eliminates hardcoded file loading.
- Makes the pipeline scalable.

---

## Dynamic DataFrame Storage

Each dataset is stored inside a Python dictionary.

```python
datasets = {
    "cpi": DataFrame,
    "gold": DataFrame,
    "sp500": DataFrame,
    ...
}
```

This allows every dataset to be processed using loops rather than repetitive code.

Example:

```python
for name, df in datasets.items():
```

Benefits:

- One transformation can be applied to every dataset.
- No additional code is required when new datasets are added.
- Simplifies future maintenance.

---

## Dataset Profiling

Each dataset is automatically inspected for:

- Number of rows and columns
- Column names
- Data types
- Missing values
- Sample records

This stage helps identify structural issues before any transformations are performed.

---

# Observations from Data Profiling

The current profiling stage revealed several inconsistencies that will be addressed during transformation.

## Yahoo Finance

Issues identified:

- Metadata rows (`Ticker`, `Date`) appear at the beginning of the dataset.
- Multi-level headers require cleaning.
- Numeric columns are currently interpreted as strings.

---

## FRED

Issues identified:

- Date column is stored as `Unnamed: 0`.
- Requires renaming.
- Date column must be converted to datetime format.

---

## World Bank

Issues identified:

- Uses yearly integer values for dates.
- Requires conversion into datetime format.

---

## Mixed Frequencies

Different datasets use different time resolutions.

Examples:

- Daily
- Monthly
- Quarterly
- Yearly

These must be standardized before merging.

---

# Upcoming Transform Stages

## Stage 1

Standardize column names.

Tasks:

- Rename `Unnamed: 0` to `Date`
- Remove inconsistent naming

---

## Stage 2

Convert all date columns to datetime format.

---

## Stage 3

Convert numeric columns to appropriate numeric data types.

---

## Stage 4

Handle missing values.

Possible techniques:

- Forward Fill
- Backward Fill
- Interpolation
- Removal (where appropriate)

---

## Stage 5

Standardize data frequency.

Example:

- Daily → Monthly
- Quarterly → Monthly
- Yearly → Monthly

---

## Stage 6

Merge all datasets into a single master dataset.

Output:

```text
data/processed/master_dataset.csv
```

---

# ETL Pipeline Roadmap

```text
Raw APIs
     │
     ▼
CSV Generation
     │
     ▼
Automatic Dataset Discovery
     │
     ▼
Dictionary-Based Storage
     │
     ▼
Dataset Profiling
     │
     ▼
Data Cleaning
     │
     ▼
Date Standardization
     │
     ▼
Frequency Alignment
     │
     ▼
Dataset Merging
     │
     ▼
Master Dataset
     │
     ▼
Feature Engineering
     │
     ▼
Machine Learning Models
```

---

# Current Progress

| Phase | Status |
|--------|--------|
| Extract | Completed |
| Dataset Discovery | Completed |
| Automated Loading | Completed |
| Data Profiling | Completed |
| Data Cleaning | In Progress |
| Date Standardization | Pending |
| Frequency Alignment | Pending |
| Dataset Merge | Pending |
| Feature Engineering | Pending |
| Machine Learning | Pending |