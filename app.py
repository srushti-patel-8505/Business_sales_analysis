import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

# Function to format large numbers into a compact readable format
def format_money(val):
    if val >= 1e6:
        return f"${val/1e6:.1f}M"
    elif val >= 1e3:
        return f"${val/1e3:.1f}K"
    return f"${val:.0f}"

# Page Config
st.set_page_config(page_title="📊 Business & Sales Analysis", layout="wide")

# Custom Styling
st.markdown("""
    <style>
    .big-title { font-size: 40px !important; color: #3498db; text-align: center; }
    .small-text { font-size: 18px !important; color: #555; text-align: center; }
    .scroll-target { visibility: hidden; }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="big-title">📊 Business & Sales Analysis</h1>', unsafe_allow_html=True)
st.markdown('<p class="small-text">Upload a dataset to explore insights step by step.</p>', unsafe_allow_html=True)

# Initialize Session State
for key in ["show_kpis", "show_sales_trend", "show_category_sales", "show_profit_dist", "show_region_sales"]:
    if key not in st.session_state:
        st.session_state[key] = False

# Sidebar - Upload CSV File
st.sidebar.header("📂 Upload Data")
uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type=["csv"])

if uploaded_file:
    # Load and Clean Data
    df = pd.read_csv(uploaded_file, encoding='ISO-8859-1')
    df.dropna(inplace=True)
    if 'Order Date' in df.columns:
        df['Order Date'] = pd.to_datetime(df['Order Date'])

    # Sidebar Filters
    st.sidebar.header("🔍 Filter Data")
    category = st.sidebar.multiselect("Select Category", df['Category'].unique(), default=df['Category'].unique())
    region = st.sidebar.multiselect("Select Region", df['Region'].unique(), default=df['Region'].unique())

    # 🗓 Date Range Filter
    if 'Order Date' in df.columns:
        min_date, max_date = df['Order Date'].min(), df['Order Date'].max()
        date_range = st.sidebar.date_input("Select Date Range", [min_date, max_date])
    else:
        date_range = None

    # 🔄 Reset All
    st.sidebar.markdown("---")
    if st.sidebar.button("🔄 Reset All"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    # Apply Filters
    filtered_df = df[
        (df['Category'].isin(category)) &
        (df['Region'].isin(region))
    ]
    if date_range and len(date_range) == 2:
        start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        filtered_df = filtered_df[(filtered_df['Order Date'] >= start_date) & (filtered_df['Order Date'] <= end_date)]

    st.session_state.filtered_df = filtered_df

    # Show Preview
    st.subheader("🔍 Filtered Dataset Preview")
    st.write(filtered_df.head())

    # Buttons Row
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if st.button("📊 Show Key Metrics"):
            st.session_state.show_kpis = True
            st.rerun()
    with col2:
        if st.button("📅 Show Sales Trend"):
            st.session_state.show_sales_trend = True
            st.rerun()
    with col3:
        if st.button("📊 Show Sales by Category"):
            st.session_state.show_category_sales = True
            st.rerun()
    with col4:
        if st.button("💰 Show Profit Distribution"):
            st.session_state.show_profit_dist = True
            st.rerun()
    with col5:
        if st.button("🌍 Show Sales by Region"):
            st.session_state.show_region_sales = True
            st.rerun()

    st.markdown('<div class="scroll-target" id="scroll-here"></div>', unsafe_allow_html=True)

    # Display Charts
    colA, colB = st.columns(2)

    if st.session_state.get("show_kpis", False):
        st.markdown('<script>document.getElementById("scroll-here").scrollIntoView();</script>', unsafe_allow_html=True)
        total_sales = filtered_df['Sales'].sum()
        total_profit = filtered_df['Profit'].sum()
        total_orders = len(filtered_df)

        with colA:
            st.subheader("📊 Key Metrics")
            k1, k2, k3 = st.columns(3)
            k1.metric("💰 Total Sales", format_money(total_sales))
            k2.metric("📈 Total Profit", format_money(total_profit))
            k3.metric("📦 Total Orders", total_orders)

    if st.session_state.get("show_sales_trend", False):
        with colB:
            st.subheader("📅 Sales Trend Over Time")
            sales_trend = filtered_df.groupby('Order Date')['Sales'].sum().reset_index()
            fig1 = px.line(sales_trend, x='Order Date', y='Sales', markers=True)
            st.plotly_chart(fig1, use_container_width=True)

    if st.session_state.get("show_category_sales", False):
        with colA:
            st.subheader("📊 Sales by Category")
            category_sales = filtered_df.groupby('Category')['Sales'].sum().reset_index().sort_values(by='Sales', ascending=False)
            fig2 = px.bar(category_sales, x='Category', y='Sales', text_auto=True, color='Category')
            st.plotly_chart(fig2, use_container_width=True)

    if st.session_state.get("show_profit_dist", False):
        with colB:
            st.subheader("💰 Profit Distribution")
            fig3 = px.histogram(filtered_df, x='Profit', nbins=40, marginal="box", color_discrete_sequence=["#2ecc71"])
            fig3.update_layout(title="Profit Distribution", xaxis_title="Profit", yaxis_title="Count")
            st.plotly_chart(fig3, use_container_width=True)

    if st.session_state.get("show_region_sales", False):
        with colA:
            st.subheader("🌍 Sales by Region")
            region_sales = filtered_df.groupby('Region')['Sales'].sum().reset_index()
            fig4 = px.pie(region_sales, values='Sales', names='Region', hole=0.4)
            st.plotly_chart(fig4, use_container_width=True)

else:
    st.warning("Please upload a CSV file to get started.")
