import streamlit as st
import pandas as pd
import plotly.express as px
import re

st.set_page_config(page_title="Airline Data Dashboard", layout="wide")

# ------------------- Load CSV -------------------
@st.cache_data
def load_data(file_path):
    df = pd.read_csv(file_path)
    df.columns = [c.strip().lower() for c in df.columns]  # normalize column names
    return df

# ------------------- Duration Parser -------------------
def parse_duration(x):
    """Converts duration strings to hours (float)"""
    x = str(x).strip()
    if not x or x.lower() in ['nan', 'none']:
        return None
    # 1) Format like "2h 30m" or "2h" or "45m"
    match = re.match(r'(?:(\d+)h)?\s*(?:(\d+)m)?', x)
    if match and (match.group(1) or match.group(2)):
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        return hours + minutes/60
    # 2) Format like "02:30"
    if ':' in x:
        parts = x.split(':')
        if len(parts) == 2:
            try:
                hours = int(parts[0])
                minutes = int(parts[1])
                return hours + minutes/60
            except:
                return None
    # 3) Pure number
    try:
        val = float(re.sub(r'[^\d.]', '', x))
        if val > 10:
            return val / 60  # assume minutes if > 10
        return val
    except:
        return None

# ------------------- Column Detection -------------------
def get_col(df, *names):
    """Return first matching column name"""
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

if dataset_choice == "All Flights":
    df = load_data("dat/Clean_Dataset.csv")
elif dataset_choice == "Economy":
    df = load_data("dat/economy.csv")
else:
    df = load_data("dat/business.csv")

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
currency = st.sidebar.selectbox(
    "Select Currency",
    ["INR", "USD", "EUR"]
)
rates = {"INR": 1, "USD": 0.012, "EUR": 0.011}  # example rates
conversion_rate = rates[currency]

# ------------------- Sidebar Filters -------------------
airlines = st.sidebar.multiselect(
    "Select Airline(s)", df[airline_col].unique(), default=df[airline_col].unique()
)
sources = st.sidebar.multiselect(
    "Select Source City", df[source_col].unique(), default=df[source_col].unique()
)
destinations = st.sidebar.multiselect(
    "Select Destination City", df[dest_col].unique(), default=df[dest_col].unique()
)
if class_col:
    classes = st.sidebar.multiselect(
        "Select Class", df[class_col].unique(), default=df[class_col].unique()
    )
else:
    classes = None



# ------------------- Apply Filters -------------------
filtered_df = df[
    (df[airline_col].isin(airlines)) &
    (df[source_col].isin(sources)) &
    (df[dest_col].isin(destinations))
].copy()

if class_col and classes is not None:
    filtered_df = filtered_df[filtered_df[class_col].isin(classes)]

# Convert prices
if price_col:
    filtered_df["converted_price"] = filtered_df[price_col] * conversion_rate
    price_to_use = "converted_price"
else:
    price_to_use = price_col

# ------------------- Dashboard -------------------
st.title("✈️ Airline Fare Dashboard")
st.markdown(f"Currently viewing **{dataset_choice}** dataset.")

# --- KPIs ---
avg_price = round(filtered_df[price_to_use].mean(), 2) if price_to_use else 0
avg_duration = round(filtered_df[duration_col].mean(), 2) if duration_col else 0
total_flights = len(filtered_df)
min_price = round(filtered_df[price_to_use].min(), 2) if price_to_use and not filtered_df.empty else 0
max_price = round(filtered_df[price_to_use].max(), 2) if price_to_use and not filtered_df.empty else 0

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Flights", total_flights)
col2.metric(f"Average Price ({currency})", avg_price)
col3.metric("Average Duration (hours)", avg_duration)
col4.metric(f"Cheapest Flight ({currency})", min_price)
col5.metric(f"Most Expensive Flight ({currency})", max_price)

# --- Charts ---
if price_to_use:
    st.subheader(f"Average Price by Airline ({currency})")
    fig1 = px.bar(
        filtered_df.groupby(airline_col)[price_to_use].mean().reset_index(),
        x=airline_col, y=price_to_use, color=airline_col,
        title=f"Average Price per Airline ({currency})"
    )
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader(f"Average Price by Source-Destination Route ({currency})")
    route_df = filtered_df.groupby([source_col, dest_col])[price_to_use].mean().reset_index()
    fig4 = px.bar(
        route_df, x=source_col, y=price_to_use, color=dest_col,
        title=f"Average Price by Route ({currency})", barmode="group"
    )
    st.plotly_chart(fig4, use_container_width=True)

if price_to_use and days_left_col:
    st.subheader(f"Price vs. Days Left ({currency})")
    fig2 = px.scatter(
        filtered_df, x=days_left_col, y=price_to_use, color=airline_col,
        trendline="ols", title=f"Price vs Days Left by Airline ({currency})"
    )
    st.plotly_chart(fig2, use_container_width=True)

if price_to_use and duration_col:
    st.subheader(f"Flight Duration vs. Price ({currency})")
    fig3 = px.scatter(
        filtered_df, x=duration_col, y=price_to_use, color=class_col if class_col else None,
        title=f"Flight Duration vs Price ({currency})" + (" (by Class)" if class_col else "")
    )
    st.plotly_chart(fig3, use_container_width=True)

st.markdown("Data source: Clean_Dataset, Economy, Business CSV files")

