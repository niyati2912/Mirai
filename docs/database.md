# Database Design

## Overview

Mirai follows a staged data architecture.

Instead of storing incoming data directly inside a relational database, all data is first collected as raw CSV files. These files are cleaned, standardized, and transformed through the ETL pipeline before being loaded into a structured dataset.

This approach keeps the original data unchanged while allowing reproducible transformations.

---

# Current Architecture

```text
               External APIs
        ┌──────────┬──────────┬──────────┐
        │          │          │          │
     FRED API  Yahoo Finance  World Bank
        │          │          │
        └──────────┴──────────┴──────────┘
                     │
                     ▼
               data/raw/*.csv
                     │
                     ▼
               ETL Pipeline
                     │
                     ▼
      data/processed/master_dataset.csv
```

At the current stage of development, CSV files act as the project's primary data storage.

---

# Data Storage Structure

```text
data/
├── raw/
│
├── processed/
│
└── models/
```

## data/raw/

Contains unmodified data downloaded directly from external sources.

Characteristics:

- Immutable
- Source-specific
- Original formatting preserved

Examples:

- cpi.csv
- unemployment.csv
- gold.csv
- sp500.csv
- india_gdp.csv

---

## data/processed/

Contains cleaned and transformed datasets produced by the ETL pipeline.

Characteristics:

- Standardized columns
- Consistent date format
- Missing values handled
- Ready for feature engineering

Future file:

```text
master_dataset.csv
```

---

## models/

Reserved for serialized machine learning models.

Future examples:

```text
economic_stress_model.pkl
forecast_model.pkl
```

---

# Data Sources

| Source | Data |
|---------|------|
| FRED | Macroeconomic indicators |
| Yahoo Finance | Financial market indicators |
| World Bank | India economic indicators |

---

# Current Dataset Inventory

## Macroeconomic Indicators

- CPI
- Unemployment
- Interest Rate
- Industrial Production
- Consumer Sentiment

---

## Financial Indicators

- S&P 500
- NASDAQ
- Gold
- Silver
- Crude Oil
- Brent Oil
- Dollar Index

---

## India Indicators

- GDP
- CPI
- Inflation
- Imports
- Exports
- Unemployment
- USD/INR
- NIFTY 50
- Sensex

---

# Planned Database Schema

After the ETL pipeline is complete, all datasets will be merged into a unified dataset.

Example schema:

| Column | Type |
|----------|---------|
| Date | DATE |
| CPI | FLOAT |
| Unemployment | FLOAT |
| InterestRate | FLOAT |
| IndustrialProduction | FLOAT |
| ConsumerSentiment | FLOAT |
| SP500 | FLOAT |
| NASDAQ | FLOAT |
| Gold | FLOAT |
| Silver | FLOAT |
| Oil | FLOAT |
| BrentOil | FLOAT |
| DollarIndex | FLOAT |
| IndiaGDP | FLOAT |
| IndiaCPI | FLOAT |
| InflationIndia | FLOAT |
| ImportsIndia | FLOAT |
| ExportsIndia | FLOAT |
| USDINR | FLOAT |
| NIFTY50 | FLOAT |
| Sensex | FLOAT |

Additional engineered features will be added later.

---

# Future Database

As Mirai grows, CSV-based storage will be replaced with PostgreSQL.

Planned architecture:

```text
External APIs
      │
      ▼
Raw Data
      │
      ▼
ETL Pipeline
      │
      ▼
PostgreSQL
      │
      ├── Economic Indicators
      ├── Financial Markets
      ├── Engineered Features
      ├── Forecast Results
      └── Model Metadata
```

Benefits:

- Faster querying
- Better scalability
- Concurrent access
- Easier integration with backend APIs

---

# Design Principles

- Preserve raw data.
- Never overwrite original datasets.
- Separate raw and processed data.
- Automate all data ingestion.
- Ensure reproducibility of transformations.
- Maintain a single source of truth for model training.

---

# Current Status

| Component | Status |
|-----------|--------|
| Raw Data Storage | Completed |
| Automated Data Collection | Completed |
| Processed Data Storage | In Progress |
| Master Dataset | Pending |
| PostgreSQL Integration | Planned |