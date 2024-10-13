import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import warnings

warnings.filterwarnings('ignore')

# Set page config
st.set_page_config(page_title="IMPORT EXPORT!!!", page_icon=":bar_chart:", layout="wide")

# Title
st.title(":bar_chart: Sample Import Export EDA")

# File uploader
fl = st.file_uploader(":file_folder: Upload a file", type=["csv", "txt", "xlsx", "xls"])

# Check if a file is uploaded
if fl is not None:
    # If a CSV file is uploaded
    if fl.name.endswith(".csv"):
        df = pd.read_csv(fl, encoding="ISO-8859-1")
else:
    # If no file is uploaded, fallback to a local dataset
    df = pd.read_csv(r"C:\Users\HP\Downloads\archive (1)\Imports_Exports_Dataset.csv", encoding="ISO-8859-1")
    df = df.sample(n = 3001,random_state = 55005)

# Check if 'Date' column exists in the dataset
if 'Date' in df.columns:
    # Convert 'Date' column to datetime
    df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
    
    # Drop rows with invalid dates
    df.dropna(subset=['Date'], inplace=True)

    # Define two columns for date filtering
    col1, col2 = st.columns((2))

    # Get the min and max date from the dataset
    startDate = df["Date"].min()
    endDate = df["Date"].max()

    # Date input for filtering
    with col1:
        date1 = st.date_input("Start Date", startDate, min_value=startDate, max_value=endDate)

    with col2:
        date2 = st.date_input("End Date", endDate, min_value=startDate, max_value=endDate)

    # Filter the dataframe between selected start and end dates
    df_filtered = df[(df["Date"] >= pd.to_datetime(date1)) & (df["Date"] <= pd.to_datetime(date2))].copy()

    # Display the filtered data
    st.dataframe(df_filtered)

else:
    st.error("The dataset does not contain a 'Date' column.")

# Sidebar filters
st.sidebar.header("Choose your filter: ")

# Filter for Category
category = st.sidebar.multiselect("Pick your Category", df["Category"].unique())

if not category:
    df2 = df.copy()
else:
    df2 = df[df["Category"].isin(category)]

# Filter for Shipping Method
shipping_method = st.sidebar.multiselect("Pick the Shipping Method", df2["Shipping_Method"].unique())

if not shipping_method:
    df3 = df2.copy()
else:
    df3 = df2[df2["Shipping_Method"].isin(shipping_method)]

# Filter for Import_Export
import_export = st.sidebar.multiselect("Pick Import/Export", df3["Import_Export"].unique())

if not import_export:
    df4 = df3.copy()
else:
    df4 = df3[df3["Import_Export"].isin(import_export)]

# Filter for Payment Terms
payment_terms = st.sidebar.multiselect("Pick the Payment Terms", df4["Payment_Terms"].unique())

if not payment_terms:
    df5 = df4.copy()
else:
    df5 = df4[df4["Payment_Terms"].isin(payment_terms)]

# ======= SUMMARY METRICS ============= #
import_export_count = df5["Import_Export"].value_counts()
total_value = df5["Value"].sum()
total_quantity = df5["Quantity"].sum()
top_countries = df5.groupby("Country")["Value"].sum().nlargest(5)

with st.container():
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Imports", import_export_count.get("Import", 0))
    col2.metric("Total Exports", import_export_count.get("Export", 0))
    col3.metric("Total Transaction Value", f"${total_value:,.2f}")
    col4.metric("Total Quantity", f"{total_quantity:,.2f}")

st.subheader("Top 5 Countries by Transaction Value")
st.write(top_countries)

# Dashboard layout for multiple plots
st.subheader("Dashboard Overview")

# Create three columns for the dashboard
col_a, col_b, col_c = st.columns(3)

# Category-wise Quantity
with col_a:
    category_df = df5.groupby(by=["Category"], as_index=False)["Quantity"].sum()
    st.subheader("Category-wise Quantity")
    fig = px.bar(category_df, x="Category", y="Quantity", text=[f'{x:,.2f}' for x in category_df["Quantity"]],
                 template="seaborn")
    st.plotly_chart(fig, use_container_width=True)

# Shipping Method-wise Quantity
with col_b:
    shipping_df = df5.groupby(by=["Shipping_Method"], as_index=False)["Quantity"].sum()
    st.subheader("Shipping Method-wise Quantity")
    fig2 = go.Figure(data=[go.Pie(labels=shipping_df["Shipping_Method"], values=shipping_df["Quantity"],
                                   textinfo='percent+label', pull=[0.05] * len(shipping_df))])
    st.plotly_chart(fig2, use_container_width=True)

# Average Weight by Category and Shipping Method
with col_c:
    avg_weight_df = df5.groupby(by=["Category", "Shipping_Method"], as_index=False)["Weight"].mean()
    st.subheader("Average Weight by Category and Shipping Method")
    fig3 = go.Figure(data=[go.Pie(labels=avg_weight_df["Category"], values=avg_weight_df["Weight"],
                                   textinfo='percent+label', hole=0.4)])
    fig3.update_traces(marker=dict(colors=px.colors.qualitative.Set2))
    st.plotly_chart(fig3, use_container_width=True)

# ======= ADDITIONAL PLOTS ============= #
# Category-wise Transaction Value
st.subheader("Category-wise Transaction Value")
category_value_df = df5.groupby("Category")["Value"].sum().reset_index()
fig5 = px.bar(category_value_df, x="Category", y="Value", color="Category", text="Value",
              template="plotly_white")
st.plotly_chart(fig5, use_container_width=True)

# Monthly Trend of Transactions
st.subheader("Monthly Trend of Transactions")
df5["Month"] = df5["Date"].dt.to_period("M").astype(str)
monthly_trend_df = df5.groupby("Month")["Value"].sum().reset_index()
st.write(monthly_trend_df)
fig6 = px.line(monthly_trend_df, x="Month", y="Value", markers=True, template="plotly_dark")
st.plotly_chart(fig6, use_container_width=True)