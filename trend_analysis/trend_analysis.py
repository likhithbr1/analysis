# trend_analysis.py
import pandas as pd
import numpy as np
from scipy import stats

# Centralized source config
SOURCE_FILE_MAP = {
    "eon": "data/sorted_file_eon.xlsx",
    "abc": "data/sorted_file_abc.xlsx",
    "xyz": "data/sorted_file_xyz.xlsx"
}

def get_valid_sources():
    return list(SOURCE_FILE_MAP.keys())

def load_data(source_system):
    if source_system not in SOURCE_FILE_MAP:
        raise ValueError(f"Unknown source system: {source_system}")
    path = SOURCE_FILE_MAP[source_system]
    df = pd.read_excel(path)
    df['date'] = pd.to_datetime(df['date'])
    return df

def generate_summary(source_system):
    df = load_data(source_system)
    reference_date = df['date'].max()
    preview_period = reference_date - pd.Timedelta(days=30)
    results = []

    for product in sorted(df['product'].unique()):
        product_data = df[df['product'] == product]
        period_data = product_data[(product_data['date'] >= preview_period) & (product_data['date'] <= reference_date)].sort_values('date')

        if period_data.empty or len(period_data) < 2:
            continue

        total_sales = period_data['total_orders'].sum()
        avg_sales = period_data['total_orders'].mean()
        x = np.arange(len(period_data))
        y = period_data['total_orders'].values

        slope, _, r_value, _, _ = stats.linregress(x, y)
        norm_slope = (slope / avg_sales * 100) if avg_sales > 0 else 0

        if abs(norm_slope) < 2:
            trend_icon, color, desc = '➡️', 'blue', 'Stable'
        elif norm_slope > 0:
            trend_icon, color, desc = ('⬆️', 'green', 'Upward') if norm_slope > 10 else ('↗️', 'green', 'Slight Upward')
        else:
            trend_icon, color, desc = ('⬇️', 'red', 'Downward') if norm_slope < -10 else ('↘️', 'red', 'Slight Downward')

        sparkline = period_data[['date', 'total_orders']].copy()
        results.append({
            "product": product,
            "total_sales": int(total_sales),
            "avg_sales": round(avg_sales, 1),
            "trend_percent": round(norm_slope, 1),
            "trend_description": desc,
            "trend_icon": trend_icon,
            "color": color,
            "r_squared": round(r_value**2, 2),
            "sparkline_data": sparkline.to_dict(orient="records")
        })

    return sorted(results, key=lambda x: x["trend_percent"], reverse=True)

def generate_detail(source_system, product, time_delta):
    df = load_data(source_system)
    reference_date = df['date'].max()
    start_date = reference_date - time_delta

    product_data = df[(df['product'] == product) & (df['date'] >= start_date)].sort_values('date')
    if product_data.empty:
        raise ValueError("No data for product in this range")

    total_sales = product_data['total_orders'].sum()
    avg_sales = product_data['total_orders'].mean()
    x = np.arange(len(product_data))
    y = product_data['total_orders'].values

    if len(x) > 1:
        slope, intercept, r_value, _, _ = stats.linregress(x, y)
        trend_y = (slope * x + intercept).tolist()
        norm_slope = (slope / avg_sales * 100) if avg_sales > 0 else 0

        if abs(norm_slope) < 2:
            desc = "Stable"
        elif norm_slope > 0:
            desc = "Upward" if norm_slope > 10 else "Slight Upward"
        else:
            desc = "Downward" if norm_slope < -10 else "Slight Downward"
    else:
        trend_y = []
        norm_slope = 0
        r_value = 0
        desc = "Insufficient Data"

    return {
        "product": product,
        "time_range_days": time_delta.days,
        "total_sales": int(total_sales),
        "avg_sales": round(avg_sales, 1),
        "trend_percent": round(norm_slope, 1),
        "trend_description": desc,
        "r_squared": round(r_value**2, 2),
        "chart_data": {
            "dates": product_data["date"].dt.strftime("%Y-%m-%d").tolist(),
            "actual": product_data["total_orders"].tolist(),
            "trendline": trend_y
        }
    }
