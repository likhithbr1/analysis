import pandas as pd
from prophet import Prophet
from datetime import timedelta
import os

# ---------- CONFIG ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOURCE_FILE_MAP = {
    "eon": os.path.join(BASE_DIR, "sorted_file.xlsx"),
    "abc": os.path.join(BASE_DIR, "data/sorted_file_abc.xlsx"),
    "xyz": os.path.join(BASE_DIR, "data/sorted_file_xyz.xlsx"),
}

# ---------- LOAD DATA ----------
def load_data(source_system):
    if source_system not in SOURCE_FILE_MAP:
        raise ValueError(f"Unknown source system: {source_system}")
    
    df = pd.read_excel(SOURCE_FILE_MAP[source_system])
    df.rename(columns={"date": "ds", "total_orders": "y", "product": "product_name"}, inplace=True)
    df["ds"] = pd.to_datetime(df["ds"])
    return df

# ---------- SUMMARY (PRODUCT LIST) ----------
def get_forecast_summary(source_system):
    df = load_data(source_system)
    return sorted(df['product_name'].unique())

# ---------- DETAILED FORECAST (PER PRODUCT) ----------
def get_forecast_detail(source_system, product):
    df = load_data(source_system)
    df_prod = df[df["product_name"] == product][["ds", "y"]].copy()

    if df_prod.shape[0] >= 60 and df_prod["y"].sum() >= 10:
        model = Prophet(daily_seasonality=True, yearly_seasonality=True)
        model.fit(df_prod)

        future = model.make_future_dataframe(periods=30)
        forecast = model.predict(future)

        forecast = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].copy()
    else:
        mean_y = df_prod.tail(30)["y"].mean() if df_prod.shape[0] >= 30 else df_prod["y"].mean()
        last_date = df_prod["ds"].max() if not df_prod.empty else pd.to_datetime("2025-05-15")
        future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=30)

        forecast = pd.DataFrame({
            "ds": future_dates,
            "yhat": [mean_y] * 30,
            "yhat_lower": [mean_y * 0.9] * 30,
            "yhat_upper": [mean_y * 1.1] * 30,
        })

    # Filter to only return next 30 days
    latest_cutoff = forecast["ds"].max() - timedelta(days=29)
    df_selected = forecast[forecast["ds"] >= latest_cutoff]

    return {
        "product": product,
        "total_forecast": round(df_selected["yhat"].sum(), 2),
        "forecast_data": df_selected.to_dict(orient="records")
    }
