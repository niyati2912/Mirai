               EXTRACT
        --------------------
        FRED
        Yahoo Finance
        World Bank
              │
              ▼
          data/raw/
              │
              ▼
            ETL.py
      ┌─────────────────┐
      │ Read CSVs       │
      │ Standardize     │
      │ Clean           │
      │ Resample        │
      │ Merge           │
      │ Save            │
      └─────────────────┘
              │
              ▼
    data/processed/master_dataset.csv
              │
              ▼
    Feature Engineering
              │
              ▼
      Machine Learning
              │
              ▼
      Economic Stress Index
              │
              ▼
      Forecast & Dashboard