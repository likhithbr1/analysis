import pandas as pd
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np

# Load your dataset
df = pd.read_excel("sales.xlsx")
df.rename(columns={"date": "ds", "total_orders": "y", "product": "product_name"}, inplace=True)
df["ds"] = pd.to_datetime(df["ds"])

# Evaluation function
def evaluate_forecast(df_full):
    products = df_full["product_name"].unique()
    eval_results = []

    for product in products:
        df_prod = df_full[df_full["product_name"] == product][["ds", "y"]].copy()
        df_prod = df_prod.sort_values("ds")

        train = df_prod[df_prod["ds"] <= "2024-12-31"]
        test = df_prod[(df_prod["ds"] > "2024-12-31") & (df_prod["ds"] <= "2025-03-15")]

        if train.shape[0] >= 60 and train["y"].sum() >= 10 and not test.empty:
            model = Prophet(daily_seasonality=True, yearly_seasonality=True)
            model.fit(train)

            future = model.make_future_dataframe(periods=len(test))
            forecast = model.predict(future)[["ds", "yhat"]]

            merged = pd.merge(test, forecast, on="ds", how="left")

            y_true = merged["y"]
            y_pred = merged["yhat"]

            mae = mean_absolute_error(y_true, y_pred)
            rmse = mean_squared_error(y_true, y_pred, squared=False)
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

# Run it
evaluation_df = evaluate_forecast(df)
print(evaluation_df)
