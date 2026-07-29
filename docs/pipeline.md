# MIRAI — Predicting Tomorrow's Economy Using Today's Invisible Signals

## Current Pipeline

```text
                           RAW DATA
                                │
      ┌─────────────────────────┼─────────────────────────┐
      │                         │                         │
 Yahoo Finance             FRED API              Other Economic Data
 (Markets & Commodities)   (Macro Indicators)    (GDP, CPI, USD-INR, etc.)
      │                         │                         │
      └─────────────────────────┴─────────────────────────┘
                                │
                                ▼
                         ETL Pipeline (etl.py)
                 Fetches and stores raw datasets
                                │
                                ▼
               Time Alignment (time_alignment.py)
       Cleans, merges and aligns all datasets by Date
                                │
                                ▼
           Master Dataset (master_dataset.csv)
                                │
                                ▼
            Feature Engineering (feature.py)
      • Percentage Change
      • Rolling Mean
      • Rolling Volatility
      • Momentum
      • Lag Features
      • Time Features
                                │
                                ▼
           Feature Table (feature_table.csv)
                                │
                                ▼
         Economic Stress Score Builder
               (ess_builder.py)
      • Rolling Z-Score Normalization
      • Category-wise Stress Scores
      • Weighted Composite ESS
      • Scale ESS to 0–100
      • Generate Future ESS Target
                                │
                                ▼
          Machine Learning Model
             (train_model.py)
      • Chronological Train/Test Split
      • Random Forest Regressor
      • Feature Importance Analysis
      • Model Evaluation
                                │
                                ▼
                 Trained Model
          models/ess_model.pkl
                                │
                                ▼
              Future Prediction
          Economic Stress Score
```

---

# Project Structure

```text
Mirai/
│
├── data/
│   ├── raw/
│   └── processed/
│       ├── master_dataset.csv
│       └── feature_table.csv
│
├── models/
│   ├── ess_model.pkl
│   ├── feature_importances.csv
│   └── ess_prediction_plot.png
│
├── scripts/
│   ├── etl.py
│   ├── time_alignment.py
│   ├── feature.py
│   ├── ess_builder.py
│   └── train_model.py
│
├── README.md
└── requirements.txt
```

---

# Current Workflow

```text
Raw Economic Data
        │
        ▼
ETL
        │
        ▼
Time Alignment
        │
        ▼
Feature Engineering
        │
        ▼
Economic Stress Score (ESS)
        │
        ▼
ESS Target Generation
        │
        ▼
Random Forest Training
        │
        ▼
Model Evaluation
        │
        ▼
ESS Prediction
```

---

# Current Features

- Multi-source economic data integration
- Automated ETL pipeline
- Time-series alignment
- Feature engineering
- Economic Stress Score (ESS) generation
- Future ESS target creation
- Random Forest prediction model
- Feature importance analysis
- Model persistence
- Prediction visualization

---

# Next Milestones

- Hyperparameter tuning
- SHAP explainability
- FastAPI prediction service
- Interactive dashboard
- Automated monthly retraining
- Additional behavioral and geopolitical indicators
- Ensemble forecasting models
- Real-time prediction pipeline