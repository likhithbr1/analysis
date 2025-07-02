# SDP Analytics Dashboard - Optimized Version

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import timedelta

# Page configuration
st.set_page_config(
    page_title="SDP Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

@st.cache_data

def load_data():
    try:
        df = pd.read_csv('SDP_agg_INS copy.csv')
        df['CREATED_MONTH'] = pd.to_datetime(df['CREATED_MONTH'])
        df = df.sort_values('CREATED_MONTH')
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

def filter_data_by_time_range(df, time_range):
    if time_range == "All":
        return df
    end_date = df['CREATED_MONTH'].max()
    start_date = end_date - {
        "6 months": timedelta(days=180),
        "1 year": timedelta(days=365),
        "2 years": timedelta(days=730)
    }[time_range]
    return df[df['CREATED_MONTH'] >= start_date]

def get_us_state_codes():
    return {
        'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA',
        'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'Florida': 'FL', 'Georgia': 'GA',
        'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA',
        'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
        'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS', 'Missouri': 'MO',
        'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH', 'New Jersey': 'NJ',
        'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH',
        'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC',
        'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT',
        'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY',
        'District of Columbia': 'DC', 'American Samoa': 'AS', 'Guam': 'GU', 'Northern Mariana Islands': 'MP',
        'Puerto Rico': 'PR', 'U.S. Virgin Islands': 'VI'
    }

def plot_dual_metric_bar(df, x_col, title):
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df[x_col], y=df['Total_orders'], name='Total Orders', marker_color='steelblue'))
    fig.add_trace(go.Bar(x=df[x_col], y=df['MRC_sum'], name='Revenue ($)', marker_color='seagreen', yaxis='y2'))
    fig.update_layout(
        title=title,
        xaxis_title=x_col,
        yaxis=dict(title='Total Orders'),
        yaxis2=dict(title='Revenue ($)', overlaying='y', side='right'),
        barmode='group',
        height=600
    )
    return fig

def plot_dual_metric_map(df, title):
    fig = px.choropleth(
        df,
        locations='STATE_CODE',
        locationmode='USA-states',
        color='Total_orders',
        hover_data=['MRC_sum'],
        scope='usa',
        title=title,
        color_continuous_scale='Blues',
        labels={'Total_orders': 'Total Orders', 'MRC_sum': 'Revenue ($)'}
    )
    return fig

def main():
    st.title("SDP Analytics Dashboard")
    df = load_data()
    if df is None:
        return

    st.subheader("Global Filters")
    time_range = st.selectbox("Select Time Range:", ["6 months", "1 year", "2 years", "All"], index=1)
    filtered_df = filter_data_by_time_range(df, time_range)
    if filtered_df.empty:
        st.warning("No data for selected time range.")
        return

    tab1, tab2, tab3 = st.tabs(["Location Wise", "Product Wise", "Brand Wise"])

    with tab1:
        st.header("Location-Wise Performance")
        chart_type = st.selectbox("Select Chart Type:", ["Bar Chart", "Map View"], key='location_chart')
        state_codes = get_us_state_codes()
        df_state = filtered_df.groupby('STATE_NAME').agg({'Total_orders': 'sum', 'MRC_sum': 'sum'}).reset_index()
        df_state['STATE_CODE'] = df_state['STATE_NAME'].map(state_codes)

        if chart_type == "Bar Chart":
            fig = plot_dual_metric_bar(df_state.sort_values('Total_orders', ascending=False), 'STATE_NAME', "Orders & Revenue by State")
        else:
            fig = plot_dual_metric_map(df_state, "State Map: Orders & Revenue")
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.header("Product-Wise Performance")
        selected_product = st.selectbox("Select Product:", sorted(filtered_df['PRODUCT'].dropna().unique()))
        chart_type = st.selectbox("Chart Type:", ["Bar Chart", "Map View"], key='product_chart')
        df_product = filtered_df[filtered_df['PRODUCT'] == selected_product]
        df_prod_grouped = df_product.groupby('STATE_NAME').agg({'Total_orders': 'sum', 'MRC_sum': 'sum'}).reset_index()
        df_prod_grouped['STATE_CODE'] = df_prod_grouped['STATE_NAME'].map(get_us_state_codes())

        if chart_type == "Bar Chart":
            fig = plot_dual_metric_bar(df_prod_grouped.sort_values('Total_orders'), 'STATE_NAME', f"{selected_product} by State")
        else:
            fig = plot_dual_metric_map(df_prod_grouped, f"{selected_product} State Map")
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.header("Brand-Wise Performance")
        selected_brand = st.selectbox("Select Brand:", sorted(filtered_df['BRAND'].dropna().unique()))
        chart_type = st.selectbox("Chart Type:", ["Bar Chart", "Map View"], key='brand_chart')
        df_brand = filtered_df[filtered_df['BRAND'] == selected_brand]
        df_brand_grouped = df_brand.groupby('STATE_NAME').agg({'Total_orders': 'sum', 'MRC_sum': 'sum'}).reset_index()
        df_brand_grouped['STATE_CODE'] = df_brand_grouped['STATE_NAME'].map(get_us_state_codes())

        if chart_type == "Bar Chart":
            fig = plot_dual_metric_bar(df_brand_grouped.sort_values('Total_orders'), 'STATE_NAME', f"{selected_brand} by State")
        else:
            fig = plot_dual_metric_map(df_brand_grouped, f"{selected_brand} State Map")
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
