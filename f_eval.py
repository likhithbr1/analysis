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

# Loop over each product
for product in df['product_name'].unique():
    print(f"\n=== Evaluating model for product: {product} ===")

    # Subset data for current product
    product_df = df[df['product_name'] == product][['ds', 'y']].copy()
    
    # Check if we have enough data
    if len(product_df) < 30:
        print("Not enough data, skipping...")
        continue

    # Train the model
    model = Prophet()
    model.fit(product_df)

    # Make future dataframe and forecast
    future = model.make_future_dataframe(periods=12, freq='M')
    forecast = model.predict(future)

    # Plot forecast
    model.plot(forecast)
    plt.title(f"Forecast for Product: {product}")
    plt.show()

    # Plot components
    model.plot_components(forecast)
    plt.title(f"Components for Product: {product}")
    plt.show()

    # Cross-validation
    try:
        df_cv = cross_validation(model, initial='365 days', period='60 days', horizon='90 days')
        df_metrics = performance_metrics(df_cv)

        # Manual metrics
        mae = mean_absolute_error(df_cv['y'], df_cv['yhat'])
        mse = mean_squared_error(df_cv['y'], df_cv['yhat'])
        rmse = np.sqrt(mse)

        print(f"MAE: {mae:.2f} | MSE: {mse:.2f} | RMSE: {rmse:.2f}")
        print("Prophet metrics summary:")
        print(df_metrics.head())

    except Exception as e:
        print(f"Cross-validation failed for {product}: {e}")
