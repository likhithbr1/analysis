import pandas as pd
import numpy as np
from prophet import Prophet
from prophet.diagnostics import cross_validation, performance_metrics
from sklearn.metrics import mean_absolute_error, mean_squared_error
import matplotlib.pyplot as plt

# Load and prepare data
file_path = "sorted_file.xlsx"
df = pd.read_excel(file_path)
df.rename(columns={"date": "ds", "total_orders": "y", "product": "product_name"}, inplace=True)
df["ds"] = pd.to_datetime(df["ds"])

# List to collect results
summary_results = []

# Loop over each product
for product in df['product_name'].unique():
    print(f"\n=== Evaluating model for product: {product} ===")

    product_df = df[df['product_name'] == product][['ds', 'y']].copy()
    
    if len(product_df) < 30:
        print("Not enough data, skipping...")
        continue

    model = Prophet()
    model.fit(product_df)

    future = model.make_future_dataframe(periods=12, freq='M')
    forecast = model.predict(future)

    model.plot(forecast)
    plt.title(f"Forecast for Product: {product}")
    plt.show()

    model.plot_components(forecast)
    plt.title(f"Components for Product: {product}")
    plt.show()

    try:
        df_cv = cross_validation(model, initial='365 days', period='60 days', horizon='90 days')
        mae = mean_absolute_error(df_cv['y'], df_cv['yhat'])
        mse = mean_squared_error(df_cv['y'], df_cv['yhat'])
        rmse = np.sqrt(mse)

        print(f"MAE: {mae:.2f} | MSE: {mse:.2f} | RMSE: {rmse:.2f}")

        summary_results.append({
            'Product': product,
            'MAE': round(mae, 2),
            'MSE': round(mse, 2),
            'RMSE': round(rmse, 2)
        })

    except Exception as e:
        print(f"Cross-validation failed for {product}: {e}")
        summary_results.append({
            'Product': product,
            'MAE': None,
            'MSE': None,
            'RMSE': None
        })

# Final summary table
summary_df = pd.DataFrame(summary_results)
print("\n=== Final Model Evaluation Summary ===")
print(summary_df)

