import pandas as pd
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np

# Step 1: Load and preprocess the data
df = pd.read_excel("sales.xlsx")
df.rename(columns={"date": "ds", "total_orders": "y", "product": "product_name"}, inplace=True)
df["ds"] = pd.to_datetime(df["ds"])

# Step 2: Aggregate to monthly totals
df["month"] = df["ds"].dt.to_period("M").dt.to_timestamp()
monthly_df = df.groupby(["product_name", "month"])["y"].sum().reset_index()
monthly_df.rename(columns={"month": "ds"}, inplace=True)

# Step 3: Evaluate using Prophet
def evaluate_monthly_forecast(df_monthly):
    products = df_monthly["product_name"].unique()
    eval_results = []

    for product in products:
        df_prod = df_monthly[df_monthly["product_name"] == product][["ds", "y"]].copy()
        df_prod = df_prod.sort_values("ds")

        train = df_prod[df_prod["ds"] <= "2024-12-01"]
        test = df_prod[(df_prod["ds"] > "2024-12-01") & (df_prod["ds"] <= "2025-03-01")]

        if train.shape[0] >= 6 and train["y"].sum() >= 10 and not test.empty:
            model = Prophet()
            model.fit(train)

            future = model.make_future_dataframe(periods=len(test), freq='M')
            forecast = model.predict(future)[["ds", "yhat"]]

            merged = pd.merge(test, forecast, on="ds", how="left")

            y_true = merged["y"]
            y_pred = merged["yhat"]

            mae = mean_absolute_error(y_true, y_pred)
            rmse = np.sqrt(mean_squared_error(y_true, y_pred))
            mape = np.mean(np.abs((y_true - y_pred) / y_true.replace(0, np.nan))) * 100
            accuracy = 100 - mape

            eval_results.append({
                "product": product,
                "MAE": round(mae, 2),
                "RMSE": round(rmse, 2),
                "MAPE (%)": round(mape, 2),
                "Accuracy (%)": round(accuracy, 2)
            })

    return pd.DataFrame(eval_results)

# Step 4: Run evaluation
results_df = evaluate_monthly_forecast(monthly_df)
print(results_df)

# Optional: Save results
results_df.to_csv("monthly_forecast_evaluation.csv", index=False)
