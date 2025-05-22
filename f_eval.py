import pandas as pd
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np

# Step 1: Load the daily sales dataset
df = pd.read_excel("sales.xlsx")
df.rename(columns={"date": "ds", "total_orders": "y", "product": "product_name"}, inplace=True)
df["ds"] = pd.to_datetime(df["ds"])

# Step 2: Convert daily data to monthly totals
df["ds"] = df["ds"].dt.to_period("M").dt.to_timestamp()
monthly_df = df.groupby(["product_name", "ds"])["y"].sum().reset_index()

# Step 3: Evaluate forecasts product by product
def evaluate_monthly_forecast(df_monthly):
    results = []

    for product in df_monthly["product_name"].unique():
        df_prod = df_monthly[df_monthly["product_name"] == product][["ds", "y"]].sort_values("ds")

        # Split into train/test
        train = df_prod[df_prod["ds"] <= "2024-12-01"]
        test = df_prod[(df_prod["ds"] > "2024-12-01") & (df_prod["ds"] <= "2025-03-01")]

        if len(train) >= 6 and train["y"].sum() >= 10 and not test.empty:
            try:
                model = Prophet()
                model.fit(train)

                future = model.make_future_dataframe(periods=len(test), freq='M')
                forecast = model.predict(future)[["ds", "yhat"]]

                # Align both to first of the month
                forecast["ds"] = forecast["ds"].dt.to_period("M").dt.to_timestamp()
                test["ds"] = test["ds"].dt.to_period("M").dt.to_timestamp()

                merged = pd.merge(test, forecast, on="ds", how="inner").dropna(subset=["y", "yhat"])

                if not merged.empty:
                    y_true = merged["y"]
                    y_pred = merged["yhat"]

                    mae = mean_absolute_error(y_true, y_pred)
                    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
                    mape = np.mean(np.abs((y_true - y_pred) / y_true.replace(0, np.nan))) * 100
                    accuracy = 100 - mape

                    results.append({
                        "product": product,
                        "MAE": round(mae, 2),
                        "RMSE": round(rmse, 2),
                        "MAPE (%)": round(mape, 2),
                        "Accuracy (%)": round(accuracy, 2)
                    })
            except:
                continue  # skip this product on failure

    return pd.DataFrame(results)

# Step 4: Run and print results
results_df = evaluate_monthly_forecast(monthly_df)
print(results_df)
results_df.to_csv("monthly_forecast_evaluation.csv", index=False)

