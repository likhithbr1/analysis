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
    toggle = st.radio("Select Metric to Display:", ["Total Orders", "Revenue"], horizontal=True, key=title)
    y_col = 'Total_orders' if toggle == "Total Orders" else 'MRC_sum'
    y_title = "Total Orders" if toggle == "Total Orders" else "Revenue ($)"
    color = '#1f77b4' if toggle == "Total Orders" else '#2ca02c'

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df[x_col],
        y=df[y_col],
        name=y_title,
        marker_color=color
    ))
    fig.update_layout(
        title=title,
        xaxis_title=x_col,
        yaxis_title=y_title,
        height=600
    )
    return fig

def plot_dual_metric_map(df, title):
    fig = px.choropleth(
        df,
        locations='STATE_CODE',
        locationmode='USA-states',
        color='Total_orders',
        hover_name='STATE_NAME',
        hover_data={'STATE_CODE': False, 'Total_orders': True, 'MRC_sum': True},
        scope='usa',
        title=title,
        color_continuous_scale='Tealgrn',
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
    product_filter = st.selectbox("Select Product (optional):", ["All"] + sorted(df['PRODUCT'].dropna().unique()))
    brand_filter = st.selectbox("Select Brand (optional):", ["All"] + sorted(df['BRAND'].dropna().unique()))
    state_filter = st.selectbox("Select State (optional):", ["All"] + sorted(df['STATE_NAME'].dropna().unique()))

    filtered_df = filter_data_by_time_range(df, time_range)

    if product_filter != "All":
        filtered_df = filtered_df[filtered_df['PRODUCT'] == product_filter]
    if brand_filter != "All":
        filtered_df = filtered_df[filtered_df['BRAND'] == brand_filter]
    if state_filter != "All":
        filtered_df = filtered_df[filtered_df['STATE_NAME'] == state_filter]

    if filtered_df.empty:
        st.warning("No data for selected filters.")
        return

    tab1, tab2, tab3 = st.tabs(["Location Wise", "Product Wise", "Brand Wise"])

    with tab1:
        st.header("Location-Wise Performance")
        chart_type = st.radio("Select Chart Type:", ["Bar Chart", "Map View"], horizontal=True, key='location_chart')
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
        st.subheader("Summary View")
        df_products = filtered_df.groupby('PRODUCT').agg({'Total_orders': 'sum', 'MRC_sum': 'sum'}).reset_index()
        fig_summary_products = plot_dual_metric_bar(df_products.sort_values('Total_orders', ascending=False), 'PRODUCT', "All Products Performance")
        st.plotly_chart(fig_summary_products, use_container_width=True)

        st.markdown("---")
        st.subheader("Detail View")
        selected_product = st.selectbox("Select Product:", sorted(filtered_df['PRODUCT'].dropna().unique()))
        chart_type = st.radio("Chart Type:", ["Bar Chart", "Map View"], horizontal=True, key='product_chart')
        df_product = filtered_df[filtered_df['PRODUCT'] == selected_product]
        df_prod_grouped = df_product.groupby('STATE_NAME').agg({'Total_orders': 'sum', 'MRC_sum': 'sum'}).reset_index()
        df_prod_grouped['STATE_CODE'] = df_prod_grouped['STATE_NAME'].map(get_us_state_codes())

        if chart_type == "Bar Chart":
            fig = plot_dual_metric_bar(df_prod_grouped.sort_values('Total_orders', ascending=False), 'STATE_NAME', f"{selected_product} by State")
        else:
            fig = plot_dual_metric_map(df_prod_grouped, f"{selected_product} State Map")
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.header("Brand-Wise Performance")
        st.subheader("Summary View")
        df_brands = filtered_df.groupby('BRAND').agg({'Total_orders': 'sum', 'MRC_sum': 'sum'}).reset_index()
        fig_summary_brands = plot_dual_metric_bar(df_brands.sort_values('Total_orders', ascending=False), 'BRAND', "All Brands Performance")
        st.plotly_chart(fig_summary_brands, use_container_width=True)

        st.markdown("---")
        st.subheader("Detail View")
        selected_brand = st.selectbox("Select Brand:", sorted(filtered_df['BRAND'].dropna().unique()))
        chart_type = st.radio("Chart Type:", ["Bar Chart", "Map View"], horizontal=True, key='brand_chart')
        df_brand = filtered_df[filtered_df['BRAND'] == selected_brand]
        df_brand_grouped = df_brand.groupby('STATE_NAME').agg({'Total_orders': 'sum', 'MRC_sum': 'sum'}).reset_index()
        df_brand_grouped['STATE_CODE'] = df_brand_grouped['STATE_NAME'].map(get_us_state_codes())

        if chart_type == "Bar Chart":
            fig = plot_dual_metric_bar(df_brand_grouped.sort_values('Total_orders', ascending=False), 'STATE_NAME', f"{selected_brand} by State")
        else:
            fig = plot_dual_metric_map(df_brand_grouped, f"{selected_brand} State Map")
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
