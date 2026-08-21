import math

from fastapi import APIRouter, HTTPException

from app.services.data_services import (
    get_ess_data,
    get_feature_importance,
    get_model_metrics,
    get_model_predictions,
)


router = APIRouter(
    prefix="/api",
    tags=["Mirai"],
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def clean_value(value):
    """
    Convert pandas / Python values into JSON-safe values.

    JSON does not support NaN or infinity, so these are converted to None.
    """
    if value is None:
        return None

    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return None

    return value


def dataframe_to_records(dataframe):
    """
    Convert a pandas DataFrame into JSON-safe records.
    """
    if dataframe is None:
        return []

    records = dataframe.to_dict(orient="records")

    cleaned_records = []

    for record in records:
        cleaned_record = {}

        for key, value in record.items():
            cleaned_record[key] = clean_value(value)

        cleaned_records.append(cleaned_record)

    return cleaned_records


# ---------------------------------------------------------------------------
# Root API
# ---------------------------------------------------------------------------

@router.get("/")
def api_root():
    return {
        "message": "Mirai API is running"
    }


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

@router.get("/dashboard")
def dashboard():
    try:
        ess_data = get_ess_data()
        feature_importance = get_feature_importance()
        model_metrics = get_model_metrics()
        model_predictions = get_model_predictions()

        return {
            "ess": dataframe_to_records(ess_data),
            "feature_importance": dataframe_to_records(
                feature_importance
            ),
            "model_metrics": dataframe_to_records(
                model_metrics
            ),
            "model_predictions": dataframe_to_records(
                model_predictions
            ),
        }

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    except Exception as exc:
        print("Dashboard API error:", repr(exc))

        raise HTTPException(
            status_code=500,
            detail=f"Unable to load dashboard data: {exc}",
        )


# ---------------------------------------------------------------------------
# ESS
# ---------------------------------------------------------------------------

@router.get("/ess")
def ess():
    try:
        data = get_ess_data()

        return {
            "data": dataframe_to_records(data)
        }

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    except Exception as exc:
        print("ESS API error:", repr(exc))

        raise HTTPException(
            status_code=500,
            detail=f"Unable to load ESS data: {exc}",
        )


# ---------------------------------------------------------------------------
# Feature Importance
# ---------------------------------------------------------------------------

@router.get("/feature-importance")
def feature_importance():
    try:
        data = get_feature_importance()

        return {
            "data": dataframe_to_records(data)
        }

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    except Exception as exc:
        print("Feature importance API error:", repr(exc))

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to load feature importance data: "
                f"{exc}"
            ),
        )


# ---------------------------------------------------------------------------
# Model Metrics
# ---------------------------------------------------------------------------

@router.get("/model-metrics")
def model_metrics():
    try:
        data = get_model_metrics()

        return {
            "data": dataframe_to_records(data)
        }

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    except Exception as exc:
        print("Model metrics API error:", repr(exc))

        raise HTTPException(
            status_code=500,
            detail=f"Unable to load model metrics: {exc}",
        )


# ---------------------------------------------------------------------------
# Model Predictions
# ---------------------------------------------------------------------------

@router.get("/model-predictions")
def model_predictions():
    try:
        data = get_model_predictions()

        return {
            "data": dataframe_to_records(data)
        }

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    except Exception as exc:
        print("Model predictions API error:", repr(exc))

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to load model predictions: "
                f"{exc}"
            ),
        )


# ---------------------------------------------------------------------------
# Forecast
# ---------------------------------------------------------------------------

@router.get("/forecast")
def forecast():
    try:
        predictions = get_model_predictions()

        return {
            "data": dataframe_to_records(predictions)
        }

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    except Exception as exc:
        print("Forecast API error:", repr(exc))

        raise HTTPException(
            status_code=500,
            detail=f"Unable to load forecast data: {exc}",
        )