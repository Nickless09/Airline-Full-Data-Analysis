import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import re
import os
import seaborn as sns

# ------------------- Paths -------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ECONOMY_FILE = os.path.join(BASE_DIR, "dat", "economy.csv")
BUSINESS_FILE = os.path.join(BASE_DIR, "dat", "business.csv")

st.set_page_config(page_title="Airline Data Dashboard", layout="wide")

# ------------------- Load CSV -------------------
@st.cache_data
def load_data(file_path):
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        return pd.DataFrame()
    df = pd.read_csv(file_path)
    df.columns = [c.strip().lower() for c in df.columns]  # normalize column names
    return df

# ------------------- Duration Parser -------------------
def parse_duration(x):
    x = str(x).strip()
    if not x or x.lower() in ['nan', 'none']:
        return None
    match = re.match(r'(?:(\d+)h)?\s*(?:(\d+)m)?', x)
    if match and (match.group(1) or match.group(2)):
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        return hours + minutes/60
    if ':' in x:
        parts = x.split(':')
        if len(parts) == 2:
            try:
                hours = int(parts[0])
                minutes = int(parts[1])
                return hours + minutes/60
            except:
                return None
    try:
        val = float(re.sub(r'[^\d.]', '', x))
        if val > 10:  # assume minutes
            return val / 60
        return val
    except:
        return None

# ------------------- Column Detection -------------------
def get_col(df, *names):
    for n in names:
        if n in df.columns:
            return n
    return None

# ------------------- Sidebar Dataset Selection -------------------
st.sidebar.title("Datasets")
dataset_choice = st.sidebar.radio(
    "Select Dataset",
    ["All Flights", "Economy", "Business"]
)

# Load individual datasets
df_econ = load_data(ECONOMY_FILE)
df_bus = load_data(BUSINESS_FILE)

# Choose dataset based on selection
if dataset_choice == "Economy":
    df = df_econ.copy()
elif dataset_choice == "Business":
    df = df_bus.copy()
else:
    df = pd.concat([df_econ, df_bus], ignore_index=True)

if df.empty:
    st.warning("No data available.")
    st.stop()

# ------------------- Detect columns -------------------
airline_col = get_col(df, "airline", "carrier")
source_col = get_col(df, "source_city", "source", "from")
dest_col = get_col(df, "destination_city", "destination", "to")
class_col = get_col(df, "class", "travel_class")
price_col = get_col(df, "price", "fare", "ticket_price")
duration_col = get_col(df, "duration", "flight_time", "time_taken", "time")
days_left_col = get_col(df, "days_left", "days_before", "daysuntilflight")

# ------------------- Clean Numeric Columns -------------------
for col in [price_col, days_left_col]:
    if col and col in df.columns:
        df[col] = df[col].astype(str).str.replace(r'[^\d.]', '', regex=True)
        df[col] = pd.to_numeric(df[col], errors='coerce')

if duration_col and duration_col in df.columns:
    df[duration_col] = df[duration_col].apply(parse_duration)

# ------------------- Currency Conversion -------------------
currency = st.sidebar.selectbox("Select Currency", ["INR", "USD", "EUR"])
rates = {"INR": 1, "USD": 0.012, "EUR": 0.011}
conversion_rate = rates[currency]

# ------------------- Sidebar Filters -------------------
airlines = st.sidebar.multiselect("Select Airline(s)", df[airline_col].unique(), default=df[airline_col].unique())
sources = st.sidebar.multiselect("Select Source City", df[source_col].unique(), default=df[source_col].unique())
destinations = st.sidebar.multiselect("Select Destination City", df[dest_col].unique(), default=df[dest_col].unique())

classes = None
if class_col:
    classes = st.sidebar.multiselect("Select Class", df[class_col].unique(), default=df[class_col].unique())

# ------------------- Apply Filters -------------------
filtered_df = df[
    (df[airline_col].isin(airlines)) &
    (df[source_col].isin(sources)) &
    (df[dest_col].isin(destinations))
]

if class_col and classes is not None:
    filtered_df = filtered_df[filtered_df[class_col].isin(classes)]

# Convert prices
if price_col:
    filtered_df["converted_price"] = filtered_df[price_col] * conversion_rate
    price_to_use = "converted_price"
else:
    price_to_use = price_col

if filtered_df.empty:
    st.warning("⚠️ No flights match the selected filters.")
    st.stop()

# ------------------- Dashboard -------------------
st.markdown("<h1 style='text-align: center;'>✈️ Airline Fare Dashboard</h1>", unsafe_allow_html=True)
st.markdown(f"Currently viewing **{dataset_choice}** dataset.")

# --- KPIs ---
avg_price = round(filtered_df[price_to_use].mean(), 2)
avg_duration = round(filtered_df[duration_col].mean(), 2)
total_flights = len(filtered_df)
min_price = round(filtered_df[price_to_use].min(), 2)
max_price = round(filtered_df[price_to_use].max(), 2)

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Flights", f"{total_flights:,}".replace(",", "."))
col2.metric(f"Average Price ({currency})", f"{avg_price:,.2f}")
col3.metric("Average Duration (hours)", avg_duration)
col4.metric(f"Cheapest Flight ({currency})", f"{min_price:,.2f}")
col5.metric(f"Most Expensive Flight ({currency})", f"{max_price:,.2f}")

# --- Charts ---
label_map = {
    airline_col: "Airline",
    source_col: "Source City",
    dest_col: "Destination City",
    price_to_use: f"Price ({currency})",
    duration_col: "Duration (hours)",
    days_left_col: "Days Left",
    class_col: "Class"
}

# Average Price by Airline
st.subheader(f"Average Price by Airline ({currency})")
fig1 = px.bar(
    filtered_df.groupby(airline_col)[price_to_use].mean().reset_index(),
    x=airline_col, y=price_to_use, color=airline_col,
    title=f"Average Price per Airline ({currency})",
    labels=label_map
)
st.plotly_chart(fig1, use_container_width=True)

# Average Price by Route
st.subheader(f"Average Price by Source-Destination Route ({currency})")
route_df = filtered_df.groupby([source_col, dest_col])[price_to_use].mean().reset_index()
fig4 = px.bar(
    route_df, x=source_col, y=price_to_use, color=dest_col,
    title=f"Average Price by Route ({currency})", barmode="group",
    labels=label_map
)
st.plotly_chart(fig4, use_container_width=True)

# Price vs Days Left
if days_left_col:
    st.subheader(f"Price vs. Days Left ({currency})")
    fig2 = px.scatter(
        filtered_df, x=days_left_col, y=price_to_use, color=airline_col,
        trendline="ols", title=f"Price vs Days Left by Airline ({currency})",
        labels=label_map
    )
    st.plotly_chart(fig2, use_container_width=True)

# Flight Duration vs Price (scatter or heatmap based on dataset size)
if duration_col:
    n_points = len(filtered_df)
    if n_points < 10000:
        chart_type = "Scatter Plot"
        fig3 = px.scatter(
            filtered_df,
            x=duration_col,
            y=price_to_use,
            color=class_col if class_col else None,
            title=f"Flight Duration vs Price ({currency})" + (" (by Class)" if class_col else ""),
            labels=label_map
        )
    else:
        chart_type = "Density Heatmap"
        fig3 = px.density_heatmap(
            filtered_df,
            x=duration_col,
            y=price_to_use,
            nbinsx=100,
            nbinsy=100,
            color_continuous_scale="Viridis",
            labels=label_map,
            title=f"Flight Duration vs Price Density Heatmap ({currency})"
        )

    with st.expander(f"Show {chart_type}"):
        st.plotly_chart(fig3, use_container_width=True)

# Heatmap of Average Price by Route
if price_to_use and duration_col and not filtered_df.empty:
    with st.expander("Show Flight Duration vs Price Chart"):
        st.subheader(f"Flight Duration vs Price ({currency})")
        fig3 = px.scatter(
            filtered_df,
            x=duration_col,
            y=price_to_use,
            color=class_col if class_col else None,
            title=f"Flight Duration vs Price ({currency})" + (" (by Class)" if class_col else ""),
            labels=label_map,
            size_max=5,   # small points
        )
        fig3.update_traces(marker=dict(size=3, opacity=0.5))  # many small round points
        st.plotly_chart(fig3, use_container_width=True)
