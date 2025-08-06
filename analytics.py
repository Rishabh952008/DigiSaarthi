import pandas as pd
import plotly.graph_objs as go
import streamlit as st

def plot_active_customers(df, contact_col='contact', timestamp_col='timestamp'):
    """
    Plots active customers for selected period using Streamlit and Plotly.

    Args:
        df (pd.DataFrame): DataFrame containing customer data.
        contact_col (str): Column name for customer contact/ID.
        timestamp_col (str): Column name for order timestamp.
    """
    # Ensure timestamp is datetime
    df[timestamp_col] = pd.to_datetime(df[timestamp_col], errors='coerce')

    # Streamlit dropdown for period selection
    period_map = {
        'Month on Month': 'M',
        'Week on Week': 'W',
        'Day on Day': 'D'
    }
    period_label = st.selectbox("Select Period", list(period_map.keys()))
    period = period_map[period_label]

    # Calculate active customers
    df['period'] = df[timestamp_col].dt.to_period(period)
    active_customers = df.groupby('period')[contact_col].nunique()

    # Plotly bar chart
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=active_customers.index.astype(str),
        y=active_customers.values,
        name='Active Customers'
    ))
    fig.update_layout(
        title=f"Active Customers ({period_label})",
        xaxis_title="Period",
        yaxis_title="Number of Active Customers"
    )

    st.plotly_chart(fig, use_container_width=True)
    
    
def plot_total_sales(df, sales_col='order_value', timestamp_col='timestamp'):
    """
    Plots total sales for selected period using Streamlit and Plotly.
    """
    df[timestamp_col] = pd.to_datetime(df[timestamp_col], errors='coerce')
    period_map = {
        'Month on Month': 'M',
        'Week on Week': 'W',
        'Day on Day': 'D'
    }
    period_label = st.selectbox("Select Period for Total Sales", list(period_map.keys()), key="sales_period")
    period = period_map[period_label]
    df['period_sales'] = df[timestamp_col].dt.to_period(period)
    total_sales = df.groupby('period_sales')[sales_col].sum()
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=total_sales.index.astype(str),
        y=total_sales.values,
        name='Total Sales'
    ))
    fig.update_layout(
        title=f"Total Sales ({period_label})",
        xaxis_title="Period",
        yaxis_title="Total Sales"
    )
    st.plotly_chart(fig, use_container_width=True)