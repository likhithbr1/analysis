import pandas as pd
import json
from prophet import Prophet
from datetime import timedelta
import os

# ---------- CONFIG ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOURCE_FILE_MAP = {
    "eon": os.path.join(BASE_DIR, "sorted_file.xlsx"),
    "sdp": os.path.join(BASE_DIR, "sorted_file_sdp.xlsx"),
    "orion": os.path.join(BASE_DIR, "sorted_file_orion.xlsx"),
}
CACHE_DIR = os.path.join(BASE_DIR, "forecast_cache")

# ---------- LOAD DATA ----------
def load_data(source_system):
    if source_system not in SOURCE_FILE_MAP:
        raise ValueError(f"Unknown source system: {source_system}")
    
    df = pd.read_excel(SOURCE_FILE_MAP[source_system])
    df.rename(columns={"date": "ds", "total_orders": "y", "product": "product_name"}, inplace=True)
    df["ds"] = pd.to_datetime(df["ds"])
    return df

# ---------- HELPER FUNCTION TO CHECK DATA SUFFICIENCY ----------
def has_sufficient_data(df_prod):
    return df_prod.shape[0] >= 60 and df_prod["y"].sum() >= 10

# ---------- FAST SUMMARY FROM CACHE ----------
def get_forecast_summary(source_system):
    """Read valid product list from cached JSON file"""
    cache_path = os.path.join(CACHE_DIR, f"forecast_cache_{source_system}.json")
    if not os.path.exists(cache_path):
        raise FileNotFoundError(f"Cached product list not found for: {source_system}")
    
    with open(cache_path, "r") as f:
        cached_data = json.load(f)
    
    return cached_data.get("products", [])

# ---------- DETAILED FORECAST (PER PRODUCT) ----------
def get_forecast_detail(source_system, product):
    df = load_data(source_system)
    df_prod = df[df["product_name"] == product][["ds", "y"]].copy()

    if has_sufficient_data(df_prod):
        model = Prophet(daily_seasonality=True, yearly_seasonality=True)
        model.fit(df_prod)

        future = model.make_future_dataframe(periods=30)
        forecast = model.predict(future)
        forecast["yhat"] = forecast["yhat"].clip(lower=0)
        forecast["yhat_lower"] = forecast["yhat_lower"].clip(lower=0)
        forecast["yhat_upper"] = forecast["yhat_upper"].clip(lower=0)

        forecast = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].copy()
        latest_cutoff = forecast["ds"].max() - timedelta(days=29)
        df_selected = forecast[forecast["ds"] >= latest_cutoff]

        return {
            "product": product,
            "total_forecast": round(df_selected["yhat"].sum(), 2),
            "forecast_data": df_selected.to_dict(orient="records")
        }
    
    return None

# ---------- OPTIONAL: GET DATA STATISTICS ----------
def get_data_statistics(source_system):
    df = load_data(source_system)
    all_products = df['product_name'].unique()
    
    stats = {
        "total_products": len(all_products),
        "products_with_sufficient_data": 0,
        "products_with_insufficient_data": 0,
        "details": []
    }

    for product in all_products:
        df_prod = df[df["product_name"] == product][["ds", "y"]].copy()
        row_count = df_prod.shape[0]
        total_orders = df_prod["y"].sum()
        sufficient = has_sufficient_data(df_prod)

        if sufficient:
            stats["products_with_sufficient_data"] += 1
        else:
            stats["products_with_insufficient_data"] += 1

        stats["details"].append({
            "product": product,
            "row_count": row_count,
            "total_orders": total_orders,
            "sufficient_data": sufficient
        })

    return stats
