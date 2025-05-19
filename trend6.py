import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Setup
st.set_page_config(page_title="Product Sales Trend", layout="wide")
st.title("📈 Product Sales Trend Dashboard")

# Load and cache data
@st.cache_data
def load_data():
    df = pd.read_excel("final.xlsx")
    df['date'] = pd.to_datetime(df['date'])
    return df

df = load_data()

# Initialize session state for selected product
if 'selected_product' not in st.session_state:
    st.session_state.selected_product = None

# Helper to generate sparkline chart
def generate_sparkline(data, color):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data['date'],
        y=data['total_orders'],
        mode='lines',
        line=dict(color=color, width=2),
        hoverinfo='skip'
    ))
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        height=40
    )
    return fig

# Main layout switch
if st.session_state.selected_product is None:
    st.subheader("All Product Trends (Sparklines)")
    reference_date = df['date'].max()
    preview_period = reference_date - timedelta(days=30)

    # Filter
    search_term = st.text_input("🔍 Search Product")

    # Collect stats for sorting
    trend_rows = []
    for product in sorted(df['product'].unique()):
        if search_term.lower() not in product.lower():
            continue

        product_data = df[df['product'] == product]
        period_data = product_data[(product_data['date'] >= preview_period) & (product_data['date'] <= reference_date)].sort_values('date')

        if period_data.empty:
            continue

        start_val = period_data.iloc[0]['total_orders']
        end_val = period_data.iloc[-1]['total_orders']
        delta = end_val - start_val
        rate = (delta / start_val * 100) if start_val != 0 else 0
        color = 'green' if delta >= 0 else 'red'
        trend_icon = '⬆️' if delta >= 0 else '⬇️'

        trend_rows.append({
            'product': product,
            'end_val': end_val,
            'rate': rate,
            'trend_icon': trend_icon,
            'color': color,
            'period_data': period_data
        })

    # Sort by highest growth
    trend_rows = sorted(trend_rows, key=lambda x: x['rate'], reverse=True)

    # Display in grid (3 per row)
    for i in range(0, len(trend_rows), 3):
        row = trend_rows[i:i+3]
        cols = st.columns(3)
        for col, item in zip(cols, row):
            with col:
                if st.button(f"{item['product']}", key=f"btn_{item['product']}"):
                    st.session_state.selected_product = item['product']
                st.markdown(f"**📦 Orders:** {int(item['end_val'])}")
                st.markdown(f"**{item['trend_icon']} {item['rate']:.1f}%**")
                st.plotly_chart(generate_sparkline(item['period_data'], item['color']), use_container_width=True, key=f"sparkline_{item['product']}")

else:
    selected_product = st.session_state.selected_product
    st.subheader(f"📊 Detailed View: {selected_product}")
    if st.button("🔙 Back to All Products"):
        st.session_state.selected_product = None

    # Detailed chart view
    time_ranges = {
        "1 Week": timedelta(weeks=1),
        "1 Month": timedelta(days=30),
        "1 Year": timedelta(days=365),
        "2 Years": timedelta(days=730)
    }

    reference_date = df['date'].max()
    product_data = df[df['product'] == selected_product]

    tabs = st.tabs(list(time_ranges.keys()))

    for i, (label, delta) in enumerate(time_ranges.items()):
        with tabs[i]:
            start_date = reference_date - delta
            period_data = product_data[(product_data['date'] >= start_date) & (product_data['date'] <= reference_date)].sort_values('date')

            if not period_data.empty:
                start_orders = period_data.iloc[0]['total_orders']
                end_orders = period_data.iloc[-1]['total_orders']
                rate_of_change = ((end_orders - start_orders) / start_orders * 100) if start_orders != 0 else 0
                trend_color = "green" if end_orders >= start_orders else "red"

                st.metric(label="Rate of Change", value=f"{rate_of_change:.2f}%", delta=f"{end_orders - start_orders}")

                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=period_data['date'],
                    y=period_data['total_orders'],
                    mode='lines',
                    line=dict(color=trend_color, width=3),
                    name="Total Orders",
                    hoverinfo='x+y'
                ))

                fig.update_layout(
                    title=f"{selected_product.upper()} - {label} Trend",
                    xaxis_title="Date",
                    yaxis_title="Total Orders",
                    showlegend=False,
                    height=550
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No data available for this period.")
