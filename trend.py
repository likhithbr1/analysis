import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Load backend Excel file (you can adjust path if needed)
df = pd.read_excel("final.xlsx")
df['date'] = pd.to_datetime(df['date'])

# Setup
st.set_page_config(page_title="Product Sales Trend", layout="wide")
st.title("📈 Product Sales Trend Dashboard")

# Sidebar - Product selection
products = df['product'].unique()
selected_product = st.sidebar.selectbox("Select a Product", sorted(products))

# Main Area - Time range selection as tabs
time_ranges = {
    "1 Week": timedelta(weeks=1),
    "1 Month": timedelta(days=30),
    "1 Year": timedelta(days=365),
    "2 Years": timedelta(days=730)
}

reference_date = df['date'].max()
product_data = df[df['product'] == selected_product]

# Tabs for different time ranges
tabs = st.tabs(list(time_ranges.keys()))

for i, (label, delta) in enumerate(time_ranges.items()):
    with tabs[i]:
        start_date = reference_date - delta
        period_data = product_data[(product_data['date'] >= start_date) & (product_data['date'] <= reference_date)].sort_values('date')

        if not period_data.empty:
            start_orders = period_data.iloc[0]['total_orders']
            end_orders = period_data.iloc[-1]['total_orders']
            trend_color = "green" if end_orders >= start_orders else "red"

            # Create Plotly chart without markers
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=period_data['date'],
                y=period_data['total_orders'],
                mode='lines',
                line=dict(color=trend_color, width=3),
                name=selected_product,
                hoverinfo='x+y'
            ))
            fig.update_layout(
                title=f"{selected_product.upper()} - {label} Trend",
                xaxis_title="Date",
                yaxis_title="Total Orders",
                showlegend=False,
                height=500
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No data available for this period.")

